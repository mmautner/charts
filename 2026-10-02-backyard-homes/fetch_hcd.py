"""Download HCD's Housing Element Annual Progress Report (APR) Table A2 and
summarize it to units by report year and unit category. Saves the small summary
and a metadata file to data/. The raw file is large, so it is not committed;
the summary plus the fetch date is enough to reproduce the charts.

Source: California Open Data, "Housing Element Annual Progress Report (APR) Data
by Jurisdiction and Year," resource "APR Table A2."
https://data.ca.gov/dataset/housing-element-annual-progress-report-apr-data-by-jurisdiction-and-year

Table A2 has 1 row per project per report year, with the units that reached each
stage (entitlement, building permit, certificate of occupancy) in that year. Units
permitted in a year = sum of the building-permit unit count over rows for that year.

Usage:
    python fetch_hcd.py                    # download, then summarize
    python fetch_hcd.py --file tablea2.csv # summarize a copy downloaded by hand
"""
import argparse, collections, csv, datetime, json, sys, tempfile, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
URL = ("https://data.ca.gov/dataset/81b0841f-2802-403e-b48e-2ef4b751f77c/resource/"
       "fe505d9b-8c36-42ba-ba30-08bc4f34e022/download/tablea2.csv")

# HCD has renamed columns before, so accept any of these spellings.
COLS = {
    "year": ["YEAR", "REPORTING_YEAR", "RPT_YEAR"],
    "juris": ["JURIS_NAME", "JURISDICTION", "JURS_NAME"],
    "unit_cat": ["UNIT_CAT", "UNIT_CATEGORY", "UNIT_CAT_DESC"],
    "bp_units": ["NO_BUILDING_PERMITS", "BP_TOTAL", "TOT_BP_UNITS", "BUILDING_PERMITS_UNITS"],
    "co_units": ["NO_OTHER_FORMS_OF_READINESS", "NO_CO", "CO_TOTAL", "TOT_CO_UNITS", "CERT_OF_OCC_UNITS"],
    "apn": ["APN", "PRIOR_APN"],
    "address": ["STREET_ADDRESS", "ADDRESS"],
}

def pick(header, key, required=True):
    for c in COLS[key]:
        if c in header:
            return c
    if required:
        sys.exit(f"No column for '{key}' (tried {COLS[key]}).\nColumns in file:\n  " + "\n  ".join(header))
    return None

def num(s):
    try:
        return float(s.replace(",", "")) if s and s.strip() else 0.0
    except ValueError:
        return 0.0

def summarize(path):
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
        r = csv.DictReader(f)
        h = r.fieldnames
        c = {k: pick(h, k, required=k in ("year", "unit_cat", "bp_units")) for k in COLS}
        agg = collections.defaultdict(lambda: {"bp_units": 0.0, "co_units": 0.0, "rows": 0})
        seen = collections.Counter()   # duplicate check on ADU permit rows
        cats = collections.Counter()
        n = 0
        for row in r:
            n += 1
            y, cat = row[c["year"]].strip(), row[c["unit_cat"]].strip()
            cats[cat] += 1
            a = agg[(y, cat)]
            bp = num(row[c["bp_units"]])
            a["bp_units"] += bp
            a["co_units"] += num(row[c["co_units"]]) if c["co_units"] else 0
            a["rows"] += 1
            if bp > 0 and "ADU" in cat.upper() and c["juris"]:
                key = (y, row[c["juris"]].strip().upper(),
                       (row[c["apn"]] if c["apn"] else "").strip(),
                       (row[c["address"]] if c["address"] else "").strip().upper())
                seen[key] += 1
    dupes = sum(v - 1 for v in seen.values() if v > 1)
    return agg, {"columns_used": c, "all_columns": h, "rows": n,
                 "unit_categories": dict(cats.most_common()),
                 "adu_permit_rows_sharing_year_juris_apn_address": dupes}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    args = ap.parse_args()
    if args.file:
        path, source = args.file, f"local copy of {URL}"
    else:
        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        try:
            print(f"Downloading {URL} ...")
            with urllib.request.urlopen(URL, timeout=600) as resp:
                while chunk := resp.read(1 << 20):
                    tmp.write(chunk)
        except Exception as e:
            sys.exit(f"Could not download {URL}: {e}\nDownload it by hand from the dataset "
                     "page in this file's docstring and rerun with --file.")
        tmp.close()
        path, source = tmp.name, URL
    agg, meta = summarize(path)
    meta.update({"source": source, "fetched_on": datetime.date.today().isoformat()})
    out = HERE / "data" / "hcd_a2_summary.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "unit_cat", "bp_units", "co_units", "rows"])
        for (y, cat), a in sorted(agg.items()):
            w.writerow([y, cat, round(a["bp_units"]), round(a["co_units"]), a["rows"]])
    (HERE / "data" / "hcd_a2_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"Wrote {out} and hcd_a2_meta.json ({meta['rows']:,} rows read)")

if __name__ == "__main__":
    main()
