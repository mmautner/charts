"""Load the Bay Area PUMS extracts and estimate shares, medians and totals with
replicate-weight standard errors: SE = sqrt(4/80 * sum((rep - full)^2)).

Every estimate comes back with its unweighted sample count (n) and, for car-free
estimates, the number of car-free sample households (n_cf). Cells with n_cf < 50 get
thin=True.
"""
import os
from pathlib import Path

import numpy as np
import pandas as pd

R = 80
HW = ["WGTP"] + [f"WGTP{i}" for i in range(1, R + 1)]
PW = ["PWGTP"] + [f"PWGTP{i}" for i in range(1, R + 1)]
THIN = 50
# CPI-U annual averages, BLS series CUUR0000SA0: 2019 = 255.657, 2024 = 313.689
CPI_2019_TO_2024 = 313.689 / 255.657

CACHE = Path(os.environ.get("PUMS_CACHE", Path(__file__).resolve().parent.parent / "cache"))

BLD_GROUP = {2: "Detached house", 3: "Townhouse", 4: "2-19 units", 5: "2-19 units",
             6: "2-19 units", 7: "2-19 units", 8: "20+ units", 9: "20+ units",
             1: "Mobile home/other", 10: "Mobile home/other"}
BLD_ORDER = ["Detached house", "Townhouse", "2-19 units", "20+ units"]
STAGE_ORDER = ["Young adults", "Midlife, no kids", "Families", "Seniors"]


def se(full, reps):
    reps = np.asarray(reps, dtype=float)
    return float(np.sqrt(4 / R * np.sum((reps - full) ** 2)))


def load(vintage=2024):
    """Housing-unit households (NP > 0) with person-derived household traits."""
    h = pd.read_pickle(CACHE / f"h_5yr_{vintage}.pkl")
    p = pd.read_pickle(CACHE / f"p_5yr_{vintage}.pkl")
    h = h[(h["TYPE"] == 1) & (h["NP"] > 0)].copy()
    adj = h["ADJINC"] / 1e6
    hadj = h["ADJHSG"] / 1e6
    dollars = CPI_2019_TO_2024 if vintage == 2019 else 1.0   # report everything in 2024 dollars
    h["inc"] = h["HINCP"] * adj * dollars
    h["rent"] = h["GRNTP"] * hadj * dollars
    h["carfree"] = (h["VEH"] == 0).astype(int)
    h["bld"] = h["BLD"].map(BLD_GROUP)
    h["renter"] = (h["TEN"] == 3).astype(int)
    h["sf"] = h["county"] == "San Francisco"

    p = p[p["SERIALNO"].isin(h["SERIALNO"])].copy()
    adult = p["AGEP"] >= 18
    g = p.groupby("SERIALNO")
    traits = pd.DataFrame({
        "hh_age": p[p["SPORDER"] == 1].set_index("SERIALNO")["AGEP"],
        "n_u6": g["AGEP"].apply(lambda a: (a < 6).sum()),
        "n_u18": g["AGEP"].apply(lambda a: (a < 18).sum()),
        "n_adults": adult.groupby(p["SERIALNO"]).sum(),
        "n_workers": p["ESR"].isin([1, 2, 4, 5]).groupby(p["SERIALNO"]).sum(),
        "any_mobility_dis": (adult & ((p["DPHY"] == 1) | (p["DOUT"] == 1))).groupby(p["SERIALNO"]).any(),
        "hh_ba": (p[p["SPORDER"] == 1].set_index("SERIALNO")["SCHL"] >= 21),
    })
    h = h.join(traits, on="SERIALNO")
    h["kids"] = h["n_u18"] > 0
    h["kids_u6"] = h["n_u6"] > 0
    h["stage"] = np.select(
        [h["kids"], h["hh_age"] >= 65, h["hh_age"] < 35],
        ["Families", "Seniors", "Young adults"], "Midlife, no kids")
    return h, p


def share(df, flag="carfree", by=None, w=HW):
    """Weighted share of df[flag] (0/1) within each group of `by`."""
    groups = [((), df)] if by is None else df.groupby(by, observed=True)
    rows = []
    for key, d in groups:
        W = d[w].to_numpy(float)
        num = (W * d[flag].to_numpy(float)[:, None]).sum(0)
        den = W.sum(0)
        r = num / den
        rows.append({**_key(by, key), "est": r[0], "se": se(r[0], r[1:]),
                     "n": len(d), "n_cf": int(d["carfree"].sum()) if "carfree" in d else None})
    return _finish(rows)


def total(df, by=None, w=HW):
    groups = [((), df)] if by is None else df.groupby(by, observed=True)
    rows = []
    for key, d in groups:
        t = d[w].to_numpy(float).sum(0)
        rows.append({**_key(by, key), "est": t[0], "se": se(t[0], t[1:]), "n": len(d),
                     "n_cf": int(d["carfree"].sum()) if "carfree" in d else None})
    return _finish(rows)


def wmedian_all(x, W):
    """Weighted median of x under each column of W."""
    o = np.argsort(x)
    x, W = x[o], W[o]
    cw = W.cumsum(0)
    idx = (cw >= cw[-1] / 2).argmax(0)
    return x[idx]


def median(df, col, by=None, w=HW):
    groups = [((), df)] if by is None else df.groupby(by, observed=True)
    rows = []
    for key, d in groups:
        d = d[d[col].notna()]
        m = wmedian_all(d[col].to_numpy(float), d[w].to_numpy(float))
        rows.append({**_key(by, key), "est": m[0], "se": se(m[0], m[1:]), "n": len(d),
                     "n_cf": int(d["carfree"].sum()) if "carfree" in d else None})
    return _finish(rows)


def diff_share(d1, d2, flag="carfree", w=HW):
    """Share in d1 minus share in d2, SE from the shared replicate weights."""
    def s(d):
        W = d[w].to_numpy(float)
        return (W * d[flag].to_numpy(float)[:, None]).sum(0) / W.sum(0)
    r = s(d1) - s(d2)
    return {"est": r[0], "se": se(r[0], r[1:]), "n1_cf": int(d1["carfree"].sum()),
            "n2_cf": int(d2["carfree"].sum())}


def _key(by, key):
    if by is None:
        return {}
    by = [by] if isinstance(by, str) else list(by)
    key = key if isinstance(key, tuple) else (key,)
    return dict(zip(by, key))


def _finish(rows):
    out = pd.DataFrame(rows)
    if "n_cf" in out and out["n_cf"].notna().all():
        # groups of car owners only (n_cf == 0) are judged on their own sample size
        out["thin"] = np.where(out["n_cf"] == 0, out["n"] < THIN, out["n_cf"] < THIN)
    return out
