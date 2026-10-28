# San Mateo and Burlingame: how the two cities fare financially

Code and data behind a planned maxmautner.com post comparing the finances of San Mateo and Burlingame:
revenue, structural balance, reserves, pensions, debt and volatility (FY2025 actuals plus city forecasts). Watermark URL: TK.

Two charts: each city's spendable general fund balance through its own forecast (`savings`) and general fund revenue
per resident by source (`revenue`). `FACTS.md` holds sourced facts for the post text (what the extra spending buys). See `STATUS.md`.

## Reproduce

From this folder, with the repo's `.venv` (pandas):

```
sh inputs/fetch.sh               # primary PDFs and DOF spreadsheets into raw/ (not committed)
python -I model/fiscal_health.py # data/fiscal_health_metrics.csv, chart_fund_balance.csv, chart_gap.csv
python -I model/build.py         # data/chart1_per_resident.csv (+ car-revenue tables from the earlier focus)
python -I model/spending.py      # data/chart_spending.csv
python -I model/jobs.py raw/lehd data  # data/jobs_2023.csv (Census LEHD)
python -I model/explain.py       # data/chart_gap_explained.csv
python charts/charts.py --social # output/*.png, social 4:5 versions, og-image.png
```

Every input number is hand-transcribed into `data/` with its source and PDF page:

- `data/fiscal_health_inputs.csv`: fund balances, forecasts, pensions, OPEB, net position, debt, assessed value,
  tax revenue history.

- `data/general_fund_fy2025.csv`: both cities' FY2025 general fund revenue by line (ACFR budgetary schedules) and
  the detail rows behind sales tax and other taxes (budget books). `model/build.py` asserts that every breakdown
  sums to its ACFR line.
- `data/population.csv`: DOF E-1, Jan 1, 2025 (May 2025 release used; May 2026 revision listed).
- `data/sales_tax_categories.csv`: HdL business-group shares (Burlingame only; San Mateo TK).
- `data/ballot_measures.csv`: Measure H (San Mateo, Nov 3, 2026), Measure S, Measure I.
- `data/secondary_checks.csv`: newspaper and brief figures checked against primary documents.
- `data/sources.csv`: every source ID, its URL, and notes on pagination.

See `METHODS.md` for definitions and findings.
