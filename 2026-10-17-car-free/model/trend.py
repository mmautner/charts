"""Trend: 2015-2019 vs 2020-2024 5-year samples, and the 1-year series 2012-2024.
Incomes in both 5-year samples are in 2024 dollars. Run: python model/trend.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pums as P
from findings import INC_BINS, INC_LABELS, OUT, TABLES, prep, show

YEARS = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024]


def side_by_side(f, name):
    a, b = f(OLD), f(NEW)
    keys = [c for c in a.columns if c not in ("est", "se", "n", "n_cf", "thin")]
    t = a.merge(b, on=keys, suffixes=("_1519", "_2024")) if keys else pd.concat(
        [a.add_suffix("_1519"), b.add_suffix("_2024")], axis=1)
    t["chg"] = t["est_2024"] - t["est_1519"]
    # samples are independent across the 2 non-overlapping 5-year periods
    t["chg_se"] = np.hypot(t["se_1519"], t["se_2024"])
    for c in ["est_1519", "se_1519", "est_2024", "se_2024", "chg", "chg_se"]:
        t[c] = t[c] * (100 if PCT else 1)
    t = t.round(1)
    t = t[keys + ["est_1519", "se_1519", "n_cf_1519", "est_2024", "se_2024", "n_cf_2024", "chg", "chg_se"]]
    print(f"\n## {name}\n{t.to_string(index=False)}")
    TABLES[name] = t


def main():
    global OLD, NEW, PCT
    OLD, NEW = prep(P.load(2019)[0]), prep(P.load(2024)[0])
    PCT = True
    side_by_side(lambda h: P.share(h), "Trend: car-free share")
    side_by_side(lambda h: P.share(h, by="region"), "Trend: car-free share by region")
    side_by_side(lambda h: P.share(h, by="county"), "Trend: car-free share by county")
    side_by_side(lambda h: P.share(h, by="stage"), "Trend: car-free share by stage")
    side_by_side(lambda h: P.share(h, by=["region", "stage"]), "Trend: by region x stage")
    side_by_side(lambda h: P.share(h, by="inc_band"), "Trend: by income (2024 $)")
    side_by_side(lambda h: P.share(h, by=["region", "inc_band"]), "Trend: by region x income (2024 $)")
    side_by_side(lambda h: P.share(h, by="bld4"), "Trend: by building")
    side_by_side(lambda h: P.share(h[h.kids_u6]), "Trend: families with a child under 6")
    side_by_side(lambda h: P.share(h[h.kids_u6], by="region"), "Trend: families with a child under 6, by region")
    for h in (OLD, NEW):
        h["lt50"] = (h["inc"] < 50e3).astype(int)
        h["ge150"] = (h["inc"] >= 150e3).astype(int)
        h["senior"] = (h["stage"] == "Seniors").astype(int)
        h["young"] = (h["stage"] == "Young adults").astype(int)
    for flag in ["lt50", "ge150", "senior", "young", "renter"]:
        side_by_side(lambda h: P.share(h[h.carfree == 1], flag), f"Trend: share of car-free households {flag}")
        side_by_side(lambda h: P.share(h[h.carfree == 1], flag, by="region"), f"Trend: share of car-free households {flag}, by region")
        side_by_side(lambda h: P.share(h, flag), f"Trend: share of ALL households {flag}")
    PCT = False
    side_by_side(lambda h: P.total(h[h.carfree == 1]), "Trend: car-free households (count)")
    side_by_side(lambda h: P.total(h[h.carfree == 1], by="region"), "Trend: car-free households by region (count)")
    side_by_side(lambda h: P.total(h[h.carfree == 1], by="inc_band"), "Trend: car-free households by income (count)")
    side_by_side(lambda h: P.total(h[h.carfree == 1], by="stage"), "Trend: car-free households by stage (count)")
    side_by_side(lambda h: P.total(h), "Trend: all households (count)")

    rows = []
    for y in YEARS:
        d = pd.read_pickle(P.CACHE / f"h_1yr_{y}.pkl")
        d = d[(d["TYPE"] == 1) & (d["NP"] > 0)].copy()
        d["carfree"] = (d["VEH"] == 0).astype(int)
        d["region"] = np.where(d["county"] == "San Francisco", "SF", "Rest of Bay")
        d["kids"] = d["HUPAC"].isin([1, 3]).astype(int)   # own child under 6 (HUPAC 1 or 3)
        for scope, s in [("Bay Area", P.share(d))] + [
                (r, P.share(g)) for r, g in d.groupby("region")]:
            rows.append({"year": y, "scope": scope, **s.iloc[0].to_dict()})
    t = pd.DataFrame(rows)
    t["est"] = (100 * t["est"]).round(1)
    t["se"] = (100 * t["se"]).round(2)
    print("\n## 1-year car-free share\n" + t.pivot(index="year", columns="scope", values=["est", "se", "n_cf"]).to_string())
    TABLES["1-year car-free share"] = t

    for k, t in TABLES.items():
        if k.startswith(("Trend", "1-year")):
            slug = "".join(c if c.isalnum() else "_" for c in k.lower()).strip("_")
            t.to_csv(OUT / f"{slug}.csv", index=False)


if __name__ == "__main__":
    main()
