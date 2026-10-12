"""Hand-entered numbers, with the exact place each comes from.

Trip speeds and distances are fetched (fetch_nhts.py). Everything below is
published in reports or product pages with no machine-readable release.
"""

# --- Who is paying -------------------------------------------------------------

# Median hourly wage, all occupations, May 2024: $49,500 a year / 2,080 hours.
# BLS Occupational Employment and Wage Statistics. https://www.bls.gov/oes/
MEDIAN_WAGE = 23.80

# Marginal tax on an extra hour of work, single filer, full-time (2,080 hours).
# Federal: IRS Rev. Proc. 2025-32, 2026 standard deduction and brackets.
STANDARD_DEDUCTION = 16_100
FEDERAL_BRACKETS = [(12_400, 0.10), (50_400, 0.12), (105_700, 0.22), (201_775, 0.24), (float("inf"), 0.32)]
FICA = 0.0765          # Social Security 6.2% + Medicare 1.45%
STATE_TAX = 0.05       # flat stand-in for state income tax
HOURS_PER_YEAR = 2_080

# --- Cars ----------------------------------------------------------------------

# AAA, "Your Driving Costs" 2026: average new vehicle costs $12,863 a year to own
# and operate at AAA's assumed 15,000 miles. Reported by Repairer Driven News,
# https://www.repairerdrivennews.com/?p=248248
NEW_CAR_ANNUAL_AT_15K = 12_863
AAA_MILES = 15_000
# Per-mile part: AAA 2025 fuel 13.0 cents at $3.15/gal, scaled to the 2026 study's
# $4.152/gal, plus AAA 2025 maintenance, repair and tires 11.04 cents.
# https://newsroom.aaa.com/wp-content/uploads/2025/09/UPDATE-AAA-Fact-Sheet-Your-Driving-Cost-9.2025-1.pdf
NEW_CAR_PER_MILE = 0.130 * 4.152 / 3.15 + 0.1104

# Edmunds True Cost to Own, 2022 Volkswagen Passat SE, 15,000 miles a year:
# $37,905 over 5 years, of which fuel $10,018, maintenance $5,873, repairs $3,074.
# https://www.edmunds.com/volkswagen/passat/2022/cost-to-own/
USED_CAR_5YR = 37_905
USED_CAR_RUNNING_5YR = 10_018 + 5_873 + 3_074
EDMUNDS_MILES = 15_000

# FHWA Highway Statistics 2022, Table VM-1: ~10,900 miles per light-duty vehicle.
# https://www.fhwa.dot.gov/policyinformation/statistics/2022/pdf/vm1.pdf
CAR_MILES_PER_YEAR = 10_900

# Gabbe & Pierce (2016), Housing Policy Debate: a bundled garage space adds about
# $1,700 a year to rent. https://accessmagazine.org/spring-2017/the-hidden-cost-of-bundled-parking/
HOME_PARKING_PER_YEAR = 1_700

# Minutes per car trip to find parking and walk to the door.
# INRIX (2017): 17 hours a year searching for parking per driver,
# https://inrix.com/press-releases/parking-pain-us/ ; AAA Foundation American
# Driving Survey 2023: 2.43 driving trips a day,
# https://aaafoundation.org/wp-content/uploads/2024/08/202408-AAAFTS-American-Driving-Survey-2023.pdf
# Plus 1 minute walking from the space (assumption).
CAR_TERMINAL_MIN = 17 * 60 / (2.43 * 365) + 1.0

# --- E-bikes -------------------------------------------------------------------

# Lectric XP Lite2, long-range battery: $999. Class 1/2, 20 mph assist; can be set
# to 28 mph (Class 3) if relabeled (Cal. Veh. Code 24016(d)).
# https://lectricebikes.com/products/xp-lite-arctic-white-long-range-ebike
EBIKE_PRICE = 999
EBIKE_LIFE_YEARS = 5   # written off to zero; Upway reports ~40% of value left at 3 years
# Replacement battery, 672 Wh: $575. https://lectricebikes.com/products/xp-long-range-battery
BATTERY_PRICE = 575
BATTERY_WH = 672
# Bosch: after 500 full charges a battery keeps 60-70% of capacity; treated here as
# end of life. https://www.bosch-ebike.com/ca/news/11-questions-about-the-ebike-battery
BATTERY_CYCLES = 500
# Evtimov et al. (2015), Transport Problems 10(3): 11-18 Wh/km measured in town.
# 12.5 Wh/km = 20.1 Wh/mile at 20 mph assist. 30 Wh/mile at 28 mph is an assumption.
WH_PER_MILE = {"Class 2": 20.1, "Class 3": 30.0}
# AAA 2026: home charging averaged 18 cents per kWh.
ELECTRICITY_PER_KWH = 0.18
# Multiscope E-bike Monitor (Netherlands, ~3,200 riders): EUR 41-54 a year. Raised
# to $150 for US shop labor. https://road.cc/content/news/dutch-e-bike-maintenance-market-worth-eu200m-year-293091
EBIKE_UPKEEP_PER_YEAR = 150
EBIKE_MILES_PER_YEAR = 3_000

# Schleinitz et al. (2017), "The German Naturalistic Cycling Study," Safety Science
# 92: 290-297, Table 4. Mean moving speed (standstill removed): pedelec 17.4 km/h,
# S-pedelec (45 km/h cap, same as US Class 3) 24.5 km/h. 9 S-pedelec riders.
EBIKE_MOVING_MPH = {"Class 2": 17.4 / 1.609, "Class 3": 24.5 / 1.609}
# Minutes per bike trip stopped or parking: 1 minute to lock and unlock (assumption)
# plus 15 s average wait per signal (Enschede, ~31,000 passages; Findings, 2019,
# https://findingspress.org/article/9636) at 2 signals per mile (assumption).
EBIKE_LOCK_MIN = 1.0
SIGNAL_WAIT_S = 15
SIGNALS_PER_MILE = 2

# Chart 1 compares this many miles a year of short trips by each vehicle.
SHORT_TRIP_MILES_PER_YEAR = 3_000

# --- Commute time series ---------------------------------------------------------

# Average one-way travel time to work, minutes, workers 16+ who did not work from home.
# 1980-2000: decennial census. Census 2000 Brief C2KBR-33, "Journey to Work: 2000",
#   https://www2.census.gov/library/publications/decennial/2000/briefs/c2kbr-33.pdf
# 2006-2019: ACS 1-year, ACS-47 (2021) Appendix Table 1,
#   https://www.census.gov/library/publications/2021/acs/acs-47.html
# 2021-2022: Census press release, https://census.gov/newsroom/press-releases/2024/travel-to-work-since-pandemic.html
# 2023-2024: "Commuting At A Glance," https://www.census.gov/topics/employment/commuting/guidance/acs-1yr.html
# No 2020 ACS 1-year estimate (pandemic data collection). 2025 ACS 1-year not yet released.
COMMUTE_DECENNIAL = {1980: 21.7, 1990: 22.4, 2000: 25.5}
COMMUTE_ACS = {2006: 25.0, 2007: 25.3, 2008: 25.5, 2009: 25.1, 2010: 25.3, 2011: 25.5, 2012: 25.7,
               2013: 25.8, 2014: 26.0, 2015: 26.4, 2016: 26.6, 2017: 26.9, 2018: 27.1, 2019: 27.6,
               2021: 25.6, 2022: 26.4, 2023: 26.8, 2024: 27.2}
