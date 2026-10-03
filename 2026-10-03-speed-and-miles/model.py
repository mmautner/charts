"""The arithmetic behind every chart. Run it on its own to print every number."""
import csv, json
from pathlib import Path
from inputs import *

HERE = Path(__file__).resolve().parent

# NHTS groups by the home county's metro size (MSASIZE), matched to NCHS categories.
GROUPS = ["MSA 1M+", "MSA under 1M", "Not in MSA"]
LABELS = {"MSA 1M+": "Big metros (1M+)", "MSA under 1M": "Smaller metros", "Not in MSA": "Rural counties"}

def load_nhts():
    path = HERE / "data" / "nhts2017_estimates.csv"
    if not path.exists():
        raise SystemExit("data/nhts2017_estimates.csv is missing. Run fetch_nhts.py first.")
    return {(r["item"], r["group"]): (float(r["estimate"]), float(r["moe"]) if r["moe"] else None)
            for r in csv.DictReader(open(path))}

def fetched_on():
    return json.loads((HERE / "data" / "nhts2017_meta.json").read_text())["fetched_on"]

# Chart 1: drop in fatal crashes from driving 5 mph slower, by road type (power model),
# against the drop from driving 5% fewer miles (crashes proportional to miles).
def fatal_drop(v0, v1, exponent):
    return 1 - (v1 / v0) ** exponent

def speed_rows():
    return [(label, v0, v1, fatal_drop(v0, v1, e)) for label, v0, v1, e in SPEED_CASES]

def extra_minutes(v0, v1, miles=EXAMPLE_TRIP_MILES):
    return 60 * miles * (1 / v1 - 1 / v0)

# Chart 2: deaths per resident (NCHS, by home county) = miles per resident (NHTS)
# x deaths per mile (derived). Big metros combine large central and large fringe
# rates, weighted by population share, because NHTS cannot split them.
def big_metro_death_rate():
    c, f = POP_SHARE_PCT["large_central_metro"], POP_SHARE_PCT["large_fringe_metro"]
    r = MVT_DEATHS_PER_100K_2017
    return (r["large_central_metro"] * c + r["large_fringe_metro"] * f) / (c + f)

def death_rates():
    r = MVT_DEATHS_PER_100K_2017
    return {"MSA 1M+": big_metro_death_rate(), "MSA under 1M": r["small_metro"], "Not in MSA": r["rural"]}

MILES_ITEM = "2a_miles_per_person_all_hh"   # counts every household member, like the death rates

def exposure_rows(nhts, item=MILES_ITEM):
    """(group, miles per resident, deaths per 100k, deaths per 100M miles)."""
    d = death_rates()
    return [(g, nhts[(item, g)][0], d[g], d[g] * 1e-5 / nhts[(item, g)][0] * 1e8) for g in GROUPS]

# Chart 3: travel-day driving per licensed driver.
def driving_rows(nhts):
    """(group, minutes/day, miles/day, mph)."""
    return [(g, nhts[("3_minutes_per_driver_day", g)][0], nhts[("3_miles_per_driver_day", g)][0],
             nhts[("3_mph_pairs", g)][0]) for g in GROUPS]

if __name__ == "__main__":
    print("Chart 1: fatal crashes, 5 mph slower")
    for label, v0, v1, drop in speed_rows():
        print(f"  {label}: -{drop:.1%}   ({extra_minutes(v0, v1):.1f} extra min per {EXAMPLE_TRIP_MILES} mi)")
    print(f"  Drive {MILES_CUT:.0%} fewer miles: -{MILES_CUT:.0%}")

    nhts = load_nhts()
    print(f"\nChart 2: by home county, 2017 (big-metro death rate {big_metro_death_rate():.2f} per 100k)")
    for item in [MILES_ITEM, "2c_miles_per_person_wtperfin", "2b_diary_vmt_per_person"]:
        rows = {g: (m, d, h) for g, m, d, h in exposure_rows(nhts, item)}
        (mb, db, hb), (mr, dr, hr) = rows["MSA 1M+"], rows["Not in MSA"]
        tag = "  (charted)" if item == MILES_ITEM else ""
        print(f"  {item}{tag}")
        for g in GROUPS:
            m, d, h = rows[g]
            print(f"    {LABELS[g]:<18} {m:>7,.0f} mi/resident  {d:>5.2f} deaths/100k  {h:.3f} deaths/100M mi")
        print(f"    rural vs big metro: +{mr/mb - 1:.1%} miles, {dr/db:.2f}x deaths, {hr/hb:.2f}x deaths per mile")

    print("\nChart 3: per licensed driver per day, 2017")
    for g, mins, mi, mph in driving_rows(nhts):
        print(f"  {LABELS[g]:<18} {mins:.1f} min  {mi:.2f} mi  {mph:.1f} mph")
    rows = {g: r for g, *r in driving_rows(nhts)}
    print(f"  rural vs big metro: {rows['Not in MSA'][1] / rows['MSA 1M+'][1] - 1:+.1%} miles, "
          f"{rows['Not in MSA'][0] / rows['MSA 1M+'][0] - 1:+.1%} minutes")
