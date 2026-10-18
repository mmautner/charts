"""Print every estimate behind the post, each with SE, unweighted n, and car-free n.
Writes the tables to data/ as CSVs. Run: python model/findings.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pums as P

OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)
pd.set_option("display.max_rows", 200)

INC_BINS = [-np.inf, 25e3, 50e3, 75e3, 100e3, 150e3, 200e3, 300e3, np.inf]
INC_LABELS = ["<25k", "25-50k", "50-75k", "75-100k", "100-150k", "150-200k", "200-300k", "300k+"]
TABLES = {}


def show(name, t, pct=True):
    t = t.copy()
    if pct:
        t["est"] = (100 * t["est"]).round(1)
        t["se"] = (100 * t["se"]).round(1)
    else:
        t["est"] = t["est"].round(0)
        t["se"] = t["se"].round(0)
    if "thin" in t:
        t["thin"] = t["thin"].map({True: "THIN", False: ""})
    print(f"\n## {name}\n{t.to_string(index=False)}")
    TABLES[name] = t


def prep(h):
    h["inc_band"] = pd.Categorical(pd.cut(h["inc"], INC_BINS, labels=INC_LABELS), INC_LABELS, ordered=True)
    h["region"] = np.where(h["sf"], "SF", "Rest of Bay")
    h["bld4"] = pd.Categorical(h["bld"].where(h["bld"].isin(P.BLD_ORDER)), P.BLD_ORDER, ordered=True)
    h["stage"] = pd.Categorical(h["stage"], P.STAGE_ORDER, ordered=True)
    return h


def composition(h, col, name):
    """Distribution of `col` among car-free vs car-owning households."""
    rows = []
    for cf, d in h.groupby("carfree"):
        for level in d[col].dropna().unique():
            d2 = d.assign(flag=(d[col] == level).astype(int))
            s = P.share(d2, "flag").iloc[0]
            rows.append({"carfree": cf, col: level, "est": s["est"], "se": s["se"],
                         "n": int((d[col] == level).sum())})
    t = pd.DataFrame(rows).sort_values(["carfree", col])
    show(name, t)


def main():
    h, p = P.load(2024)
    h = prep(h)
    nosf = h[~h["sf"]]

    show("Car-free share, all households", P.share(h))
    show("Car-free share, excluding SF", P.share(nosf))
    show("Car-free households (count)", P.total(h[h.carfree == 1]), pct=False)
    show("Car-free households by region (count)", P.total(h[h.carfree == 1], by="region"), pct=False)
    pp = p.merge(h[["SERIALNO", "carfree", "region"]], on="SERIALNO")
    show("People in car-free households (count)", P.total(pp[pp.carfree == 1], w=P.PW), pct=False)
    show("Share of people in car-free households", P.share(pp, w=P.PW))

    show("Car-free share by county", P.share(h, by="county"))
    show("Car-free share by life stage", P.share(h, by="stage"))
    show("Car-free share by life stage x region", P.share(h, by=["region", "stage"]))
    show("Car-free share by income", P.share(h, by="inc_band"))
    show("Car-free share by income x region", P.share(h, by=["region", "inc_band"]))
    show("Car-free share by building", P.share(h, by="bld4"))
    show("Car-free share by building x region", P.share(h, by=["region", "bld4"]))
    show("Car-free share by tenure x region", P.share(h, by=["region", "renter"]))
    h["inc100"] = np.where(h["inc"] < 100e3, "<100k", "100k+")
    show("Car-free share by building x income, excl SF", P.share(h[~h.sf], by=["inc100", "bld4"]))
    show("Car-free share by building x income, SF", P.share(h[h.sf], by=["inc100", "bld4"]))
    show("Car-free share by renter x building, excl SF", P.share(h[~h.sf], by=["renter", "bld4"]))

    # Who car-free households are
    composition(h, "stage", "Life stage among car-free vs car households")
    composition(h, "inc_band", "Income among car-free vs car households")
    composition(h, "bld", "Building among car-free vs car households")
    composition(h, "region", "Region among car-free vs car households")
    show("Median income by car-free", P.median(h, "inc", by="carfree"), pct=False)
    show("Median income by car-free x region", P.median(h, "inc", by=["region", "carfree"]), pct=False)
    show("Median income by car-free x stage", P.median(h, "inc", by=["stage", "carfree"]), pct=False)
    show("Median household size", P.median(h, "NP", by="carfree"), pct=False)
    h["one_person"] = (h["NP"] == 1).astype(int)
    show("Share living alone", P.share(h, "one_person", by="carfree"))
    show("Share renting", P.share(h, "renter", by="carfree"))
    h["mob"] = h["any_mobility_dis"].fillna(False).astype(int)
    h["ba"] = h["hh_ba"].fillna(False).astype(int)
    h["noworker"] = (h["n_workers"] == 0).astype(int)
    for flag, label in [("mob", "adult with ambulatory/independent-living disability"),
                        ("ba", "householder has BA+"), ("noworker", "no employed member")]:
        show(f"Share with {label}, by car-free x income", P.share(h, flag, by=["carfree", "inc_band"]))

    # Choice vs constraint: profile of car-free households by income band
    cf = h[h.carfree == 1].copy()
    cf["senior"] = (cf["stage"] == "Seniors").astype(int)
    cf["young"] = (cf["stage"] == "Young adults").astype(int)
    cf["big_bldg"] = (cf["bld"] == "20+ units").astype(int)
    cf["sf_i"] = cf["sf"].astype(int)
    for flag in ["senior", "young", "mob", "ba", "noworker", "big_bldg", "sf_i", "renter", "one_person"]:
        show(f"Car-free households: share {flag} by income", P.share(cf, flag, by="inc_band"))

    for k, t in TABLES.items():
        slug = "".join(c if c.isalnum() else "_" for c in k.lower()).strip("_")
        t.to_csv(OUT / f"{slug}.csv", index=False)


if __name__ == "__main__":
    main()
