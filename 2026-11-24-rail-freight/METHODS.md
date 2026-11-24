# Methods: rail freight vs. passenger traffic by country

All values are **millions** of metric ton-km (freight) and passenger-km. The ratio is freight ton-km ÷ passenger-km.
The **charts and the post show US units**: short ton-miles (2,000 lb) and passenger-miles, converted in
`charts/charts.py` (ton-km ÷ 1.45997, passenger-km ÷ 1.609344). The data files stay in the metric units the
sources publish. In US units every freight-to-passenger ratio is 1.102× the metric one (US 2024: 97 vs 88);
per-person comparisons between countries are unchanged.
Nothing is interpolated. A blank cell means no source in hand covers that cell. TK marks a number that exists
but couldn't be fetched.

## Definitions

- **freight_tkm**: rail freight ton-km on the country's network.
- **pkm_mainline**: intercity + regional/commuter rail (including S-Bahn, RER, Japanese private suburban
  railways). Excludes metros/subways, light rail, trams, monorails, people movers.
- **pkm_all_rail**: mainline + metros, light rail, trams.
- **pkm_reported**: the rail passenger-km total as published by ITF (preferred) or the World Bank. Its coverage
  varies by country and isn't documented; it's kept for comparison and as a fallback for countries with no
  national source here. It's never relabeled as mainline or all-rail.
- **population**: World Bank SP.POP.TOTL. 2025 rows have none; charts use 2024 population for them.
- Fiscal-year sources are filed under the year the fiscal year **starts**. Japan (MLIT) and Great Britain
  (ORR, DfT rail) use April–March. US NTD report years are agency fiscal years (mostly July–June); Amtrak's is
  October–September.

## Country sources and choices

**United States**
- Freight, 1916–1970: Census, *Historical Statistics of the U.S., Colonial Times to 1970*, series Q 340
  (revenue ton-miles, class I–III railroads). Hand-transcribed from the scanned PDF (no text layer):
  `inputs/us_hsus_1916_1970.csv`.
- Freight, 2019/2024/2025: STB R-1 annual reports, Schedule 755 line 110 (revenue ton-miles), summed over
  all Class I railroads (`model/stb_r1.py`). Short ton-miles × 1.45997 = metric ton-km. The STB totals match
  World Bank 2019 and ITF 2024 **exactly** (2,357 and 2,180 billion tkm), so WDI (1995–2003) and ITF
  (2004–2024) US freight is Class I revenue freight. That excludes regional and short-line railroads and
  non-revenue (company) freight.
- Freight 1975 (and 1979–85 as a check): Census, *Statistical Abstract 1987*, table 1048, Class I "tons carried
  one mile" (AAR; scanned, transcribed in `inputs/us_statab.csv`). 1971–74 and 1976–79 are not in the dataset.
- Freight 1980–2024 and passengers: BTS *National Transportation Statistics* tables 1-50 (railroad ton-miles, AAR)
  and 1-40 (passenger-miles). bts.gov refuses scripts, so Max downloaded both workbooks by hand into `raw/bts/`
  (`freight-miles.xlsx`, `passenger-miles.xlsx`; sheet `1-40`, not the stale `1-40_all`). BTS 1-50 matches the
  STB Class I totals exactly for 2019 and 2024.
- Passengers, mainline = BTS "Intercity/Amtrak" (AAR to 1980, FRA operational data table 1.02 from 1985,
  calendar years) + "Commuter rail" (APTA to 1995, NTD after). Available 1960, 1965, 1970, 1975, 1980, 1985,
  then every year 1990–2025. 1971–74, 1976–79, 1981–84 and 1986–89 have no commuter-rail figure and are left
  blank, not interpolated. The 1970 BTS values (intercity 6,179, commuter 4,592) equal Census Q 309+Q 310 and
  Q 308, so the two series join cleanly.
- all_rail = mainline + BTS transit heavy rail + light rail (which includes streetcar and hybrid rail), from 1980.
  Monorail, cable car and inclined plane are in BTS "Other" with non-rail modes and are left out (tiny).
- Amtrak cross-check: *Statistical Abstract* (AAR revenue passenger-miles) differs from BTS (FRA) by 4–11%
  (1985: 4,977 vs 4,451; 1990: 6,125 vs 6,398). BTS is used as one consistent series 1985–2025.
- NTD + Amtrak FY2025 (the earlier fallback) is still computed but no longer chosen; BTS covers 2025.
- ITF's US passenger series counts **Amtrak only for 2004–2013** (8.7–11.0 billion pkm) and jumps to
  ~36 billion in 2014. Flagged in `notes`; left out of the time chart.

**Japan** (`model/japan.py`, all MLIT)
- Long series: 鉄道統計年報 FY2023 table (22) 運輸成績の推移. JR (JNR before FY1987) and all non-JR operators
  (民鉄, including municipal 公営 subways and trams), FY1960, 1965, 1970, then annually FY1975–FY2023. This
  is **all_rail**.
- FY2024: 鉄道輸送統計年報 2024 (e-Stat 00600350). Its FY2019 and FY2023 totals match the long series within 0.04%.
- Mainline split, **FY2019 and FY2023 only**, from the per-operator table (2) 運輸成績表. Mainline = total
  minus Tokyo Metro, Osaka Metro (大阪市高速電気軌道), all municipal 公営 operators (subways and trams), and
  named monorail/AGT/tram operators and lines (25–26 matched by name; list printed by the script, about 2.2
  billion pkm). Mainline is 89% of all rail in both years. Japanese subways run through onto suburban lines, so any operator
  split is approximate.
- **FY1987 freight left blank**: the table gives JR 10.0 billion tkm, half of FY1986 (20.1) and FY1988 (23.0),
  the year JNR was broken up. It looks like a partial year.

**Germany**
- 1960–2002: Destatis *Fachserie 8 Reihe 2, Eisenbahnverkehr 2002*, tables 1.3/1.4.1 (scanned; transcribed in
  `inputs/germany_fachserie_1960_2002.csv`). West Germany for 1960, 1970, 1980 and 1990; unified Germany from 1990.
  Freight is **tariff** ton-km.
- 2007–2024 passengers: *Verkehr in Zahlen 2025/2026* (BMV/DLR), "Eisenbahnen" (Nah- + Fernverkehr incl.
  S-Bahn): mainline. Taken from DLR's copy because bmv.de times out from here.
- Freight 2004+: **Eurostat** (harmonised EU definition) is preferred. VIZ's figure is 7% higher (138.2 vs
  128.5 billion tkm in 2019) because it includes company material, container tare weight and estimates for
  small firms, and it was revised upward from 2016. ITF's figure is 12% lower than Eurostat's (113.1). All
  three are in `data/qa_sources.csv`.
- **all_rail is TK**: U-Bahn/Stadtbahn/Straßenbahn passenger-km are in Destatis GENESIS 46181-0005, which
  needs a (free) login; guest API access is refused. Destatis's public half-year table gives about 8.3 billion
  pkm for trams/U-Bahn in H1 2025.

**France** (SDES, *Bilan annuel des transports 2024*)
- Mainline (2000–2024): table F3 "Ensemble": TGV + intercity + TER + Île-de-France trains and RER, including
  RATP-run RER lines and tram-train T4.
- all_rail: mainline + Paris Métro + Île-de-France trams (F2.a) + provincial metros (F2.a). **Provincial trams
  are reported together with buses and are left out**, so all_rail slightly understates.
- Freight (1980–2024): table E3.a1 total (national + international + transit), metropolitan France.
- Eurostat's France pkm is 5–6% below SDES mainline; ITF's is ~17% below; the World Bank's (112 billion in 2019)
  sits between SDES mainline and SDES all-rail.

**Great Britain** (Northern Ireland excluded; per-capita uses UK population, about 3% overstating the denominator)
- Mainline: ORR table 1230, National Rail passenger-km, 1938 and 1946 onward (calendar years to 1983,
  April–March from 1984). Excludes Eurostar, Underground and light rail.
- all_rail: DfT TSGB0101 "Rail" (National Rail + London Underground + other metros and trams), 1952 onward.
- Freight: DfT TSGB0401 (1953–1981, rounded to billions) and ORR table 1310 (April 1982 onward,
  excluding engineering trains).

**China**
- NBS *China Statistical Yearbook 2025*, tables 16-6 and 16-8, railway column (1978, 1980, 1985, 1990–2024).
  The tables are published only as images; transcribed in `inputs/china_nbs_1978_2024.csv`. The 2019 freight
  value equals the World Bank's exactly. Railways only, so this is mainline. **all_rail is TK**: urban rail
  transit passenger-km aren't in the yearbook. Pre-1978: TK. The NBS database API refuses scripts.

**Italy, Spain, Netherlands, Switzerland**: Eurostat `rail_go_total` / `rail_pa_total` (2004–2025), treated as
mainline (Eurostat rail statistics cover railways, not metros or trams). Country primaries not checked.

**Canada, Australia, South Korea, Russia, India**: ITF and World Bank only (`pkm_reported`), shown as
"uncertain definition" in the charts. Canada's ~1.5 billion pkm matches VIA Rail alone, without GO Transit,
exo or West Coast Express commuter rail. South Korea's ~94–100 billion almost certainly includes Seoul-area
metros. Russia and India use 2019, because the World Bank's last year (2021) is COVID-distorted.

## Spanish ITF data
ITF's Spain freight (3.9 billion tkm in 2024) is 58% below Eurostat's (9.3). It's probably one operator, but
unconfirmed. Eurostat is used.

## Not done (asked for, not completed)
- Mitchell's *International Historical Statistics*, UIC RAILISA: not accessed (paywalled / not tried).
- US passengers 1971–74, 1976–79, 1981–84, 1986–89 (no commuter-rail series); Germany all-rail, China all-rail and pre-1978, Japan pre-1960,
  France passengers pre-2000: TK, as above.

## QA
`python -I model/qa.py data` compares every source for 2019 and for each country's latest year and lists
gaps above 10% (`data/qa_sources.csv`). Most flagged gaps are definitional (mainline vs. all-rail vs. reported).
The true disagreements are Germany freight (ITF 113 / Eurostat 129 / VIZ 138 billion tkm, 2019), Spain
(ITF far below Eurostat), and the US ITF passenger series' 2004–2013 Amtrak-only break.
