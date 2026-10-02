"""Load the fetched permit series and print every number the charts use,
next to HCD's own published figures."""
import csv, json
from pathlib import Path
from inputs import HCD_PUBLISHED_ADU_PERMITS, HCD_PUBLISHED_ADU_SHARE

HERE = Path(__file__).resolve().parent
YEARS = list(range(2018, 2026))   # APR Table A2 starts in 2018

def is_adu(cat):
    return "ADU" in cat.upper()   # covers ADU and JADU spellings

def load_hcd():
    path = HERE / "data" / "hcd_a2_summary.csv"
    if not path.exists():
        raise SystemExit("data/hcd_a2_summary.csv is missing. Run fetch_hcd.py first.")
    adu, total, adu_co, mf5, sfd = {}, {}, {}, {}, {}
    for r in csv.DictReader(open(path)):
        try:
            y = int(r["year"])
        except ValueError:
            continue
        bp, co = int(r["bp_units"]), int(r["co_units"])
        total[y] = total.get(y, 0) + bp
        if r["unit_cat"].strip() == "SFD":
            sfd[y] = sfd.get(y, 0) + bp
        if r["unit_cat"].strip() == "5+":
            mf5[y] = mf5.get(y, 0) + bp
        if is_adu(r["unit_cat"]):
            adu[y] = adu.get(y, 0) + bp
            adu_co[y] = adu_co.get(y, 0) + co
    return adu, total, adu_co, mf5, sfd

def load_census():
    path = HERE / "data" / "census_bps_ca.json"
    if not path.exists():
        raise SystemExit("data/census_bps_ca.json is missing. Run fetch_census.py first.")
    return {int(y): v for y, v in json.loads(path.read_text())["years"].items()}

if __name__ == "__main__":
    adu, total, adu_co, mf5, sfd = load_hcd()
    bps = load_census()   # printed only as a cross-check; the charts use APR data alone
    print("year  ADU permits  ADU COs  APR 5+ units  ADUs per 5+ unit  all APR permits  ADU share  Census 5+ units  HCD published")
    for y in YEARS:
        if y not in adu:
            continue
        pub = HCD_PUBLISHED_ADU_PERMITS.get(y)
        print(f"{y}  {adu[y]:>11,}  {adu_co.get(y,0):>7,}  {mf5[y]:>12,}  {adu[y]/mf5[y]:>16.2f}  {total[y]:>15,}  {adu[y]/total[y]:>8.1%}"
              f"  {bps[y]['5plus_units']:>15,}  {'' if pub is None else f'{pub:,}'}")
    for y, pub in HCD_PUBLISHED_ADU_PERMITS.items():
        if y in adu:
            print(f"{y}: fetched {adu[y]:,} vs HCD published {pub:,} ({adu[y]/pub - 1:+.0%})")
    ys = [y for y in YEARS if y in adu]
    for y in ys:
        print(f"{y}: {adu[y]:,} ADUs vs {sfd[y]:,} detached houses (ratio {adu[y]/sfd[y]:.2f})")
    print(f"2018 and 2019: {adu[2018]+adu[2019]:,} ADU permits, {adu_co[2018]+adu_co[2019]:,} ADU completions")
    print(f"{ys[0]} to {ys[-1]}: {sum(adu[y] for y in ys):,} ADU permits, {sum(adu_co[y] for y in ys):,} ADU completions")
