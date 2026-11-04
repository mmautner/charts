# Methods and caveats: California vs. Texas pedestrian deaths

Every number is in `data/ca_tx_pedestrian_rates.csv` (inputs and outputs, with SE, unweighted n where it
applies, and source URL). Charts read only `data/`. FARS 2010-2024 are fetched; road-owner detail is usable only in 2016 and 2021-2024.

## Sources

- **Deaths:** NHTSA FARS national CSV files, person file, `PER_TYP` 5 (pedestrian) and `INJ_SEV` 4 (fatal),
  by state of the crash. 2016-2023 are final files (2023 final released 2026-04-01). 2024 is the annual report
  file, not final. Check: 2017 all-person deaths total 37,473 and 2022 pedestrians total 7,593, matching NHTSA.
- **VMT:** FHWA Highway Statistics table VM-2, all systems, in each year's edition (2007-2024).
- **Population:** Census PEP. 2010-2019 from the 2010-2020 intercensal file (`sc-est2020int-alldata6`, which
  counts each person once; the `alldata5` file double-counts multiracial people). 2020-2025 from Vintage 2025.
  The without-largest-metro test uses Vintage 2020 county and state figures for 2010-2012 and 2017, and Vintage
  2025 for 2021-2024, so each subtraction uses one vintage.
- **Walking:** 2017 NHTS public-use files plus replicate weights. Home state (`HHSTATE`). A walk trip is
  `TRPTRANS` 01. Annual totals use `WTTRDFIN` (365 x person weight). Persons are age 5+.
- **Commute check:** ACS 2019 1-year B08301 (Census API). It matches the summary-file sequence 36 exactly.
- **Walking over time:** ACS 1-year B08301, 2010-2024 (no standard 2020 release), walkers (`B08301_019`) over
  commuters (all workers minus `B08301_021`, worked from home). 90% MOEs combine the published MOEs with the
  Census proportion formula (ratio formula if the proportion one goes negative). Dividing by commuters rather
  than all workers keeps the 2021+ work-from-home jump (to 14-21% of workers) from looking like less walking.
  Unweighted ACS person samples were about 470,000 (CA) and 315,000 (TX) in 2010 (`B00001`, not published
  after 2019). Also the 2009 NHTS (100 jackknife replicates, Var = 99/100 x sum of squared deviations, 2009
  User's Guide p. 7-1; walk = `TRPTRANS` 23; `DAYWGT` replicates are already 365 x the person weight).

## Uncertainty

- NHTS: stratified jackknife (JKn), 98 replicates, Var = 6/7 x sum of (replicate - full)^2. Death rates per walk
  trip or hour are recomputed under each replicate.
- Deaths: treated as Poisson for year-to-year randomness, SE = sqrt(count).
- Combined SE = rate x sqrt(relative SE of deaths^2 + relative SE of exposure^2). 90% MOE = 1.645 x SE.
- No cell is under 50 sample cases. The smallest NHTS group is Texas without Dallas-Fort Worth and Houston:
  10,650 households and 4,604 walk trips.

## Caveats

1. **Self-reported walking undercounts short trips.** Diary respondents leave out short walks (to the car,
   across a parking lot, around the block). If Californians leave out the same share as Texans, the ratio holds.
   If Texans leave out more (their walks are more incidental), Texas walking is undercounted and the Texas
   per-walk rate is too high. The 2017 NHTS can't tell which. Weekly recall (`NWALKTRP`, which includes walks for
   exercise) shows a much smaller gap: 260 vs. 239 walks per person per year, a ratio of 1.09. The diary shows
   1.94. This is the biggest soft spot in the per-walk comparison.
2. **Add-on coverage.** Both add-ons are statewide: California 24,021 add-on households plus 2,078 national,
   Texas 22,873 plus 1,568. Texas add-on households show up in every metro size class and in rural areas
   (6,110 outside the four largest metros). Dallas-Fort Worth is oversampled (37% of Texas households, 26% of
   weight), and Los Angeles is undersampled (12% of California households, 32% of weight). The weights correct
   for both, so either state's estimate stands for the whole state.
3. **Walk miles are unreliable in the raw file.** `TRPMILES` is a routed distance. Two Texas "walk" trips of
   1,537 and 1,153 miles with no duration carry ~40% of Texas's weighted walk miles (SE 29.6 on a mean of 87.6).
   A cleaned version keeps trips with a valid duration and drops trips over 1 mile faster than 6 mph (1,193 trips
   dropped). It gives 84 vs. 43 miles per person, a ratio of 1.97, close to the trip and minute ratios. Trips and
   hours are the measures to use.
4. **Single year.** The NHTS-based rates use 2017 deaths. A 2016-2018 average changes little: California 17.2
   vs. Texas 31.9 per 100 million walk trips.
5. **Different populations.** Deaths are counted where the crash happened and include all ages and
   non-residents. Walking is counted for residents age 5+. FARS pedestrians also include people who weren't
   on a "trip" (standing in the road, getting out of a stopped car).
6. **Exposure from 2017 only.** No survey of all walking measures either state after 2017, so 2022-2024 rates
   can only use residents and VMT. The 2022 NHTS public file has 7,893 households nationwide and identifies
   only the Census division, not the state (California is 1 of 5 Pacific states; Texas 1 of 4 West South
   Central states). Its only add-on samples were bought by Tennessee DOT, Virginia DOT and the Oahu MPO
   ([FHWA, NextGen NHTS State of the Practice, p. 2](https://nhts.ornl.gov/assets/NextGen%20NHTS_State%20of%20Practice_032423.pdf));
   none for California or Texas. The only post-2017 state measure is the ACS walk-to-work share: 2017 to 2024,
   California 2.75% to 2.87% (90% MOEs 0.07 and 0.10 points, a change about equal to its own MOE) and Texas
   1.62% to 1.82% (MOEs 0.08 and 0.09, a small rise beyond the MOE). Commutes only, and work-from-home changes
   who is in the denominator.
7. **VM-2 methods breaks.** Texas has footnoted years (2008, 2014: FHWA notes the 2014 drop runs counter to other
   indicators). California's VMT fell from 340.8 billion (2019) to 315.2 billion (2022) and has partly come back.
   Read VMT trends with care.
8. **FARS road coding changed.** `ROUTE` codes were reorganized in 2023, and 2022 spells "US Highway" without
   periods. Matching is by name. Road owner (`RD_OWNER`) is missing for almost all Texas crashes and for many
   California crashes in 2017-2019, so ownership shares are California-only and 2022+.
9. **No causal claim.** This is a cross-sectional comparison of 2 states. It can't show that lower driving
   caused more walking, or that more walking caused more deaths.

## Walking 2009 vs. 2017 (NHTS)

| per person age 5+, per year | CA 2009 | CA 2017 | TX 2009 | TX 2017 |
|---|---|---|---|---|
| Walk trips (diary) | 184 (SE 3.7) | 151 (3.9) | 105 (2.7) | 78 (2.8) |
| All trips (diary) | 1,377 | 1,201 | 1,359 | 1,194 |
| Walk share of trips | 13.4% | 12.6% | 7.7% | 6.5% |
| Weekly-recall walks x 52 | 206 (2.5) | 260 (3.9) | 203 (2.9) | 239 (3.2) |

Unweighted 2009 walk trips: CA 20,077, TX 11,742. The diary shows less walking in 2017, but trips of every kind
fell about 13% and the survey moved from phone to web/mail, so the change over time is not reliable. The
weekly-recall measure moves the other way, and the question changed. 2009 (phone interview, item L3,
[Extended Interview p. 2](https://nhts.ornl.gov/2009/pub/ExtendedInterview.pdf)): "In the past week, how many
times did {you/SUBJECT} take a walk outside including walking the dog and walks for exercise?" 2017 (web or
phone, `NWALKTRIP`, [Retrieval Instrument p. 28](https://nhts.ornl.gov/assets/2016/NHTS_Retrieval_Instrument_20180228.pdf)):
"In the past 7 days, how many times did [you] take a walk outside including walks to exercise, go somewhere,
or to walk the dog (e.g., walk to a friend's house, walk around the neighborhood, walk to the store, etc.)?"
2017 adds walks "to go somewhere" with examples, which by itself would raise counts, so the 2009-2017 rise in
recall walks is not a trend. Neither measure shows walking rising in either state on a like-for-like basis,
which is the only claim the post makes from it.

## Weekly-recall check on the per-walk rate

Using the weekly recall count instead of the diary (2017 deaths / (walks per person x persons age 5+)):
California 940 / 9.52 billion walks = 9.9 per 100 million; Texas 608 / 6.09 billion = 10.0. The ratio is
~0.99, so by this measure the two states are even. The California advantage per walk shows up only in the
travel-day diary. The two measures count different things: the recall question covers walks for exercise and
dog walks, which happen mostly on residential streets, while the diary records walks as trips.
