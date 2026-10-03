#!/usr/bin/env python3
"""Download the 2017 National Household Travel Survey (NHTS) public-use files and
summarize them to weighted estimates by the home county's metro size, with jackknife
margins of error. Saves the small summary and a metadata file to data/. The raw files
are ~1.2 GB unzipped, so they are not committed; the summary plus the fetch date is
enough to reproduce the charts.

Source: FHWA, 2017 NHTS public-use files and replicate weights.
https://nhts.ornl.gov/  (csv.zip, Replicates.zip; codebook v1.2)

Needs pandas and scipy in addition to ../requirements.txt.
Tested with Python 3.12.3, pandas==3.0.2, numpy==2.4.4, scipy==1.17.1.
pandas.read_sas reads the .sas7bdat replicate-weight files; no pyreadstat needed.

Usage:
    python fetch_nhts.py               # download to a temp folder, then summarize
    python fetch_nhts.py --dir nhts    # keep (or reuse) the raw files in ./nhts
"""
import argparse, datetime, json, tempfile
import shutil
import sys
import urllib.request
import warnings
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.simplefilter("ignore", pd.errors.PerformanceWarning)   # wide replicate-weight frames

HERE = Path(__file__).resolve().parent
_ap = argparse.ArgumentParser()
_ap.add_argument("--dir", help="folder holding (or to receive) the raw NHTS files; default: a temp folder")
_args = _ap.parse_args()
DATA = Path(_args.dir).resolve() if _args.dir else Path(tempfile.mkdtemp(prefix="nhts2017-"))
OUT = HERE / "data"
BASE = "https://nhts.ornl.gov/assets/2016/download/"

R, N_STRATA = 98, 14
FACT = 6.0 / 7.0                       # JKn: n_h = 7 units per variance stratum -> (n_h-1)/n_h
T_CRIT = stats.t.ppf(0.975, R - N_STRATA)   # 84 df = 1.989


# ---------------------------------------------------------------- data access
def fetch(zip_name, members):
    DATA.mkdir(parents=True, exist_ok=True)
    if all((DATA / m).exists() for m in members):
        return
    zpath = DATA / zip_name
    if not zpath.exists():
        print(f"downloading {BASE + zip_name} ...", file=sys.stderr, flush=True)
        req = urllib.request.Request(BASE + zip_name, headers={"User-Agent": "Mozilla/5.0"})
        tmp = zpath.with_suffix(".part")
        with urllib.request.urlopen(req, timeout=600) as r, open(tmp, "wb") as f:
            shutil.copyfileobj(r, f)
        tmp.rename(zpath)
    with zipfile.ZipFile(zpath) as z:
        names = {Path(n).name.lower(): n for n in z.namelist()}
        for m in members:
            with z.open(names[m.lower()]) as src, open(DATA / m, "wb") as dst:
                shutil.copyfileobj(src, dst)


fetch("csv.zip", ["hhpub.csv", "vehpub.csv", "perpub.csv", "trippub.csv"])
fetch("Replicates.zip", ["hhwgt.sas7bdat", "perwgt.sas7bdat"])

ID = {"HOUSEID": str, "PERSONID": str}
hh = pd.read_csv(DATA / "hhpub.csv", dtype={"HOUSEID": str, "MSASIZE": str, "URBRUR": str},
                 usecols=["HOUSEID", "MSASIZE", "URBRUR", "HHSIZE", "HHVEHCNT", "WTHHFIN"])
veh = pd.read_csv(DATA / "vehpub.csv", dtype={"HOUSEID": str}, usecols=["HOUSEID", "BESTMILE"])
per = pd.read_csv(DATA / "perpub.csv", dtype=ID, usecols=["HOUSEID", "PERSONID", "DRIVER", "WTPERFIN"])
trip = pd.read_csv(DATA / "trippub.csv", dtype=ID,
                   usecols=["HOUSEID", "PERSONID", "WTTRDFIN", "DRVR_FLG", "TRPTRANS", "VMT_MILE", "TRVLCMIN"])
hw = pd.read_sas(DATA / "hhwgt.sas7bdat", encoding="latin-1")
pw = pd.read_sas(DATA / "perwgt.sas7bdat", encoding="latin-1")

HCOLS = ["WTHHFIN"] + [f"WTHHFIN{i}" for i in range(1, R + 1)]
TD = ["WTTRDFIN"] + [f"WTTRDFIN{i}" for i in range(1, R + 1)]     # annualized travel-day weights
PF = ["WTPERFIN"] + [f"WTPERFIN{i}" for i in range(1, R + 1)]     # person weights

# ------------------------------------------------------------- sanity checks
assert round(hh.WTHHFIN.sum()) == 118_208_251, "household weight total"
assert round(per.loc[per.DRIVER == 1, "WTPERFIN"].sum()) == 223_277_172, "licensed driver total"
assert len(hw) == len(hh) and len(pw) == len(per)
m = hh[["HOUSEID", "WTHHFIN"]].merge(hw[["HOUSEID", "WTHHFIN"]], on="HOUSEID", validate="1:1")
assert np.allclose(m.WTHHFIN_x, m.WTHHFIN_y), "replicate file full-sample weight != public file"
assert np.allclose(pw.WTTRDFIN, 365 * pw.WTPERFIN)
_dv = trip[(trip.DRVR_FLG == 1) & (trip.VMT_MILE >= 0)]
VMT_TOTAL = (_dv.WTTRDFIN * _dv.VMT_MILE).sum()
assert round(VMT_TOTAL / 1e6) == 2_105_882, "FHWA Table 1d household VMT (millions)"

# ------------------------------------------------------------------ estimator
def ratio(num, den, Wn, Wd=None, scale=1.0):
    """Ratio estimator sum(w*num)/sum(w*den), recomputed under the full-sample weight
    (column 0) and each of the 98 replicate weights (columns 1-98); MOE is the JKn
    variance from the replicate spread. Wd defaults to Wn."""
    Wd = Wn if Wd is None else Wd
    th = scale * (Wn * num[:, None]).sum(0) / (Wd * den[:, None]).sum(0)
    return th[0], T_CRIT * np.sqrt(FACT * ((th[1:] - th[0]) ** 2).sum())


# ---------------------------------------------------------------- groupings
MSA_LABEL = {"01": "MSA <250k", "02": "MSA 250k-499,999", "03": "MSA 500k-999,999",
             "04": "MSA 1M-2.99M", "05": "MSA 3M+", "06": "Not in MSA"}
GROUPS = [
    ("NATIONAL", lambda d: np.ones(len(d), bool)),
    ("Not in MSA", lambda d: (d.MSASIZE == "06").values),
    ("MSA under 1M", lambda d: d.MSASIZE.isin(["01", "02", "03"]).values),
    ("MSA 1M+", lambda d: d.MSASIZE.isin(["04", "05"]).values),
] + [(f"  {k}={v}", (lambda kk: lambda d: (d.MSASIZE == kk).values)(k)) for k, v in MSA_LABEL.items()]
URB = [("NATIONAL", lambda d: np.ones(len(d), bool)),
       ("  01=Urban", lambda d: (d.URBRUR == "01").values),
       ("  02=Rural", lambda d: (d.URBRUR == "02").values)]

records = []


def add(item, group, est, moe=np.nan, n_hh=np.nan, n_persons=np.nan):
    records.append(dict(item=item, group=group.strip(), estimate=est, moe=moe, n_hh=n_hh, n_persons=n_persons))


# ------------------------------------------------- household miles (items 1, 2a)
veh["missing"] = veh.BESTMILE < 0                       # -9 = not ascertained
veh["ok_miles"] = veh.BESTMILE.where(~veh.missing, 0.0)
g = veh.groupby("HOUSEID").agg(nveh=("BESTMILE", "size"), n_missing=("missing", "sum"), miles=("ok_miles", "sum"))
H = hh.merge(hw.drop(columns="WTHHFIN"), on="HOUSEID", validate="1:1").merge(g, on="HOUSEID", how="left")
H[["nveh", "n_missing", "miles"]] = H[["nveh", "n_missing", "miles"]].fillna(0)
assert (H.nveh == H.HHVEHCNT).all()
# Choice: a household with ANY vehicle whose BESTMILE is missing has an unknown total, so it is
# dropped (complete-case). Zero-vehicle households have no vehicles to be missing and count as 0 miles.
# The sensitivity table bounds the effect by instead counting missing vehicles as 0 miles.
H = H.assign(valid=H.n_missing == 0, M=H.miles.where(H.n_missing == 0, np.nan), M_lb=H.miles)
N_DROP = int((~H.valid).sum())
SHARE_DROP = H.loc[~H.valid, "WTHHFIN"].sum() / H.WTHHFIN.sum()


def hh_miles_rows(frame, groups, tag, per_person=False):
    for name, f in groups:
        d = frame[f(frame)]
        for sub, keep in (("all_hh", d.valid), ("excl_zero_veh", d.valid & (d.HHVEHCNT > 0))):
            s = d[keep]
            den = s.HHSIZE.values.astype(float) if per_person else np.ones(len(s))
            # per-person: sum(w*miles)/sum(w*HHSIZE), i.e. person-weighted with weight WTHHFIN x HHSIZE
            est, moe = ratio(s.M.values, den, s[HCOLS].values)
            add(f"{tag}_{sub}", name, est, moe, n_hh=len(s))


hh_miles_rows(H, GROUPS, "1_hh_miles")
hh_miles_rows(H, URB, "1x_hh_miles_urbrur")
hh_miles_rows(H, GROUPS, "2a_miles_per_person", per_person=True)

# -------------------------------------------- trip file: items 2b and 3
# Choice: only DRVR_FLG == 1 trips (respondent drove) count as driving. VMT_MILE and TRVLCMIN are
# defined only for those trips. Trips with a missing (-9/-1) distance or duration are dropped from
# that measure alone, so miles and minutes each use every trip valid for them.
dr = trip[trip.DRVR_FLG == 1].copy()
okv, okm = dr.VMT_MILE >= 0, dr.TRVLCMIN >= 0
key = ["HOUSEID", "PERSONID"]
vmt_v = dr[okv].groupby(key).VMT_MILE.sum().rename("vmt_v")
min_v = dr[okm].groupby(key).TRVLCMIN.sum().rename("mins_v")
both = dr[okv & okm].groupby(key).agg(vmt=("VMT_MILE", "sum"), mins=("TRVLCMIN", "sum"))

P = (per.drop(columns="WTPERFIN")
     .merge(pw[key + PF + TD], on=key, validate="1:1")
     .merge(vmt_v, on=key, how="left").merge(min_v, on=key, how="left").merge(both, on=key, how="left")
     .merge(hh[["HOUSEID", "MSASIZE", "URBRUR"]], on="HOUSEID", validate="m:1"))
for c in ("vmt_v", "mins_v", "vmt", "mins"):
    P[c] = P[c].fillna(0.0)     # persons with no driving trips count as 0 (item 3 includes non-drivers-that-day)
assert len(P) == len(per) and not (P[P.DRIVER != 1].vmt_v > 0).any()

# Item 2b: annual driven VMT per person. Numerator uses annualized trip weights (WTTRDFIN = 365 x
# WTPERFIN), denominator uses person weights, so the ratio is recomputed under the matching replicate.
for name, f in GROUPS:
    d = P[f(P)]
    est, moe = ratio(d.vmt_v.values, np.ones(len(d)), d[TD].values, d[PF].values)
    add("2b_diary_vmt_per_person", name, est, moe, n_hh=int(f(hh).sum()), n_persons=len(d))

# Item 3: per licensed driver (DRIVER == 1) on the travel day.
Dv = P[P.DRIVER == 1]
for name, f in GROUPS:
    d = Dv[f(Dv)]
    W, one = d[TD].values, np.ones(len(d))
    nh, npn = d.HOUSEID.nunique(), len(d)
    e, mo = ratio(d.mins_v.values, one, W); add("3_minutes_per_driver_day", name, e, mo, nh, npn)
    e, mo = ratio(d.vmt_v.values, one, W); add("3_miles_per_driver_day", name, e, mo, nh, npn)
    # mph(pairs): miles and minutes summed over the same trips (both valid); mph(means): ratio of the two daily means
    e, mo = ratio(d.vmt.values, d.mins.values, W, scale=60); add("3_mph_pairs", name, e, mo, nh, npn)
    e, mo = ratio(d.vmt_v.values, d.mins_v.values, W, scale=60); add("3_mph_means", name, e, mo, nh, npn)

# ------------------------------------------------------------ sensitivity
for name, f in GROUPS[:4]:
    d = H[f(H)]
    s = d[d.valid]
    est_cc, _ = ratio(s.M.values, np.ones(len(s)), s[HCOLS].values)
    est_lb, _ = ratio(d.M_lb.values, np.ones(len(d)), d[HCOLS].values)
    share = 100 * d.loc[~d.valid, "WTHHFIN"].sum() / d.WTHHFIN.sum()
    add("sens_complete_case_mean", name, est_cc, n_hh=len(s))
    add("sens_missing_as_zero_mean", name, est_lb, n_hh=len(d))
    add("sens_dropped_weight_share_pct", name, share, n_hh=int((~d.valid).sum()))

# ---------------------------------------------- extra: person-weight version of 2a
Q = P[key + ["MSASIZE", "URBRUR"] + PF].merge(H[["HOUSEID", "M", "HHSIZE", "valid"]], on="HOUSEID", validate="m:1")
Q = Q[Q.valid].assign(pm=lambda x: x.M / x.HHSIZE)
for name, f in GROUPS:
    d = Q[f(Q)]
    est, moe = ratio(d.pm.values, np.ones(len(d)), d[PF].values)
    add("2c_miles_per_person_wtperfin", name, est, moe, n_hh=d.HOUSEID.nunique(), n_persons=len(d))

# ------------------------------------------------------------------ output
rec = pd.DataFrame(records)
OUT.mkdir(exist_ok=True)
rec.to_csv(OUT / "nhts2017_estimates.csv", index=False, columns=["item", "group", "estimate", "moe", "n_hh", "n_persons"])
look = {(r.item, r.group): r for r in rec.itertuples()}


def fmt(x, d=0):
    return f"{x:,.{d}f}"


def render(title, header, rows):
    w = [max(len(str(r[i])) for r in [header] + rows) for i in range(len(header))]
    line = lambda r: "  ".join([str(r[0]).ljust(w[0])] + [str(r[i]).rjust(w[i]) for i in range(1, len(header))])
    return "\n".join([title, line(header), "-" * len(line(header))] + [line(r) for r in rows])


def hh_table(title, groups, tag):
    rows = []
    for disp, _ in groups:
        a, b = look[(f"{tag}_all_hh", disp.strip())], look[(f"{tag}_excl_zero_veh", disp.strip())]
        rows.append([disp, fmt(a.estimate), fmt(a.moe), fmt(a.n_hh), fmt(b.estimate), fmt(b.moe), fmt(b.n_hh)])
    return render(title, ["", "est(all hh)", "+/-MOE", "n_hh", "est(excl 0-veh)", "+/-MOE", "n_hh"], rows)


T1 = hh_table("ITEM 1. Avg annual household vehicle miles (BESTMILE summed per hh; household-weighted)", GROUPS, "1_hh_miles")
T1u = hh_table("ITEM 1 cross-check by URBRUR", URB, "1x_hh_miles_urbrur")
T2 = hh_table("ITEM 2a. Annual household vehicle miles per person (sum hh miles / sum persons; weight = WTHHFIN x HHSIZE)",
              GROUPS, "2a_miles_per_person")

rows = []
for disp, _ in GROUPS:
    r = look[("2b_diary_vmt_per_person", disp.strip())]
    rows.append([disp, fmt(r.estimate), fmt(r.moe), fmt(r.n_hh), fmt(r.n_persons)])
T2b = render("ITEM 2b. Annual personally-driven VMT per person, from travel-day trips (VMT_MILE x WTTRDFIN / sum WTPERFIN; persons in person file)",
             ["", "est", "+/-MOE", "n_hh", "n_persons"], rows)

rows = []
for disp, _ in GROUPS:
    k = disp.strip()
    a, b, c, e = (look[(f"3_{t}", k)] for t in ("minutes_per_driver_day", "miles_per_driver_day", "mph_pairs", "mph_means"))
    rows.append([disp, fmt(a.estimate, 1), fmt(a.moe, 1), fmt(b.estimate, 1), fmt(b.moe, 1), fmt(c.estimate, 1),
                 fmt(c.moe, 1), fmt(e.estimate, 1), fmt(e.moe, 1), fmt(a.n_hh), fmt(a.n_persons)])
T3 = render("ITEM 3. Travel-day private-vehicle driving per licensed driver (DRIVER==1; drivers with no driving trips count as 0)",
            ["", "min/day", "+/-MOE", "mi/day", "+/-MOE", "mph(pairs)", "+/-MOE", "mph(means)", "+/-MOE", "n_hh", "n_drivers"], rows)

rows = []
for disp, _ in GROUPS[:4]:
    k = disp.strip()
    cc, lb, sh = look[("sens_complete_case_mean", k)], look[("sens_missing_as_zero_mean", k)], look[("sens_dropped_weight_share_pct", k)]
    rows.append([disp, fmt(cc.estimate), fmt(lb.estimate), fmt(lb.n_hh), fmt(sh.n_hh), f"{sh.estimate:.1f}%"])
TS = render("SENSITIVITY: complete-case vs missing-BESTMILE-as-zero lower bound (all hh)",
            ["", "complete-case", "missing=0 (lower bd)", "n_hh all", "n_hh dropped", "wtd share dropped"], rows)

rows = []
for disp, _ in GROUPS:
    r = look[("2c_miles_per_person_wtperfin", disp.strip())]
    rows.append([disp, fmt(r.estimate), fmt(r.moe), fmt(r.n_hh), fmt(r.n_persons)])
T2c = render("EXTRA ITEM 2c. Household BESTMILE / HHSIZE per person in person file (persons 5+), weight = WTPERFIN (complete-case hh, all hh incl. 0-veh)",
             ["", "est", "+/-MOE", "n_hh", "n_persons"], rows)

TRANS = {3: "car", 4: "SUV", 6: "pickup", 5: "van", 8: "motorcycle/moped", 18: "rental car", 7: "golf cart", 9: "RV"}
trans = " | ".join(f"{k:02d} {TRANS.get(k, '?')} {v:,}" for k, v in dr.TRPTRANS.value_counts().items())
HEADER = f"""NHTS 2017 weighted estimates (computed from public-use files; nothing estimated or filled in)

FILES ({BASE}csv.zip, Replicates.zip, codebook_v1.2.xlsx)
  hhpub.csv {len(hh):,} hh | vehpub.csv {len(veh):,} veh | perpub.csv {len(per):,} persons | trippub.csv {len(trip):,} trips
  Replicate weights are NOT in the 4 CSVs. Separate Replicates.zip: hhwgt.sas7bdat (WTHHFIN1-98), perwgt.sas7bdat (WTPERFIN1-98, WTTRDFIN1-98)

CODES (codebook_v1.2.xlsx)
  MSASIZE (hhpub): 01 MSA <250,000 | 02 250,000-499,999 | 03 500,000-999,999 | 04 MSA/CMSA 1,000,000-2,999,999 | 05 3 million+ | 06 Not in MSA/CMSA
    Groups: Not in MSA = 06 | MSA under 1M = 01,02,03 | MSA 1M+ = 04,05
  URBRUR (hhpub): 01 Urban | 02 Rural
  BESTMILE (vehpub): annual miles, 0-200,000; -9 = not ascertained ({int(veh.missing.sum()):,} vehicles). HHSIZE, HHVEHCNT (hhpub; HHVEHCNT equals vehicle rows in every hh)
  DRIVER (perpub): 01 yes | 02 no | -1 skip. Licensed driver = 01 ({per.loc[per.DRIVER == 1, 'WTPERFIN'].sum():,.0f} weighted, matches FHWA Table 4 "drivers")
  DRVR_FLG (trippub): 01 = respondent drove on trip. VMT_MILE: miles, personally driven vehicle trips (-1 skip, -9 NA). TRVLCMIN: minutes (-9 NA)
    DRVR_FLG=1 trips by TRPTRANS: {trans}

WEIGHTS
  Households and vehicles: WTHHFIN (sum {hh.WTHHFIN.sum():,.0f}). Weighting report: vehicle weights are the household weights, so vehpub uses hhpub WTHHFIN
  Persons: WTPERFIN (sum {per.WTPERFIN.sum():,.0f}; person file is essentially age 5+)
  Travel-day person/trip: WTTRDFIN = 365 x WTPERFIN exactly (annualized). Trip-file WTTRDFIN equals the person-level value; replicates come from perwgt
VARIANCE: stratified jackknife (JKn), 98 replicates = 14 strata x 7 units (2017 NHTS Weighting Report s2.2).
  Var = (6/7) x sum over 98 of (theta_r - theta)^2. MOE = t(0.975, df 98-14=84) = {T_CRIT:.3f} x SE. Every ratio is recomputed under each replicate.

RULES
  Item 1: hh miles = sum of BESTMILE over hh vehicles; zero-vehicle hh = 0. Households with any BESTMILE = -9 are dropped ({N_DROP:,} hh, {100 * SHARE_DROP:.1f}% of weight; see sensitivity).
  Item 2a: sum of hh miles / sum of persons, i.e. person-weighted with weight WTHHFIN x HHSIZE. Same hh set as item 1.
  Item 2b: FHWA-style diary method. Annual VMT = sum(VMT_MILE x WTTRDFIN) over DRVR_FLG=1 trips, divided by sum(WTPERFIN). Reproduces FHWA total of {round(VMT_TOTAL / 1e6):,} million.
  Item 3: denominator = all DRIVER=1 persons (non-drivers-that-day count as 0). mi/day uses all driving trips with valid VMT_MILE ({int((~okv).sum()):,} trips missing). min/day uses all with valid TRVLCMIN ({int((~okm).sum()):,} missing).
    mph(pairs) = total miles / total minutes over trips where both are valid. mph(means) = (mi/day) / (min/day) x 60 using the two separate sets.
  n_hh = unweighted households contributing to the cell. Item 3 n_hh = households with at least one licensed driver.
  Not computable: nothing requested was left out.
"""
print("\n\n".join([HEADER, T1, T1u, T2, T2b, T3, TS]) + "\n")
print(T2c)
meta = {
    "source": f"{BASE}csv.zip and Replicates.zip (2017 NHTS public-use files, codebook v1.2)",
    "fetched_on": datetime.date.today().isoformat(),
    "checks_passed": {"household_weight_total": 118_208_251, "licensed_driver_total": 223_277_172,
                      "annual_vmt_millions_fhwa": round(VMT_TOTAL / 1e6)},
    "rows": len(rec),
}
(OUT / "nhts2017_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
print(f"\nwrote {OUT / 'nhts2017_estimates.csv'} ({len(rec)} rows) and nhts2017_meta.json; all sanity-check asserts passed")
