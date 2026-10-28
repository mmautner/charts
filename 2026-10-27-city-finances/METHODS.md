# Methods and findings

FY2025 = July 1, 2024 to June 30, 2025. General fund (GF) figures come from each city's audited ACFR unless a row
says "city forecast": San Mateo's 2026-28 adopted budget (10-year forecast), and Burlingame's March 11, 2026 mid-year
report (five-year forecast) plus its FY2026-27 adopted budget. Sources and pages: `data/fiscal_health_inputs.csv`,
`data/general_fund_fy2025.csv`, `data/sources.csv`. Computed values: `data/fiscal_health_metrics.csv`.
Population: DOF E-1, Jan 1, 2025 (San Mateo 104,315; Burlingame 31,552). Dollars are nominal.

## Findings, ranked by how much they carry the post

1. **Both cities' own forecasts drain their general fund reserves by ~2031, at about the same rate.** Average FY2028-31
   deficit: San Mateo $14.4M a year (~7.7% of revenue), Burlingame $8.4M (~7.9%). By FY2031 each has ~$15M left:
   San Mateo $15.0M (13% of its June 2025 balance), Burlingame $15.3M. But Burlingame's $15.3M is all restricted
   pension trust money ($22.3M), so its spendable balance is ~−$7.0M. Its unassigned balance turns negative in
   FY2027-28. San Mateo's goes negative in FY2032-33.
2. **The deficits have different causes.** Burlingame's day-to-day operations run a surplus of $4.1M to $5.0M every
   year; the deficit comes from moving $10-13M a year into capital projects (a new City Hall among them). San Mateo
   is short ~$5.1M a year even before any transfers out, and that already assumes $4-5M a year of unspecified
   "budget savings". Burlingame can close its gap by cutting or delaying capital projects; San Mateo needs new
   revenue or service cuts. Measure H (~$7M a year) would cover about half of San Mateo's gap.
3. **Burlingame has ~1.7x the general fund revenue per resident** ($2,970 vs. $1,717). The gap narrows without hotel
   tax ($2,331 vs. $1,672) and without hotel and sales tax ($1,780 vs. $1,412), but it doesn't close. Assessed value
   is $563K vs. $365K per resident.
4. **Burlingame's revenue is more fragile.** Hotel tax is 21.5% of its GF (San Mateo 2.6%). Tax revenue fell 32% from
   FY2019 to FY2021 (San Mateo: 6%), and FY2025 hotel tax is still 31% below FY2019.
5. **Once fire is counted the same way, Burlingame's long-term liabilities are heavier.** San Mateo kept its
   pre-2019 fire pensions on its own books; Burlingame's firefighters have been CCFD employees since 2010.
   Each city's cost share of its fire agency is added (SMC Fire 60%, CCFD 42%), which is arithmetic, not a figure
   either city reports.
   - **Pensions per resident:** San Mateo $2,654; Burlingame $3,600, or $2,757 after its $26.6M pension trust.
     Contributions to the trust have been paused for 3 years.
   - **Retiree medical (OPEB) per resident:** San Mateo $130; Burlingame $1,227. Burlingame still owes retiree
     medical for fire staff who retired before 2010.
   - **Unrestricted net position per resident:** San Mateo −$582; Burlingame +$954. Burlingame stays ahead, but its
     lead shrinks from $2,194 to $1,536.
6. **Reserves today are similar relative to spending** (San Mateo 63%, Burlingame 60% of GF spending plus transfers
   out). San Mateo's are mostly unassigned. Burlingame's are mostly earmarked: its Economic Stability Reserve is set
   at 24% of revenue by policy, plus the pension trust.
7. **Burlingame's higher revenue goes into higher spending, not savings.** FY2025 general fund spending, including
   money moved to capital project and debt funds: $3,038 vs. $1,733 per resident (1.75x; revenue is 1.73x). $775 of
   the $1,305 gap is parks, recreation and library (2.4x) plus capital projects and debt (3.2x). Police is close
   (1.1x). Since both forecasts run short by ~8% of revenue, Burlingame's bigger budget makes its gap bigger per
   resident ($267 vs. $138 a year) without being worse proportionally.
   - Check: Burlingame has ~1 job located in the city per resident vs. San Mateo's 0.57 (Census LEHD 2023). Per
     resident plus local job, Burlingame spends 1.38x as much: narrower, not closed.
   - San Mateo fire includes ~$7.3M of legacy fire pension costs from the budget's "SMC Fire and Legacy Costs" line,
     taken out of the ACFR's non-departmental line (assumed; TK: confirm with San Mateo Finance). San Mateo's capital
     line excludes a $9.1M non-cash lease entry.
   - Four Burlingame spending lines were garbled in the ACFR text layer and recovered as final budget minus variance;
     the lines sum exactly to the reported total (asserted in `model/spending.py`).
8. **Burlingame carries more governmental debt**: $2,392 vs. $874 per resident. San Mateo's total debt is larger
   ($7,486 per capita), but it is mostly sewer debt repaid from sewer rates.

## What Burlingame does with the extra money (parks, recreation, capital, debt)

Per resident (DOF Jan 2025 population). Parks and recreation use each city's FY2025-26 adopted division budgets (same
year, same basis; `data/parks_rec_divisions_fy2026.csv`); capital and debt use FY2025 actuals
(`data/capital_debt_fy2025.csv`).

- **Park and landscape upkeep, including street trees: $309 vs. $95 (3.2x).** Burlingame's Parks Division also tends
  14,000+ street trees and 1,700+ park trees (0.50 trees per resident vs. San Mateo's 0.24), 49 medians and
  roundabouts, 23 parking areas and the Burlingame Ave and Broadway business districts. Park land per resident is
  about the same: Burlingame 93.55 developed park acres (3.0 per 1,000) vs. San Mateo's 289.7 acres of parks, civic
  grounds and medians (2.8 per 1,000). San Mateo states its upkeep cost as ~$29,000 per acre; Burlingame doesn't
  report one, and its tree crew isn't budgeted separately.
- **Recreation: $216 vs. $101 gross, but $73 vs. $59 after program fees (1.2x).** Fees cover ~66% of Burlingame's
  recreation and aquatics vs. ~41% of San Mateo's. San Mateo's golf course pays for itself.
- **Library: $211 vs. $89 (2.4x),** with ~2.2x the visits and ~1.7x the checkouts per person served (IMLS FY2024);
  cost per visit is about the same.
- **Capital projects: $411 vs. $106 (3.9x).** Burlingame's FY2025 projects (all funds, $18.4M): Town Square plaza on a
  former downtown parking lot ($3.9M), Cuernavaca Field turf and ADA renovation ($2.6M), street resurfacing ($1.8M),
  sidewalks ($1.1M), new City Hall in leased space ($1.0M; $4.0M more budgeted for FY2026). San Mateo's resolution
  for Measure H says it has over $350M of unfunded capital needs.
- **Debt: $116 vs. $57 (2.0x).** Burlingame's is mostly the 2019 Community Center bonds ($2.0M a year, half from
  Measure I; $52.7M project). San Mateo's largest is Measure S-funded general obligation bonds ($2.69M).
- **Public works (+$181): density and cost per mile.** San Mateo is ~20% denser (Census land area). MTC's 2022 survey
  gives ~5.4 lane miles per 1,000 residents in Burlingame vs. ~4.1 in San Mateo (1.3x), and Burlingame's non-utility
  public works budget is ~$63,000 per lane mile vs. ~$35,000 (scopes differ). An earlier version used the ACFRs' street
  miles (152 vs. 204), which mix centerline and curb miles; corrected 2026-10-27.
- **Fire (+$165): density at the department level.** Both departments space stations ~1 per 2.3 square miles. SMC
  Fire's area is ~8,000 residents per square mile vs. CCFD's ~4,800 (Hillsborough is ~1,800), so ~18,400 vs. ~11,000
  residents per station and ~$290 vs. ~$560 of member payments per resident served. Burlingame pays 42% of CCFD, below
  its 48% share of population and calls. (Corrected 2026-10-27: 2 staffed Burlingame stations, not 3.)
- **Administration and planning (+$121): scale.** Fixed city offices (council, manager, clerk, attorney, finance, HR,
  IT, planning) spread over a third as many residents. An inference, not measured.
- **Police (+$63): about the same** (1.1x).
- TK: Burlingame's FY2026-27 Parks Division budget jumps 26.5%, mostly from a $2.7M insurance allocation (bg_budget_2627
  PDF 153); cause unstated.

## Checks

- Dominant-place analog: the revenue gap is tested without hotel tax and without hotel + sales tax (finding 3).
- Both forecasts are checked to chain: each year's ending balance = prior ending + that year's result
  (`model/fiscal_health.py`). San Mateo's PDF text layer swaps the FY2030 and FY2031 columns; the order is fixed by
  that check.
- **Forecast vintages differ.** San Mateo's is June 2026 (adopted budget). Burlingame's is March 2026: its FY2027
  is −$2.3M there and −$3.3M in the June adopted budget. The June budget book doesn't republish years after FY2027.
- Burlingame's forecast table was read from the text records of an EMF image embedded in a Word file. Values are
  as printed, and every year's balance chains.
- "Before transfers out" basis (finding 2): both exclude all transfers out (capital and debt service). San Mateo's
  revenue includes transfers in (~$10M a year); Burlingame's operating line excludes its ~$2.1-2.3M a year of
  transfers in. So the comparison, if anything, favors San Mateo.
- Burlingame's ACFR MD&A says $27.2M assigned and $8.0M unassigned; its budget book says $24.2M and $11.2M. The total
  is the same; the discrepancy is TK.
- Not inflation-adjusted.

## Earlier car-revenue analysis (dropped as the focus)

Burlingame's autos and transportation sales tax is ~3.9% of its GF (HdL FY2025: 26% of ~$14.0M local 1%). Car
lease tax goes to the lessor's city (R&TC 7205.1). San Mateo's category data is TK. Details:
`data/sales_tax_categories.csv`, `data/chart2_car_share.csv`, `data/chart3_sensitivity.csv`.
