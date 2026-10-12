"""Fetch the 2022 NHTS trip file and summarize driver trips by distance.

Writes data/nhts2022_short_trips.csv and data/nhts2022_meta.json. To reuse a copy
already on disk: python fetch_nhts.py --dir path/to/unzipped/csv
"""
import argparse, csv, io, json, urllib.request, zipfile, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
URL = "https://nhts.ornl.gov/assets/2022/download/csv.zip"
CAR_MODES = {"01", "02", "03", "04"}   # TRPTRANS: car, SUV, van, pickup
CUT = 8.0                              # "short trip" upper bound, miles

def rows(src):
    if src:
        yield from csv.DictReader(open(Path(src) / "tripv2pub.csv", newline=""))
        return
    with urllib.request.urlopen(URL) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    yield from csv.DictReader(io.TextIOWrapper(z.open("tripv2pub.csv"), newline=""))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dir"); a = ap.parse_args()
    bins = {"short": [0.0, 0.0, 0.0, 0], "all": [0.0, 0.0, 0.0, 0]}   # miles*w, minutes*w, w, n
    for r in rows(a.dir):
        if r["TRPTRANS"] not in CAR_MODES or r["DRVR_FLG"] != "01":
            continue
        try:
            mi, mn, w = float(r["TRPMILES"]), float(r["TRVLCMIN"]), float(r["WTTRDFIN"])
        except ValueError:
            continue
        if mi <= 0 or mn <= 0 or w <= 0:
            continue
        for k in (["short", "all"] if mi <= CUT else ["all"]):
            b = bins[k]; b[0] += mi * w; b[1] += mn * w; b[2] += w; b[3] += 1
    out = HERE / "data"; out.mkdir(exist_ok=True)
    with open(out / "nhts2022_short_trips.csv", "w", newline="") as f:
        wr = csv.writer(f); wr.writerow(["trips", "mph", "mean_miles", "share_of_driver_miles", "n"])
        for k, (m, t, w, n) in bins.items():
            wr.writerow([k, round(m / t * 60, 2), round(m / w, 3), round(m / bins["all"][0], 3), n])
    (out / "nhts2022_meta.json").write_text(json.dumps({
        "source": URL, "file": "tripv2pub.csv",
        "fetched_on": datetime.date.today().isoformat(),
        "definition": f"Driver trips (DRVR_FLG=01) by car, SUV, van or pickup; short = TRPMILES <= {CUT}. "
                      "Speed = sum(miles*WTTRDFIN) / sum(TRVLCMIN*WTTRDFIN). TRVLCMIN is self-reported.",
    }, indent=2))
    print(open(out / "nhts2022_short_trips.csv").read())

if __name__ == "__main__":
    main()
