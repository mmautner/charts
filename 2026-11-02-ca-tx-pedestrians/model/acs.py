"""Walk-to-work shares for California and Texas from ACS 1-year table B08301, 2010-2024 (no standard 2020
1-year release). Two denominators: all workers, and workers who commute (all workers minus those who worked
from home). MOEs are the published 90% MOEs, combined with the Census Bureau's ratio/proportion formulas
(ACS General Handbook, ch. 8): proportion when the numerator is a subset of the denominator.

Usage: python -I model/acs.py raw/census/acs_series data
"""
import json, math, sys
from pathlib import Path
import pandas as pd

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
URL = "https://api.census.gov/data/{y}/acs/acs1?get=NAME,B08301_001E,B08301_019E,B08301_021E&for=state:06,48 (with MOEs)"


def prop(x, mx, y, my):
    """Share x/y and its 90% MOE; falls back to the ratio formula when the proportion one goes negative."""
    p = x / y
    inside = mx ** 2 - p ** 2 * my ** 2
    return p, math.sqrt(inside if inside > 0 else mx ** 2 + p ** 2 * my ** 2) / y


rows = []
for f in sorted(SRC.glob("b08301_*.json")):
    y = int(f.stem.split("_")[1])
    h, *data = json.loads(f.read_text())
    for r in data:
        d = {k: float(v) for k, v in zip(h, r) if k.startswith("B08301")}
        name = r[h.index("NAME")]
        T, Tm, W, Wm, H, Hm = (d[f"B08301_{c}"] for c in ("001E", "001M", "019E", "019M", "021E", "021M"))
        p, m = prop(W, Wm, T, Tm)
        C, Cm = T - H, math.sqrt(Tm ** 2 + Hm ** 2)
        pc, mc = prop(W, Wm, C, Cm)
        ph, mh = prop(H, Hm, T, Tm)
        base = dict(geo=name, year=y, source=URL.format(y=y))
        rows += [base | dict(measure="walk_share_of_workers", value=p, moe90=m, se=m / 1.645, numerator=W, denominator=T),
                 base | dict(measure="walk_share_of_commuters", value=pc, moe90=mc, se=mc / 1.645, numerator=W, denominator=C,
                             note="commuters = workers minus those who worked from home"),
                 base | dict(measure="work_from_home_share", value=ph, moe90=mh, se=mh / 1.645, numerator=H, denominator=T)]
df = pd.DataFrame(rows).sort_values(["measure", "geo", "year"])
df.to_csv(OUT / "acs_walk_commute.csv", index=False)
print(df[df.measure == "walk_share_of_commuters"].pivot(index="year", columns="geo", values="value").mul(100).round(2).to_string())
