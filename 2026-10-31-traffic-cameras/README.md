# Traffic cameras: harm prevented by speed and red light cameras

Code and data behind a planned maxmautner.com post on automated traffic enforcement. Watermark short URL: maxmautner.com/traffic-cameras.

Four charts:

- `speed-cameras`: injury crashes near 101 Chicago speed cameras, 2015-17, actual (raw count, 1,530) vs.
  expected without cameras (empirical Bayes estimate, 1,734). Source: Sutton & Tilahun, UIC report to the City
  of Chicago, Jan. 30, 2022, Table 1 (PDF p. 36); published as Tilahun, *Transportation Research Record*
  2677(1), 2023.
- `red-light-cameras`: modeled change in per capita fatal crash rates in cities that turned red light cameras on
  (57) or off (14). Source: Hu & Cicchino, *Journal of Safety Research* 61:141-148 (2017),
  doi:10.1016/j.jsr.2017.02.019. Values checked against Tables 3-8 of the IIHS manuscript (July 2016,
  `raw/iihs/hu_cicchino_2017.pdf`, not committed).
- `camera-communities`: U.S. communities operating red light and speed camera programs by year (IIHS counts,
  transcribed from the chart series embedded in IIHS's red light running and speed pages, updated July 2026).
- `who-pays`: share of Chicago camera tickets that incurred late fees or went unpaid, low- vs. upper-income
  neighborhoods, 2016-19 (same UIC report, ch. 5). The report does not state its income cutoffs (TK).

`data/nyc_speed_cameras.csv` holds figures from NYC DOT's 2024 speed camera report (corridor and 24/7 results),
not charted.

Why Chicago for speed cameras: of the US candidates it is the only one that reports crash counts with an
empirical Bayes control (corrects for cameras being sited at high-crash spots) and has a readable primary
document. The IIHS Montgomery County study (Hu & McCartt 2016) measures the share of crashes that were
serious, not the number of crashes; NYC DOT's reports are simple camera-vs.-comparison tallies.

## Reproduce

```
sh inputs/fetch.sh                # primary documents into raw/ (not committed)
python charts/charts.py --social  # output/*.png and social 4:5 versions
```

`data/` holds the hand-transcribed inputs with source URL and table/page per row; `data/secondary_checks.csv`
holds FHWA CMF Clearinghouse values (unrounded, with standard errors) used only as a cross-check.
