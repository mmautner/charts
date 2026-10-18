#!/usr/bin/env python3
"""Download the Census Bureau's ACS PUMS California files and cut them to the 9 Bay Area
counties. The raw files are ~3.4 GB unzipped, so they are not committed; the Bay Area
extracts go to a cache folder (pickled DataFrames) that model/ reads.

Sources (U.S. Census Bureau, American Community Survey Public Use Microdata Sample):
  2020-2024 5-year  https://www2.census.gov/programs-surveys/acs/data/pums/2024/5-Year/
  2015-2019 5-year  https://www2.census.gov/programs-surveys/acs/data/pums/2019/5-Year/
  1-year, 2012-2024 https://www2.census.gov/programs-surveys/acs/data/pums/<year>/1-Year/
                    (no standard 1-year release for 2020)
  PUMA names        https://www2.census.gov/geo/tiger/TIGER2024/PUMA20/tl_2024_06_puma20.zip
                    https://www2.census.gov/geo/tiger/TIGER2019/PUMA/tl_2019_06_puma10.zip

The Bay Area is every PUMA whose 5-digit code starts with one of the 9 county FIPS codes.
That rule holds for California's 2010 and 2020 PUMAs (checked against the TIGER names),
not its 2000 PUMAs, which is why the 1-year series starts in 2012.

Usage:
    python inputs/fetch_pums.py --raw RAWDIR --cache CACHEDIR
"""
import argparse
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

COUNTIES = {"001": "Alameda", "013": "Contra Costa", "041": "Marin", "055": "Napa",
            "075": "San Francisco", "081": "San Mateo", "085": "Santa Clara",
            "095": "Solano", "097": "Sonoma"}
BASE = "https://www2.census.gov/programs-surveys/acs/data/pums/{y}/{span}/csv_{f}ca.zip"
ONE_YEAR = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024]

R = 80
HW = ["WGTP"] + [f"WGTP{i}" for i in range(1, R + 1)]
PW = ["PWGTP"] + [f"PWGTP{i}" for i in range(1, R + 1)]
HCOLS = ["SERIALNO", "PUMA", "ADJHSG", "ADJINC", "NP", "TYPEHUGQ", "TYPE", "BLD", "BDSP",
         "TEN", "VEH", "HINCP", "FINCP", "GRNTP", "RNTP", "SMOCP", "VALP", "GRPIP", "HUPAC",
         "HHT", "HHT2", "NOC", "NRC", "R18", "R60", "R65", "WIF", "MV", "YRBLT", "YBL", "HHL",
         "LNGI", "MULTG", "FS", "PARTNER", "NPF"] + HW
PCOLS = ["SERIALNO", "SPORDER", "PUMA", "ADJINC", "AGEP", "SEX", "RELSHIPP", "JWTRNS",
         "JWMNP", "JWAP", "POVPIP", "ESR", "DIS", "DPHY", "DOUT", "DREM", "DEYE", "SCHL",
         "SCH", "PINCP", "WAGP", "NATIVITY", "RAC1P", "HISP", "POWPUMA", "POWSP", "COW",
         "WKHP", "MIG"] + PW
ONE_YEAR_HCOLS = ["SERIALNO", "PUMA", "PUMA10", "PUMA20", "ADJINC", "NP", "TYPEHUGQ", "TYPE",
                  "VEH", "BLD", "TEN", "HINCP", "HUPAC", "R65"] + HW


def download(url, dest):
    if dest.exists():
        return dest
    print(f"downloading {url}", file=sys.stderr, flush=True)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".part")
    with urllib.request.urlopen(url, timeout=900) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f)
    tmp.rename(dest)
    return dest


def bay_extract(zpath, want):
    """Stream the CSV inside zpath, keep Bay Area rows and the columns in `want` that exist."""
    with zipfile.ZipFile(zpath) as z:
        name = next(n for n in z.namelist() if n.endswith(".csv"))
        with z.open(name) as f:
            header = f.readline().decode().strip().split(",")
        # 2012-2016 1-year files spell the replicate weights in lowercase (wgtp1 ...)
        upper = {c.upper(): c for c in header}
        cols = [upper[c] for c in want if c in upper]
        str_cols = {c: str for c in ("SERIALNO", "PUMA", "PUMA10", "PUMA20") if c in cols}
        parts = []
        with z.open(name) as f:
            for chunk in pd.read_csv(f, usecols=cols, dtype=str_cols, chunksize=200_000):
                chunk.columns = chunk.columns.str.upper()
                # 2012-2021 1-year files with mixed PUMA vintages carry PUMA10/PUMA20 instead
                if "PUMA" not in chunk:
                    chunk["PUMA"] = chunk.get("PUMA20", chunk.get("PUMA10"))
                chunk = chunk[chunk["PUMA"].str.zfill(5).str[:3].isin(COUNTIES)]
                parts.append(chunk)
    df = pd.concat(parts, ignore_index=True)
    df["PUMA"] = df["PUMA"].str.zfill(5)
    df["county"] = df["PUMA"].str[:3].map(COUNTIES)
    if "TYPEHUGQ" in df and "TYPE" not in df:
        df["TYPE"] = df.pop("TYPEHUGQ")
    return df


def puma_names(zpath):
    """PUMA code -> name from the TIGER shapefile's .dbf (fixed-width records)."""
    with zipfile.ZipFile(zpath) as z:
        raw = z.read(next(n for n in z.namelist() if n.endswith(".dbf")))
    n_rec = int.from_bytes(raw[4:8], "little")
    hdr_len = int.from_bytes(raw[8:10], "little")
    rec_len = int.from_bytes(raw[10:12], "little")
    fields, pos = [], 32
    while raw[pos] != 0x0D:
        fields.append((raw[pos:pos + 11].split(b"\0")[0].decode(), raw[pos + 16]))
        pos += 32
    rows = []
    for i in range(n_rec):
        rec = raw[hdr_len + i * rec_len + 1: hdr_len + (i + 1) * rec_len]
        vals, off = {}, 0
        for name, width in fields:
            vals[name] = rec[off:off + width].decode("latin-1").strip()
            off += width
        rows.append(vals)
    df = pd.DataFrame(rows)
    code = next(c for c in df if c.startswith("PUMACE"))
    name = next(c for c in df if c.startswith("NAMELSAD"))
    return df[[code, name]].rename(columns={code: "PUMA", name: "name"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="folder for (or holding) the downloaded zips")
    ap.add_argument("--cache", required=True, help="folder for the Bay Area extracts")
    ap.add_argument("--skip-1yr", action="store_true")
    a = ap.parse_args()
    raw, cache = Path(a.raw).resolve(), Path(a.cache).resolve()
    cache.mkdir(parents=True, exist_ok=True)

    for tiger, url in [("puma20", "https://www2.census.gov/geo/tiger/TIGER2024/PUMA20/tl_2024_06_puma20.zip"),
                       ("puma10", "https://www2.census.gov/geo/tiger/TIGER2019/PUMA/tl_2019_06_puma10.zip")]:
        names = puma_names(download(url, raw / f"{tiger}.zip"))
        names = names[names["PUMA"].str[:3].isin(COUNTIES)]
        names.to_csv(cache / f"{tiger}_names.csv", index=False)
        print(f"{tiger}: {len(names)} Bay Area PUMAs", file=sys.stderr)

    for y in (2024, 2019):
        for f, cols in (("h", HCOLS), ("p", PCOLS)):
            out = cache / f"{f}_5yr_{y}.pkl"
            if out.exists():
                continue
            z = download(BASE.format(y=y, span="5-Year", f=f), raw / f"{f}ca_{y}.zip")
            df = bay_extract(z, cols)
            df.to_pickle(out)
            print(f"{out.name}: {len(df):,} rows", file=sys.stderr)

    if not a.skip_1yr:
        for y in ONE_YEAR:
            out = cache / f"h_1yr_{y}.pkl"
            if out.exists():
                continue
            z = download(BASE.format(y=y, span="1-Year", f="h"), raw / f"hca_1yr_{y}.zip")
            df = bay_extract(z, ONE_YEAR_HCOLS)
            df["year"] = y
            df.to_pickle(out)
            print(f"{out.name}: {len(df):,} rows", file=sys.stderr)


if __name__ == "__main__":
    main()
