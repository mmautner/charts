#!/bin/sh
# Download raw inputs into raw/ (not committed). Run from the post folder: sh inputs/fetch.sh
# Hand-transcribed inputs (scanned or image-only tables) live in inputs/*.csv with their citations.
# Download by hand into raw/bts/ (bts.gov refuses scripts): NTS table 1-40 https://www.bts.gov/content/us-passenger-miles
# saved as passenger-miles.xlsx, and table 1-50 https://www.bts.gov/content/us-ton-miles-freight saved as freight-miles.xlsx.
# Also not fetchable automatically (HTTP 403 to scripts):
# amtrak.com, railroads.dot.gov (FRA), Destatis GENESIS (needs a login), NBS data.stats.gov.cn API.
set -e
UA="Mozilla/5.0"
mkdir -p raw/bts raw/census/statab raw/wb raw/oecd raw/eurostat raw/ntd raw/stb/files/rev raw/census raw/japan/fy2024 raw/japan/nenpo_fy2019 \
         raw/japan/nenpo_fy2023 raw/viz raw/destatis raw/france raw/uk raw/china raw/amtrak

# World Bank WDI
for ind in IS.RRS.GOOD.MT.K6 IS.RRS.PASG.KM SP.POP.TOTL; do
  curl -s "https://api.worldbank.org/v2/country/USA;DEU;JPN;FRA;GBR;CHN;RUS;IND;CAN;AUS;CHE;NLD;KOR;ITA;ESP/indicator/$ind?format=json&per_page=5000&date=1960:2025" -o raw/wb/$ind.json
done
# ITF / OECD
for f in DF_STFREIGHT DF_STPASS; do
  curl -s -H "Accept: application/vnd.sdmx.data+csv;labels=both" "https://sdmx.oecd.org/public/rest/data/OECD.ITF,DSD_ST@$f,1.0/all?startPeriod=1970" -o raw/oecd/$f.csv
done
# Eurostat
for d in rail_go_total rail_pa_total rail_go_typeall rail_pa_typepas; do
  curl -s "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/$d?format=TSV&compressed=false" -o raw/eurostat/$d.tsv
done
# US: NTD time series 2.1 passenger miles by mode (Socrata aggregate)
curl -s -G "https://data.transportation.gov/resource/npsm-38gk.csv" --data-urlencode "\$select=mode,report_year,sum(value) as pmt" \
  --data-urlencode "\$where=field='Passenger Miles Traveled'" --data-urlencode "\$group=mode,report_year" \
  --data-urlencode "\$order=mode,report_year" --data-urlencode "\$limit=5000" -o raw/ntd/ts21_pmt_by_mode.csv
# US: STB R-1 Class I annual reports
B=https://www.stb.gov/wp-content/uploads
( cd raw/stb/files
  for rr in BNSF/2019/R1-BNSF-2019.xlsx CSX/2019/R1-CSX-2019.zip GTC/2019/R1-GTC-2019.xlsx KCS/2019/R1-KCS-2019.xlsx \
            NS/2019/R1-NS-2019.xlsx SOO/2019/R1-SOO-2019.xlsx UP/2019/R1-UP-2019.xlsx; do curl -s -A "$UA" -O "$B/econdata/R1/$rr"; done
  for f in R1-BNSF-2024.xlsx R1-CSX-2024.zip R1-GTC-2024.xlsx R1-NS-2024.xlsx R1-SOO-KCSR-2024.xlsx R1-UP-2024.zip \
           R1-CSX-2025.zip R1-GTC-2025.xlsx R1-NS-2025.xlsx R1-SOO-KCSR-2025.xlsx R1-UP-2025.zip; do curl -s -A "$UA" -O "$B/$f"; done
  ( cd rev && curl -s -A "$UA" -O "$B/R1-BNSF-2025-REV-SCHEDULES-10-23-2026.xlsx" )
  for z in *.zip; do mkdir -p "${z%.zip}" && unzip -o -q "$z" -d "${z%.zip}"; done )
# US: Historical Statistics (scanned; transcribed into inputs/us_hsus_1916_1970.csv)
curl -sL -o raw/census/statab/1987-05.pdf https://www2.census.gov/library/publications/1986/compendia/statab/107ed/1987-05.pdf
curl -sL -o raw/census/statab/1996_transind.pdf https://www2.census.gov/library/publications/1996/compendia/statab/116ed/tables/transind.pdf
curl -s -o raw/census/hist_stats_chQ.pdf https://www2.census.gov/library/publications/1975/compendia/hist_stats_colonial-1970/hist_stats_colonial-1970p2-chQ.pdf
# Amtrak FY2025 release (passenger-miles in inputs/amtrak.csv)
curl -sL -A "$UA" -o raw/amtrak/fy2025.html https://media.amtrak.com/2025/11/amtrak-a-year-of-records/
# Japan: MLIT 鉄道輸送統計年報 2024 (e-Stat) and 鉄道統計年報 FY2019 / FY2023
for id in 000040366428 000040366700; do curl -sL "https://www.e-stat.go.jp/stat-search/file-download?statInfId=$id&fileKind=0" -o raw/japan/fy2024/$id.xls; done
curl -sL -A "$UA" -o raw/japan/nenpo_fy2023/001977439.xls https://www.mlit.go.jp/tetudo/content/001977439.xls
curl -sL -A "$UA" -o raw/japan/nenpo_fy2023/001977414.xlsx https://www.mlit.go.jp/tetudo/content/001977414.xlsx
curl -sL -A "$UA" -o raw/japan/nenpo_fy2019/001460060.xlsx https://www.mlit.go.jp/tetudo/content/001460060.xlsx
# Germany: Verkehr in Zahlen 2025/2026 (DLR) and Destatis Fachserie 8 Reihe 2 (2002, transcribed into inputs/)
curl -s -o raw/viz/VIZ_2025_2026.pdf https://elib.dlr.de/221967/1/VIZ_2025_2026_Download.pdf
curl -sL -o raw/destatis/FS-8-2-J-2002.pdf https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/DEHeft_derivate_00054943/FS-8-2-J-2002.pdf
# France: SDES Bilan annuel des transports 2024
curl -sL -A "$UA" -o raw/france/voyageurs.xlsx "https://www.statistiques.developpement-durable.gouv.fr/media/8866/download?inline"
curl -sL -A "$UA" -o raw/france/marchandises.xlsx "https://www.statistiques.developpement-durable.gouv.fr/media/8865/download?inline"
# Great Britain: ORR and DfT
curl -sL -A "$UA" -o raw/uk/table-1230.ods https://dataportal.orr.gov.uk/media/1477/table-1230-passenger-kilometres.ods
curl -sL -A "$UA" -o raw/uk/table-1310.ods https://dataportal.orr.gov.uk/media/1998/table-1310-freight-moved-by-commodity.ods
curl -s -o raw/uk/tsgb0101.ods https://assets.publishing.service.gov.uk/media/69395b7e6a12691d48491d13/tsgb0101.ods
curl -s -o raw/uk/tsgb0401.ods https://assets.publishing.service.gov.uk/media/69398beecfacd5e888491d46/tsgb0401.ods
# China: NBS yearbook 2025 tables (images; transcribed into inputs/china_nbs_1978_2024.csv)
for t in C16-06 C16-08; do curl -s -A "$UA" -o raw/china/$t.jpg "https://www.stats.gov.cn/sj/ndsj/2025/html/$t.jpg"; done
