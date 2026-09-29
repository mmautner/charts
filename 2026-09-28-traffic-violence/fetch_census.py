"""Download the Census Bureau's Vintage 2025 national population estimate for
July 1, 2024. Saves the raw CSV and a small JSON summary (with the fetch date) to
data/. Commit both, so the charts reproduce as published even after Census revises.

Source: U.S. Census Bureau, Population Division, NST-EST2025-ALLDATA
(released January 2026). Dataset page:
https://www.census.gov/data/datasets/time-series/demo/popest/2020s-national-total.html
"""
import csv, datetime, io, json, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
URL = ("https://www2.census.gov/programs-surveys/popest/datasets/"
       "2020-2025/state/totals/NST-EST2025-ALLDATA.csv")
YEAR = 2024

def main():
    try:
        raw = urllib.request.urlopen(URL, timeout=60).read()
    except Exception as e:
        sys.exit(f"Could not download {URL}: {e}\n"
                 "If the Census Bureau moved the file, find NST-EST2025-ALLDATA on the "
                 "dataset page in this file's docstring and update URL.")
    (HERE / "data" / "NST-EST2025-ALLDATA.csv").write_bytes(raw)
    for row in csv.DictReader(io.StringIO(raw.decode("latin-1"))):
        if row["SUMLEV"] == "010":  # summary level 010 = the United States
            pop = int(row[f"POPESTIMATE{YEAR}"])
            break
    else:
        sys.exit("No national (SUMLEV 010) row found in the file.")
    out = {"source": URL, "vintage": 2025, "estimate_date": f"{YEAR}-07-01",
           "fetched_on": datetime.date.today().isoformat(), "population": pop}
    (HERE / "data" / "census_population.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"US resident population, July 1, {YEAR} (Vintage 2025): {pop:,}")

if __name__ == "__main__":
    main()
