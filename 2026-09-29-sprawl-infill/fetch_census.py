"""Download the 2 Census files the charts use and save them to data/:

1. ACS 2020-2024 5-year table B25034 (year structure built) for every census tract
   in the 50 states and DC, via the Census Data API. Needs a free API key in the
   CENSUS_API_KEY environment variable: https://api.census.gov/data/key_signup.html
2. The 2024 Census tract gazetteer (land area and internal point for each tract).
   No key needed. Run with --gazetteer-only to fetch just this file.

Commit data/, so the charts reproduce as published even after Census revises.
"""
import csv, datetime, io, json, os, sys, time, urllib.request, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ACS_YEAR = 2024
ACS_URL = "https://api.census.gov/data/{y}/acs/acs5?get={v}&for=tract:*&in=state:{s}&key={k}"
GAZ_URL = (f"https://www2.census.gov/geo/docs/maps-data/data/gazetteer/"
           f"{ACS_YEAR}_Gazetteer/{ACS_YEAR}_Gaz_tracts_national.zip")
ACS_VARS = [f"B25034_{i:03d}E" for i in range(1, 12)]
STATES = ("01 02 04 05 06 08 09 10 11 12 13 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 "
          "31 32 33 34 35 36 37 38 39 40 41 42 44 45 46 47 48 49 50 51 53 54 55 56").split()
ACS_FILE = HERE / "data" / "acs_b25034_tracts.csv"
GAZ_FILE = HERE / "data" / "gazetteer_tracts.csv"

def get(url, tries=4):
    for i in range(tries):
        try:
            return urllib.request.urlopen(url, timeout=120).read()
        except Exception as e:
            if i == tries - 1:
                sys.exit(f"Could not download {url.split('&key=')[0]}: {e}")
            time.sleep(2 ** i)

def fetch_acs(key):
    with open(ACS_FILE, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["GEOID"] + ACS_VARS)
        for st in STATES:
            rows = json.loads(get(ACS_URL.format(y=ACS_YEAR, v=",".join(ACS_VARS), s=st, k=key)))
            head = rows[0]
            for r in rows[1:]:
                d = dict(zip(head, r))
                w.writerow([d["state"] + d["county"] + d["tract"]] + [max(int(d[v] or 0), 0) for v in ACS_VARS])
            print(f"  state {st}: {len(rows) - 1} tracts")

def fetch_gazetteer():
    z = zipfile.ZipFile(io.BytesIO(get(GAZ_URL)))
    text = z.read(z.namelist()[0]).decode("latin-1")
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    reader.fieldnames = [c.strip() for c in reader.fieldnames]
    with open(GAZ_FILE, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["GEOID", "ALAND_SQMI", "INTPTLAT", "INTPTLONG"])
        for r in reader:
            w.writerow([r["GEOID"], r["ALAND_SQMI"].strip(), r["INTPTLAT"].strip(), r["INTPTLONG"].strip()])

def main():
    (HERE / "data").mkdir(exist_ok=True)
    info_path = HERE / "data" / "fetch_info.json"
    info = json.loads(info_path.read_text()) if info_path.exists() else {}
    today = datetime.date.today().isoformat()
    if "--gazetteer-only" not in sys.argv:
        key = os.environ.get("CENSUS_API_KEY") or sys.exit("Set CENSUS_API_KEY (see docstring).")
        fetch_acs(key)
        info["acs"] = {"table": "B25034", "survey": f"ACS 5-year {ACS_YEAR - 4}-{ACS_YEAR}",
                       "source": f"https://api.census.gov/data/{ACS_YEAR}/acs/acs5", "fetched_on": today}
    fetch_gazetteer()
    info["gazetteer"] = {"source": GAZ_URL, "fetched_on": today}
    info_path.write_text(json.dumps(info, indent=2) + "\n")
    print(f"Wrote {ACS_FILE.name}, {GAZ_FILE.name}, fetch_info.json to data/")

if __name__ == "__main__":
    main()
