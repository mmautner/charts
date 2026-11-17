# 50 years of flat infill

Code and inputs behind the charts in
["50 years of flat infill"](https://maxmautner.com/infill) on maxmautner.com.

The charts answer 2 questions: how many homes the US has built each decade on land that
was already urban (infill) versus land that wasn't (greenfield), and whether Houston's
1998 lot-size reform made its core build more than comparable Texas cores.

## Reproduce

From this folder, after `pip install -r ../requirements.txt`:

```
python fetch_census.py   # downloads ACS B25034 and the tract gazetteer to data/
python model.py          # prints every number the charts use
python charts.py         # writes the 10 PNGs to output/
```

`fetch_census.py` needs a free Census API key in `CENSUS_API_KEY`
([sign up](https://api.census.gov/data/key_signup.html)). Run it once and commit `data/`.
After that, the charts reproduce from the committed files.

## Inputs

| Input | Source |
|---|---|
| Housing units by year built, every census tract | [ACS 2020–2024 5-year, table B25034](https://data.census.gov/table/ACSDT5Y2024.B25034), fetched via the Census Data API |
| Tract land area and internal point | [2024 Census tract gazetteer](https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.2024.html) |
| 425 homes per sq mi as "already urban" (200 and 1,275 as sensitivity checks) | [Census 2020 urban area criteria, 87 FR 16706](https://www.federalregister.gov/documents/2022/03/24/2022-06180/urban-area-criteria-for-the-2020-census-final-criteria) |
| California population at each decennial census, 1970–2020 | [Census Bureau, Historical Population Change Data (1910–2020)](https://www.census.gov/data/tables/time-series/dec/popchange-data-text.html) |
| US population at each decennial census, 1960–2020 | Same Census table |
| Occupied homes, California and US, 1960–2000; California crowding (more than 1 person per room), 1960–2000 | [Census Bureau, Historical Census of Housing Tables: Crowding](https://www.census.gov/data/tables/time-series/dec/coh-crowding.html) |
| Occupied homes, 2010 and 2020 | Census 2010 SF1 (H003002) and 2020 DHC (H3_002N), via the Census Data API |
| Household population (residents of occupied homes, excluding group quarters), California and US, 1960–2020 | 1960–1990 printed census volumes (table numbers and links in `inputs.py`); Census 2000 SF1 (P027002), 2010 SF1 (P016001) and 2020 DHC (P15_001N), via the Census Data API |
| Median home value, California and US, 1940–2000 | [Census Bureau, Historical Census of Housing Tables: Home Values](https://www.census.gov/data/tables/time-series/dec/coh-values.html) (unadjusted) |
| Median home value, California and US, 2005–2024 | ACS 1-year, table B25077, via the Census Data API (no standard 2020 release) |
| Los Angeles zoned capacity | Monkkonen, Lens & Manville, [Built-Out Cities?](https://ternercenter.berkeley.edu/wp-content/uploads/2023/04/MLM-Built-Out-Cities-2020.pdf) (Terner Center, 2020), citing Morrow (2013); City of Los Angeles, [Historic Housing and Land Use Study](https://planning.lacity.gov/odocument/3eaaa5ce-d96c-4325-a1b8-557218bbd0f5/Historic_Housing_and_Land_Use_Study.pdf), pp. 90 and 92 |
| Los Angeles population | Census Bureau, Population of the 100 Largest Cities (1960–1990); 2000 and 2010 SF1; 2020 PL 94-171 |
| Houston's 1998 minimum lot size reform inside I-610 | [Gray & Millsap (2020), *Journal of Planning Education and Research*](https://journals.sagepub.com/doi/10.1177/0739456X20935156) |
| I-610 outline and downtown Dallas and San Antonio centers | Traced by hand; see `inputs.py` |

All hand-entered values live in `inputs.py` with their citations.

## Method

**Infill vs. greenfield.** For each decade, a tract's starting density is the number of
still-standing homes built before that decade, divided by its land area. Homes built in
the decade count as infill if the tract was already at 425+ homes per sq mi, the density
at which the Census Bureau starts drawing urban areas from individual blocks, applied here
to whole tracts. That is only ~2/3 of a home per acre, so "infill" includes large-lot
suburbs as well as city neighborhoods. Otherwise they count as greenfield. The 2020s are
left off the chart because the ACS covers only part of the decade.

**California.** The same infill/greenfield split, restricted to California tracts (FIPS 06). Per-resident figures divide a decade's infill by California's population at the census that began it. `model.py` also prints the partial 2020s column; its infill share is usable, but its count covers only part of the decade, since the 5-year survey pools responses from 2020–2024.

**Homes per resident and residents per home.** Homes built per 1,000 residents divides each decade's still-standing homes by the population at the census that began it. Residents per occupied home is household population over occupied homes, which leaves out people in dorms, prisons, nursing homes and barracks and matches the Census Bureau's average household size; it starts in 1960 because the 1940 and 1950 crowding tables count only homes that reported persons per room. Crowding stops at 2000: the decennial census dropped the rooms question, and the ACS figures that replace it are not comparable.

**Texas cores.** Houston's core is every tract whose internal point falls inside I-610.
Dallas's and San Antonio's are every tract within a circle around downtown with the same
area as the loop (~90 sq mi). Dallas kept its large-lot rules through the 2010s; whether
San Antonio changed its lot-size rules over the period is TK.

## Assumptions and limitations

- **Demolished homes are missing.** B25034 counts homes standing at survey time, so every
  decade is undercounted by the homes since torn down, the oldest decades most. That also
  lowers starting densities, so infill is understated.
- **Teardowns count as new homes.** A house replaced by 3 townhouses counts as 3 new
  homes, not 2. Infill counts are gross, not net. In the Texas comparison this bias
  favors Houston, whose inner-loop townhouses mostly replaced older houses.
- **Definition sensitivity.** The long-run infill share depends on the definition.
  Counting a tract as urban only if it crossed 425 a full decade earlier gives a share
  that rises from 20% in the 1950s to 29% in the 2000s, rather than holding at 30–38%.
  Infill stays roughly flat from the 1970s under both, but not at the same level: the
  strict definition gives 4.4 million a decade in the 1970s through 1990s, 5.7 million in
  the 2000s and 5.1 million in the 2010s, not ~7 million. `model.py` prints both, plus the
  200 and 1,275 thresholds.
- **Tract geography.** Density is measured at the tract, so building in a small town
  inside a large rural tract counts as greenfield.
- **Year built is self-reported** and heaps on round years.
- **The Texas comparison is coarse.** Decade bins put the 1998 reform inside the 1990s,
  the cores are a highway loop and 2 circles, and West University Place (a separate city
  inside I-610 not covered by the reform) is included. It shows no Houston-specific jump
  at this resolution; it cannot rule out a smaller effect or a change in housing type.
