"""Build the chart tables from the hand-transcribed inputs in data/. Any input marked TK stays TK.
usage (from the post folder): python -I model/build.py
writes data/chart1_per_resident.csv, data/chart2_car_share.csv, data/chart3_sensitivity.csv"""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
gf = pd.read_csv(DATA / "general_fund_fy2025.csv")
pop = pd.read_csv(DATA / "population.csv")
cats = pd.read_csv(DATA / "sales_tax_categories.csv")
pop = pop[pop.vintage == "DOF E-1 May 2025 release"].set_index("city").population

def amt(city, line):
    return gf[(gf.city == city) & (gf.line == line)].amount_usd.iloc[0]

# Every ACFR line sums to the ACFR total, and every detail breakdown sums to its ACFR line.
for city in ("San Mateo", "Burlingame"):
    lines = gf[(gf.city == city) & (gf.level == "ACFR line")].amount_usd.sum()
    assert lines == amt(city, "Total revenues"), city
assert amt("San Mateo", "Sales taxes") == sum(amt("San Mateo", l) for l in (
    "Sales tax - local 1%", "Sales tax - Prop 172", "Sales tax - Measure S (0.25%)"))
assert amt("San Mateo", "Other taxes") == sum(amt("San Mateo", l) for l in (
    "Property transfer tax (base)", "Property transfer tax - Measure CC", "Business license tax",
    "Transient occupancy tax (general fund)", "Franchises"))
assert amt("Burlingame", "Other taxes") == sum(amt("Burlingame", l) for l in (
    "Franchise tax", "Business licenses", "Real property transfer tax", "State HOPTR"))

# ---------------------------------------------------------------- chart 1: general fund revenue per resident
groups = {
    "San Mateo": {
        "Property tax": ["Property taxes"],
        "Sales tax": ["Sales taxes"],
        "Hotel tax": ["Transient occupancy tax (general fund)"],
        "Property transfer tax": ["Property transfer tax (base)", "Property transfer tax - Measure CC"],
        "Business and franchise taxes": ["Business license tax", "Franchises"],
        "Charges for services": ["Charges for services"],
    },
    "Burlingame": {
        "Property tax": ["Property taxes"],
        "Sales tax": ["Sales and use taxes"],
        "Hotel tax": ["Transient occupancy taxes"],
        "Property transfer tax": ["Real property transfer tax"],
        "Business and franchise taxes": ["Business licenses", "Franchise tax"],
        "Charges for services": ["Charges for services"],
    },
}
rows = []
for city, g in groups.items():
    total = amt(city, "Total revenues")
    used = 0
    for source, lines in g.items():
        v = sum(amt(city, l) for l in lines)
        used += v
        rows.append((city, source, v))
    rows.append((city, "Everything else", total - used))  # fines, permits, grants, interest, parking, other
    rows.append((city, "Total", total))
c1 = pd.DataFrame(rows, columns=["city", "source", "amount_usd"])
c1["population"] = c1.city.map(pop)
c1["per_resident_usd"] = (c1.amount_usd / c1.population).round(2)
c1["share_of_general_fund"] = (c1.amount_usd / c1.city.map(lambda c: amt(c, "Total revenues"))).round(4)
c1.to_csv(DATA / "chart1_per_resident.csv", index=False)

# ---------------------------------------------------------------- chart 2: car-linked share of the general fund
# HdL category shares apply to the 1% local tax (incl. county pools), not to Measure I/S, Prop 172 or other revenue.
def share(city, cat):
    r = cats[(cats.city == city) & (cats.category == cat) & cats.period.str.startswith("FY2024-25")]
    v = r.share_of_1pct.iloc[0] if len(r) else "TK"
    return "TK" if v == "TK" else float(v)

local1 = {"San Mateo": amt("San Mateo", "Sales tax - local 1%"),
          "Burlingame": amt("Burlingame", "Sales tax - local 1% (rounded)")}
rows = []
for city in ("San Mateo", "Burlingame"):
    gf_total = amt(city, "Total revenues")
    sales = amt(city, "Sales taxes" if city == "San Mateo" else "Sales and use taxes")
    for cat in ("Autos and transportation", "Fuel and service stations"):
        s = share(city, cat)
        dollars = "TK" if s == "TK" else round(s * local1[city])
        gf_share = "TK" if s == "TK" else round(dollars / gf_total, 4)
        rows.append((city, cat, s, local1[city], dollars, gf_total, gf_share,
                     round(sales / gf_total, 4), round(local1[city] / gf_total, 4)))
c2 = pd.DataFrame(rows, columns=["city", "category", "share_of_local_1pct", "local_1pct_usd", "category_usd",
                                 "general_fund_usd", "category_share_of_general_fund",
                                 "all_sales_tax_share_of_general_fund", "local_1pct_share_of_general_fund"])
c2.to_csv(DATA / "chart2_car_share.csv", index=False)

# ---------------------------------------------------------------- chart 3: arithmetic, a 10% drop in autos receipts
c3 = c2[c2.category == "Autos and transportation"][["city", "category_usd", "general_fund_usd"]].copy()
c3["drop_pct"] = 0.10
c3["loss_usd"] = c3.category_usd.map(lambda v: "TK" if v == "TK" else round(0.10 * v))
c3["loss_share_of_general_fund"] = [("TK" if l == "TK" else round(l / g, 4)) for l, g in zip(c3.loss_usd, c3.general_fund_usd)]
c3["loss_per_resident_usd"] = [("TK" if l == "TK" else round(l / pop[c], 2)) for l, c in zip(c3.loss_usd, c3.city)]
c3.to_csv(DATA / "chart3_sensitivity.csv", index=False)

print(c1.to_string(index=False), "\n")
print(c2.to_string(index=False), "\n")
print(c3.to_string(index=False))
