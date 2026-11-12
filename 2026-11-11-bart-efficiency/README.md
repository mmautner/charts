# BART's SB 63 efficiency strategies: what they're worth

Code and data behind a maxmautner.com post arguing BART's SB 63 early action strategies are unambitious, and that the
decisions that matter most will be made in BART's 2027 union contracts. Watermark short URL: maxmautner.com/bart-efficiency.

One chart:

- `bart-strategies`: 2 stacked columns on one scale, from zero. The 9 strategies BART adopted under SB 63 (5 revenue
  items and 4 cost items, each stacked as one segment), and the same strategies with 3 options BART's 2027 union
  contracts will decide stacked on top, so the second column is cumulative, against a dashed line at the $57 million
  deficit BART forecasts for fiscal 2028 even with Measure RTM (June 11, 2026 budget deck, p. 7). Segments are the
  midpoint of each estimate range; each segment's label gives its full range.

**These are estimates, not agency figures.** Neither MTC's Phase 1 review nor BART put a dollar figure on any
strategy. `data/estimates.csv` gives each estimate's basis and timing.

## Sources

- MTC, [Final Phase One Financial Efficiency Review Report](https://mtc.ca.gov/sites/default/files/documents/2026-05/Final%20Phase%20One%20Financial%20Efficiency%20Review%20Report_20260527.pdf), May 27, 2026: BART's strategies (pp. 58–59), shorter trains ~$12M a year (p. 58).
- BART FY27 [adopted budget resolution](https://www.bart.gov/sites/default/files/2026-07/EDD-Resolution%20to%20Adopt%20the%20FY27%20Budget%20%285%29.pdf): parking $22.4M, labor and benefits $803.7M for 3,697.6 operating FTEs.
- BART [June 11, 2026 budget deck](https://www.bart.gov/sites/default/files/2026-06/Presentation%20-%20Resolution%20to%20Approve%20the%20FY27%20Budget.pdf), p. 7: net results with Measure RTM of -$57M (FY28), -$54M, -$47M, -$28M (FY31).
- BART Inspector General, [overtime audit](https://oig.bart.gov/files/d8c036b58/BART+Overtime+Risks+Can+be+Reduced+by+Strategic+Improvements+in+Oversight+and+Management+June+13+-+2025.pdf), June 13, 2025: $80.9M in FY24; ~$6M from double time to time and a half.
- BART [FY25 ACFR](https://www.bart.gov/sites/default/files/2026-01/BART%20ACFR%202025%20-%20Final%20%28SECURED%29.pdf): overtime +$9.1M in FY25; Note 10, self-insurance.
- Contra Costa Civil Grand Jury [Report 2608](https://contracosta.courts.ca.gov/system/files/general/report-2608-signed-cover.pdf) (p. 9: existing revenue initiatives) and [BART's response](https://contracosta.courts.ca.gov/system/files/general/response-report-no-2608-bart-board-directors.pdf) (p. 23: ATU location-based staffing ~11% of the workforce).
- BART [funding fact sheet](https://www.bart.gov/sites/default/files/2026-03/FundingOverview_Factsheet_030426.pdf), Mar. 2026: fare gates ~$10M a year.
- SF Board of Supervisors [Res. 55-25](https://sfbos.org/sites/default/files/r0055-25.pdf): SFO lease $2.5M a year.
- SF Examiner, [Sept. 22, 2025](https://www.sfexaminer.com/news/transit/why-bart-train-operator-loves-his-job--warts-and-all/article_606e13ad-eda9-4033-8aac-3acb73cbd006.html): 486 train operators, per a BART spokesman.

## Other sources cited in the post

Linked once in the post or not at all, to keep the post readable; listed here so every claim can be checked.

- BART union contracts: [ATU](https://www.bart.gov/sites/default/files/2025-04/ATU%20%282021-2027%29%20%5BInterim%5D.pdf) and [SEIU](https://www.bart.gov/sites/default/files/2026-04/SEIU%20%282021-2027%29.pdf) (cover pages: July 1, 2021 – June 30, 2027); [AFSCME extension](https://www.bart.gov/sites/default/files/2024-08/Resolutions%20Ratifying%20the%20Agreements%20to%20Extend%20the%20Collective%20Bargaining%20Agreements%20-%20AFSCME.pdf) through June 30, 2027; police unions listed 2018–2026 on BART's [contracts page](https://www.bart.gov/about/jobs/cba).
- BART [SB 63 strategies decision document](https://bart.legistar1.com/bart/attachments/f481d4b4-6b24-4789-92f2-babbcbc4b5d2.pdf), adopted June 11, 2026.
- BART [Alternative Service Plan](https://www.bart.gov/sites/default/files/2026-02/FY27%20Alternative%20Service%20Plan_Resolution%20-%20Attachment%201.pdf): $133M non-service cuts; 70% service-hour cut saves ~$176M.
- Paratransit broker contract, [AC Transit board item 21-471a](https://actransit.granicusideas.com/meetings/745-board-of-directors/agenda_items/672e4fa9f2b670c234005bfd-7-dot-d-21-471a-consider-authorizing-the-general-mana), Nov. 2024.
- BART parking: [hours](https://www.bart.gov/guide/parking) and [July 2026 rate changes](https://www.bart.gov/news/articles/2026/news20260513).
- BART [train control modernization](https://www.bart.gov/node/41126): 28 trains an hour through the Transbay Tube in 2030.
- AP via the [Atlanta Journal-Constitution](https://www.ajc.com/news/2026/10/some-us-transit-systems-weigh-whether-to-run-trains-without-a-human-at-the-controls/), Oct. 2026: Washington Metro Red Line plan.
- [Streetsblog SF](https://sf.streetsblog.org/2018/02/09/bart-managers-suss-out-long-term-plans-at-annual-workshop), Feb. 9, 2018: general manager's answer on driverless trains.
- Election results: [KQED](https://www.kqed.org/voterguide/california/regional-measure-rtm).
- SB 63 [text](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202520260SB63); SB 1031 [MTC handout](https://es.mtc.ca.gov/sites/default/files/meetings/attachments/6012/6bi_Handout_Summary_Sheet_SB_1031.pdf), May 24, 2024.

## Judgment calls

- Adopted items are counted only beyond what the FY27 budget already includes.
- Overtime rules: the Inspector General's ~$6M plus ~5–10% of overtime from leave-counting, missed-break and
  no-cap rules, net of some straight-time backfill.
- Station staffing: 15–25% of the ~470 location-staffed positions through attrition at ~$190K each, with ~1/3
  redeployed to platforms and trains.
- Driverless trains: 486 operators at ~$190K is ~$92M; keeping ~20–45% of that for roving attendants and control
  staff leaves ~$50–75M. 2030s, only if BART's board chooses it; capital costs (platform doors) not included. Shown hatched.

## Reproduce

```
sh inputs/fetch.sh                # source PDFs into raw/ (not committed)
python charts/charts.py --social  # output/*.png and the social 4:5 version
```
