"""Hand-entered numbers, with the exact place each comes from.

The permit series are fetched (fetch_hcd.py, fetch_census.py). These figures are
HCD's own published summaries, kept here so model.py can check the fetched series
against them.
"""

# HCD, Accessory Dwelling Unit Handbook (March 2026), "ADUs in California," p. 4.
# https://www.hcd.ca.gov/sites/default/files/docs/policy-and-research/ADU-Handbook-Update.pdf
# "Between 2016-2024, the number of ADUs permitted annually in the state grew from
# 1,336 to 30,354 ... In 2024, ADUs comprised more than 26.6 percent of all homes
# permitted statewide."
# HCD, Accessory Dwelling Unit Handbook (2025 edition), p. 4: 26,924 ADUs permitted
# in 2023, "more than 21 percent of all homes permitted statewide."
HCD_PUBLISHED_ADU_PERMITS = {2016: 1_336, 2023: 26_924, 2024: 30_354}
HCD_PUBLISHED_ADU_SHARE = {2023: 0.21, 2024: 0.266}
