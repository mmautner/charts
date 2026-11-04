#!/bin/sh
# Download the raw inputs into raw/ (not committed). Run from the post folder: sh inputs/fetch.sh
# Then: python -I model/fars.py raw/fars/x data; python -I model/nhts.py raw/nhts/x data;
#       python -I model/nhts2009.py raw/nhts2009/x data; python -I model/acs.py raw/census/acs_series data; python -I model/rates.py
# The ACS call needs CENSUS_API_KEY in the environment.
set -u
UA='Mozilla/5.0'
get() { curl -sfL -A "$UA" -o "$1" "$2" || echo "missing: $1 ($2)"; }
mkdir -p raw/fars/x raw/nhts/x raw/fhwa raw/census

for y in $(seq 2010 2024); do
  get raw/fars/FARS$y.zip https://static.nhtsa.gov/nhtsa/downloads/FARS/$y/National/FARS${y}NationalCSV.zip
  mkdir -p raw/fars/x/$y && unzip -o -j -q -C raw/fars/FARS$y.zip '*erson.*' '*ccident.*' -d raw/fars/x/$y
done

get raw/nhts/csv.zip https://nhts.ornl.gov/assets/2016/download/csv.zip
get raw/nhts/Replicates.zip https://nhts.ornl.gov/assets/2016/download/Replicates.zip
mkdir -p raw/nhts2009/x
get raw/nhts2009/Ascii.zip https://nhts.ornl.gov/2009/download/Ascii.zip
get raw/nhts2009/ReplicatesASCII.zip https://nhts.ornl.gov/2009/download/ReplicatesASCII.zip
unzip -o -j -q raw/nhts2009/Ascii.zip 'Ascii/DAYV2PUB.CSV' 'Ascii/PERV2PUB.CSV' 'Ascii/HHV2PUB.CSV' -d raw/nhts2009/x
unzip -o -j -q raw/nhts2009/ReplicatesASCII.zip per50wt.csv -d raw/nhts2009/x
unzip -o -j -q raw/nhts/csv.zip -d raw/nhts/x && unzip -o -j -q raw/nhts/Replicates.zip -d raw/nhts/x

for y in $(seq 2007 2024); do
  get raw/fhwa/vm2_$y.xlsx https://www.fhwa.dot.gov/policyinformation/statistics/$y/xls/vm2.xlsx 2>/dev/null ||
    true
  [ -s raw/fhwa/vm2_$y.xlsx ] || { rm -f raw/fhwa/vm2_$y.xlsx; get raw/fhwa/vm2_$y.xls https://www.fhwa.dot.gov/policyinformation/statistics/$y/xls/vm2.xls; }
done

P=https://www2.census.gov/programs-surveys/popest/datasets
get raw/census/NST-EST2025-ALLDATA.csv $P/2020-2025/state/totals/NST-EST2025-ALLDATA.csv
get raw/census/sc-est2020int-alldata6.csv $P/2010-2020/intercensal/state/asrh/sc-est2020int-alldata6.csv
get raw/census/co-est2020-alldata.csv $P/2010-2020/counties/totals/co-est2020-alldata.csv
get raw/census/acs2019_b08301_api.json "https://api.census.gov/data/2019/acs/acs1?get=NAME,B08301_001E,B08301_001M,B08301_019E,B08301_019M,B08301_021E,B08301_021M&for=state:06,48&key=${CENSUS_API_KEY:-}"
mkdir -p raw/census/acs_series
for y in 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2021 2022 2023 2024; do   # no standard 2020 1-year release
  get raw/census/acs_series/b08301_$y.json "https://api.census.gov/data/$y/acs/acs1?get=NAME,B08301_001E,B08301_001M,B08301_002E,B08301_002M,B08301_003E,B08301_003M,B08301_019E,B08301_019M,B08301_021E,B08301_021M&for=state:06,48&key=${CENSUS_API_KEY:-}"
done
get raw/census/acs_series/b00001_2010.json "https://api.census.gov/data/2010/acs/acs1?get=NAME,B00001_001E&for=state:06,48&key=${CENSUS_API_KEY:-}"   # unweighted sample; not published after 2019
