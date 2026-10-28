"""Render this post's charts into output/ from data/ (chart_fund_balance.csv, chart1_per_resident.csv,
jobs_2023.csv).
usage (from the post folder): python charts/charts.py [--social]"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
POST = HERE.parent
sys.path.insert(0, str(POST.parent))  # repo root, for style.py

import matplotlib.pyplot as plt
import pandas as pd
from style import BG, INK, GREY, LIGHT, COPPER, BODY, DPI, Page, font, setup_font, style_axes

WATERMARK = "maxmautner.com/burlingame-vs-san-mateo"
DATA, OUT = POST / "data", POST / "output"
BLUE = "#2f6c9e"                              # San Mateo; Burlingame is COPPER (pair checked with the dataviz validator)
CITY = {"San Mateo": BLUE, "Burlingame": COPPER}
MINUS = "−"


def money(x, sign=False):
    s = f"${abs(x):,.0f}"
    return (MINUS + s) if x < 0 else (("+" + s) if sign else s)


def chart_area(p, top_gap=0.3, bottom_gap=0.85, left=1.0, right=0.4):
    return p.fig.add_axes([left / p.W, (p.bottom + bottom_gap) / p.H, (p.W - left - right) / p.W,
                           (p.H - p.top - p.bottom - top_gap - bottom_gap) / p.H])


def bare(ax):
    ax.set_facecolor(BG); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)


# ---------------------------------------------------------------- A. both cities spend down their savings
def balance(fmt, name):
    d = pd.read_csv(DATA / "chart_fund_balance.csv")
    start = d[d.fiscal_year_ending == 2025].set_index("city").per_resident_usd
    end = d[d.fiscal_year_ending == 2031].set_index("city").per_resident_usd
    assert all(1050 < start[c] < 1200 for c in CITY), "title: ~$1,100 per resident in 2025"
    assert end["San Mateo"] < 0.15 * start["San Mateo"] and end["Burlingame"] < 0, "title: spent down by 2031"
    p = Page(fmt, "San Mateo and Burlingame both forecast spending down ~$1,100 per resident of general fund "
                  "savings by 2031",
             "General fund money each city can spend, per resident. Actual through June 2025, then each city's own "
             "forecast.",
             "",
             "Sources: San Mateo and Burlingame FY2025 audited financial reports; San Mateo 2026-28 budget (June 2026); "
             "Burlingame five-year forecast (March 2026); California Department of Finance population, Jan. 1, 2025, "
             "used for every year. Money each city can spend includes rainy-day reserves; Burlingame's excludes ~$22 "
             "million in a trust that can only pay pensions. San Mateo's 2026 drop includes $25 million moved to a "
             "capital projects reserve; its forecast assumes $4-5 million a year in savings not yet identified and "
             "falls below zero in 2033. Neither includes Measure H, San Mateo's sales tax on the Nov.\u00a03\u00a0ballot.",
             WATERMARK)
    k = p.k
    ax = chart_area(p, left=1.15, right=1.55, bottom_gap=0.95, top_gap=0.45)
    style_axes(ax, k)
    ax.axvspan(2025, 2031.2, color="#efebe2", zorder=0, lw=0)
    ax.axhline(0, color=INK, lw=1.2, zorder=1)
    for c, col in CITY.items():
        s = d[d.city == c].sort_values("fiscal_year_ending")
        a = s[s.fiscal_year_ending <= 2025]
        f = s[s.fiscal_year_ending >= 2025]
        ax.plot(a.fiscal_year_ending, a.per_resident_usd, color=col, lw=3.2, solid_capstyle="round", zorder=3)
        ax.plot(f.fiscal_year_ending, f.per_resident_usd, color=col, lw=3.2, ls=(0, (2.2, 1.4)), zorder=3)
        ax.plot([2031], [end[c]], "o", color=col, ms=8 * k, mec=BG, mew=2, zorder=4)
        ax.text(2031.25, end[c] + (70 if c == "San Mateo" else -70), f"{c}\n{money(end[c])}", color=INK,
                fontsize=15 * k, va="center", linespacing=1.15)
    ax.text(2024.0, 1290, "Actual", color=GREY, fontsize=13 * k, ha="center", va="bottom")
    ax.text(2028.1, 1290, "City forecast", color=GREY, fontsize=13 * k, ha="center", va="bottom")
    ax.set_xlim(2022.8, 2031.2); ax.set_ylim(-400, 1400)
    ax.set_xticks(range(2023, 2032)); ax.set_xticklabels([str(y) for y in range(2023, 2032)])
    ax.set_yticks(range(-400, 1401, 200))
    ax.set_yticklabels([money(t) for t in range(-400, 1401, 200)])
    ax.set_xlabel("Fiscal year ending June", color=GREY, fontsize=13 * k, labelpad=10)
    ax.set_ylabel("Dollars per resident", color=GREY, fontsize=13 * k, labelpad=10)
    p.save(OUT / name)


# ---------------------------------------------------------------- C/D. revenue and spending per resident (a matched pair)
NEUTRALS = ["#cfc8b8", "#e2dccf", "#d6d0c2", "#e8e3d8", "#dcd6c9"]
WRAP = {"Parks, recreation and library": "Parks, recreation\nand library", "Capital projects and debt":
        "Capital projects\nand debt", "Administration and planning": "Administration\nand planning"}


def stacked(p, get, order, emphasis):
    """Two stacked columns (San Mateo, Burlingame) on a shared $0-3,300 scale. emphasis: {segment: fill color};
    emphasized segments get white-on-color values and their names in ink, the rest in neutral tints."""
    k = p.k
    small = k < 1                                           # social 4:5: less height for the same 6 segments
    ax = chart_area(p, left=1.15, right=0.4, bottom_gap=0.6 if small else 0.75, top_gap=0.45 if small else 0.55)
    style_axes(ax, k)
    ax.grid(False)
    neutral = iter(NEUTRALS * 2)
    shades = {s: emphasis.get(s) or next(neutral) for s in order}
    xs = {"San Mateo": 0, "Burlingame": 1}
    w = 0.42
    fs = (12 if small else 14) * k
    ymax = 3300
    per_in = ymax / ax.get_position().height / p.H          # dollars of axis per inch of page
    line = fs / 72 * 1.25 * per_in                          # one text line, in axis dollars
    names, outside, tops = [], [], {}                       # side labels: [y, text, segment]
    for c, x in xs.items():
        base = 0
        for s in order:
            h = get(c, s)
            ax.bar(x, h, bottom=base, width=w, color=shades[s], edgecolor=BG, lw=2)
            mid = base + h / 2
            if h >= 0.9 * line:  # value inside the segment
                ax.text(x, mid, money(h), color=BG if shades[s] == COPPER else INK, fontsize=fs, ha="center",
                        va="center")
            thin = h < 0.9 * line                           # too thin to hold its value: label it beside the bar
            if thin and c == "San Mateo":
                outside.append([mid, (WRAP.get(s, s) + " " if s in emphasis else "") + money(h), s])
            if c == "Burlingame":
                names.append([mid, WRAP.get(s, s) + (f" {money(h)}" if thin else ""), s])
            base += h
        tops[c] = base
        ax.text(x, base + 0.3 * line, money(base), color=INK, fontproperties=font("serif", 24 * k), ha="center",
                va="bottom")

    def spread(labels, top):
        """Keep labels centered on their segments but at least their own height apart, within [0, top]."""
        hgt = lambda t: (t.count("\n") + 1) * line * 1.05
        for i in range(1, len(labels)):
            labels[i][0] = max(labels[i][0], labels[i - 1][0] + (hgt(labels[i - 1][1]) + hgt(labels[i][1])) / 2)
        if labels and labels[-1][0] + hgt(labels[-1][1]) / 2 > top:
            labels[-1][0] = top - hgt(labels[-1][1]) / 2
            for i in range(len(labels) - 2, -1, -1):
                labels[i][0] = min(labels[i][0], labels[i + 1][0] - (hgt(labels[i + 1][1]) + hgt(labels[i][1])) / 2)
        return labels

    for y, lab, s in spread(names, tops["Burlingame"]):
        ax.text(1 + w / 2 + 0.05, y, lab, color=INK if s in emphasis else BODY, fontsize=fs, va="center",
                linespacing=1.1)
    for y, lab, s in spread(outside, tops["San Mateo"]):
        ax.text(0 + w / 2 + 0.04, y, lab, color=INK if s in emphasis else BODY, fontsize=fs, va="center")
    ax.set_xlim(-0.4, 1.9); ax.set_ylim(0, ymax)
    ax.set_xticks([0, 1]); ax.set_xticklabels(list(xs), fontsize=16 * k, color=INK)
    ax.set_yticks(range(0, 3001, 500)); ax.set_yticklabels([money(t) for t in range(0, 3001, 500)])
    ax.set_ylabel("Dollars per resident", color=GREY, fontsize=13 * k, labelpad=10)
    ax.spines["bottom"].set_visible(True); ax.spines["bottom"].set_color(GREY)


def revenue(fmt, name):
    r = pd.read_csv(DATA / "chart1_per_resident.csv")
    merge = {"Property transfer tax": "Other taxes", "Business and franchise taxes": "Other taxes"}
    r["source"] = r.source.replace(merge)
    r = r.groupby(["city", "source"], as_index=False).per_resident_usd.sum()
    get = lambda c, s: r[(r.city == c) & (r.source == s)].per_resident_usd.iloc[0]
    order = ["Property tax", "Sales tax", "Hotel tax", "Other taxes", "Charges for services", "Everything else"]
    tot = {c: get(c, "Total") for c in CITY}
    for c in CITY:
        assert abs(sum(get(c, s) for s in order) - tot[c]) < 0.1
    assert 1.70 <= tot["Burlingame"] / tot["San Mateo"] < 1.75, "title: 1.7 times"
    p = Page(fmt, f"Burlingame's general fund takes in {money(tot['Burlingame'])} per resident, 1.7x San "
                  f"Mateo's, and {money(get('Burlingame', 'Hotel tax'))} of it is hotel tax",
             "General fund revenue per resident by source, fiscal year July 2024 to June 2025. Each bar adds up to the "
             "total above it.",
             "",
             "Sources: City of San Mateo and City of Burlingame FY2025 audited financial reports (general fund); San "
             "Mateo 2026-28 and Burlingame FY2026-27 budgets for the split of other taxes; California Department of "
             "Finance population, Jan. 1, 2025. Sales tax includes each city's own quarter-cent tax (Measure S in San "
             "Mateo, Measure I in Burlingame). Other taxes: property transfer, business license and franchise taxes. "
             "Everything else: fines, permits, grants, investment income, parking and other revenue.",
             WATERMARK)
    stacked(p, get, order, {"Hotel tax": COPPER})
    p.save(OUT / name)


# ---------------------------------------------------------------- og image
def og_image(name):
    r = pd.read_csv(DATA / "chart1_per_resident.csv")
    get = lambda c, s: r[(r.city == c) & (r.source == s)].per_resident_usd.iloc[0]
    tot = {c: get(c, "Total") for c in CITY}
    assert 1.70 <= tot["Burlingame"] / tot["San Mateo"] < 1.75, "headline: 1.7 times"
    fig = plt.figure(figsize=(8, 4.2), dpi=DPI, facecolor=BG)
    fig.text(0.05, 0.88, "Burlingame\u2019s city\ngovernment collects\n1.7x as much\nrevenue per resident\nas San Mateo\u2019s",
             fontproperties=font("serif", 24), color=INK, va="top", linespacing=1.15)
    fig.text(0.05, 0.06, WATERMARK, fontsize=11, color=GREY, va="bottom")
    ax = fig.add_axes([0.56, 0.16, 0.38, 0.62]); bare(ax)
    w = 0.5
    for x, c in enumerate(("San Mateo", "Burlingame")):
        hotel = get(c, "Hotel tax")
        ax.bar(x, tot[c] - hotel, width=w, color=LIGHT, edgecolor=BG, lw=2)
        ax.bar(x, hotel, bottom=tot[c] - hotel, width=w, color=COPPER, edgecolor=BG, lw=2)
        ax.text(x, tot[c] + 60, money(tot[c]), fontproperties=font("serif", 17), color=INK, ha="center", va="bottom")
        ax.text(x, -90, c, fontsize=11, color=INK, ha="center", va="top")
    ax.text(1 + w / 2 + 0.06, tot["Burlingame"] - get("Burlingame", "Hotel tax") / 2, "Hotel\ntax", fontsize=10,
            color=INK, va="center", linespacing=1.1)
    ax.text(-0.45, 3500, "City revenue per resident, 2024-25", fontsize=10, color=GREY, va="bottom")
    ax.set_xlim(-0.45, 1.75); ax.set_ylim(-420, 3450)
    fig.savefig(OUT / name, facecolor=BG); plt.close(fig)

CHARTS = [("savings", balance), ("revenue", revenue)]

if __name__ == "__main__":
    setup_font()
    plt.rcParams["text.parse_math"] = False
    social = "--social" in sys.argv
    OUT.mkdir(exist_ok=True)
    for slug, f in CHARTS:
        f("blog", f"{slug}.png")
        if social:
            f("social", f"social-{slug}-4x5.png")
    og_image("og-image.png")
    print(f"Wrote {len(CHARTS) * (2 if social else 1) + 1} charts to {OUT}")
