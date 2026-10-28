# Status (2026-10-27)

Holistic comparison of the two cities' finances. Burlingame's five-year forecast and both fire agencies' pension
figures are in (see METHODS.md findings 1, 2 and 5). Charts built 2026-10-27 (blog, social, og-image); awaiting Max's review.

## Charts (output/)

1. `savings`: spendable GF balance per resident, FY2023-25 actual + city forecasts to FY2031. Starts at FY2023
   because Burlingame's FY2022 ACFR row conflicts with the city's own chart. Burlingame excludes its restricted
   pension trust. Uses Jan 2025 population for every year.
2. `revenue`: FY2025 GF revenue per resident by source; hotel tax emphasized.
Dropped 2026-10-27 at Max's request: `budget-gap`, stacked `spending`, then `extra-spending` (a list of reasons with
bars; better as prose). Their facts are in `FACTS.md` for the post text; data and models are kept.
Colors: San Mateo #2f6c9e, Burlingame COPPER (pair passes the dataviz validator on BG).

## TK

- San Mateo fire calls by city (SMC Fire doesn't publish them), to compare cost per call.

- San Mateo legacy fire costs' location in the ACFR (assumed non-departmental).

- Burlingame ACFR vs. budget split of assigned/unassigned fund balance.
- Burlingame forecast for FY2028-31 as of the June 2026 budget (only the March 2026 version is published).
- Bay Area CPI series if the charts show trends in real dollars.

## Settled

- Short URL: maxmautner.com/burlingame-vs-san-mateo (watermark on all charts and og-image; redirect added to the blog's
  s3_website.yml -> /2026/10/27/city-finances.html, uncommitted). Post file: _posts/2026-10-28-city-finances.md (published: false).
