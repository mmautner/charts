# Facts for the post text: what Burlingame does with its extra money

Sourced facts, not prose. Per resident uses DOF Jan. 1, 2025 population (San Mateo 104,315; Burlingame 31,552).
Spending is FY2025 general fund (July 2024 to June 2025), including money moved to capital project and debt funds.
Sources and pages: `data/sources.csv`, `data/gap_reasons.csv`, `data/spending_by_function_fy2025.csv`,
`data/parks_rec_divisions_fy2026.csv`, `data/capital_debt_fy2025.csv`, `data/library_fy2024.csv`. Values are computed
in `model/explain.py` (`data/chart_gap_explained.csv`).

## The totals

- Burlingame takes in $2,970 per resident, San Mateo $1,717: $1,253 more (1.7x).
- Burlingame spends $3,038 per resident, San Mateo $1,733: $1,305 more (1.75x). The extra revenue is all spent.
- Parks and recreation, the library and capital projects account for $775 of the $1,305 (59%).

## Item by item (extra spending per resident, largest first)

1. **Capital projects and debt, +$363** ($526 vs. $163).
   - FY2025 projects (all funds, $18.4M): Town Square plaza on a former downtown parking lot ($3.9M), Cuernavaca Field
     turf and accessibility renovation ($2.6M), street resurfacing ($1.8M), sidewalks ($1.1M), new City Hall fit-out
     in leased space ($1.0M; $4.0M more budgeted for FY2026).
   - Debt is mostly the 2019 Community Center bonds: ~$2.0M a year, half paid from Measure I, on a $52.7M project.
   - Contrast: San Mateo's Measure H resolution says it has over $350M of unfunded capital needs.
2. **Parks and recreation, +$290** ($502 vs. $212; libraries excluded).
   - Park land per resident is about the same: 3.0 developed acres per 1,000 in Burlingame, 2.8 in San Mateo.
   - Burlingame's parks crew also cares for 15,700 city trees (0.50 per resident vs. 0.24, 2.1x), 49 medians and
     roundabouts, 23 parking lots and the Burlingame Ave and Broadway business districts.
   - Recreation is mostly fee-funded: fees cover ~2/3 of Burlingame's recreation costs vs. ~2/5 of San Mateo's. After
     fees, recreation costs $73 vs. $59 per resident (2025-26 budgets).
   - San Mateo's figure includes its golf course (~$28 per resident), which golf fees pay for, so this gap is slightly
     understated.
3. **Public works, +$181** ($285 vs. $104).
   - San Mateo is ~20% denser (8,597 vs. 7,182 residents per square mile of land; Census 2024 Gazetteer).
   - Lane miles (MTC 2022, same method for both): Burlingame 170.8, San Mateo 428.2, so ~5.4 vs. ~4.1 per 1,000
     residents (1.3x).
   - Burlingame also spends more per lane mile on streets, storm drains, traffic and engineering: ~$63,000 vs.
     ~$35,000 (2025-26 budgets, all funds). The budgets' scopes differ (Burlingame's engineering also manages utility
     projects), so treat the per-mile gap as rough.
   - Corrected 2026-10-27: the ACFRs' street miles (152 vs. 204) are not comparable (centerline vs. curb miles).
4. **Fire, +$165** ($511 vs. $346): density at the department level.
   - Both regional departments space staffed stations about equally: ~1 per 2.3 square miles of land (CCFD 6 over
     13.8 sq mi; SMC Fire 9 over 20.6 sq mi).
   - SMC Fire's area (San Mateo, Belmont, Foster City) has ~8,000 residents per square mile; CCFD's (Burlingame,
     Hillsborough, Millbrae) ~4,800. So each SMC Fire station serves ~18,400 people vs. ~11,000 (~1.7x), and member
     cities pay ~$290 vs. ~$560 per resident served (FY2025).
   - Burlingame pays 42% of CCFD by formula, below its 48% share of CCFD's population and calls.
   - Corrected 2026-10-27: Burlingame has 2 staffed stations, not 3 (Station 36 is administration).
5. **Library, +$122** ($211 vs. $89).
   - Per person served (federal Public Libraries Survey FY2024): 2.3x the spending, 2.2x the visits, 1.7x the
     checkouts, 1.7x the hours open. Cost per visit is about the same ($21.87 vs. $20.73).
   - Heavier use reflects who lives there as well as what the city offers; don't present it as caused by the spending.
6. **Administration and planning, +$121** ($344 vs. $223).
   - The same city offices (council, manager, clerk, attorney, finance, HR, IT, planning) spread over a third as many
     residents. An inference; neither city measures it.
7. **Police, +$63** ($659 vs. $595): about the same.

## Context worth a sentence

- Burlingame has ~1 job located in the city per resident; San Mateo 0.57 (Census LEHD, 2023). Counting residents plus
  local jobs, Burlingame spends 1.38x as much per person rather than 1.75x.
- Both cities' own forecasts run general fund deficits of ~8% of revenue in 2028-31. Burlingame's day-to-day budget
  stays in surplus and the gap comes from capital transfers; San Mateo's operations run short before any transfers.
