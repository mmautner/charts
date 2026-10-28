"""Compare the two cities' finances from data/fiscal_health_inputs.csv and data/general_fund_fy2025.csv.
usage (from the post folder): python -I model/fiscal_health.py   ->   data/fiscal_health_metrics.csv"""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
raw = pd.read_csv(DATA / "fiscal_health_inputs.csv")
gf = pd.read_csv(DATA / "general_fund_fy2025.csv")
CITIES = ("San Mateo", "Burlingame")

def v(city, metric):
    x = raw[(raw.city == city) & (raw.metric == metric)].value.iloc[0]
    return x if x == "TK" else float(x)

def line(city, name):
    return float(gf[(gf.city == city) & (gf.line == name)].amount_usd.iloc[0])

# San Mateo's 10-year forecast must chain: each year's ending fund balance = prior ending + that year's result.
fb = v("San Mateo", "forecast_fund_balance_fy2029")
for y in range(2030, 2037):
    fb += v("San Mateo", f"forecast_result_fy{y}")
    key = f"forecast_fund_balance_fy{y}"
    if key in set(raw.metric):
        assert abs(fb - v("San Mateo", key)) < 2, (y, fb)

rows = []
def add(metric, unit, f, note=""):
    for c in CITIES:
        try:
            val = f(c)
        except TypeError:          # an input is TK
            val = "TK"
        rows.append((c, metric, val if val == "TK" else round(val, 4), unit, note))

pop = lambda c: v(c, "population_2025")
hotel = {"San Mateo": line("San Mateo", "Transient occupancy tax (general fund)"),
         "Burlingame": line("Burlingame", "Transient occupancy taxes")}
sales = {"San Mateo": line("San Mateo", "Sales taxes"), "Burlingame": line("Burlingame", "Sales and use taxes")}

add("GF revenue per resident", "USD", lambda c: v(c, "gf_revenue_fy2025") / pop(c))
add("GF revenue per resident, without hotel tax", "USD", lambda c: (v(c, "gf_revenue_fy2025") - hotel[c]) / pop(c),
    "check: does the gap survive without visitor taxes")
add("GF revenue per resident, without hotel and sales tax", "USD",
    lambda c: (v(c, "gf_revenue_fy2025") - hotel[c] - sales[c]) / pop(c))
add("Hotel tax share of GF revenue", "share", lambda c: hotel[c] / v(c, "gf_revenue_fy2025"))
add("GF spending per resident (before transfers)", "USD", lambda c: v(c, "gf_expenditures_fy2025") / pop(c))
add("GF result FY2025 (net change in fund balance)", "USD", lambda c: v(c, "gf_net_change_fy2025"))
add("GF result FY2027 budget", "USD", lambda c: v(c, "forecast_result_fy2027"))
add("GF result FY2027 as share of revenue", "share",
    lambda c: v(c, "forecast_result_fy2027") / (v(c, "forecast_fy2027_revenue_incl_transfers_in") if c == "San Mateo"
                                                 else v(c, "forecast_fy2027_revenue")))
add("FY2027 operating result before capital transfers", "USD",
    lambda c: (v(c, "forecast_fy2027_revenue_incl_transfers_in") - v(c, "forecast_fy2027_spending_excl_transfers_out"))
    if c == "San Mateo" else (v(c, "forecast_fy2027_revenue") + v(c, "forecast_fy2027_other_transfers_in")
                              - v(c, "forecast_fy2027_departmental") - v(c, "forecast_fy2027_debt_transfers")),
    "San Mateo: before ALL transfers out (capital and debt split not given), so this flatters San Mateo")
add("GF fund balance June 2025", "USD", lambda c: v(c, "gf_fund_balance_2025"))
add("GF fund balance as share of GF spending + transfers out", "share",
    lambda c: v(c, "gf_fund_balance_2025") / (v(c, "gf_expenditures_fy2025") + v(c, "gf_transfers_out_fy2025")))
add("GF fund balance per resident", "USD", lambda c: v(c, "gf_fund_balance_2025") / pop(c))
add("GF fund balance growth 2016-2025", "share", lambda c: v(c, "gf_fund_balance_2025") / v(c, "gf_fund_balance_2016") - 1)
add("Net pension liability per resident", "USD", lambda c: v(c, "net_pension_liability") / pop(c),
    "San Mateo includes former firefighters; Burlingame excludes fire (Central County Fire's books)")
add("Net pension liability less pension trust, per resident", "USD",
    lambda c: (v(c, "net_pension_liability") - v(c, "pension_trust_balance")) / pop(c))
add("Net pension liability as multiple of GF revenue", "x", lambda c: v(c, "net_pension_liability") / v(c, "gf_revenue_fy2025"))
add("Net OPEB liability per resident", "USD", lambda c: v(c, "net_opeb_liability") / pop(c))
add("Unrestricted net position, governmental, per resident", "USD",
    lambda c: v(c, "unrestricted_net_position_governmental") / pop(c))
add("Governmental debt per resident", "USD", lambda c: v(c, "governmental_debt") / pop(c))
add("Assessed value per resident", "USD", lambda c: v(c, "assessed_value_2025") / pop(c))
add("Assessed value growth 2016-2025", "share", lambda c: v(c, "assessed_value_2025") / v(c, "assessed_value_2016") - 1)
add("Tax revenue change FY2019 to FY2021 (pandemic)", "share", lambda c: v(c, "tax_revenue_2021") / v(c, "tax_revenue_2019") - 1)
add("Tax revenue change FY2016 to FY2025 (nominal)", "share", lambda c: v(c, "tax_revenue_2025") / v(c, "tax_revenue_2016") - 1)
add("Tax revenue FY2025 vs FY2019 (nominal)", "share", lambda c: v(c, "tax_revenue_2025") / v(c, "tax_revenue_2019") - 1)

# Burlingame's March 2026 forecast must chain the same way.
fb = v("Burlingame", "gf_fund_balance_2025")
for y, key in ((2026, "_march"), (2027, "_march"), (2028, ""), (2029, ""), (2030, ""), (2031, "")):
    fb += v("Burlingame", f"forecast_result_fy{y}{key}")
    assert abs(fb - v("Burlingame", f"forecast_fund_balance_fy{y}{key}")) < 2, (y, fb)

# Fire: San Mateo kept its pre-2019 fire pensions; Burlingame's fire pensions sit with CCFD. Adding each city's
# cost share of its fire agency's liabilities is arithmetic (neither city reports these amounts as its own).
fire = lambda c, m: v(c, m) + v(c, "fire_agency_cost_share") * v(c, f"fire_agency_{m}")
fire_note = "city + cost share of fire agency (SMC Fire 60%; CCFD 42%); arithmetic allocation"
add("Net pension liability incl. fire agency share, per resident", "USD", lambda c: fire(c, "net_pension_liability") / pop(c), fire_note)
add("Net pension liability incl. fire share, less pension trust, per resident", "USD",
    lambda c: (fire(c, "net_pension_liability") - v(c, "pension_trust_balance")) / pop(c), fire_note)
add("Net OPEB liability incl. fire agency share, per resident", "USD", lambda c: fire(c, "net_opeb_liability") / pop(c), fire_note)
add("Unrestricted net position incl. fire agency share, per resident", "USD",
    lambda c: (v(c, "unrestricted_net_position_governmental")
               + v(c, "fire_agency_cost_share") * v(c, "fire_agency_unrestricted_net_position")) / pop(c), fire_note)

# Forecasts, FY2028-31 (the years both cities' forecasts cover after the current budget)
yrs = range(2028, 2032)
add("Forecast GF result, avg FY2028-31", "USD", lambda c: sum(v(c, f"forecast_result_fy{y}") for y in yrs) / 4)
add("Forecast GF result before transfers out, avg FY2028-31", "USD",
    lambda c: sum(v(c, f"forecast_result_fy{y}") + v(c, f"forecast_transfers_out_fy{y}") for y in yrs) / 4
    if c == "San Mateo" else sum(v(c, f"forecast_operating_fy{y}") for y in yrs) / 4,
    "San Mateo: adds back all transfers out (capital + debt). Burlingame: revenues over expenditures before transfers")
add("Forecast GF fund balance FY2031", "USD", lambda c: v(c, "forecast_fund_balance_fy2031"))
add("Forecast GF fund balance FY2031, excluding restricted pension trust", "USD",
    lambda c: v(c, "forecast_fund_balance_fy2031") - (v(c, "gf_restricted_pension_trust_2025") if c == "Burlingame" else 0))
add("Forecast GF fund balance FY2031 as share of June 2025", "share",
    lambda c: v(c, "forecast_fund_balance_fy2031") / v(c, "gf_fund_balance_2025"))

# ---------------------------------------------------------------- chart tables
# Chart A: general fund balance the city can spend, per resident (Jan 2025 population held constant).
# San Mateo: total GF balance (its restricted + nonspendable is <$1M). Burlingame: excludes the restricted pension trust.
trust = v("Burlingame", "forecast_pension_trust_restricted")
fbrows = []
for y in range(2023, 2032):
    kind = "actual" if y <= 2025 else "forecast"
    has = ((raw.city == "San Mateo") & (raw.metric == f"forecast_fund_balance_fy{y}")).any()
    sm = v("San Mateo", f"gf_fund_balance_{y}") if kind == "actual" else \
        v("San Mateo", f"forecast_fund_balance_fy{y}") if has else None
    if sm is None:   # FY2026 and FY2028 are not separate rows: chain from the yearly results
        prev = [r for r in fbrows if r[0] == "San Mateo"][-1][3]
        sm = prev + v("San Mateo", f"forecast_result_fy{y}") - (25_000_000 if y == 2026 else 0)
    if kind == "actual":
        bg = v("Burlingame", f"gf_spendable_{y}")
    else:
        key = f"forecast_fund_balance_fy{y}" + ("_march" if y in (2026, 2027) else "")
        bg = v("Burlingame", key) - trust
    for c, val in (("San Mateo", sm), ("Burlingame", bg)):
        fbrows.append((c, y, kind, val, round(val / pop(c), 2)))
fbt = pd.DataFrame(fbrows, columns=["city", "fiscal_year_ending", "kind", "spendable_balance_usd", "per_resident_usd"])
assert abs(fbt[(fbt.city == "San Mateo") & (fbt.fiscal_year_ending == 2027)].spendable_balance_usd.iloc[0]
           - v("San Mateo", "forecast_fund_balance_fy2027")) < 2
fbt.to_csv(DATA / "chart_fund_balance.csv", index=False)

# Chart B: average yearly result FY2028-31, split into operations (incl. transfers in) and transfers out.
g = []
for c in CITIES:
    if c == "San Mateo":
        out_ = sum(v(c, f"forecast_transfers_out_fy{y}") for y in yrs) / 4
        net = sum(v(c, f"forecast_result_fy{y}") for y in yrs) / 4
        ops = net + out_
    else:
        ops = sum(v(c, f"forecast_operating_fy{y}") + v(c, f"forecast_other_transfers_in_fy{y}") for y in yrs) / 4
        out_ = sum(v(c, f"forecast_capital_transfers_fy{y}") + v(c, f"forecast_debt_transfers_fy{y}") for y in yrs) / 4
        net = ops - out_
        assert abs(net - sum(v(c, f"forecast_result_fy{y}") for y in yrs) / 4) < 2
    for part, val in (("Operations", ops), ("Transfers out to capital projects and debt", -out_), ("Net result", net)):
        g.append((c, part, round(val), round(val / pop(c), 2)))
pd.DataFrame(g, columns=["city", "part", "avg_usd_per_year", "per_resident_usd"]).to_csv(DATA / "chart_gap.csv", index=False)

out = pd.DataFrame(rows, columns=["city", "metric", "value", "unit", "note"])
out.to_csv(DATA / "fiscal_health_metrics.csv", index=False)
print(out.pivot(index="metric", columns="city", values="value")[list(CITIES)].to_string())
