"""Cross-source QA: for 2019 (last year before COVID, and the last year WDI covers for most countries)
and for each country's latest year, compare every source's freight ton-km and passenger-km and flag
gaps over 10%. Writes data/qa_sources.csv.

Usage: python -I model/qa.py data
"""
import sys
from pathlib import Path
import pandas as pd

FREIGHT = ["freight_tkm", "freight_tkm_viz"]
PAX = ["pkm_mainline", "pkm_all_rail", "pkm_reported"]


def main(data):
    data = Path(data)
    o = pd.read_csv(data / "source_observations.csv")
    o["label"] = o["source"].str.split(",").str[0].str.slice(0, 40) + " [" + o["measure"] + "]"
    rows = []
    for iso, g in o.groupby("iso"):
        latest = g[g.measure.isin(FREIGHT + PAX)].year.max()
        for year in sorted({2019, min(latest, 2024)}):
            for kind, ms in (("freight", FREIGHT), ("passenger", PAX)):
                s = g[(g.year == year) & g.measure.isin(ms)]
                if s.empty:
                    continue
                ref = s[s.measure == ms[0]]
                # reference: the value the dataset uses (first measure of the group, chosen source)
                for _, r in s.iterrows():
                    rows.append(dict(country=r.country, year=year, kind=kind, source=r.label, value_mil=round(r.value)))
    q = pd.DataFrame(rows)
    out = []
    for (c, y, k), g in q.groupby(["country", "year", "kind"]):
        lo, hi = g.value_mil.min(), g.value_mil.max()
        spread = hi / lo - 1 if lo else float("nan")
        for _, r in g.iterrows():
            out.append(dict(r, min_mil=lo, max_mil=hi, spread=round(spread, 3), flag="gap>10%" if spread > 0.10 else ""))
    q = pd.DataFrame(out)
    q.to_csv(data / "qa_sources.csv", index=False)
    pd.set_option("display.width", 200, "display.max_rows", 500, "display.max_colwidth", 60)
    flagged = q[q.flag != ""]
    print("Country-year-kind cells where sources differ by more than 10% (max/min - 1):\n")
    for (c, y, k), g in flagged.groupby(["country", "year", "kind"]):
        print(f"{c} {y} {k}: spread {g.spread.iloc[0]:.0%}")
        for _, r in g.sort_values("value_mil").iterrows():
            print(f"    {r.value_mil:>12,.0f}  {r.source}")
    ok = q[q.flag == ""].groupby(["country", "year", "kind"]).size()
    print(f"\n{len(ok)} cells agree within 10%; {flagged.groupby(['country','year','kind']).ngroups} cells differ by more.")


if __name__ == "__main__":
    main(sys.argv[1])
