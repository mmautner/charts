# Driving 5 mph slower beats driving 5% less

Code and data behind the charts in ["Driving 5 mph slower beats driving 5% less"](https://maxmautner.com/slower) on maxmautner.com.

The charts compare 2 ways to cut the chance of a fatal crash: driving 5 mph slower, and
driving 5% fewer miles. They then split the gap in traffic deaths between rural and
big-metro residents into miles driven and deaths per mile, and show how driving time,
distance, and speed differ by where drivers live.

## Reproduce

From this folder, after `pip install -r ../requirements.txt`:

```
pip install pandas scipy   # needed by fetch_nhts.py only
python fetch_nhts.py       # 2017 NHTS public-use files, summarized to weighted estimates
python model.py            # prints every number the charts use
python charts.py           # writes the PNGs to output/
```

Commit `data/`. The NHTS files are ~1.2 GB unzipped, so `fetch_nhts.py` commits only its
summary (`nhts2017_estimates.csv`, 118 rows with margins of error) and a metadata file
recording the fetch date and the totals it checked. To reuse a copy already on disk:
`python fetch_nhts.py --dir path/to/nhts`.

## Inputs

| Input | Source |
|---|---|
| Fatal-crash exponents of the power model: 4.1 (rural roads, freeways), 2.6 (urban roads) | [Elvik 2009, TØI Report 1034/2009](https://www.toi.no/publications/the-power-model-of-the-relationship-between-speed-and-road-safety-update-and-new-analyses-article27943-29.html); in `inputs.py` |
| Traffic deaths per 100,000 by urbanization of county of residence, 2017, age-adjusted: 8.3 large central metro, 9.6 large fringe metro, 12.8 small metro, 19.7 rural | [NCHS Data Brief 343](https://stacks.cdc.gov/view/cdc/79883), Figure 2; in `inputs.py` |
| Population shares of large central (30.5%) and large fringe (24.7%) metro counties, 2013 scheme | [NCHS Urban-Rural Classification Scheme for Counties](https://www.cdc.gov/nchs/data_access/urban_rural.htm); in `inputs.py` |
| Household vehicle miles per person; minutes, miles, and speed driven per licensed driver per day; by metro size of the home county | [2017 National Household Travel Survey](https://nhts.ornl.gov/) public-use files and replicate weights, fetched |

## Method

**5 mph slower vs. 5% fewer miles.** Fatal crashes change by (new speed / old speed) raised
to the power-model exponent, minus 1. Driving 5% fewer miles at the same speed is taken to
cut crashes 5%, which assumes the miles cut are as dangerous as the miles kept.

**Miles and deaths by home.** NHTS groups households by the metro size of their home county
(`MSASIZE`): not in a metro area, metro under 1 million, and metro of 1 million+. These
match the NCHS county categories, which are also built from metro definitions. NHTS
cannot separate large central from large fringe metro counties, so the big-metro death
rate is the population-weighted mean of the 2 (8.88 per 100,000). Width is household
vehicle miles per person (`2a`: each household's annual vehicle miles divided by everyone
in it, so the denominator covers all ages like the death rates). Area is deaths per
100,000 residents. Height is deaths divided by miles.

**Driving time and speed.** Travel-day driving per licensed driver, counting drivers who
did not drive that day as 0. Speed is total miles divided by total minutes over trips
with both recorded.

`fetch_nhts.py` recomputes every estimate under the survey's 98 replicate weights and
checks its weighted totals against FHWA's published figures (households, licensed
drivers, and annual vehicle miles) before writing anything.

## Limitations

- **Individual vs. average speed.** Elvik's exponents come from changes in a road's
  average speed. A [2019 meta-analysis](https://toi.brage.unit.no/toi-xmlui/bitstream/11250/2602278/1/Elvik_10.1016_j.aap.2018.11.014.pdf)
  found the same relationship for individual drivers. Elvik's
  [later work](https://toi.brage.unit.no/toi-xmlui/handle/11250/2602719) found a given
  percentage cut matters less at low starting speeds, so the 25 to 20 mph figure is likely
  high.
- **Whose crashes.** Slowing down reduces the crashes a driver causes and their severity.
  Fewer miles also cuts exposure to other drivers. The chart compares the 2 as if they
  act on the same crashes.
- **Height is derived.** Deaths per mile divides residents' deaths (including pedestrians
  and people killed by someone else's driving) by residents' miles driven. It describes
  the risk attached to residents' driving, not a measured crash rate per mile.
- **Other miles measures.** `model.py` prints the chart with 2 other NHTS measures: miles
  per person aged 5+ (`2c`: +18% miles, 1.88× deaths per mile) and travel-diary miles
  (`2b`: +24% miles, 1.79× deaths per mile). The finding that most of the death gap is
  per-mile risk holds under all 3.
- **Age adjustment.** Death rates are age-adjusted; miles are not.
- **Year.** Both deaths and miles are 2017, the last NHTS before the pandemic. The 2022
  NHTS captured only ~71% of external estimates of household miles.
- **County averages.** A walkable neighborhood and an exurban subdivision in the same big
  metro fall in the same category.
- **First fetch.** The committed summary was produced by the analysis in `fetch_nhts.py`
  run in a separate environment, because nhts.ornl.gov was not reachable where the charts
  were built (see `nhts2017_meta.json`). Rerunning `fetch_nhts.py` should reproduce it.
