"""Pedestrian deaths in California and Texas from NHTSA FARS person files.

Pedestrian death = PER_TYP 5 (pedestrian) and INJ_SEV 4 (fatal injury), by the state of the crash.
Also tabulates where those deaths happened (route signing, functional class, urban/rural) from the
accident file, and the largest county in each state for the without-dominant-place test.

Usage: python -I model/fars.py raw/fars/x data
"""
import sys
from pathlib import Path
import pandas as pd

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
STATES = {6: "California", 48: "Texas"}
BIG_COUNTY = {6: (37, "Los Angeles County"), 48: (201, "Harris County")}
# Metros matching NHTS HH_CBSA (2013 OMB delineations): county FIPS
METROS = {6: {"Los_Angeles_metro": [37, 59]},
          48: {"Dallas_Fort_Worth_metro": [85, 113, 121, 139, 221, 231, 251, 257, 367, 397, 425, 439, 497],
               "Houston_metro": [15, 39, 71, 157, 167, 201, 291, 339, 473]}}
URL = "https://static.nhtsa.gov/nhtsa/downloads/FARS/{y}/National/FARS{y}NationalCSV.zip"
STATUS = {y: "final" for y in range(2010, 2023)} | {2023: "final (released 2026-04-01)", 2024: "annual report file, not final"}


def read(folder, stem, cols):
    f = next(p for p in folder.iterdir() if p.name.lower() == f"{stem}.csv")
    clean = lambda c: c.upper().replace("\u00ef\u00bb\u00bf", "").replace("\u00cf\u00bb\u00bf", "")   # UTF-8 BOM read as latin-1
    return pd.read_csv(f, usecols=lambda c: clean(c) in cols, encoding="latin-1", low_memory=False).rename(columns=clean)


rows, where = [], []
OWNER = {"City or Municipal Highway Agency": "city", "State Highway Agency": "state", "State Toll Road": "state",
         "County Highway Agency": "county", "Town or Township Highway Agency": "city"}


def road_group(d):
    """Road type x owner for the breakdown chart. FUNC_SYS 1-2 freeways, 3-4 main roads (arterials),
    5-7 smaller streets (collectors and local), anything else unknown."""
    owner = d.RD_OWNERNAME.astype(str).str.strip().map(OWNER).fillna("owner not reported")
    f = d.FUNC_SYS
    g = pd.Series("road type unknown", index=d.index)
    g[f.isin([1, 2])] = "freeway or expressway"
    g[f.isin([3, 4])] = "main road, " + owner[f.isin([3, 4])]
    g[f.isin([5, 6, 7])] = "smaller street"
    return g

for y in sorted(int(p.name) for p in SRC.iterdir() if p.name.isdigit()):
    per = read(SRC / str(y), "person", {"STATE", "ST_CASE", "COUNTY", "PER_TYP", "INJ_SEV", "LOCATION"})
    acc = read(SRC / str(y), "accident", {"ST_CASE", "ROUTENAME", "FUNC_SYS", "RUR_URB", "RD_OWNERNAME", "LGT_COND"})
    ped = per[(per.PER_TYP == 5) & (per.INJ_SEV == 4)].merge(acc, on="ST_CASE", how="left", validate="m:1")
    us = len(ped)
    for st, name in STATES.items():
        d = ped[ped.STATE == st]
        cfips, cname = BIG_COUNTY[st]
        base = dict(year=y, state=name, file_status=STATUS.get(y, ""), source=URL.format(y=y))
        rows.append(base | dict(measure="pedestrian_deaths", value=len(d)))
        rows.append(base | dict(measure=f"pedestrian_deaths_{cname.replace(' ', '_')}", value=int((d.COUNTY == cfips).sum())))
        for mname, cos in METROS[st].items():
            rows.append(base | dict(measure=f"pedestrian_deaths_{mname}", value=int(d.COUNTY.isin(cos).sum())))
        # Light (LGT_COND, same codes 2010-2024): 1 daylight, 4 dawn, 5 dusk; 2/3/6 dark (not lighted, lighted, unknown)
        rows.append(base | dict(measure="pedestrian_deaths_daylight_dawn_dusk", value=int(d.LGT_COND.isin([1, 4, 5]).sum())))
        rows.append(base | dict(measure="pedestrian_deaths_dark", value=int(d.LGT_COND.isin([2, 3, 6]).sum())))
        # Walker location (LOCATION, same codes 2010-2024; labeled from 2015): 11 not at intersection, on roadway,
        # not in marked crosswalk; 13 same, crosswalk availability unknown (used more in early years). 98/99 unknown.
        rows.append(base | dict(measure="pedestrian_deaths_midblock_not_in_crosswalk", value=int(d.LOCATION.isin([11, 13]).sum())))
        rows.append(base | dict(measure="pedestrian_deaths_location_known", value=int((~d.LOCATION.isin([98, 99])).sum())))
        if "ROUTENAME" not in d or "FUNC_SYS" not in d:     # older files code road type differently
            continue
        for grp, n in road_group(d).value_counts().items():
            where.append(dict(year=y, state=name, group=grp, deaths=int(n), scope="statewide", source=URL.format(y=y)))
        for grp, n in road_group(d[d.COUNTY != cfips]).value_counts().items():
            where.append(dict(year=y, state=name, group=grp, deaths=int(n), scope=f"excluding {cname}", source=URL.format(y=y)))
        # Route signing by name: the numeric ROUTE codes were reorganized in the 2023 file.
        rt = d.ROUTENAME.astype(str).str.strip()
        state_signed = rt.str.match(r"^(U\.?S\.? Highway|State Highway)$")   # 2022 spells it "US Highway"
        # FUNC_SYS: 1 Interstate, 2 other freeway/expressway, 3 other principal arterial, 4 minor arterial,
        # 5 major collector, 6 minor collector, 7 local
        arterial = d.FUNC_SYS.isin([3, 4])
        state_owned = d.RD_OWNERNAME.astype(str).str.strip().isin(["State Highway Agency", "State Toll Road"])
        rows.append(base | dict(measure="pedestrian_deaths_on_interstate_us_or_state_routes", value=int((state_signed | (rt == "Interstate")).sum())))
        rows.append(base | dict(measure="pedestrian_deaths_on_state_routes_non_interstate", value=int(state_signed.sum())))
        rows.append(base | dict(measure="pedestrian_deaths_on_freeways_func_1_2", value=int(d.FUNC_SYS.isin([1, 2]).sum())))
        rows.append(base | dict(measure="pedestrian_deaths_on_arterials_func_3_4", value=int(arterial.sum())))
        # surface state highways (El Camino Real type): US- or state-signed principal or minor arterial
        rows.append(base | dict(measure="pedestrian_deaths_on_surface_state_arterials", value=int((state_signed & arterial).sum())))
        # road owner is reported for most California crashes but almost no Texas crashes
        rows.append(base | dict(measure="pedestrian_deaths_road_owner_reported", value=int((~d.RD_OWNERNAME.astype(str).str.contains("Not Reported|Unknown|nan")).sum())))
        rows.append(base | dict(measure="pedestrian_deaths_on_state_owned_roads", value=int(state_owned.sum())))
        rows.append(base | dict(measure="pedestrian_deaths_on_state_owned_arterials", value=int((state_owned & arterial).sum())))
        rows.append(base | dict(measure="pedestrian_deaths_on_city_owned_arterials", value=int((d.RD_OWNERNAME.astype(str).str.strip().eq("City or Municipal Highway Agency") & arterial).sum())))
        rows.append(base | dict(measure="pedestrian_deaths_urban", value=int((d.RUR_URB == 2).sum())))
    rows.append(dict(year=y, state="United States", file_status=STATUS.get(y, ""), source=URL.format(y=y),
                     measure="pedestrian_deaths", value=us))

df = pd.DataFrame(rows)
df.to_csv(OUT / "fars_pedestrian_deaths.csv", index=False)
pd.DataFrame(where).to_csv(OUT / "fars_deaths_by_road.csv", index=False)
print(df.pivot_table(index=["state", "measure"], columns="year", values="value").to_string())
