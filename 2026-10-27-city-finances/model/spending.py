"""General fund spending per resident by function, FY2025, from data/spending_by_function_fy2025.csv.
usage (from the post folder): python -I model/spending.py   ->   data/chart_spending.csv"""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
s = pd.read_csv(DATA / "spending_by_function_fy2025.csv")
pop = pd.read_csv(DATA / "population.csv")
pop = pop[pop.vintage == "DOF E-1 May 2025 release"].set_index("city").population
a = lambda c, f: float(s[(s.city == c) & (s.function == f)].amount_usd.iloc[0])

sm_lines = ["Police", "Fire", "Parks and recreation", "Library", "Public works", "Community development",
            "General government", "Non-departmental", "Capital outlay", "Debt service"]
bg_lines = ["General government", "Fire", "Fire - disaster preparedness", "Police", "Police communications dispatch",
            "Police - parking enforcement", "Public works", "Community development", "Parks recreation and library",
            "Capital outlay"]
assert abs(sum(a("San Mateo", f) for f in sm_lines) - a("San Mateo", "Total expenditures")) < 2
assert abs(sum(a("Burlingame", f) for f in bg_lines) - a("Burlingame", "Total expenditures")) < 2

legacy = a("San Mateo", "Fire and legacy fire costs (budget basis)") - a("San Mateo", "Fire")
lease = a("San Mateo", "Lease inception (non-cash)")
groups = {
    "San Mateo": {
        "Police": a("San Mateo", "Police"),
        "Fire": a("San Mateo", "Fire") + legacy,
        "Parks, recreation and library": a("San Mateo", "Parks and recreation") + a("San Mateo", "Library"),
        "Public works": a("San Mateo", "Public works"),
        "Planning and building": a("San Mateo", "Community development"),
        "Administration": a("San Mateo", "General government") + a("San Mateo", "Non-departmental") - legacy,
        "Capital projects and debt": a("San Mateo", "Capital outlay") - lease + a("San Mateo", "Debt service")
                                     + a("San Mateo", "Transfers out (capital and debt)"),
    },
    "Burlingame": {
        "Police": sum(a("Burlingame", f) for f in ("Police", "Police communications dispatch", "Police - parking enforcement")),
        "Fire": a("Burlingame", "Fire") + a("Burlingame", "Fire - disaster preparedness"),
        "Parks, recreation and library": a("Burlingame", "Parks recreation and library"),
        "Public works": a("Burlingame", "Public works"),
        "Planning and building": a("Burlingame", "Community development"),
        "Administration": a("Burlingame", "General government"),
        "Capital projects and debt": a("Burlingame", "Capital outlay") + a("Burlingame", "Transfers out to capital projects")
                                     + a("Burlingame", "Transfers out to debt service"),
    },
}
rows = []
for c, g in groups.items():
    for f, v in g.items():
        rows.append((c, f, round(v), round(v / pop[c], 2)))
    tot = sum(g.values())
    ops = tot - g["Capital projects and debt"]
    rows += [(c, "Day-to-day services", round(ops), round(ops / pop[c], 2)),
             (c, "Total", round(tot), round(tot / pop[c], 2))]
out = pd.DataFrame(rows, columns=["city", "function", "amount_usd", "per_resident_usd"])
out.to_csv(DATA / "chart_spending.csv", index=False)
w = out.pivot(index="function", columns="city", values="per_resident_usd")[["San Mateo", "Burlingame"]]
w["gap"] = w.Burlingame - w["San Mateo"]; w["ratio"] = (w.Burlingame / w["San Mateo"]).round(2)
print(w.sort_values("gap", ascending=False).to_string())
