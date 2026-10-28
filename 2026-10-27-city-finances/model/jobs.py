"""Jobs located in each city (Census LEHD LODES8 workplace area characteristics, 2023), summed from census blocks
to places with the LODES block crosswalk. usage (from the post folder): python -I model/jobs.py raw/lehd data
writes data/jobs_2023.csv"""
import sys
from pathlib import Path
import pandas as pd

raw, out = Path(sys.argv[1]), Path(sys.argv[2])
x = pd.read_csv(raw / "ca_xwalk.csv.gz", usecols=["tabblk2020", "stplc", "stplcname"], dtype=str)
w = pd.read_csv(raw / "ca_wac_S000_JT00_2023.csv.gz", usecols=["w_geocode", "C000", "CNS18"], dtype={"w_geocode": str})
m = w.merge(x, left_on="w_geocode", right_on="tabblk2020", how="left")
assert m.stplc.notna().mean() > 0.99
names = {"Burlingame city, CA": "Burlingame", "San Mateo city, CA": "San Mateo"}
r = m[m.stplcname.isin(names)].groupby("stplcname")[["C000", "CNS18"]].sum().rename(index=names)
r = r.rename(columns={"C000": "jobs_all", "CNS18": "jobs_accommodation_food"})
pop = pd.read_csv(out / "population.csv")
pop = pop[pop.vintage == "DOF E-1 May 2025 release"].set_index("city").population
r["population_2025"] = pop
r["jobs_per_resident"] = (r.jobs_all / r.population_2025).round(3)
r["source"] = "LEHD LODES8 WAC S000 JT00 2023 (all jobs, primary and secondary); blocks to places via ca_xwalk.csv.gz"
r.index.name = "city"
r.to_csv(out / "jobs_2023.csv")
print(r.drop(columns="source").to_string())
