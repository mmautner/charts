#!/bin/sh
# Primary documents behind data/express_lanes_funding.csv, into raw/ (not committed).
set -e
cd "$(dirname "$0")/.."
mkdir -p raw
# San Mateo County Express Lanes JPA, Application for Toll Facility to the California Transportation
# Commission, June 28, 2019. Funding table: Exhibit 14, Project Capital Funding (PDF p. 52).
curl -sL -o raw/smcel-ctc-toll-facility-application-2019-06-28.pdf "https://catc.ca.gov/-/media/ctc-media/documents/programs/toll-facilities-program/sm101hotlane_ctcapplication_tollfacility_v07_complete.pdf"
# Caltrans Inspector General's scope (external entities receiving state and federal funds through Caltrans)
curl -sL -o raw/caltrans-ig-about.html "https://ig.dot.ca.gov/about-us"
