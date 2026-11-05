# RTM oversight: who can audit the 101 express lanes' money

Code and data behind a planned maxmautner.com post comparing Measure RTM's oversight with the US 101 express
lanes in San Mateo County. Watermark short URL: maxmautner.com/rtm-oversight.

One chart:

- `express-lanes-funding`: the express lanes' $514.3 million planned budget by funding source, grouped by
  whether an inspector general can audit it. State and federal money ($282.8 million: SB 1 Solutions for
  Congested Corridors $200M, SB 1 Local Partnership Program $21.8M, STIP regional share $33.5M, ITIP $18M,
  repurposed federal earmark $9.5M) falls under Caltrans' Inspector General, which audits "external entities
  that receive state and federal transportation funds from Caltrans"
  ([ig.dot.ca.gov/about-us](https://ig.dot.ca.gov/about-us)). Regional bridge tolls ($95M) and local money
  ($83.5M) answer to no inspector general; RM3 created one for BART only
  ([MTC RM3 FAQ](https://es.mtc.ca.gov/sites/default/files/documents/2023-02/RM_3_FAQ_02-07-2023.pdf)).
  Private sector money ($53M) is shown but is not public.

## Source

San Mateo County Express Lanes Joint Powers Authority,
[Application for Toll Facility to the California Transportation Commission](https://catc.ca.gov/-/media/ctc-media/documents/programs/toll-facilities-program/sm101hotlane_ctcapplication_tollfacility_v07_complete.pdf),
June 28, 2019, Exhibit 14, Project Capital Funding (PDF p. 52). Every row of `data/express_lanes_funding.csv`
is a line of that exhibit, in thousands of dollars converted to millions.

Judgment calls:

- "Local money" is Measure A ($30.5M) plus the line "JPA (Toll Revenue / Others)" ($53M), which the application
  says would be fronted with Measure A sales tax or other local funds and repaid from future toll revenue.
- The exhibit marks ITIP as a federal source; it is grouped with state money either way, since Caltrans'
  Inspector General covers both.
- The exhibit does not name the bridge toll program behind "Regional Toll Funds."
- This is the 2019 plan. Streetsblog put the finished project near $600 million; how the added cost was
  funded is not broken out here.

## Reproduce

```
sh inputs/fetch.sh                # source pages into raw/ (not committed)
python charts/charts.py --social  # output/*.png and the social 4:5 version
```

`data/express_lanes_funding.csv` holds the hand-transcribed figures with source URL per row.
