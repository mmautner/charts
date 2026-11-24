# Rail freight vs. rail passengers, by country

Code and data behind the maxmautner.com post "In the US, trains carry freight. In Japan, they carry people."
Short URL: maxmautner.com/rail-freight. The post uses `2-scatter-mainline` and `3-ratio-over-time`.

Dataset: `data/rail_freight_passenger.csv`. One row per country-year, with columns `freight_tkm`, `pkm_mainline`,
`pkm_all_rail`, `pkm_reported` and `population` (all in millions), plus the source and notes for each row. Every
source value, including ones not chosen, is in `data/source_observations.csv`. The cross-source check is
`data/qa_sources.csv`. Definitions, sources and gaps: [METHODS.md](METHODS.md).

Candidate charts (`output/<name>.png` and `output/social-<name>-4x5.png`): `1-ratio-{mainline,allrail}`,
`2-scatter-{mainline,allrail}`, `3-ratio-over-time`, `4-share`, `5-small-multiples`. These are drafts to pick from.

```
sh inputs/fetch.sh                                  # raw/ (not committed)
python -I model/stb_r1.py raw/stb/files data        # data/us_class1_ton_miles.csv
python -I model/japan.py raw/japan data             # data/japan_rail.csv
python -I model/assemble.py raw inputs data         # data/rail_freight_passenger.csv, source_observations.csv
python -I model/qa.py data                          # data/qa_sources.csv, prints >10% gaps
python charts/charts.py --social                    # output/
```

The model scripts need `pandas openpyxl xlrd odfpy pypdf` in addition to the repo requirements. Hand-transcribed
inputs (scanned or image-only tables: US Historical Statistics, Destatis Fachserie 1960–2002, NBS yearbook) are
in `inputs/*.csv`, with page references.
