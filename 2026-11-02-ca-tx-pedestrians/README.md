# California vs. Texas: pedestrian deaths per person, per mile driven, per walk

Code and data behind a planned maxmautner.com post. Watermark short URL: `maxmautner.com/walking-deaths`.

Charts: `deaths-and-traffic` (change since 2010 in people killed while walking in California and in miles
driven per resident, 2010-2023) and `driving-and-walking` (miles driven per resident and the share of commuters
who walk to work, California vs. Texas, 2010-2023), plus `og-image.png`. Deaths by road type and owner
(`data/fars_deaths_by_road.csv`) and the per-mile/per-walk rates are computed but not charted. Post draft: not
written yet.

```
sh inputs/fetch.sh                       # raw/ (not committed); ACS needs CENSUS_API_KEY
python -I model/fars.py raw/fars/x data  # data/fars_pedestrian_deaths.csv
python -I model/nhts.py raw/nhts/x data  # data/nhts2017_walking.csv, nhts2017_walk_totals_replicates.csv
python -I model/nhts2009.py raw/nhts2009/x data      # data/nhts2009_walking.csv
python -I model/acs.py raw/census/acs_series data   # data/acs_walk_commute.csv (needs CENSUS_API_KEY at fetch)
python -I model/rates.py                 # data/ca_tx_pedestrian_rates.csv (+ population.csv, vmt_vm2.csv)
python charts/charts.py --social         # output/*.png, social 4:5 versions, og-image.png
```
