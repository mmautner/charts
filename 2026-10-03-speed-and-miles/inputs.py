"""Hand-entered numbers, with the exact place each comes from.

The travel figures are fetched (fetch_nhts.py). These are published in reports
with no machine-readable release, so they are recorded here by hand.
"""

# Elvik, R. (2009). "The Power Model of the relationship between speed and road
# safety: Update and new analyses." TOI Report 1034/2009, Institute of Transport
# Economics, Oslo. Meta-analysis of 115 studies.
# https://www.toi.no/publications/the-power-model-of-the-relationship-between-speed-and-road-safety-update-and-new-analyses-article27943-29.html
# Best-estimate exponents for fatal accidents: 4.1 on rural roads and freeways,
# 2.6 on urban roads. Change in fatal crashes = (new speed / old speed) ** exponent - 1.
FATAL_EXPONENT_RURAL_FREEWAY = 4.1
FATAL_EXPONENT_URBAN = 2.6

# Speed cases shown in the chart: (label, from mph, to mph, exponent).
SPEED_CASES = [
    ("Freeway, 65 to 60 mph", 65, 60, FATAL_EXPONENT_RURAL_FREEWAY),
    ("Rural highway, 55 to 50 mph", 55, 50, FATAL_EXPONENT_RURAL_FREEWAY),
    ("City arterial, 35 to 30 mph", 35, 30, FATAL_EXPONENT_URBAN),
    ("Neighborhood street, 25 to 20 mph", 25, 20, FATAL_EXPONENT_URBAN),
]
MILES_CUT = 0.05          # the comparison: drive 5% fewer miles at the same speed
EXAMPLE_TRIP_MILES = 20   # for the "extra minutes" figure

# Olaisen, R. H., Rossen, L. M., Warner, M., & Anderson, R. N. (2019).
# "Unintentional Injury Death Rates in Rural and Urban Areas: United States,
# 1999-2017." NCHS Data Brief No. 343. https://stacks.cdc.gov/view/cdc/79883
# Figure 2: age-adjusted motor vehicle traffic death rates per 100,000, 2017, by
# urbanization of the decedent's county of RESIDENCE (2013 NCHS scheme).
MVT_DEATHS_PER_100K_2017 = {
    "large_central_metro": 8.3,
    "large_fringe_metro": 9.6,
    "small_metro": 12.8,   # medium and small metro counties (under 1 million)
    "rural": 19.7,         # micropolitan and noncore (nonmetro) counties
}

# Share of US population in each 2013 NCHS county category, used to combine the
# large central and large fringe rates into 1 "MSA 1M+" rate to match NHTS, which
# cannot separate the two. Source: NCHS, "NCHS Urban-Rural Classification Scheme
# for Counties," https://www.cdc.gov/nchs/data_access/urban_rural.htm, table
# comparing the 2023 and 2013 schemes, "Percent of U.S. resident population,"
# 2013 scheme column.
POP_SHARE_PCT = {"large_central_metro": 30.5, "large_fringe_metro": 24.7}
