# Caltrain's SB 63 efficiency strategies: what they're worth

Code and data behind a planned maxmautner.com post arguing Caltrain's SB 63 early action strategies are
unambitious. Watermark short URL: maxmautner.com/caltrain-efficiency.

One chart:

- `caltrain-strategies`: 2 stacked columns on one scale, from zero. The 6 strategies Caltrain adopted under SB 63
  (operator contract, plus 5 smaller items stacked as one segment) and the 3 options its own documents point to that
  it isn't pursuing, against a dashed line at the ~$75 million average yearly deficit Caltrain projects for fiscal
  2027 to 2034 (Hatch/JPB deck, Apr. 2025), about what Measure RTM gives it each year. Segments are the midpoint of
  each estimate range; each segment's label gives its full range, and the title gives each column's.

**These are estimates, not agency figures.** Neither MTC's Phase 1 review nor Caltrain put a dollar figure on any
strategy. `data/estimates.csv` gives each estimate's basis and timing.

## Sources

- MTC, [Final Phase One Financial Efficiency Review Report](https://mtc.ca.gov/sites/default/files/documents/2026-05/Final%20Phase%20One%20Financial%20Efficiency%20Review%20Report_20260527.pdf), May 27, 2026: Caltrain's strategies (pp. 60–61), FFGA waiver savings $10.0M in FY2024-25 (p. 96).
- Caltrain FY27 budget, [June 4, 2026 board packet](https://www.caltrain.com/media/37123/download): rail operations $129.3M, total operating expense $254.0M, GoPass $14.1M, parking $4.1M, ~$75M a year from the measure (resolution, p. 94).
- Caltrain operator rebid, [Oct. 9, 2025 deck](https://www.caltrain.com/media/35950/download): rail services projected $138.2M (FY26) to $213.8M (FY35), new contract July 1, 2029.
- Caltrain energy update, [Apr. 27, 2026](https://www.caltrain.com/media/37001/download); GoPass update, [Apr. 27, 2026](https://www.caltrain.com/media/37000/download); parking strategy, [Feb. 2026](https://www.caltrain.com/media/36796/download).
- Hatch, [non-fare revenue strategies](https://www.caltrain.com/media/35113/download), Apr. 2025 (priority table, p. 20).

## Judgment calls

- Operator contract: $4–9M a year after a competitive rebid, ~2–5% of the $168.3M Caltrain projects for the rail
  operator in FY30 (Oct. 9, 2025 deck, p. 9); $1–3M a year during the extension.
- 2-person crews: $6–11M a year, ~4–7% of the same $168.3M FY30 projection, net of roving fare inspectors and
  platform staff.
  Caltrain's current crew counts are not in these sources (TK).
- Crowding-based trains: the FY25 waiver savings ($10.0M in FY2024-25, which included ~3 months before electrified service began)
  scaled to a full year with cost growth. A cost avoided, not saved, and the FTA decides.
- Ground leases: Hatch's portfolio-wide range, which it bases on staff estimates of ground lease value; mostly
  after 2030, shown hatched.

## Reproduce

```
sh inputs/fetch.sh                # source PDFs into raw/ (not committed)
python charts/charts.py --social  # output/*.png and the social 4:5 version
```
