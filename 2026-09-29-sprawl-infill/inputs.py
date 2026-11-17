"""Every hand-entered input the charts use, with the exact place it comes from.

The housing data itself is fetched (see fetch_census.py). What lives here are the
definitions: the density threshold for "already urban" and the geography of the
Houston comparison.
"""

# U.S. Census Bureau, "Urban Area Criteria for the 2020 Census - Final Criteria,"
# Federal Register 87 FR 16706 (March 24, 2022). Initial urban cores are census
# blocks with at least 425 housing units per square mile; 200 fills in the rest of
# an urban area; every urban area needs a nucleus of at least 1,275.
# https://www.federalregister.gov/documents/2022/03/24/2022-06180/urban-area-criteria-for-the-2020-census-final-criteria
URBAN_CORE_HU_PER_SQMI = 425
SENSITIVITY_HU_PER_SQMI = (200, 1275)  # the Census's other 2 thresholds

# Houston's I-610 loop, traced through its interchanges (lat, lon). Checked by eye
# against an OpenStreetMap basemap; tract assignment uses each tract's internal point.
# West University Place, a separate city inside the loop that Houston's reform did not
# cover, is included (a handful of tracts).
I610_LOOP = [
    (29.8065, -95.4540), (29.8085, -95.3830), (29.8070, -95.3290),
    (29.8065, -95.2949), (29.7952, -95.2783), (29.7780, -95.2730),
    (29.7300, -95.2680), (29.6930, -95.3060), (29.6770, -95.3870),
    (29.6830, -95.4490), (29.7300, -95.4580), (29.7850, -95.4560),
]

# Comparison cores: circles around downtown with the same area as the I-610 loop.
# Centers are the downtown business districts, to ~0.01 degree.
DOWNTOWNS = {
    "Dallas": (32.7767, -96.7970),
    "San Antonio": (29.4241, -98.4936),
}

# Houston's 1998 amendment to Chapter 42 of its Code of Ordinances cut the minimum
# lot size inside I-610 from 5,000 sq ft to as low as 1,400 sq ft.
# Gray & Millsap (2020), "Subdividing the Unzoned City," Journal of Planning
# Education and Research. doi:10.1177/0739456X20935156
HOUSTON_REFORM_YEAR = 1998

# California resident population at each decennial census, used to put infill per
# resident: a decade's homes are divided by the population when it began.
# U.S. Census Bureau, "Historical Population Change Data (1910-2020)."
# https://www.census.gov/data/tables/time-series/dec/popchange-data-text.html
CA_FIPS = "06"
CA_POPULATION = {
    1940: 6_907_387, 1950: 10_586_223, 1960: 15_717_204,
    1970: 19_953_134, 1980: 23_667_902, 1990: 29_760_021,
    2000: 33_871_648, 2010: 37_253_956, 2020: 39_538_223,
}

# US resident population, same source as CA_POPULATION.
US_POPULATION = {
    1960: 179_323_175, 1970: 203_211_926, 1980: 226_545_805, 1990: 248_709_873,
    2000: 281_421_906, 2010: 308_745_538, 2020: 331_449_281,
}

# Household population: residents of occupied homes, leaving out the ~2-3% in group
# quarters (dorms, prisons, nursing homes, barracks), so residents per occupied home
# matches the Census Bureau's average household size.
# 1960: 1960 Census of Population, Vol. 1 Part 1 (US Summary), Table 62.
#   https://www2.census.gov/library/publications/decennial/1960/population-volume-1/vol-01-01-h.pdf
# 1970: US: 1970 Census, Vol. 1 Part 1 (US Summary), Table 65.
#   https://www2.census.gov/library/publications/decennial/1970/population-volume-1/1970a_us1-08.pdf
#   CA: 1970 Census, Vol. 1 Part 6 (California), Table 22.
#   https://www2.census.gov/prod2/decennial/documents/1970a_ca1-02.pdf
# 1980: US: PC80-1-B1 (US Summary), Table 46. https://archive.org/details/1980censusofpopu8011u
#   CA: PC80-1-B6 (California), Table 14: 23,667,902 total minus 568,049 in group quarters.
#   https://www2.census.gov/library/publications/decennial/1980/volume-1/california/1980a_caab-03.pdf
# 1990: 1990 CP-1-1 (US Summary), Tables 26 and 263.
#   https://www2.census.gov/library/publications/decennial/1990/cp-1/cp-1-1.pdf
# 2000: Census 2000 SF1, P027002. 2010: Census 2010 SF1, P016001.
# 2020: Census 2020 DHC, P15_001N (Census Data API).
CA_HH_POPULATION = {
    1960: 15_207_432, 1970: 19_374_198, 1980: 23_099_853, 1990: 29_008_161,
    2000: 33_051_894, 2010: 36_434_140, 2020: 38_620_291,
}
US_HH_POPULATION = {
    1960: 174_373_302, 1970: 197_399_913, 1980: 220_796_157, 1990: 242_012_129,
    2000: 273_643_273, 2010: 300_758_215, 2020: 323_210_265,
}

# Occupied housing units (households) at each census, for residents per occupied home.
# 1960-2000: U.S. Census Bureau, Historical Census of Housing Tables, "Crowding."
# https://www.census.gov/data/tables/time-series/dec/coh-crowding.html
# (crowding1960.txt ... crowding2000.txt). The 1940 and 1950 tables count only units
# that reported persons per room, so the series starts in 1960.
# 2010: Census 2010 SF1, H003002. 2020: Census 2020 DHC, H3_002N (Census Data API).
CA_OCCUPIED = {
    1960: 4_982_108, 1970: 6_573_861, 1980: 8_629_866, 1990: 10_381_206,
    2000: 11_502_870, 2010: 12_577_498, 2020: 13_475_623,
}
US_OCCUPIED = {
    1960: 53_023_875, 1970: 63_449_747, 1980: 80_389_673, 1990: 91_947_410,
    2000: 105_480_101, 2010: 116_716_292, 2020: 126_817_580,
}

# California occupied units with more than 1 person per room, same Census crowding
# tables. Stops at 2000: the decennial census dropped the rooms question after 2000,
# and the ACS that replaced it is not comparable (it reports ~8% for California in 2010).
CA_CROWDED_SHARE = {1960: 0.095, 1970: 0.079, 1980: 0.074, 1990: 0.123, 2000: 0.152}

# Median value of owner-occupied homes, nominal dollars.
# 1940-2000: U.S. Census Bureau, Historical Census of Housing Tables, "Home Values" (unadjusted).
#   https://www2.census.gov/programs-surveys/decennial/tables/time-series/coh-values/values-unadj.txt
# 2005-2024: ACS 1-year, B25077 (Census Data API). 2020 is missing: the Census Bureau did not
#   release standard 2020 ACS 1-year estimates.
CA_MEDIAN_VALUE = {
    1940: 3_527, 1950: 9_564, 1960: 15_100, 1970: 23_100, 1980: 84_500, 1990: 195_500,
    2000: 211_500, 2005: 477_700, 2006: 535_700, 2007: 532_300, 2008: 467_000, 2009: 384_200,
    2010: 370_900, 2011: 355_600, 2012: 349_400, 2013: 373_100, 2014: 412_700, 2015: 449_100,
    2016: 477_500, 2017: 509_400, 2018: 546_800, 2019: 568_500, 2021: 648_100, 2022: 715_900,
    2023: 725_800, 2024: 759_500,
}
US_MEDIAN_VALUE = {
    1940: 2_938, 1950: 7_354, 1960: 11_900, 1970: 17_000, 1980: 47_200, 1990: 79_100,
    2000: 119_600, 2005: 167_500, 2006: 185_200, 2007: 194_300, 2008: 197_600, 2009: 185_200,
    2010: 179_900, 2011: 173_600, 2012: 171_900, 2013: 173_900, 2014: 181_200, 2015: 194_500,
    2016: 205_000, 2017: 217_600, 2018: 229_700, 2019: 240_500, 2021: 281_400, 2022: 320_900,
    2023: 340_200, 2024: 360_600,
}

# City of Los Angeles zoned capacity: residents its zoning could hold if every lot were built
# to its maximum.
# 1960 (~10M) and 2020 (~4M, "where it stays today"): Monkkonen, Lens & Manville, "Built-Out
#   Cities?", Terner Center, Feb. 2020, citing Morrow (2013).
#   https://ternercenter.berkeley.edu/wp-content/uploads/2023/04/MLM-Built-Out-Cities-2020.pdf
# Early 1970s (10.5M) and the 1981 General Plan Zoning Consistency Program that cut it to 4M:
#   City of Los Angeles, Historic Housing and Land Use Study, pp. 90 and 92 of the PDF.
#   https://planning.lacity.gov/odocument/3eaaa5ce-d96c-4325-a1b8-557218bbd0f5/Historic_Housing_and_Land_Use_Study.pdf
LA_ZONED_CAPACITY = {1960: 10.0e6, 1970: 10.5e6, 1990: 4.0e6, 2020: 4.0e6}
LA_REZONING_START = 1981

# City of Los Angeles population at each census. 1960-1990: Census Bureau, "Population of the
# 100 Largest Cities" (POP-twps0027). 2000/2010: SF1 P001001. 2020: PL 94-171 P1_001N.
LA_POPULATION = {
    1960: 2_479_015, 1970: 2_816_061, 1980: 2_966_850, 1990: 3_485_398,
    2000: 3_694_820, 2010: 3_792_621, 2020: 3_898_747,
}
