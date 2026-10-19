# The years Americans outlive driving

Code and data behind the charts in the post on older drivers on maxmautner.com at
[maxmautner.com/senior-driving](https://maxmautner.com/senior-driving).

Two charts. Per 100 million miles driven in 2017, how often drivers of each age were in a fatal
crash and how many people outside their vehicle were killed. And how many years Americans can
expect to live after 65 without driving, by sex.

## Reproduce

From this folder (Python with pandas, numpy, openpyxl; matplotlib for the charts):

```
sh inputs/fetch.sh                                         # NHTS 2017/2022, FARS 2017, life tables, FHWA DL-20 into raw/
CENSUS_API_KEY=... python -I inputs/fetch_census.py raw/census   # 2020 Census DHC (key from the environment only)
python -I model/estimates.py raw data      # share not driving by age, years not driving (Sullivan), 2017 vs 2022
python -I model/crash_risk.py raw data     # FARS / NHTS: fatal crashes and deaths per mile by driver age; how non-drivers 65+ travel
python -I model/chart_data.py              # data/chart_*.csv, the series the charts draw
python charts/charts.py --social           # output/*.png, social 4:5 versions, og-image.png
```

`charts/charts.py` reads only `data/chart_*.csv`, so the charts re-render without the raw
downloads. `raw/` is not committed.

## Inputs

| Input | Source |
|---|---|
| 2017 National Household Travel Survey: persons, trips, 98 jackknife replicate weights | [nhts.ornl.gov](https://nhts.ornl.gov/) |
| 2022 National Household Travel Survey (check only; no replicate weights published) | [nhts.ornl.gov](https://nhts.ornl.gov/) |
| NHTSA Fatality Analysis Reporting System 2017, national CSVs | [static.nhtsa.gov](https://static.nhtsa.gov/nhtsa/downloads/FARS/2017/National/FARS2017NationalCSV.zip) |
| NCHS U.S. life tables, 2017 (also 2019, 2022-2024 as checks) | [NVSR 68-07](https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/NVSR/68_07/) |
| 2020 Census DHC: population, group quarters, nursing facilities by age and sex (P12, PCO1, PCO5) | [api.census.gov](https://api.census.gov/data/2020/dec/dhc) |
| FHWA Highway Statistics DL-20, licensed drivers by age | [fhwa.dot.gov](https://www.fhwa.dot.gov/policyinformation/statistics.cfm) |

## Method

**Years not driving.** Sullivan method: each age group's share of people who don't drive (NHTS
derived driver status, `DRIVER` = 2) times the person-years lived in that group from the life
table, summed from 65. The headline counts 2020 Census nursing-facility residents as non-drivers
(the survey covers households only). SEs from the 98 replicate weights,
SE = sqrt(6/7 × Σ(rep − est)²); life tables and Census counts treated as fixed. The 2022 survey
gives lower figures (`data/survey_2017_vs_2022.csv`) but has fewer than 50 non-drivers in most
age cells, so the charts use 2017.

**Crash risk per mile.** Numerator: FARS 2017 drivers of light vehicles (body types 1-49: cars,
SUVs, vans, pickups) in fatal crashes, by driver age; 416 drivers with unknown age dropped.
Denominator: NHTS 2017 vehicle miles (`VMT_MILE`) on trips the person drove in a car, SUV, van or
pickup, annualized with the trip weight (365 × person weight). Others killed = deaths outside the
driver's vehicle (other vehicles' occupants, pedestrians, cyclists); in multi-vehicle crashes every
involved driver is credited, so this measures involvement, not blame. FARS has no sampling error;
SEs come from the survey miles. NHTS covers household residents' travel, so commercial and visitor
miles are missing from the denominator for every age group.

## Data

| File | What it holds |
|---|---|
| `chart_crash_per_mile.csv` | Chart 1: crashes and others killed per 100M miles, 4 age groups, SE, counts, survey trips |
| `chart_years_not_driving.csv` | Chart 2: life expectancy at 65, years driving / not driving, SE, n, trips per day |
| `crash_risk_by_age_2017.csv` | All age groups and rollups: miles, drivers, crash and death counts and rates, shares, SEs, n |
| `nondrivers_65plus_modes_2017.csv` | Trips per day and mode shares for people 65+ who drive and don't, SE, n |
| `years_not_driving.csv` | Every specification (household only, + nursing homes, + all group quarters, life-table years, urban/rural, without CA/NY, 2022) |
| `not_driving_by_age5.csv`, `not_driving_by_age1_2017.csv` | Share not driving by age, SE, MOE, n |
| `not_driving_65plus_totals.csv` | Counts and shares of people 65+ not driving |
| `survey_2017_vs_2022.csv` | Diagnostics behind using 2017 |
| `census_2020_nursing.csv` | 2020 Census nursing-facility shares by age and sex |
