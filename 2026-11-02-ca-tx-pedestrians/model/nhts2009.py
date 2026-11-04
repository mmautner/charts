"""Walking in California and Texas from the 2009 NHTS, with jackknife standard errors, for comparison with 2017.

Per person (age 5+), per year:
  walk trips = sum(WTTRDFIN x walk trips) / sum(WTPERFIN)          TRPTRANS 23 = walk (2009 codes)
  all trips  = same with every trip
  walk share = walk trips / all trips
  weekly-recall walks = NWALKTRP (walks in the past 7 days) x 52, persons with a valid answer
WTTRDFIN = 365 x WTPERFIN on the day file (checked below).

Variance: 100 jackknife replicates (2009 NHTS User's Guide, p. 7-1): Var = (99/100) x sum_r (theta_r - theta)^2.
Person replicates WTPERFIN1-100 and travel-day replicates DAYWGT1-100 come from per50wt.csv.

Usage: python -I model/nhts2009.py raw/nhts2009/x data
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
R, FACT = 100, 99 / 100
URL = "https://nhts.ornl.gov/2009/download/Ascii.zip (replicates: ReplicatesASCII.zip)"
key = ["HOUSEID", "PERSONID"]
ID = {"HOUSEID": str, "PERSONID": str, "HHSTATE": str}

per = pd.read_csv(SRC / "PERV2PUB.CSV", dtype=ID, usecols=key + ["HHSTATE", "WTPERFIN", "NWALKTRP"])
per = per[per.HHSTATE.isin(["CA", "TX"])]
day = pd.read_csv(SRC / "DAYV2PUB.CSV", dtype=ID, usecols=key + ["HHSTATE", "TRPTRANS", "WTTRDFIN"])
day = day[day.HHSTATE.isin(["CA", "TX"])]
PF = [f"WTPERFIN{i}" for i in range(1, R + 1)]
DW = [f"DAYWGT{i}" for i in range(1, R + 1)]
rep = pd.read_csv(SRC / "per50wt.csv", dtype={"HOUSEID": str, "PERSONID": str}, usecols=key + PF + ["WTPERFIN"] + DW + ["DAYWGT"])
rep = rep.rename(columns={"WTPERFIN": "WTPERFIN_rep0", "DAYWGT": "DAYWGT0"})

agg = pd.DataFrame({"trips_all": day.groupby(key).size(),
                    "walk_trips": day[day.TRPTRANS == 23].groupby(key).size()}).reset_index()
P = per.merge(rep, on=key, validate="1:1").merge(agg, on=key, how="left")
P[["trips_all", "walk_trips"]] = P[["trips_all", "walk_trips"]].fillna(0.0)
assert np.allclose(P.WTPERFIN, P.WTPERFIN_rep0)
tw = day.drop_duplicates(key).merge(per[key + ["WTPERFIN"]], on=key)
assert np.allclose(tw.WTTRDFIN, 365 * tw.WTPERFIN)
# DAYWGT (replicate file) is already annualized: 365 x the person weight, blank for persons with no trips
present = P.DAYWGT0.notna()
assert np.allclose(P.DAYWGT0[present], 365 * P.WTPERFIN[present])
assert np.allclose(P.DAYWGT1[present], 365 * P.WTPERFIN1[present])
P = P.copy()
P[["DAYWGT0"] + DW] = P[["DAYWGT0"] + DW].fillna(0.0)
assert (P.trips_all[~present] == 0).all()

Wp = P[["WTPERFIN"] + PF].to_numpy()
Wd = P[["DAYWGT0"] + DW].to_numpy()
P["nwalk_wk"] = P.NWALKTRP.where(P.NWALKTRP >= 0, np.nan)

rows = []
for st, name in [("CA", "California"), ("TX", "Texas")]:
    m = (P.HHSTATE == st).to_numpy()
    persons = Wp[m].sum(0)
    walk = (Wd[m] * P.walk_trips.to_numpy()[m, None]).sum(0)
    alltr = (Wd[m] * P.trips_all.to_numpy()[m, None]).sum(0)
    ok = m & P.nwalk_wk.notna().to_numpy()
    recall = 52 * (Wp[ok] * P.nwalk_wk.to_numpy()[ok, None]).sum(0) / Wp[ok].sum(0)
    se = lambda th: float(np.sqrt(FACT * ((th[1:] - th[0]) ** 2).sum()))
    n_hh, n_p = P[m].HOUSEID.nunique(), int(m.sum())
    n_walk = int(day[(day.HHSTATE == st) & (day.TRPTRANS == 23)].shape[0])
    for measure, th, unit, n in [("walk_trips_per_person", walk / persons, "walk trips per person per year", n_walk),
                                 ("trips_per_person", alltr / persons, "trips per person per year", int((day.HHSTATE == st).sum())),
                                 ("walk_share_of_trips", walk / alltr, "share of trips", n_walk),
                                 ("weekly_recall_walks_per_person", recall, "walks per person per year (past-7-days x 52)", int(ok.sum()))]:
        rows.append(dict(survey="NHTS 2009", geo=name, measure=measure, value=th[0], unit=unit, se=se(th),
                         moe90=1.645 * se(th), n_unweighted=n, households=n_hh, persons=n_p, source=URL))
    rows.append(dict(survey="NHTS 2009", geo=name, measure="persons_age5plus", value=persons[0], unit="persons",
                     se=se(persons), moe90=1.645 * se(persons), n_unweighted=n_p, households=n_hh, persons=n_p, source=URL))
df = pd.DataFrame(rows)
df.to_csv(OUT / "nhts2009_walking.csv", index=False)
print(df[["geo", "measure", "value", "se", "n_unweighted", "households"]].to_string())
