"""Download the Census Building Permits Survey annual state files and save
California's units permitted by building size, with the fetch date, to data/.

Source: U.S. Census Bureau, Building Permits Survey, annual state files.
https://www2.census.gov/econ/bps/State/  (file stYYYYa.txt per year)
Columns 7, 10, 13, 16 are units in 1-unit, 2-unit, 3-4 unit, and 5+ unit
buildings (permit-issuing places plus imputation, the "Units" columns).
"""
import csv, datetime, io, json, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
URL = "https://www2.census.gov/econ/bps/State/st{y}a.txt"
YEARS = range(2016, 2026)

def main():
    out = {"source": URL.format(y="YYYY"), "fetched_on": datetime.date.today().isoformat(), "years": {}}
    for y in YEARS:
        try:
            raw = urllib.request.urlopen(URL.format(y=y), timeout=60).read().decode("latin-1")
        except Exception as e:
            sys.exit(f"Could not download {URL.format(y=y)}: {e}")
        (HERE / "data" / f"bps_st{y}a.txt").write_text(raw)
        for row in csv.reader(io.StringIO(raw)):
            if len(row) > 16 and row[4].strip() == "California":
                u = {"1_unit": int(row[6]), "2_units": int(row[9]), "3_4_units": int(row[12]), "5plus_units": int(row[15])}
                u["total"] = sum(u.values())
                out["years"][str(y)] = u
                break
        else:
            sys.exit(f"No California row in {URL.format(y=y)}")
        print(y, out["years"][str(y)])
    (HERE / "data" / "census_bps_ca.json").write_text(json.dumps(out, indent=2) + "\n")

if __name__ == "__main__":
    main()
