#!/bin/sh
# Download every public input into raw/ (never commit raw/). Run from the post folder:
#   sh inputs/fetch.sh            # everything
#   sh inputs/fetch.sh lt7019     # one target
# Census DHC tables need a key in the environment:
#   CENSUS_API_KEY=... python -I inputs/fetch_census.py raw/census
set -eu
R=raw
get() { mkdir -p "$R/$1"; [ -s "$R/$1/$2" ] || curl -fsSL -o "$R/$1/$2" "$3"; }
NVSR=https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/NVSR
FHWA=https://www.fhwa.dot.gov/policyinformation/statistics
only=${1:-all}
want() { [ "$only" = all ] || [ "$only" = "$1" ]; }

if want nhts17; then  # 2017 NHTS public CSVs + 98 jackknife replicate weights (SAS)
  get nhts17 csv.zip https://nhts.ornl.gov/assets/2016/download/csv.zip
  get nhts17 Replicates.zip https://nhts.ornl.gov/assets/2016/download/Replicates.zip
  (cd $R/nhts17 && unzip -o -q csv.zip perpub.csv hhpub.csv trippub.csv && unzip -o -q Replicates.zip perwgt.sas7bdat hhwgt.sas7bdat)
fi
if want nhts22; then  # 2022 NHTS public CSVs (v2); no replicate weights are published
  get nhts22 csv.zip https://nhts.ornl.gov/assets/2022/download/csv.zip
  (cd $R/nhts22 && unzip -o -q csv.zip perv2pub.csv hhv2pub.csv tripv2pub.csv)
fi
# NCHS U.S. life tables (Table 2 = males, Table 3 = females)
if want lt6807; then for t in 02 03; do get lt6807 Table$t.xlsx $NVSR/68_07/Table$t.xlsx; done; fi   # 2017
if want lt7019; then for t in 02 03; do get lt7019 Table$t.xlsx $NVSR/70-19/Table$t.xlsx; done; fi   # 2019
if want lt7402; then for t in 02 03; do get lt7402 table$t.xlsx $NVSR/74-02/table$t.xlsx; done; fi   # 2022
if want lt7406; then for t in 02 03; do get lt7406 Table$t.xlsx $NVSR/74-06/Table$t.xlsx; done; fi   # 2023
if want lt7505; then for t in 02 03; do get lt7505 Table$t.xlsx $NVSR/75-05/Table$t.xlsx; done; fi   # 2024
# FHWA Highway Statistics DL-20 (licensed drivers by age and sex, % of population)
if want fhwa; then
  get fhwa dl20_2017.cfm  $FHWA/2017/dl20.cfm   # the 2017 .xls is password-protected; parse the HTML table
  get fhwa dl20_2022.xlsx $FHWA/2022/xls/dl20.xlsx
  get fhwa dl20_2023.xlsx $FHWA/2023/xls/dl20.xlsx
  for y in 2010 2012 2014 2015 2016 2018 2019 2020 2021; do get fhwa dl20_$y.cfm $FHWA/$y/dl20.cfm; done
fi
if want fars; then   # NHTSA FARS 2017 national CSVs (every fatal crash)
  get fars FARS2017NationalCSV.zip https://static.nhtsa.gov/nhtsa/downloads/FARS/2017/National/FARS2017NationalCSV.zip
fi
# Documentation used for methods notes
if want docs; then
  get docs ug2017.pdf https://nhts.ornl.gov/assets/2017UsersGuide.pdf
  get docs cb2017.pdf https://nhts.ornl.gov/assets/codebook_v1.2.pdf
  get docs codebook2022.xlsx https://nhts.ornl.gov/assets/2022/doc/codebook.xlsx
  # 2017 weighting report (wt2017.pdf), 2022 user guide (ug2022.pdf) and 2022 weighting
  # report (memo2022.pdf) were downloaded from the nhts.ornl.gov documentation page.
fi
