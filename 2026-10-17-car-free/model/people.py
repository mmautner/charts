"""Person-level cuts: commute mode of workers, age of residents, and the difference tests
behind the headline comparisons. Run: python model/people.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pums as P
from findings import INC_BINS, INC_LABELS, OUT, TABLES, prep, show

# JWTRNS (2019+ coding)
MODE = {1: "Car", 2: "Transit", 3: "Transit", 4: "Transit", 5: "Transit", 6: "Transit",
        7: "Taxi/other", 8: "Taxi/other", 12: "Taxi/other", 9: "Bike", 10: "Walk",
        11: "Work from home"}


def persons(vintage):
    h, p = P.load(vintage)
    h = prep(h)
    p = p.merge(h[["SERIALNO", "carfree", "region", "inc_band", "stage", "bld"]], on="SERIALNO")
    p["mode"] = p["JWTRNS"].map(MODE)
    p["inc100"] = np.where(p["SERIALNO"].map(h.set_index("SERIALNO")["inc"]) < 100e3, "<100k", "100k+")
    return h, p


def mode_shares(w, by, name):
    rows = []
    for key, d in w.groupby(by, observed=True):
        for m in ["Car", "Transit", "Walk", "Bike", "Work from home", "Taxi/other"]:
            s = P.share(d.assign(flag=(d["mode"] == m).astype(int)), "flag", w=P.PW).iloc[0]
            rows.append({**P._key(by, key), "mode": m, "est": s["est"], "se": s["se"],
                         "n": len(d), "n_cf": s["n_cf"]})
    t = pd.DataFrame(rows)
    t["thin"] = np.where(t["n_cf"] == 0, t["n"] < P.THIN, t["n_cf"] < P.THIN)
    show(name, t)


def test(name, d1, d2):
    r = P.diff_share(d1, d2)
    a, b = P.share(d1).iloc[0], P.share(d2).iloc[0]
    print(f"\n## TEST {name}\n  {100*a.est:.1f}% (SE {100*a.se:.1f}, n_cf {a.n_cf}) vs "
          f"{100*b.est:.1f}% (SE {100*b.se:.1f}, n_cf {b.n_cf}); diff {100*r['est']:+.1f} pts, "
          f"SE {100*r['se']:.1f}, z {r['est']/r['se']:.1f}")


def main():
    h, p = persons(2024)
    w = p[p["mode"].notna()]
    mode_shares(w, "carfree", "Commute mode of workers by household car-free")
    mode_shares(w, ["region", "carfree"], "Commute mode by region x car-free")
    mode_shares(w[w.carfree == 1], "inc100", "Commute mode of car-free workers by income")
    mode_shares(w[(w.carfree == 1)], ["region", "inc100"], "Commute mode of car-free workers by region x income")

    h0, p0 = persons(2019)
    w0 = p0[p0["mode"].notna()]
    mode_shares(w0, ["region", "carfree"], "2015-19 commute mode by region x car-free")

    # residents' age: share of people living car-free, by age band
    p["age_band"] = pd.cut(p["AGEP"], [-1, 5, 17, 24, 34, 49, 64, 74, 84, 200],
                           labels=["0-5", "6-17", "18-24", "25-34", "35-49", "50-64", "65-74", "75-84", "85+"])
    show("Share of people in car-free households by age", P.share(p, by="age_band", w=P.PW))
    show("Share of people in car-free households by age x region", P.share(p, by=["region", "age_band"], w=P.PW))
    p0["age_band"] = pd.cut(p0["AGEP"], [-1, 5, 17, 24, 34, 49, 64, 74, 84, 200],
                            labels=["0-5", "6-17", "18-24", "25-34", "35-49", "50-64", "65-74", "75-84", "85+"])
    show("2015-19 share of people in car-free households by age", P.share(p0, by="age_band", w=P.PW))

    # senior households by householder age
    s = h[h.hh_age >= 65].copy()
    s["hh_age_band"] = pd.cut(s["hh_age"], [64, 74, 84, 200], labels=["65-74", "75-84", "85+"])
    show("Car-free share of senior households by householder age x region", P.share(s, by=["region", "hh_age_band"]))
    s0 = prep(P.load(2019)[0])
    s0 = s0[s0.hh_age >= 65].copy()
    s0["hh_age_band"] = pd.cut(s0["hh_age"], [64, 74, 84, 200], labels=["65-74", "75-84", "85+"])
    show("2015-19 car-free share of senior households by householder age x region", P.share(s0, by=["region", "hh_age_band"]))
    show("Car-free senior households: share living alone, disability",
         pd.concat([P.share(h[(h.stage == "Seniors") & (h.carfree == 1)].assign(f=(h.NP == 1).astype(int)), "f").assign(what="alone"),
                    P.share(h[(h.stage == "Seniors") & (h.carfree == 1)].assign(f=h.any_mobility_dis.fillna(False).astype(int)), "f").assign(what="mobility disability")]))

    # headline comparisons with difference SEs
    nosf = h[~h.sf]
    test("Rest of Bay: seniors vs young adults", nosf[nosf.stage == "Seniors"], nosf[nosf.stage == "Young adults"])
    test("Bay: seniors vs young adults", h[h.stage == "Seniors"], h[h.stage == "Young adults"])
    test("SF: seniors vs young adults", h[h.sf & (h.stage == "Seniors")], h[h.sf & (h.stage == "Young adults")])
    test("Rest of Bay: 100k+ in 20+ units vs <100k detached",
         nosf[(nosf.inc >= 100e3) & (nosf.bld == "20+ units")], nosf[(nosf.inc < 100e3) & (nosf.bld == "Detached house")])
    test("Rest of Bay: 100k+ in 20+ units vs <100k detached, householder under 65",
         nosf[(nosf.inc >= 100e3) & (nosf.bld == "20+ units") & (nosf.hh_age < 65)],
         nosf[(nosf.inc < 100e3) & (nosf.bld == "Detached house") & (nosf.hh_age < 65)])
    test("Rest of Bay: owners in 20+ units vs renters in detached houses",
         nosf[(nosf.renter == 0) & (nosf.bld == "20+ units")], nosf[(nosf.renter == 1) & (nosf.bld == "Detached house")])
    test("SF: families vs rest-of-Bay young adults", h[h.sf & (h.stage == "Families")], nosf[nosf.stage == "Young adults"])

    for k, t in TABLES.items():
        slug = "".join(c if c.isalnum() else "_" for c in k.lower()).strip("_")
        t.to_csv(OUT / f"{slug}.csv", index=False)


if __name__ == "__main__":
    main()
