# Who lives without a car in the Bay Area

Code and data behind the charts in the post on car-free households on maxmautner.com
at [maxmautner.com/sf-car-free](https://maxmautner.com/sf-car-free).

The charts describe the ~269,000 Bay Area households with no vehicle: who heads them, how
income splits them into a constrained group and a group that chose it, how that mix
shifted between 2015-19 and 2020-24 outside San Francisco, and how their workers'
commutes changed.

## Reproduce

From this folder, after `pip install -r ../requirements.txt pandas`:

```
python inputs/fetch_pums.py --raw RAWDIR --cache cache   # ~1.5 GB of downloads; Bay Area extracts to cache/
PUMS_CACHE=cache python model/findings.py                # every 2020-24 estimate, printed and saved to data/
PUMS_CACHE=cache python model/trend.py                   # 2015-19 vs 2020-24, and the 1-year series
PUMS_CACHE=cache python model/people.py                  # commute modes, ages, difference tests
PUMS_CACHE=cache python model/chart_data.py              # data/chart_*.csv, the series the charts draw
python charts/charts.py --social                         # output/*.png, social 4:5 versions, og-image.png
```

`charts/charts.py` reads only `data/chart_*.csv`, so the charts re-render without the
microdata. `cache/` is not committed.

## Inputs

| Input | Source |
|---|---|
| 2020-2024 and 2015-2019 5-year PUMS, California households and persons | [ACS PUMS](https://www2.census.gov/programs-surveys/acs/data/pums/2024/5-Year/), [2019](https://www2.census.gov/programs-surveys/acs/data/pums/2019/5-Year/) |
| 1-year PUMS, California households, 2012-2019 and 2021-2024 | `https://www2.census.gov/programs-surveys/acs/data/pums/<year>/1-Year/` |
| PUMA names (to check the county-prefix rule) | [TIGER 2024 PUMA20](https://www2.census.gov/geo/tiger/TIGER2024/PUMA20/tl_2024_06_puma20.zip), [TIGER 2019 PUMA10](https://www2.census.gov/geo/tiger/TIGER2019/PUMA/tl_2019_06_puma10.zip) |
| CPI-U annual averages, 2019 = 255.657, 2024 = 313.689 | [BLS series CUUR0000SA0](https://data.bls.gov/timeseries/CUUR0000SA0); in `model/pums.py` |

## Method

**Universe.** Housing units (`TYPEHUGQ`/`TYPE` = 1) with at least 1 person, in the 9 Bay Area
counties, identified by the first 3 digits of the PUMA code (county FIPS). That rule holds
for California's 2010 and 2020 PUMAs, checked against every TIGER PUMA name; it fails for
the 2000 PUMAs, so the 1-year series starts in 2012.

**Car-free** means `VEH` = 0. Income is `HINCP` × `ADJINC`/1e6; 2015-19 incomes are then
moved to 2024 dollars with CPI-U.

**Life stage**, from the householder's age and whether anyone under 18 lives there:
families (anyone under 18), seniors (householder 65+), young adults (householder under 35),
midlife (35-64).

**Disability** flags a household with an adult reporting ambulatory difficulty (`DPHY`) or
difficulty living independently (`DOUT`).

**Commute mode** is `JWTRNS` for workers. "Car" includes riding as a passenger; PUMS can't
separate it from driving a work or borrowed vehicle.

**Standard errors** come from the 80 replicate weights, SE = sqrt(4/80 × Σ(rep − full)²).
Charts show 90% intervals (1.645 × SE). Differences within one sample use the shared
replicates; differences across the 2 non-overlapping 5-year samples treat them as
independent. Every table in `data/` carries the unweighted sample count (`n`) and the
car-free sample count (`n_cf`). Cells under 50 car-free sample households are flagged
`thin`; none of the charted cells are.

## Limitations

- **Choice vs. constraint is inferred**, from income, age and disability. The survey
  doesn't ask why a household has no car.
- **Building type isn't causal.** Households that plan to live car-free may pick apartments.
- **2020-24 includes 2020**, when Census Bureau collection was disrupted.
- **CPI-U is national.** Bay Area incomes rose faster than CPI-U, so households moved up the
  income bands between the 2 periods. The within-band rise in car-free shares outside SF may
  partly reflect who moved into each band.
- **"Workers" includes anyone who worked last week.** Remote workers count, and their
  "commute" is working from home.
