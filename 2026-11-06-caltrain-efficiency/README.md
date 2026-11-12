# Caltrain's SB 63 efficiency strategies: what they're worth

Code and data behind a planned maxmautner.com post arguing Caltrain's SB 63 early action strategies are
unambitious. Watermark short URL: maxmautner.com/caltrain-efficiency.

One chart:

- `caltrain-strategies`: 2 stacked columns on one scale, from zero. The 6 strategies Caltrain adopted under SB 63
  (operator contract, plus 5 smaller items stacked as one segment), and the same strategies with the 3 options its own
  documents point to that it isn't pursuing stacked on top, so the second column is cumulative, against a dashed line at the ~$75 million average yearly deficit Caltrain projects for fiscal
  2027 to 2034 (Hatch/JPB deck, Apr. 2025), about what Measure RTM gives it each year. Segments are the midpoint of
  each estimate range; each segment's label gives its full range.

**These are estimates, not agency figures.** Neither MTC's Phase 1 review nor Caltrain put a dollar figure on any
strategy. `data/estimates.csv` gives each estimate's basis and timing.

## Sources

- MTC, [Final Phase One Financial Efficiency Review Report](https://mtc.ca.gov/sites/default/files/documents/2026-05/Final%20Phase%20One%20Financial%20Efficiency%20Review%20Report_20260527.pdf), May 27, 2026: Caltrain's strategies (pp. 60–61), FFGA waiver savings $10.0M in FY2024-25 (p. 96).
- Caltrain FY27 budget, [June 4, 2026 board packet](https://www.caltrain.com/media/37123/download): rail operations $129.3M, total operating expense $254.0M, GoPass $14.1M, parking $4.1M, ~$75M a year from the measure (resolution, p. 94).
- Caltrain operator rebid, [Oct. 9, 2025 deck](https://www.caltrain.com/media/35950/download): rail services projected $138.2M (FY26) to $213.8M (FY35), new contract July 1, 2029.
- Caltrain energy update, [Apr. 27, 2026](https://www.caltrain.com/media/37001/download); GoPass update, [Apr. 27, 2026](https://www.caltrain.com/media/37000/download); parking strategy, [Feb. 2026](https://www.caltrain.com/media/36796/download).
- Hatch, [non-fare revenue strategies](https://www.caltrain.com/media/35113/download), Apr. 2025 (priority table, p. 20).

## Other sources cited in the post

Linked once in the post or not at all, to keep the post readable; listed here so every claim can be checked.

- Caltrain [Dec. 4, 2025 board packet](https://www.caltrain.com/media/36143/download): TASI fee structure, 114-train requirement and waiver terms, fare increases through 2030, insurance coverage.
- Caltrain board minutes: [Oct. 9, 2025](https://www.caltrain.com/media/36128/download) (TASI extension, 7–0) and [Dec. 2025](https://www.caltrain.com/media/36591/download) (fares, 7–1).
- Caltrain [SB 63 strategies deck](https://www.caltrain.com/media/37136/download), June 4, 2026 (implementation plans by August 2028).
- Caltrain [2011 operator contract](https://caltrain.com/media/35682/download) and a rider's [May 2026 letter](https://www.caltrain.com/media/37043/download) on crew size.
- FRA crew-size rule, [Federal Register](https://www.govinfo.gov/content/pkg/FR-2024-04-09/html/2024-06625.htm), Apr. 9, 2024.
- TASI union agreements: [BLET](https://blet.org/news/blets-caltrain-members-ratify-new-contract-with-tasi/) and [SMART](https://www.smart-union.org/tentative-agreement-reached-with-transitamerica-services-tasi/).
- Election results: [KQED](https://www.kqed.org/voterguide/california/regional-measure-rtm).
- SB 63 [text](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202520260SB63); SB 1031 [MTC handout](https://es.mtc.ca.gov/sites/default/files/meetings/attachments/6012/6bi_Handout_Summary_Sheet_SB_1031.pdf), May 24, 2024.

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
