"""Write the series each chart draws to data/chart_*.csv, unrounded, with SE, unweighted n,
and car-free sample n. charts/charts.py reads only these files.
Run: python model/chart_data.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pums as P
from findings import OUT, prep
from people import MODE

INC3 = ["Under $50k", "$50-100k", "$100k+"]


def inc3(h):
    return pd.Categorical(np.select([h.inc < 50e3, h.inc < 100e3], INC3[:2], INC3[2]), INC3, ordered=True)


def flag_share(d, flag, by):
    return P.share(d.assign(f=flag.astype(int)), "f", by=by)


def main():
    old, new = prep(P.load(2019)[0]), prep(P.load(2024)[0])
    _, pnew = P.load(2024)
    _, pold = P.load(2019)
    h = new
    h["mob"] = h["any_mobility_dis"].fillna(False).astype(int)

    # 1. life stage of car-free vs car-owning households
    rows = []
    for scope, d in [("Bay Area", h), ("Rest of Bay", h[~h.sf])]:
        for stage in P.STAGE_ORDER:
            t = flag_share(d, d["stage"] == stage, "carfree")
            rows.append(t.assign(scope=scope, stage=stage))
    pd.concat(rows).to_csv(OUT / "chart_stage_mix.csv", index=False)

    # 2. car-free rate by life stage, SF vs rest of Bay
    P.share(h, by=["region", "stage"]).to_csv(OUT / "chart_stage_rate.csv", index=False)

    # 3. car-free households by income: share seniors / young adults; disability vs car owners
    cf = h[h.carfree == 1]
    a = flag_share(cf, cf["stage"] == "Seniors", "inc_band").assign(series="Seniors")
    b = flag_share(cf, cf["stage"] == "Young adults", "inc_band").assign(series="Young adults")
    c = P.share(h, "mob", by=["carfree", "inc_band"]).assign(series="Disability")
    c2 = P.share(h[~h.sf], "mob", by=["carfree", "inc_band"]).assign(series="Disability, excl SF")
    pd.concat([a, b, c, c2]).to_csv(OUT / "chart_income_profile.csv", index=False)

    # 4. rest-of-Bay car-free households by income, 2015-19 vs 2020-24 (2024 dollars)
    rows = []
    for period, d in [("2015-19", old), ("2020-24", new)]:
        r = d[~d.sf & (d.carfree == 1)].copy()
        r["inc3"] = inc3(r)
        rows.append(P.total(r, by="inc3").assign(period=period))
    pd.concat(rows).to_csv(OUT / "chart_income_shift.csv", index=False)

    # 5. commute mode of workers in car-free households, by region and period
    rows = []
    for period, hh, pp in [("2015-19", old, pold), ("2020-24", new, pnew)]:
        w = pp.merge(hh[["SERIALNO", "carfree", "region"]], on="SERIALNO")
        w = w[(w.carfree == 1) & w["JWTRNS"].notna()]
        w["mode"] = w["JWTRNS"].map(MODE)
        for region, d in w.groupby("region"):
            for m in ["Car", "Transit", "Work from home", "Walk", "Bike"]:
                t = P.share(d.assign(f=(d["mode"] == m).astype(int)), "f", w=P.PW)
                rows.append(t.assign(period=period, region=region, mode=m))
    pd.concat(rows).to_csv(OUT / "chart_commute.csv", index=False)

    # 6. car-free rate by building x income, excluding SF
    r = h[~h.sf].copy()
    r["inc100"] = np.where(r.inc < 100e3, "Under $100k", "$100k+")
    P.share(r, by=["inc100", "bld4"]).to_csv(OUT / "chart_building.csv", index=False)

    # 7. 1-year series
    rows = []
    for y in [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024]:
        d = pd.read_pickle(P.CACHE / f"h_1yr_{y}.pkl")
        d = d[(d["TYPE"] == 1) & (d["NP"] > 0)].copy()
        d["carfree"] = (d["VEH"] == 0).astype(int)
        d["region"] = np.where(d["county"] == "San Francisco", "SF", "Rest of Bay")
        rows.append(P.share(d).assign(year=y, region="Bay Area"))
        rows.append(P.share(d, by="region").assign(year=y))
    pd.concat(rows).to_csv(OUT / "chart_trend.csv", index=False)


if __name__ == "__main__":
    main()
