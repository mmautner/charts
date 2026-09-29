"""Every input the charts use, with the exact place it comes from.

Only the population figure is fetched programmatically (see fetch_census.py).
The rest are published in PDFs or web pages with no API, so they are recorded
here by hand. Check any of them against the cited source.
"""

# National Safety Council, Injury Facts, "Odds of Dying" (2024 data).
# https://injuryfacts.nsc.org/all-injuries/preventable-death-overview/odds-of-dying/
# Lifetime odds of dying in a motor vehicle crash: 1 in 101.
LIFETIME_ODDS_CRASH_DEATH = 1 / 101

# National Safety Council, Injury Facts, "Motor Vehicle: Introduction".
# https://injuryfacts.nsc.org/motor-vehicle/overview/introduction/
# Motor vehicle crash deaths in the United States, 2024.
CRASH_DEATHS_2024 = 39_254

# McCormick, T. H., Salganik, M. J., & Zheng, T. (2010). "How Many People Do You
# Know?: Efficiently Estimating Personal Network Size." Journal of the American
# Statistical Association, 105(489), 59-70. doi:10.1198/jasa.2009.ap08518
# Section 4.1, p. 64: "We estimated a mean network size of 611 (median, 472)."
# "Know" means: you know them and they know you by sight or by name, you could
# contact them, they live in the US, and you have had contact in the past 2 years.
NETWORK_SIZE_MEAN = 611
NETWORK_SIZE_MEDIAN = 472

# NHTSA, "The Economic and Societal Impact of Motor Vehicle Crashes, 2019
# (Revised)," DOT HS 813 403 (2023).
# https://crashstats.nhtsa.dot.gov/Api/Public/ViewPublication/813403
# Table 1-3, "Incidence Summary - 2019 Total Police-Reported and Unreported
# Injuries," p. 16, "Total" column. Counts are injured survivors by Maximum
# Abbreviated Injury Scale (MAIS) level; MAIS 3 = serious, 4 = severe, 5 = critical.
# MAIS 3 = 132,222 police-reported + 8,945 unreported. The 36,500 deaths are FARS
# (36,355) plus 145 people who died in hospital more than 30 days after the crash
# (Table 2-2, p. 34).
FATALITIES_2019 = 36_500
MAIS3_2019 = 141_167
MAIS4_2019 = 19_285
MAIS5_2019 = 7_187
