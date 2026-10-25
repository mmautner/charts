#!/bin/sh
# Download raw inputs into raw/. Run from the post folder: sh inputs/fetch.sh
set -u
UA='Mozilla/5.0'
mkdir -p raw/irs raw/census raw/fhwa raw/caltrans raw/cbo raw/crs

# IRS Statistics of Income county data, tax years 2011-2023 (the 2012 file is not posted)
# https://www.irs.gov/statistics/soi-tax-stats-county-data
for y in 11 13 14 15 16 17 18 19 20 21 22 23; do
  curl -sf -A "$UA" -o raw/irs/${y}incyallagi.csv https://www.irs.gov/pub/irs-soi/${y}incyallagi.csv || echo "missing: IRS 20$y"
done

# Census Vintage 2025 population estimates: states and counties
P=https://www2.census.gov/programs-surveys/popest/datasets/2020-2025
curl -sf -A "$UA" -o raw/census/NST-EST2025-ALLDATA.csv $P/state/totals/NST-EST2025-ALLDATA.csv
curl -sf -A "$UA" -o raw/census/co-est2025-alldata.csv $P/counties/totals/co-est2025-alldata.csv
# ACS 2024 1-year households (B11001), table-based summary file (no API key needed)
curl -sf -A "$UA" -o raw/census/acsdt1y2024-b11001.dat \
  https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/acsdt1y2024-b11001.dat

# FHWA Highway Statistics 2024: VM-2 (vehicle-miles by state), FE-221 (apportionments, cited in the post)
for t in vm2 fe221; do
  curl -sf -A "$UA" -o raw/fhwa/${t}_2024.xlsx https://www.fhwa.dot.gov/policyinformation/statistics/2024/xls/$t.xlsx \
    || echo "missing: FHWA $t"
done

# Caltrans California Public Road Data 2024 (Table 6: daily vehicle-miles by county)
curl -sf -A "Mozilla/5.0 (Macintosh) Chrome/126" -o raw/caltrans/hpms-2024-prd-a11y.pdf \
  https://dot.ca.gov/-/media/dot-media/programs/research-innovation-system-information/documents/hpms/hpms-2024-prd-a11y.pdf

# CRS: R48845 (Table A-2, general-fund transfers), R47900 (transit operating assistance history)
curl -sf -A "$UA" -o raw/crs/R48845.pdf https://www.congress.gov/crs_external_products/R/PDF/R48845/R48845.12.pdf
curl -sf -A "$UA" -o raw/crs/R47900.pdf https://www.congress.gov/crs_external_products/R/PDF/R47900/R47900.3.pdf

# CBO Highway Trust Fund baseline, June 2026. cbo.gov refuses scripted downloads: open this URL in a
# browser and save it to raw/cbo/51300-2026-06-highwaytrustfund.pdf
echo "manual: https://www.cbo.gov/system/files/2026-06/51300-2026-06-highwaytrustfund.pdf -> raw/cbo/"
