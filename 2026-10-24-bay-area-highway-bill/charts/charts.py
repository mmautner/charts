"""Render this post's charts into output/ from data/ (chart_bay_area_shares.csv, bay_area_bailout_summary.csv).
usage (from the post folder): python charts/charts.py [--social]"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
POST = HERE.parent
sys.path.insert(0, str(POST.parent))  # repo root, for style.py

import matplotlib.pyplot as plt
import pandas as pd
from style import BG, INK, GREY, LIGHT, COPPER, BODY, DPI, Page, font, setup_font

WATERMARK = "maxmautner.com/bay-area-highway-bill"
DATA, OUT = POST / "data", POST / "output"
TAN = "#e3c9ad"


def chart_area(p, top_gap=0.3, bottom_gap=0.85, left=1.0, right=0.4):
    return p.fig.add_axes([left / p.W, (p.bottom + bottom_gap) / p.H, (p.W - left - right) / p.W,
                           (p.H - p.top - p.bottom - top_gap - bottom_gap) / p.H])


def bare(ax):
    ax.set_facecolor(BG); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)


# ---------------------------------------------------------------- B. Bay Area: highway bailout share vs. the transit tax
def bay_area(fmt, name):
    m = pd.read_csv(DATA / "bay_area_bailout_summary.csv").set_index("item")
    get = lambda key: m.loc[[i for i in m.index if i.startswith(key)][0]]
    tax = get("Transit sales tax on the Nov 3 ballot, per year")
    lo = get("Bay Area share of projected highway-account gap, avg FY2028-36, low")
    hi = get("Bay Area share of projected highway-account gap, avg FY2028-36, high")
    past = get("Bay Area share of highway-account bailouts")
    assert 1.25 <= lo.billions < 1.35 and lo.billions > tax.billions, "title: ~$1.3B, more than the tax"
    assert past.billions > 10 * tax.billions, "note: more than 10 years of the tax"
    p = Page(fmt, f"The Bay Area will pay ~${lo.billions:.1f} billion a year to bail out America\u2019s highways, "
                  f"more than the ${tax.billions * 1000:.0f} million its Nov.\u00a03 transit tax would\u00a0raise",
             "The gas tax hasn\u2019t covered the federal highway fund\u2019s costs since 2008. Congress fills the gap "
             "with general tax money, mostly income taxes, and the Bay Area pays 5% of those with 2% of the people.",
             "",
             "Sources: CBO Highway Trust Fund baseline (June 2026); IRS county income tax data 2011-2023; CRS R48845; "
             "Public Transit Revenue Measure District impartial analysis (Aug. 2026). Bay Area: Alameda, Contra Costa, "
             "San Francisco, San Mateo and Santa Clara counties. Highway bailout: the Bay Area\u2019s share of the "
             "highway account\u2019s projected yearly shortfall in 2028-2036, by its 2022-2023 share of federal income "
             f"tax (5.1%, the lowest since 2018; at 6.1% it would be ${hi.billions:.1f} billion). The gas tax here means "
             "all federal fuel and truck taxes. The bailouts have mostly been borrowed, so this is the Bay Area\u2019s "
             "share of the taxes that repay them.", WATERMARK)
    k = p.k
    ax = chart_area(p, left=0.4, right=0.4, bottom_gap=0.3, top_gap=0.15)
    bare(ax)
    ax.set_xlim(0, 1.75); ax.set_ylim(-1.0, 3.2)
    fs = 16 * k
    h = 1.0
    for y, lab, v, txt, col in (
            (2.0, "Bay Area\u2019s share of the yearly highway bailout", lo.billions, f"${lo.billions:.2f} billion",
             COPPER),
            (0.35, "Nov. 3 transit sales tax, raised per year", tax.billions, f"${tax.billions * 1000:.0f} million",
             LIGHT)):
        ax.text(0, y + h / 2 + 0.12, lab, fontsize=fs, color=INK, va="bottom")
        ax.barh(y, v, height=h, color=col, edgecolor=BG)
        ax.text(v + 0.03, y, txt, fontsize=fs + 2 * k, color=INK, va="center")
    note = (f"Since 2008 the Bay Area has already put ~${past.billions:.0f} billion into highway bailouts, "
            "more than 10 years of the transit tax.")
    from style import wrap, font as _f
    ax.text(0, -0.55, wrap(note, _f("sans", 15 * k), p.W - 0.8), fontsize=15 * k, color=BODY, va="center",
            linespacing=1.3)
    p.save(OUT / name)


# ---------------------------------------------------------------- C. who pays: gas tax vs income tax
def shares(fmt, name):
    d = pd.read_csv(DATA / "chart_bay_area_shares.csv").set_index("measure")
    drive = d.loc["Share of U.S. vehicle-miles driven, 2024", "share"]
    tax = d.loc["Share of federal income tax, 2023", "share"]
    pop = d.loc["Share of U.S. population, 2025", "share"]
    assert 3.9 < tax / drive < 4.3
    p = Page(fmt, f"The Bay Area does {drive * 100:.1f}% of America\u2019s driving but pays {tax * 100:.1f}% of the "
                  f"income taxes now bailing out America\u2019s\u00a0highways",
             "The 5 counties voting on the Nov. 3 transit tax.",
             "",
             "Sources: Caltrans California Public Road Data 2024 (daily vehicle-miles by county); FHWA Highway "
             "Statistics 2024 VM-2; IRS county income tax data 2023 (total tax liability); Census 2025 estimates. "
             "Counties: Alameda, Contra Costa, San Francisco, San Mateo, Santa Clara. Driving: vehicle-miles on the "
             "counties' roads, including visitors and freight. Federal gas taxes are charged per gallon, so a "
             "county's share tracks its driving. General federal revenue, which has covered the highway fund's "
             "shortfalls since 2008, comes mostly from income taxes. The income tax share was 5.1-6.1% in 2018-2023.",
             WATERMARK)
    k = p.k
    ax = chart_area(p, left=0.4, right=0.4, bottom_gap=0.3, top_gap=0.2)
    bare(ax)
    ax.set_xlim(0, 0.068); ax.set_ylim(-0.6, 3.6)
    fs = 16 * k
    rows = [(2.75, "Share of America\u2019s driving", "and so of the gas tax", drive, TAN),
            (1.4, "Share of America\u2019s people", "for comparison", pop, LIGHT),
            (0.05, "Share of America\u2019s income taxes", "and so of the highway bailouts", tax, COPPER)]
    for y, lab, sub, v, col in rows:
        ax.text(0, y + 0.36, sub, fontsize=fs * 0.85, color=GREY, va="bottom")
        ax.text(0, y + 0.62, lab, fontsize=fs, color=INK, va="bottom")
        ax.barh(y, v, height=0.6, color=col, edgecolor=BG)
        ax.text(v + 0.0008, y, f"{v * 100:.1f}%", fontsize=fs + 2 * k, color=INK, va="center")
    p.save(OUT / name)


# ---------------------------------------------------------------- og image
def og_image(name):
    m = pd.read_csv(DATA / "bay_area_bailout_summary.csv").set_index("item")
    get = lambda key: m.loc[[i for i in m.index if i.startswith(key)][0], "billions"]
    lo = get("Bay Area share of projected highway-account gap, avg FY2028-36, low")
    tax = get("Transit sales tax on the Nov 3 ballot, per year")
    fig = plt.figure(figsize=(8, 4.2), dpi=DPI, facecolor=BG)
    fig.text(0.05, 0.88, "The Bay Area will pay\nmore to bail out\nAmerica\u2019s highways\nthan to keep its own\ntrains and buses running",
             fontproperties=font("serif", 24), color=INK, va="top", linespacing=1.15)
    fig.text(0.05, 0.06, WATERMARK, fontsize=11, color=GREY, va="bottom")
    ax = fig.add_axes([0.6, 0.2, 0.36, 0.6]); bare(ax)
    for y, lab, v, txt, col in ((1, "Its share of highway bailouts", lo, f"${lo:.2f}B", COPPER),
                                (0, "Its Nov. 3 transit tax", tax, f"${tax * 1000:.0f}M", LIGHT)):
        ax.barh(y, v, height=0.45, color=col)
        ax.text(0, y + 0.3, lab, fontsize=12, color=INK, va="bottom")
        ax.text(v + 0.03, y, txt, fontsize=14, color=INK, va="center")
    ax.text(0, -0.55, "Per year", fontsize=10.5, color=GREY, va="center")
    ax.set_xlim(0, 1.75); ax.set_ylim(-0.75, 1.75)
    fig.savefig(OUT / name, facecolor=BG); plt.close(fig)


CHARTS = [("bay-area-bailout", bay_area), ("who-pays", shares)]

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
