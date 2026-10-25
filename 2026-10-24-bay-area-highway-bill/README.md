# The Bay Area's highway bill

Code and data behind the charts in the post on Bay Area taxpayers and federal highway bailouts on
maxmautner.com at [maxmautner.com/bay-area-highway-bill](https://maxmautner.com/bay-area-highway-bill).

Two charts. The Bay Area's share of the federal Highway Trust Fund's projected shortfall, if Congress keeps
covering it with general revenue, against the regional transit sales tax on the Nov. 3, 2026 ballot. And the
Bay Area's share of U.S. driving, people and federal income tax.

## Reproduce

From this folder (Python with pandas, numpy; matplotlib for the charts):

```
sh inputs/fetch.sh                           # IRS, Census, FHWA, Caltrans into raw/; CBO PDF by hand (see script)
python -I model/bay_area_share.py raw data   # data/bay_area_tax_share.csv
python -I model/bay_area_bailout.py raw data # data/bay_area_bailout*.csv, data/chart_bay_area_shares.csv
python charts/charts.py --social             # output/*.png, social 4:5 versions, og-image.png
```

`charts/charts.py` reads only `data/`, so the charts re-render without the raw downloads. `raw/` is not
committed. Hand-transcribed inputs, each with its source: `data/crs_general_fund_transfers.csv` (CRS R48845
Table A-2), `data/cbo_htf_baseline_2026_06.csv` (CBO, June 2026), `data/bay_area_vmt_2024.csv` (Caltrans,
FHWA), `data/transit_gaps.csv` (MTC, RTA, SEPTA). See `METHODS.md` for definitions, checks and open items.
