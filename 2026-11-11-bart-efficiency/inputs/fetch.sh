#!/bin/sh
# Source documents into raw/ (not committed). Every figure in data/estimates.csv cites one of these.
mkdir -p raw && cd raw
curl -sL -o mtc-phase1.pdf "https://mtc.ca.gov/sites/default/files/documents/2026-05/Final%20Phase%20One%20Financial%20Efficiency%20Review%20Report_20260527.pdf"
curl -sL -o grand-jury-2608.pdf "https://contracosta.courts.ca.gov/system/files/general/report-2608-signed-cover.pdf"
curl -sL -o bart-response-2608.pdf "https://contracosta.courts.ca.gov/system/files/general/response-report-no-2608-bart-board-directors.pdf"
curl -sL -o bart-oig-overtime.pdf "https://oig.bart.gov/files/d8c036b58/BART+Overtime+Risks+Can+be+Reduced+by+Strategic+Improvements+in+Oversight+and+Management+June+13+-+2025.pdf"
curl -sL -o bart-fy27-budget.pdf "https://www.bart.gov/sites/default/files/2026-07/EDD-Resolution%20to%20Adopt%20the%20FY27%20Budget%20%285%29.pdf"
curl -sL -o bart-fy27-deck.pdf "https://www.bart.gov/sites/default/files/2026-06/Presentation%20-%20Resolution%20to%20Approve%20the%20FY27%20Budget.pdf"
curl -sL -o bart-acfr-fy25.pdf "https://www.bart.gov/sites/default/files/2026-01/BART%20ACFR%202025%20-%20Final%20%28SECURED%29.pdf"
curl -sL -o bart-fact-sheet.pdf "https://www.bart.gov/sites/default/files/2026-03/FundingOverview_Factsheet_030426.pdf"
curl -sL -o sfbos-r0055-25.pdf "https://sfbos.org/sites/default/files/r0055-25.pdf"
