"""The arithmetic behind both charts. Run it on its own to print every number.

Infill vs. greenfield: for each decade, a tract's starting density is the homes built
before that decade (and still standing) divided by its land area. Homes built in the
decade count as infill if the tract was already at 425+ homes per square mile.
"""
import csv, math
from pathlib import Path
import numpy as np
from matplotlib.path import Path as Polygon
from inputs import *

HERE = Path(__file__).resolve().parent
# B25034 columns from oldest to newest. The first is the pre-1940 baseline, the last
# ("2020 or later") is a partial decade.
COLS = ["B25034_011E", "B25034_010E", "B25034_009E", "B25034_008E", "B25034_007E",
        "B25034_006E", "B25034_005E", "B25034_004E", "B25034_003E", "B25034_002E"]
LABELS = ["pre-1940", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]

def load():
    """Tracts with positive land area, as numpy arrays."""
    acs_path, gaz_path = HERE / "data" / "acs_b25034_tracts.csv", HERE / "data" / "gazetteer_tracts.csv"
    if not (acs_path.exists() and gaz_path.exists()):
        raise SystemExit("data/ is missing the Census files. Run fetch_census.py first.")
    gaz = {r["GEOID"]: r for r in csv.DictReader(open(gaz_path))}
    geoid, built, land, lat, lon = [], [], [], [], []
    missing = 0
    for r in csv.DictReader(open(acs_path)):
        g = gaz.get(r["GEOID"])
        if g is None:
            missing += 1
            continue
        if float(g["ALAND_SQMI"]) <= 0:
            continue
        geoid.append(r["GEOID"]); built.append([int(r[c]) for c in COLS])
        land.append(float(g["ALAND_SQMI"])); lat.append(float(g["INTPTLAT"])); lon.append(float(g["INTPTLONG"]))
    assert missing < 100, f"{missing} ACS tracts have no gazetteer match; check vintages"
    return {"geoid": np.array(geoid), "built": np.array(built), "land": np.array(land),
            "lat": np.array(lat), "lon": np.array(lon)}

def infill_by_decade(t, threshold=URBAN_CORE_HU_PER_SQMI, lag=1):
    """Homes built per decade, split by whether the tract was already urban.
    lag=1: urban when the decade began. lag=2: urban a full decade earlier (strict)."""
    cum = t["built"].cumsum(axis=1)
    out = []
    for k in range(lag, len(COLS)):
        urban = cum[:, k - lag] / t["land"] >= threshold
        new = t["built"][:, k]
        out.append({"decade": LABELS[k], "total": int(new.sum()),
                    "infill": int(new[urban].sum()), "greenfield": int(new[~urban].sum())})
    return out

def state(t, fips):
    """The tracts of one state, by the 2-digit FIPS prefix of their GEOID."""
    m = np.char.startswith(t["geoid"], fips)
    return {k: v[m] for k, v in t.items()}

def per_1000_residents(rows, population, key="infill"):
    """Homes per 1,000 residents for each decade that has a census at its start."""
    return {r["decade"]: r[key] / population[int(r["decade"][:4])] * 1e3
            for r in rows if int(r["decade"][:4]) in population}

def residents_per_home(population, occupied):
    """Household residents per occupied home at each census year both series cover."""
    return {y: population[y] / occupied[y] for y in sorted(occupied) if y in population}

def miles(lat1, lon1, lat2, lon2):
    dy = (lat2 - lat1) * 69.05
    dx = (lon2 - lon1) * 69.05 * np.cos(np.radians((lat1 + lat2) / 2))
    return np.hypot(dx, dy)

def loop_area_sqmi():
    lat0 = np.mean([p[0] for p in I610_LOOP])
    x = np.array([lon for _, lon in I610_LOOP]) * 69.05 * math.cos(math.radians(lat0))
    y = np.array([lat for lat, _ in I610_LOOP]) * 69.05
    return abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))) / 2

def texas_cores(t):
    """Masks for Houston inside I-610 and equal-area circles around downtown Dallas
    and San Antonio."""
    tx = np.char.startswith(t["geoid"], "48")
    inside = Polygon([(lon, lat) for lat, lon in I610_LOOP]).contains_points(np.c_[t["lon"], t["lat"]])
    radius = math.sqrt(loop_area_sqmi() / math.pi)
    cores = {"Houston": tx & inside}
    for city, (la, lo) in DOWNTOWNS.items():
        cores[city] = tx & (miles(la, lo, t["lat"], t["lon"]) <= radius)
    return cores, radius

def core_series(t, first="1960s", last="2010s"):
    cores, _ = texas_cores(t)
    i, j = LABELS.index(first), LABELS.index(last) + 1
    return LABELS[i:j], {c: t["built"][m, i:j].sum(axis=0) for c, m in cores.items()}

if __name__ == "__main__":
    t = load()
    print(f"{len(t['land']):,} tracts\n")
    rows = infill_by_decade(t)
    print("Homes built per decade (millions), infill = tract at 425+ homes/sq mi when decade began")
    for r in rows:
        print(f"  {r['decade']:>8}  total {r['total']/1e6:5.2f}  infill {r['infill']/1e6:5.2f}"
              f"  greenfield {r['greenfield']/1e6:5.2f}  infill share {r['infill']/r['total']:.0%}")
    for thr in SENSITIVITY_HU_PER_SQMI:
        print(f"\nInfill share at {thr} homes/sq mi: " + ", ".join(
            f"{r['decade']} {r['infill']/r['total']:.0%}" for r in infill_by_decade(t, thr)))
    print("\nStrict definition (urban a full decade before): " + ", ".join(
        f"{r['decade']} {r['infill']/1e6:.2f}M infill / {r['greenfield']/1e6:.2f}M greenfield"
        for r in infill_by_decade(t, lag=2)))
    ca = state(t, CA_FIPS)
    ca_rows = infill_by_decade(ca)
    per_k = per_1000_residents(ca_rows, CA_POPULATION)
    print(f"\nCalifornia ({len(ca['land']):,} tracts), homes built per decade (thousands)")
    for r in ca_rows:
        extra = f"  infill per 1,000 residents {per_k[r['decade']]:4.0f}" if r["decade"] in per_k and r["decade"] != "2020s" else ""
        print(f"  {r['decade']:>8}  total {r['total']/1e3:6.0f}  infill {r['infill']/1e3:6.0f}"
              f"  greenfield {r['greenfield']/1e3:6.0f}  infill share {r['infill']/r['total']:.0%}{extra}")
    for thr in SENSITIVITY_HU_PER_SQMI:
        print(f"  California infill at {thr} homes/sq mi: " + ", ".join(
            f"{r['decade']} {r['infill']/1e3:.0f}K" for r in infill_by_decade(ca, thr)))
    tot_k = per_1000_residents(ca_rows, CA_POPULATION, "total")
    print("  All homes built per 1,000 residents at the decade's start: " + ", ".join(
        f"{d} {v:.0f}" for d, v in tot_k.items() if d != "2020s"))
    ca_pph, us_pph = residents_per_home(CA_HH_POPULATION, CA_OCCUPIED), residents_per_home(US_HH_POPULATION, US_OCCUPIED)
    print("  Residents per occupied home, California / US: " + ", ".join(
        f"{y} {ca_pph[y]:.2f}/{us_pph[y]:.2f}" for y in ca_pph))
    yrs = sorted(CA_OCCUPIED)
    print("  California household residents added per occupied home added: " + ", ".join(
        f"{a}s {(CA_HH_POPULATION[b] - CA_HH_POPULATION[a]) / (CA_OCCUPIED[b] - CA_OCCUPIED[a]):.2f}"
        for a, b in zip(yrs, yrs[1:])))
    print("  California homes with more than 1 person per room: " + ", ".join(
        f"{y} {v:.1%}" for y, v in CA_CROWDED_SHARE.items()))
    print("  The 2020s column pools 2020-2024 survey responses and covers only part of the decade;"
          " its share is usable, its count is not.")

    labels, series = core_series(t)
    cores, radius = texas_cores(t)
    print(f"\nTexas cores (~{loop_area_sqmi():.0f} sq mi each; circle radius {radius:.2f} mi)")
    for c, v in series.items():
        print(f"  {c:>12} ({cores[c].sum()} tracts, {t['land'][cores[c]].sum():.0f} sq mi land): "
              + ", ".join(f"{l} {n/1e3:.1f}K" for l, n in zip(labels, v))
              + f"  | 2010s / 1990s = {v[-1]/v[labels.index('1990s')]:.1f}x")
