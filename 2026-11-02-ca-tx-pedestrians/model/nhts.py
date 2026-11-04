"""Walking in California and Texas from the 2017 NHTS, with jackknife standard errors.

Per person (age 5+, the NHTS person universe), per year:
  walk trips  = sum(WTTRDFIN x walk trip) / sum(WTPERFIN)          TRPTRANS 01 = walk
  walk miles  = same with TRPMILES (trips with TRPMILES < 0 dropped from miles only)
  walk minutes = same with TRVLCMIN (trips with TRVLCMIN < 0 dropped from minutes only)
Also state totals (annual walk trips, miles, hours), the share of trips that are walks, and the
weekly-recall measure NWALKTRP (walks in the past 7 days, including walks for exercise) x 52.

Variance: JKn, 98 replicates in 14 strata of 7 (2017 NHTS Weighting Report s2.2):
  Var = (6/7) x sum_r (theta_r - theta)^2. Every statistic is recomputed under each replicate.

Geography: HHSTATE (home state). Sensitivity groups drop the largest metro in each state
(HH_CBSA 31080 Los Angeles-Long Beach-Anaheim; 19100 Dallas-Fort Worth; 26420 Houston).

Usage: python -I model/nhts.py raw/nhts/x data
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
R, FACT = 98, 6.0 / 7.0
key = ["HOUSEID", "PERSONID"]
ID = {"HOUSEID": str, "PERSONID": str, "HHSTATE": str, "HH_CBSA": str, "SMPLSRCE": str}

hh = pd.read_csv(SRC / "hhpub.csv", dtype=ID, usecols=["HOUSEID", "HHSTATE", "HH_CBSA", "SMPLSRCE"])
hh = hh[hh.HHSTATE.isin(["CA", "TX"])]
per = pd.read_csv(SRC / "perpub.csv", dtype=ID, usecols=key + ["NWALKTRP", "R_AGE"])
trip = pd.read_csv(SRC / "trippub.csv", dtype=ID,
                   usecols=key + ["TRPTRANS", "TRPMILES", "TRVLCMIN", "LOOP_TRIP", "WHYTRP1S"])
pw = pd.read_sas(SRC / "perwgt.sas7bdat", encoding="latin-1")
PF = ["WTPERFIN"] + [f"WTPERFIN{i}" for i in range(1, R + 1)]
TD = ["WTTRDFIN"] + [f"WTTRDFIN{i}" for i in range(1, R + 1)]
pw = pw[key + PF + TD]
for c in key:
    pw[c] = pw[c].astype(str).str.strip()
assert np.allclose(pw.WTTRDFIN, 365 * pw.WTPERFIN)

t = trip[trip.HOUSEID.isin(hh.HOUSEID)]
walk = t[t.TRPTRANS == 1]
# Cleaned miles: TRPMILES is a routed distance and has implausible values (two Texas "walk" trips of
# 1,537 and 1,153 miles with no duration). Keep walk trips with a valid duration, and drop trips over
# 1 mile whose implied speed is above 6 mph.
_mph = walk.TRPMILES / (walk.TRVLCMIN.clip(lower=1) / 60)
CLEAN = (walk.TRPMILES >= 0) & (walk.TRVLCMIN > 0) & ~((walk.TRPMILES > 1) & (_mph > 6))
agg = pd.DataFrame({
    "trips_all": t.groupby(key).size(),
    "walk_trips": walk.groupby(key).size(),
    "walk_trips_noloop": walk[walk.LOOP_TRIP != 1].groupby(key).size(),
    "walk_miles": walk[walk.TRPMILES >= 0].groupby(key).TRPMILES.sum(),
    "walk_mins": walk[walk.TRVLCMIN >= 0].groupby(key).TRVLCMIN.sum(),
    "walk_miles_clean": walk[CLEAN].groupby(key).TRPMILES.sum(),
}).reset_index()
P = (per.merge(hh, on="HOUSEID", validate="m:1").merge(pw, on=key, validate="1:1")
     .merge(agg, on=key, how="left"))
P = P.copy()
for c in ("trips_all", "walk_trips", "walk_trips_noloop", "walk_miles", "walk_mins", "walk_miles_clean"):
    P[c] = P[c].fillna(0.0)
P["nwalk_wk"] = P.NWALKTRP.where(P.NWALKTRP >= 0, np.nan)   # -9/-8/-7 = missing

N_MISS = {"walk_miles": int((walk.TRPMILES < 0).sum()), "walk_mins": int((walk.TRVLCMIN < 0).sum()),
          "dropped_by_miles_cleaning": int((~CLEAN).sum())}

GROUPS = {
    "California": lambda d: d.HHSTATE == "CA",
    "Texas": lambda d: d.HHSTATE == "TX",
    "California excl. Los Angeles metro": lambda d: (d.HHSTATE == "CA") & (d.HH_CBSA != "31080"),
    "Texas excl. Dallas-Fort Worth metro": lambda d: (d.HHSTATE == "TX") & (d.HH_CBSA != "19100"),
    "Texas excl. Dallas-Fort Worth and Houston metros": lambda d: (d.HHSTATE == "TX") & ~d.HH_CBSA.isin(["19100", "26420"]),
    "Los Angeles metro": lambda d: (d.HHSTATE == "CA") & (d.HH_CBSA == "31080"),
}


def reps(num, W):
    """Weighted total under the full weight and each replicate: array of length 99."""
    return (W * num[:, None]).sum(0)


rows = []
for g, f in GROUPS.items():
    d = P[f(P)]
    Wt, Wp = d[TD].values, d[PF].values
    pop = reps(np.ones(len(d)), Wp)
    base = dict(group=g, n_households=d.HOUSEID.nunique(), n_persons=len(d),
                n_walk_trips=int((d.walk_trips).sum()))
    for m, col in [("walk_trips", "walk_trips"), ("walk_trips_excl_loop", "walk_trips_noloop"),
                   ("walk_miles", "walk_miles"), ("walk_miles_cleaned", "walk_miles_clean"), ("walk_minutes", "walk_mins"), ("all_trips", "trips_all")]:
        tot = reps(d[col].values, Wt)
        rows.append(base | dict(measure=f"{m}_annual_total", theta=tot))
        rows.append(base | dict(measure=f"{m}_per_person_per_year", theta=tot / pop))
    wt, at = reps(d.walk_trips.values, Wt), reps(d.trips_all.values, Wt)
    rows.append(base | dict(measure="walk_share_of_trips", theta=wt / at))
    ok = d.nwalk_wk.notna().values
    wk = reps(d.nwalk_wk.fillna(0).values, Wp) / reps(ok.astype(float), Wp)
    rows.append(base | dict(measure="weekly_recall_walks_per_person_per_year", theta=52 * wk,
                            n_persons=int(ok.sum())))
    rows.append(base | dict(measure="persons_age5plus", theta=pop))

out = []
for r in rows:
    th = r.pop("theta")
    se = np.sqrt(FACT * ((th[1:] - th[0]) ** 2).sum())
    out.append(r | dict(estimate=th[0], se=se, replicates=th))
df = pd.DataFrame(out)

# CA / TX ratios of per-person walking, with replicate SEs (same replicate index = same design)
for m in ["walk_trips", "walk_miles", "walk_miles_cleaned", "walk_minutes"]:
    a = df[(df.group == "California") & (df.measure == f"{m}_per_person_per_year")].replicates.iloc[0]
    b = df[(df.group == "Texas") & (df.measure == f"{m}_per_person_per_year")].replicates.iloc[0]
    th = a / b
    df.loc[len(df)] = dict(group="California / Texas", measure=f"{m}_per_person_ratio", estimate=th[0],
                           se=np.sqrt(FACT * ((th[1:] - th[0]) ** 2).sum()), replicates=th,
                           n_households=np.nan, n_persons=np.nan, n_walk_trips=np.nan)

df.drop(columns="replicates").to_csv(OUT / "nhts2017_walking.csv", index=False)
# replicate totals are kept (small) so model/rates.py can carry the jackknife into death rates
rep = df[df.measure.str.endswith("_annual_total")][["group", "measure", "replicates"]]
pd.DataFrame([[g, m] + list(v) for g, m, v in rep.itertuples(index=False)],
             columns=["group", "measure"] + [f"r{i}" for i in range(R + 1)]).to_csv(OUT / "nhts2017_walk_totals_replicates.csv", index=False)

pd.set_option("display.width", 200)
show = df.drop(columns="replicates")
show["moe90"] = 1.645 * show.se
print(show[~show.measure.str.endswith("annual_total")].to_string(index=False, float_format=lambda x: f"{x:,.3f}"))
print("\nwalk trips missing TRPMILES / TRVLCMIN (CA+TX):", N_MISS)
print("sample source by state (01 national, 02 add-on):")
print(pd.crosstab(hh.HHSTATE, hh.SMPLSRCE))
