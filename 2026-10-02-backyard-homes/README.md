# 1 in 4 new California homes is in someone's backyard

Code and data behind the charts in "1 in 4 new California homes is in someone's backyard" (TK: post URL) on maxmautner.com.

The charts compare California's accessory dwelling unit (ADU) permits with permits for
detached houses and for units in buildings of 5+ units, and show ADUs as a share of all units permitted. Both
charts use HCD's Annual Progress Report data alone, so every number in them comes from
the same city reports.

## Reproduce

From this folder, after `pip install -r ../requirements.txt`:

```
python fetch_hcd.py      # HCD APR Table A2, summarized to units by year and category
python fetch_census.py   # optional cross-check: Census Building Permits Survey, California
python model.py          # prints every number the charts use, next to the cross-checks
python charts.py         # writes the PNGs to output/
```

Commit `data/`. Table A2 is large, so `fetch_hcd.py` commits only its summary
(`hcd_a2_summary.csv`) and a metadata file recording the fetch date, the columns it used,
and the unit categories it found. To summarize a copy downloaded by hand:
`python fetch_hcd.py --file tablea2.csv`.

## Inputs

| Input | Source |
|---|---|
| ADU, detached house, 5+ unit, and all units permitted, by year | [HCD APR data, Table A2](https://data.ca.gov/dataset/housing-element-annual-progress-report-apr-data-by-jurisdiction-and-year), fetched |
| Units permitted in buildings of 5+ units, California (cross-check only) | [Census Building Permits Survey, annual state files](https://www2.census.gov/econ/bps/State/), fetched |
| HCD's published ADU totals (1,336 in 2016; 26,924 in 2023; 30,354 in 2024; 26.6% share in 2024) | [HCD ADU Handbook, March 2026](https://www.hcd.ca.gov/sites/default/files/docs/policy-and-research/ADU-Handbook-Update.pdf), p. 4; used only as a check, in `inputs.py` |

## Method

Table A2 has 1 row per project per report year, with the units that reached each stage
in that year. ADU permits in a year are the sum of building-permit units over rows in the
ADU category (JADUs are reported in that category). The share divides ADU permits by
building-permit units across all categories in the same table, so numerator and
denominator come from the same reports.

## Limitations

- **Self-reported.** Cities report APR data; HCD does not verify it. Cities file late and
  correct earlier years, so totals for recent years rise after first publication.
- **APR counts run high.** The fetched Table A2 totals run ~30% above HCD's own
  published ADU counts (39,056 vs 30,354 for 2024), and the APR's 5+ unit counts run well
  above the Census survey's in every year (82,496 vs 52,772 in 2022). Duplicate rows
  explain little of it (2,881 ADU permit rows share a year, jurisdiction, parcel, and
  address). The gap hits every housing type, so shares and ratios within the APR hold up
  better than its levels; the charts lead with those. The causes are unresolved: late and
  corrected filings since HCD's publication, and differences in what each source counts as
  a permitted unit, are both plausible.
- **First fetch.** The committed summary was built from Table A2 rows pulled through the
  data.ca.gov API (see `hcd_a2_meta.json`), because the CSV download was blocked where it
  was run. Rerunning `fetch_hcd.py` normally should reproduce it.
- **Permits are not homes.** A permit can lapse, and some ADU permits legalize units
  that already existed. Neither is measured here.
- **Check against HCD.** `model.py` prints the fetched totals next to HCD's published
  figures. A large gap means a duplicate or definitional difference to resolve before
  publishing.
