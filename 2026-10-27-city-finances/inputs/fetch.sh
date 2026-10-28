#!/bin/sh
# Download the primary documents into raw/. Run from the post folder: sh inputs/fetch.sh
# raw/ is not committed. The model reads only data/, which is hand-transcribed from these files
# (each row cites its URL and PDF page).
set -u
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
mkdir -p raw/sanmateo raw/burlingame raw/dof raw/elections
get() { curl -sfL -A "$UA" -o "$1" "$2" || echo "missing: $1 ($2)"; }

# City of San Mateo. The FY2025 ACFR was re-posted under a new ID; the old link
# (DocumentCenter/View/100608) now returns 404. Same pagination.
SM=https://www.cityofsanmateo.org/DocumentCenter/View
get raw/sanmateo/acfr_fy2025.pdf                    $SM/102039/2025-Annual-Comprehension-Financial-Report
get raw/sanmateo/measure_s_compliance_fy2025.pdf    $SM/100610/2025-Measure-S-Compliance-Report
get raw/sanmateo/adopted_budget_2026_28.pdf         $SM/105937/2026-28-Adopted-Budget
get raw/sanmateo/adopted_budget_2025_26.pdf         $SM/105831/Adopted-2025-26-Budget

# City of Burlingame (site moved from Revize to CivicPlus; old cms6.revize.com links return 404)
BG=https://www.burlingame.org/DocumentCenter/View
get raw/burlingame/acfr_fy2025.pdf                  $BG/8102/ACFR-FY-24-25-PDF
get raw/burlingame/adopted_budget_fy2026.pdf        $BG/6980/Adopted-Budget-FY-25-26-PDF
get raw/burlingame/adopted_budget_fy2027.pdf        $BG/9211/Adopted-Budget-FY-26-27-PDF
get raw/burlingame/sales_tax_2Q2025.pdf             $BG/7506/City-of-Burlingame-Sales-Tax-Update-2Q-2025-PDF
get raw/burlingame/sales_tax_3Q2025.pdf             $BG/8326

# State Department of Finance E-1, May 2025 release (Jan 1, 2025 estimates) and May 2026 release
DOF=https://dof.ca.gov/media/docs/forecasting/Demographics/estimates-e1
get raw/dof/E-1_2025_InternetVersion.xlsx           $DOF/E-1_2025_InternetVersion.xlsx
get raw/dof/E-1_2026_InternetVersion.xlsx           $DOF/E-1_2026_InternetVersion.xlsx

# San Mateo County Elections: Measure H (City of San Mateo), Nov 3, 2026. Scanned PDFs, no text layer.
EL=https://smcacre.gov/system/files
get raw/elections/measure_h_resolution.pdf          "$EL/2026-07/52-ENG-M301-Contest%20Code-Reso-San%20Mateo%20Transactions%20and%20Use%20Tax_Redacted.pdf"
get raw/elections/measure_h_impartial.pdf           "$EL/2026-08/52-ENG-MH-ImpartialAnalysis-San-Mateo-Transactions-and-Use-Tax-Redacted.pdf"

# Burlingame mid-year report and five-year forecast (March 11, 2026; Legistar matter 11062)
get raw/burlingame/midyear_fy2026_staff_report.docx https://burlingameca.legistar1.com/burlingameca/attachments/d3a75ab7-7ba8-41e5-b508-5238c92bc9b3.docx

# Fire agencies
mkdir -p raw/fire raw/lehd
get raw/fire/ccfd_acfr_fy2025.pdf    https://www.ccfd.org/files/0bfee9050/CCFD-ACFR-2025-Final-11-25-25.pdf
get raw/fire/ccfd_budget_fy2027.pdf  "https://ccfd.specialdistrict.org/files/638dc81dd/Adopted+Budget+FY+26-27-web.pdf"
get raw/fire/smcfire_afr_fy2025.pdf  "https://smcfire.ca.gov/files/f3a170d9f/FY+25+Annual+Financial+Report+-+Final.pdf"

# Census LEHD jobs by workplace, 2023, and block crosswalk (model/jobs.py)
get raw/lehd/ca_wac_S000_JT00_2023.csv.gz https://lehd.ces.census.gov/data/lodes/LODES8/ca/wac/ca_wac_S000_JT00_2023.csv.gz
get raw/lehd/ca_xwalk.csv.gz              https://lehd.ces.census.gov/data/lodes/LODES8/ca/ca_xwalk.csv.gz
