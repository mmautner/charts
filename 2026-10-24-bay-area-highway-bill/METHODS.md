# Methods

## Definitions

**Bay Area** = the five counties in the Public Transit Revenue Measure District: Alameda, Contra Costa,
San Francisco, San Mateo, Santa Clara (6.29M people, 1.8% of the U.S., Census 2025).

**Transit tax:** 0.5% sales tax (1.0% in San Francisco) for 14 years, ~$980M a year, majority vote
(district legal counsel's impartial analysis, Aug. 2026,
https://mtc.ca.gov/sites/default/files/documents/2026-08/PublicTransitRevenueMeasureDistrict_IA.pdf).
Per household: $419 (2,340,877 households, ACS 2024 1-year B11001, summary file
acsdt1y2024-b11001.dat). Sales tax is paid partly by visitors and businesses.

**Highway bailouts:** 10 transfers from the Treasury general fund into the Highway Trust Fund, FY2008-2022,
$271.5B (highway account $211.4B, transit account $60.1B), CRS R48845 (Sept. 2026) Table A-2,
https://www.congress.gov/crs-product/R48845 (`data/crs_general_fund_transfers.csv`).
**Projected shortfall:** CBO, Baseline Projections: Highway Trust Fund Accounts (June 2026),
https://www.cbo.gov/system/files/2026-06/51300-2026-06-highwaytrustfund.pdf: highway account runs out in
FY2028; highway-account shortfall averages $24.9B a year FY2028-36 (`data/cbo_htf_baseline_2026_06.csv`).

## Bay Area tax share

IRS SOI county data, total tax liability (A10300), Bay Area ÷ all counties (`model/bay_area_share.py`,
`data/bay_area_tax_share.csv`): 4.0% (2011), 4.4% (2013), 4.7-5.0% (2014-2017), 5.5-6.1% (2018-2021),
5.1-5.2% (2022-2023), with ~2% of returns.

## Why totals, not per household

The charts compare regional totals. Per-household figures were dropped: the highway share falls on
income-tax payers and the sales tax on shoppers (including businesses, ~42% of sales tax nationally per
EY/COST, and visitors), so dividing both by households overstated the transit tax for typical households.
SPUR's voter guide estimates the transit tax at ~$7 a month ($82 a year) for people earning up to 80% of
median income (method not published). Households (ACS 2024 1-year B11001): 2,340,877.

## Attribution

Each transfer is assigned to the Bay Area by that year's income tax share (2011's share for 2008-2010; 2012
interpolated). Projections use the 2022-23 share (low, used in the chart title), the 2018-23 mean and the
2018-23 maximum. Individual income tax is the largest source of non-payroll federal revenue (CBO Monthly
Budget Review, May 2025: $1.83T individual vs. $0.30T corporate, Oct.-May FY2025); corporate taxes, likely
more Bay-heavy, are not modeled separately. The transfers were largely borrowed, so this is the Bay Area's
share of the tax base that services that debt.

## Results (`model/bay_area_bailout.py`, `data/bay_area_bailout_summary.csv`)

| | |
|---|---|
| Bay Area share of projected highway-account shortfall, avg FY2028-36 | $1.27B / $1.38B / $1.51B a year (low / mean / high share); $544 / $591 / $645 per household |
| Same, whole fund including the transit account | $1.87-2.22B a year |
| Bay Area share of highway-account transfers, FY2008-2022 | $10.4B, $4,434 per 2024 household (~$0.7B a year averaged over the transfer years) |
| Bay Area share of all transfers, FY2008-2022 | $13.4B |
| Transit tax, 10 years / 14 years | $9.8B / $13.7B |

"On track to pay" assumes Congress keeps covering the shortfall from general revenue, as in all 10 cases
since 2008.

## Driving vs. income tax (`data/chart_bay_area_shares.csv`)

Bay Area roads carry 115.2M vehicle-miles a day (Caltrans California Public Road Data 2024, Table 6 county
totals), 42.1B a year, 1.28% of U.S. vehicle-miles (FHWA 2024 VM-2: 3,294B). Income tax share 5.18% (2023) =
4.06× (4.0-4.8× over 2018-2023). Vehicle-miles on the counties' roads include visitors and through freight;
federal fuel taxes are per gallon and partly on trucks, so this is a proxy for the Bay Area's share of
fuel-tax payments.

## What comes back

California received 9.43% of federal highway apportionments in FY2024 with 11.6% of the population (FHWA
FE-221). Spread by population, the Bay Area's portion would be ~1.5%. Approximation only.

## Other facts in the post

- Transit deficits, FY2027: BART $378M, SFMTA $322M, AC Transit $73M, Caltrain $65M ($838M), MTC
  third-party review by Macias Gini & O'Connell,
  https://blog.bayareametro.gov/posts/third-party-review-confirms-top-transit-agencies-operating-deficits
- Federal transit operating assistance ended for urbanized areas of 200,000+ in FY1998 (TEA-21); exceptions
  for agencies with 100 or fewer buses and some paratransit; preventive maintenance counts as capital. CRS
  R47900, https://www.congress.gov/crs-product/R47900
- Surface transportation programs extended through Dec. 11, 2026 by P.L. 119-103 (H.R. 6500, signed Sept. 2,
  2026). Dec. 11 is not a deadline for a general-fund transfer: CBO has the transit account running dry in
  FY2027 and the highway account in FY2028, so the next transfer will most likely be decided by the Congress
  that starts in January 2027. (Corrected after a reader pointed out that another short extension is likely.)
- House members whose districts include part of the 5 counties (119th Congress districts, Census
  CD119-county relationship file): CA-8 Garamendi, CA-9 Harder, CA-10 DeSaulnier, CA-11 Pelosi, CA-12 Simon,
  CA-14 Wahab (sworn in Sept. 2, 2026), CA-15 Mullin, CA-16 Liccardo, CA-17 Khanna, CA-18 Lofgren,
  CA-19 Panetta. Confirmed against the House Clerk's member list (MemberData.xml, published Oct. 1, 2026;
  Wahab sworn in Sept. 2, 2026) and senate.gov (Padilla, Schiff).

## TK

- MTC region's actual federal highway receipts (the ~1.5% is a population-based approximation).
- Nov. 3 outcome.
