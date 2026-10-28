"""Where Burlingame's extra general fund spending per resident goes, FY2025, with a plain reason for each item.
usage (from the post folder): python -I model/explain.py   ->   data/chart_gap_explained.csv"""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
s = pd.read_csv(DATA / "chart_spending.csv")
s["function"] = s.function.replace({"Administration": "Administration and planning", "Planning and building": "Administration and planning"})
s = s.groupby(["city", "function"], as_index=False).per_resident_usd.sum()
fx = pd.read_csv(DATA / "spending_by_function_fy2025.csv")
r = pd.read_csv(DATA / "gap_reasons.csv").set_index(["city", "metric"]).value
pop = {"San Mateo": 104315, "Burlingame": 31552}
per = lambda c, f: s[(s.city == c) & (s.function == f)].per_resident_usd.iloc[0]
lib = {"San Mateo": fx[(fx.city == "San Mateo") & (fx.function == "Library")].amount_usd.iloc[0],
       "Burlingame": 6649871}   # bg_acfr PDF 155 (data/parks_recreation.csv)
lib = {c: v / pop[c] for c, v in lib.items()}

def gap(f):
    return per("Burlingame", f) - per("San Mateo", f)

f = lambda c, m: float(r[c, m])
miles = {c: f(c, "lane_miles_2022") / pop[c] * 1000 for c in pop}
per_mile = {c: f(c, "pw_non_utility_budget_fy2026") / f(c, "lane_miles_2022") for c in pop}
density = {c: pop[c] / f(c, "land_area_sq_mi") for c in pop}
per_station = {c: pop[c] / f(c, "fire_stations") for c in pop}
trees = {c: f(c, "city_trees") / pop[c] for c in pop}
rows = [
    ("Parks and recreation", gap("Parks, recreation and library") - (lib["Burlingame"] - lib["San Mateo"]),
     f"{trees['Burlingame'] / trees['San Mateo']:.1f} times the city trees per resident, plus medians and downtown "
     "planting"),
    ("Capital projects and debt", gap("Capital projects and debt"),
     "Town Square, a sports field, new City Hall, Community Center bonds"),
    ("Public works", gap("Public works"),
     f"San Mateo is ~{density['San Mateo'] / density['Burlingame'] - 1:.0%} denser: {miles['Burlingame'] / miles['San Mateo']:.1f} "
     "times the lane miles per resident in Burlingame, which also spends more per mile"),
    ("Fire", gap("Fire"),
     f"A fire station for every ~{round(per_station['Burlingame'], -2):,.0f} residents vs. ~"
     f"{round(per_station['San Mateo'], -2):,.0f}"),
    ("Library", lib["Burlingame"] - lib["San Mateo"], "About twice the visits per person, at the same cost per visit"),
    ("Administration and planning", gap("Administration and planning"),
     "The same city offices, spread over a third as many residents"),
    ("Police", gap("Police"), "About the same"),
]
out = pd.DataFrame(rows, columns=["item", "gap_per_resident_usd", "reason"]).round({"gap_per_resident_usd": 2})
assert abs(out.gap_per_resident_usd.sum() - gap("Total")) < 0.5
assert 1.25 < miles["Burlingame"] / miles["San Mateo"] < 1.4 and per_mile["Burlingame"] > per_mile["San Mateo"]
out.to_csv(DATA / "chart_gap_explained.csv", index=False)
print(out.to_string(index=False)); print("total", round(gap("Total"), 2), "| per lane mile", {c: round(v) for c, v in per_mile.items()}, "| density", {c: round(v) for c, v in density.items()})
