"""Pedestrian death rates for California and Texas: per resident, per mile driven, per walk trip,
per hour walked. Writes the tidy file data/ca_tx_pedestrian_rates.csv (every input and output, with
source URLs) plus the small input tables the charts read.

Inputs: data/fars_pedestrian_deaths.csv (model/fars.py), data/nhts2017_walk_totals_replicates.csv
(model/nhts.py), and raw Census and FHWA files under raw/ (population and VMT are extracted to
data/population.csv and data/vmt_vm2.csv on the first run; later runs read those).

Uncertainty, two sources, reported separately and combined:
  - NHTS sampling: jackknife over 98 replicates (walk totals recomputed under each replicate).
  - Year-to-year randomness in deaths: Poisson, SE(count) = sqrt(count).
  Combined SE of a rate = rate x sqrt(rel_se_deaths^2 + rel_se_exposure^2). 90% MOE = 1.645 x SE.

Usage: python -I model/rates.py
"""
import csv
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
RAW, DATA = HERE / "raw", HERE / "data"
FACT, Z90 = 6.0 / 7.0, 1.645
FIPS = {"California": "06", "Texas": "48"}
SRC = {
    "pep2025": "https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/state/totals/NST-EST2025-ALLDATA.csv",
    "pep_int": "https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/intercensal/state/asrh/sc-est2020int-alldata6.csv",
    "pep_co2025": "https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv",
    "pep_co2020": "https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/counties/totals/co-est2020-alldata.csv",
    "vm2": "https://www.fhwa.dot.gov/policyinformation/statistics/{y}/vm2.cfm",
    "nhts": "https://nhts.ornl.gov/assets/2016/download/csv.zip (and Replicates.zip)",
    "acs": "https://api.census.gov/data/2019/acs/acs1?get=NAME,group(B08301)&for=state:06,48",
}
METRO_COUNTIES = {"Los Angeles metro": ("06", [37, 59]),
                  "Dallas-Fort Worth metro": ("48", [85, 113, 121, 139, 221, 231, 251, 257, 367, 397, 425, 439, 497])}


# ------------------------------------------------------------------ inputs
V2020_YEARS = [2010, 2011, 2012, 2017]


def population():
    f = DATA / "population.csv"
    if f.exists():
        return pd.read_csv(f, dtype={"fips": str})
    rows = []
    a = pd.read_csv(RAW / "census/sc-est2020int-alldata6.csv", dtype={"STATE": str})
    a = a[(a.SEX == 0) & (a.ORIGIN == 0)]
    for st, fp in FIPS.items():
        for y in range(2010, 2020):
            rows.append(dict(geo=st, fips=fp, year=y, population=int(a.loc[a.STATE == fp, f"POPESTIMATE{y}"].sum()),
                             vintage="2010-2020 intercensal", source=SRC["pep_int"]))
    b = pd.read_csv(RAW / "census/NST-EST2025-ALLDATA.csv", dtype={"STATE": str})
    for st, fp in FIPS.items():
        for y in range(2020, 2026):
            rows.append(dict(geo=st, fips=fp, year=y, population=int(b.loc[b.STATE == fp, f"POPESTIMATE{y}"].iloc[0]),
                             vintage="Vintage 2025", source=SRC["pep2025"]))
    # county-based sensitivity (2010-2012, 2017) uses Vintage 2020 for both the state and the metro so they match
    c = pd.read_csv(RAW / "census/co-est2020-alldata.csv", dtype={"STATE": str}, encoding="latin-1")
    for y in V2020_YEARS:
        for st, fp in FIPS.items():
            rows.append(dict(geo=f"{st} (Vintage 2020)", fips=fp, year=y, vintage="Vintage 2020", source=SRC["pep_co2020"],
                             population=int(c.loc[(c.STATE == fp) & (c.SUMLEV == 40), f"POPESTIMATE{y}"].iloc[0])))
        for m, (fp, cos) in METRO_COUNTIES.items():
            rows.append(dict(geo=m, fips=fp, year=y, vintage="Vintage 2020", source=SRC["pep_co2020"],
                             population=int(c.loc[(c.STATE == fp) & (c.SUMLEV == 50) & c.COUNTY.isin(cos), f"POPESTIMATE{y}"].sum())))
    c = pd.read_csv(RAW / "census/co-est2025-alldata.csv", dtype={"STATE": str}, encoding="latin-1")
    for m, (fp, cos) in METRO_COUNTIES.items():
        for y in range(2020, 2026):
            rows.append(dict(geo=m, fips=fp, year=y, vintage="Vintage 2025", source=SRC["pep_co2025"],
                             population=int(c.loc[(c.STATE == fp) & (c.SUMLEV == 50) & c.COUNTY.isin(cos), f"POPESTIMATE{y}"].sum())))
    df = pd.DataFrame(rows)
    df.to_csv(f, index=False)
    return df


def vmt():
    f = DATA / "vmt_vm2.csv"
    if f.exists():
        return pd.read_csv(f)
    rows = []
    for p in sorted((RAW / "fhwa").glob("vm2_*")):
        y = int(p.stem.split("_")[1])
        sheet = pd.read_excel(p, header=None, sheet_name="A")
        for st in FIPS:
            hit = sheet[sheet[0].astype(str).str.strip().str.match(rf"^{st}\b")]
            vals = [v for v in hit.iloc[0].values[1:] if isinstance(v, (int, float)) and not pd.isna(v)]
            # first block of the row ends with the grand total (millions of vehicle miles, all systems)
            total = vals[16] if len(vals) > 16 and y >= 2009 else vals[14]
            rows.append(dict(state=st, year=y, vmt_millions=float(total), source=SRC["vm2"].format(y=y),
                             row_label=str(hit.iloc[0, 0]).strip()))
    df = pd.DataFrame(rows)
    df.to_csv(f, index=False)
    return df


pop, vm = population(), vmt()
fars = pd.read_csv(DATA / "fars_pedestrian_deaths.csv")
reps = pd.read_csv(DATA / "nhts2017_walk_totals_replicates.csv")
RC = [f"r{i}" for i in range(99)]


def P(geo, y):
    return int(pop[(pop.geo == geo) & (pop.year == y)].population.iloc[0])


def V(st, y):
    return float(vm[(vm.state == st) & (vm.year == y)].vmt_millions.iloc[0])


def D(st, y, measure="pedestrian_deaths"):
    return int(fars[(fars.state == st) & (fars.year == y) & (fars.measure == measure)].value.iloc[0])


def W(group, measure):
    return reps[(reps.group == group) & (reps.measure == measure)][RC].values[0].astype(float)


def jk_se(th):
    return float(np.sqrt(FACT * ((th[1:] - th[0]) ** 2).sum()))


out = []


def add(kind, geo, year, measure, value, unit, source, se_sampling=np.nan, se_deaths=np.nan, n=np.nan, note=""):
    se = np.sqrt(np.nan_to_num(se_sampling) ** 2 + np.nan_to_num(se_deaths) ** 2) if not (np.isnan(se_sampling) and np.isnan(se_deaths)) else np.nan
    out.append(dict(kind=kind, geo=geo, year=year, measure=measure, value=value, unit=unit,
                    se_nhts_sampling=se_sampling, se_deaths_poisson=se_deaths, se_combined=se,
                    moe90_combined=Z90 * se if not np.isnan(se) else np.nan, n_unweighted=n, source=source, note=note))


FARS_URL = "https://static.nhtsa.gov/nhtsa/downloads/FARS/{y}/National/FARS{y}NationalCSV.zip"
YEARS = list(range(2010, 2025))
for st in FIPS:
    for y in YEARS:
        d, p, v = D(st, y), P(st, y), V(st, y)
        status = fars[(fars.state == st) & (fars.year == y)].file_status.iloc[0]
        add("input", st, y, "pedestrian_deaths", d, "deaths", FARS_URL.format(y=y), note=f"FARS {status}; PER_TYP 5, INJ_SEV 4, state of crash")
        add("input", st, y, "population", p, "residents", pop[(pop.geo == st) & (pop.year == y)].source.iloc[0])
        add("input", st, y, "vmt", v, "million vehicle miles", SRC["vm2"].format(y=y), note="FHWA Highway Statistics VM-2, all systems")
        add("output", st, y, "vmt_per_resident", v * 1e6 / p, "miles per resident", "VM-2 / Census PEP")
        add("output", st, y, "deaths_per_100k_residents", d / p * 1e5, "deaths per 100,000 residents", "FARS / Census PEP",
            se_deaths=np.sqrt(d) / p * 1e5, note=f"FARS {status}")
        add("output", st, y, "deaths_per_billion_vmt", d / v * 1e3, "deaths per billion vehicle miles", "FARS / VM-2",
            se_deaths=np.sqrt(d) / v * 1e3, note=f"FARS {status}")

# NHTS 2017 walking exposure
for st in FIPS:
    for label, years in [("2017", [2017]), ("2016-2018 average", [2016, 2017, 2018])]:
        d = np.mean([D(st, y) for y in years])
        se_d = np.sqrt(sum(D(st, y) for y in years)) / len(years)
        for m, unit, scale, div in [("walk_trips", "deaths per 100 million walk trips", 1e8, 1),
                                    ("walk_minutes", "deaths per million hours walked", 1e6, 60),
                                    ("walk_miles_cleaned", "deaths per 100 million miles walked", 1e8, 1)]:
            tot = W(st, f"{m}_annual_total") / div
            rate = d / tot * scale
            if label == "2017":
                add("input", st, 2017, f"nhts_{m}_annual_total" + ("_hours" if div == 60 else ""), tot[0],
                    "walk hours per year" if div == 60 else unit.split("per ")[-1].replace("100 million ", "").replace("million ", ""),
                    SRC["nhts"], se_sampling=jk_se(tot))
            add("output", st, label, f"deaths_per_{m.replace('walk_minutes', 'walk_hours')}", rate[0], unit,
                "FARS / NHTS 2017", se_sampling=jk_se(rate), se_deaths=se_d / tot[0] * scale,
                note="NHTS 2017 exposure; deaths " + label)

# California vs Texas ratios (CA / TX) for 2017
for m, scale, div in [("walk_trips", 1e8, 1), ("walk_minutes", 1e6, 60)]:
    a, b = D("California", 2017) / (W("California", f"{m}_annual_total") / div), D("Texas", 2017) / (W("Texas", f"{m}_annual_total") / div)
    r = a / b
    rel_d = np.sqrt(1 / D("California", 2017) + 1 / D("Texas", 2017))
    add("output", "California / Texas", 2017, f"ratio_deaths_per_{m}", r[0], "ratio", "FARS / NHTS 2017",
        se_sampling=jk_se(r), se_deaths=r[0] * rel_d)

# Without the largest metro (2017; Vintage 2020 county population; NHTS HH_CBSA)
for st, metro, nhts_group in [("California", "Los Angeles metro", "California excl. Los Angeles metro"),
                              ("Texas", "Dallas-Fort Worth metro", "Texas excl. Dallas-Fort Worth metro")]:
    mkey = "pedestrian_deaths_" + metro.replace(" ", "_").replace("-", "_")
    d = D(st, 2017) - D(st, 2017, mkey)
    p = P(f"{st} (Vintage 2020)", 2017) - P(metro, 2017)
    add("input", nhts_group, 2017, "pedestrian_deaths", d, "deaths", FARS_URL.format(y=2017), note="county FIPS list in model/fars.py")
    add("input", nhts_group, 2017, "population", p, "residents", SRC["pep_co2020"])
    add("output", nhts_group, 2017, "deaths_per_100k_residents", d / p * 1e5, "deaths per 100,000 residents",
        "FARS / Census PEP V2020", se_deaths=np.sqrt(d) / p * 1e5)
    for m, unit, scale, div in [("walk_trips", "deaths per 100 million walk trips", 1e8, 1),
                                ("walk_minutes", "deaths per million hours walked", 1e6, 60)]:
        tot = W(nhts_group, f"{m}_annual_total") / div
        rate = d / tot * scale
        add("output", nhts_group, 2017, f"deaths_per_{m.replace('walk_minutes', 'walk_hours')}", rate[0], unit,
            "FARS / NHTS 2017", se_sampling=jk_se(rate), se_deaths=np.sqrt(d) / tot[0] * scale)

# Without the largest metro, recent years (Vintage 2025 county and state populations)
for st, metro in [("California", "Los Angeles metro"), ("Texas", "Dallas-Fort Worth metro")]:
    mkey = "pedestrian_deaths_" + metro.replace(" ", "_").replace("-", "_")
    for y in [2021, 2022, 2023, 2024]:
        d, p = D(st, y) - D(st, y, mkey), P(st, y) - P(metro, y)
        add("output", f"{st} excl. {metro}", y, "deaths_per_100k_residents", d / p * 1e5, "deaths per 100,000 residents",
            "FARS / Census PEP V2025", se_deaths=np.sqrt(d) / p * 1e5, n=d)

# Without the largest metro, 2010-2012 (Vintage 2020 county and state populations), for the trend test
for st, metro in [("California", "Los Angeles metro"), ("Texas", "Dallas-Fort Worth metro")]:
    mkey = "pedestrian_deaths_" + metro.replace(" ", "_").replace("-", "_")
    for y in [2010, 2011, 2012]:
        d, p = D(st, y) - D(st, y, mkey), P(f"{st} (Vintage 2020)", y) - P(metro, y)
        add("output", f"{st} excl. {metro}", y, "deaths_per_100k_residents", d / p * 1e5, "deaths per 100,000 residents",
            "FARS / Census PEP V2020", se_deaths=np.sqrt(d) / p * 1e5, n=d)
    for y in [2010, 2011, 2012, 2021, 2022, 2023, 2024]:
        add("input", f"{st} excl. {metro}", y, "pedestrian_deaths", D(st, y) - D(st, y, mkey), "deaths", FARS_URL.format(y=y),
            note="county FIPS list in model/fars.py")

# Where pedestrians died (share of state's pedestrian deaths)
for st in FIPS:
    for y in [2017, 2023]:
        for m in ["pedestrian_deaths_on_arterials_func_3_4", "pedestrian_deaths_on_state_routes_non_interstate",
                  "pedestrian_deaths_on_interstate_us_or_state_routes", "pedestrian_deaths_on_surface_state_arterials",
                  "pedestrian_deaths_on_freeways_func_1_2", "pedestrian_deaths_road_owner_reported",
                  "pedestrian_deaths_on_state_owned_roads", "pedestrian_deaths_on_state_owned_arterials",
                  "pedestrian_deaths_on_city_owned_arterials",
                  "pedestrian_deaths_urban"]:
            add("output", st, y, "share_" + m, D(st, y, m) / D(st, y), "share of pedestrian deaths", FARS_URL.format(y=y),
                n=D(st, y, m))

# NHTS per-person walking and ACS commute (secondary check)
w = pd.read_csv(DATA / "nhts2017_walking.csv")
for r in w[w.measure.str.contains("per_person|share|ratio")].itertuples():
    add("input", r.group, 2017, "nhts_" + r.measure, r.estimate, "", SRC["nhts"], se_sampling=r.se,
        n=r.n_persons, note=f"unweighted households {r.n_households:.0f}, walk trips {r.n_walk_trips:.0f}" if not np.isnan(r.n_households) else "")
acs = list(csv.reader(open(RAW / "census/acs2019_b08301_api.json").read().replace("[", "").replace("]", "").splitlines()))
hdr = [h.strip('" ,') for h in acs[0]]
for row in acs[1:]:
    row = dict(zip(hdr, [x.strip('" ,') for x in row]))
    tot = float(row["B08301_001E"])
    for code, lab in [("019", "walked"), ("021", "worked_from_home")]:
        add("input", row["NAME"], 2019, f"acs_commute_share_{lab}", float(row[f"B08301_{code}E"]) / tot, "share of workers 16+",
            SRC["acs"], se_sampling=float(row[f"B08301_{code}M"]) / 1.645 / tot, note="ACS 1-year B08301; SE from published 90% MOE, ignores MOE of total")

df = pd.DataFrame(out)
df.to_csv(DATA / "ca_tx_pedestrian_rates.csv", index=False)
pd.set_option("display.width", 250, "display.max_colwidth", 40)
show = df[df.kind == "output"][["geo", "year", "measure", "value", "se_nhts_sampling", "se_deaths_poisson", "moe90_combined", "n_unweighted"]]
print(show.to_string(index=False, float_format=lambda x: f"{x:,.3f}"))
