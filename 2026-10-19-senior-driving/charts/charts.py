"""Render this post's charts into output/ from the data/chart_*.csv files.
usage (from the post folder): python charts/charts.py [--social]"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
POST = HERE.parent
sys.path.insert(0, str(POST.parent))  # repo root, for style.py

import matplotlib.pyplot as plt
import pandas as pd
from style import BG, INK, GREY, LIGHT, COPPER, BODY, DPI, Page, font, setup_font

WATERMARK = "maxmautner.com/senior-driving"
DATA, OUT = POST / "data", POST / "output"
Z90 = 1.645
TAN = "#e3c9ad"


def chart_area(p, pad=0.35, left=0.4, right=0.4, bottom_extra=0.0):
    return p.fig.add_axes([left / p.W, (p.bottom + pad + bottom_extra) / p.H, (p.W - left - right) / p.W,
                           (p.H - p.top - p.bottom - pad - bottom_extra) / p.H])


def bare(ax):
    ax.set_facecolor(BG); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)


# ---------------------------------------------------------------- 1. crash risk per mile
def per_mile(fmt, name):
    d = pd.read_csv(DATA / "chart_crash_per_mile.csv").set_index("driver_age")
    young, old = d.loc["16-24"], d.loc["75+"]
    assert abs(old.crashes_per_100M_miles / young.crashes_per_100M_miles - 1) < 0.05, "title: as often"
    ratio = old.others_killed_per_100M_miles / young.others_killed_per_100M_miles
    assert 0.45 < ratio < 0.55, "title: half"
    assert old.drivers_killed > old.others_killed + (d.loc["75+", "fatal_crash_involvements"] * 0), "note: most deaths are the drivers"
    order = ["16-24", "25-64", "65-74", "75+"]
    moe = max(Z90 * max(d.loc[g, "crashes_se"], d.loc[g, "others_killed_se"]) for g in order)
    p = Page(fmt, "Per mile, drivers 75 and older crash as often as drivers under 25 but kill half as many others",
             "Per 100 million miles driven, by driver age, 2017",
             "",
             "Sources: NHTSA Fatality Analysis Reporting System 2017; 2017 National Household Travel Survey "
             f"({int(young.n_driver_trips):,} driver trips under 25, {int(old.n_driver_trips):,} at 75 and older). "
             "Others: people killed outside the driver's vehicle, counted for each driver in the crash. "
             f"90% margins of error are \u00b1{moe:.1f} or less. Drivers 16 to 19 alone: "
             f"{young.teen_16_19_crashes_per_100M_miles:.1f} crashes.", WATERMARK)
    k = p.k
    ax = chart_area(p, left=1.75 if fmt == "blog" else 1.6, right=0.6)
    bare(ax)
    n = len(order)
    xmax = 4.5
    names = {"16-24": "Under 25", "25-64": "25 to 64", "65-74": "65 to 74", "75+": "75 and\nolder"}
    for i, g in enumerate(order):
        r = d.loc[g]
        y = (n - 1 - i) * 2.6
        ax.text(-0.12, y + 0.45, names[g], fontsize=17 * k, color=INK, ha="right", va="center", linespacing=1.1)
        for dy, v, c, lab in [(0.9, r.crashes_per_100M_miles, TAN, "In a fatal crash"),
                              (0, r.others_killed_per_100M_miles, COPPER, "Others killed")]:
            ax.barh(y + dy, v, height=0.8, color=c, edgecolor=BG, lw=1.5)
            ax.text(v + xmax * 0.015, y + dy, f"{v:.1f}", fontsize=16 * k, color=INK, va="center")
            if i == 0:
                ax.text(xmax * 0.015, y + dy, lab, fontsize=13 * k, color=INK if c == TAN else BG, va="center")
    ax.set_xlim(0, xmax); ax.set_ylim(-0.6, (n - 1) * 2.6 + 1.5)
    p.save(OUT / name)


# ---------------------------------------------------------------- 2. years not driving
def years(fmt, name):
    d = pd.read_csv(DATA / "chart_years_not_driving.csv").set_index("sex")
    f, m = d.loc["F"], d.loc["M"]
    assert round(f.years_not_driving) == 6 and abs(m.years_not_driving - 2.5) < 0.15, "title numbers"
    p = Page(fmt, "At 65, American women can expect about 6 more years of life without driving, men about 2.5",
             "Remaining life expectancy at 65, split into expected years driving and not driving, 2017. "
             "Each bar adds to remaining life expectancy.",
             "",
             "Source: FHWA 2017 National Household Travel Survey (who drives; "
             f"{int(f.n):,} women and {int(m.n):,} men 65 and older), NCHS U.S. life tables 2017, 2020 Census "
             "(nursing-home residents, counted as not driving). Expected years from the Sullivan method: each age's share "
             "not driving times the years lived at that age. Thin lines show the 90% margin of error. Not driving: the "
             "survey's derived driver status. The smaller 2022 survey gives lower estimates, with too few non-drivers at "
             "each age to replace 2017. Foley et al. (2002) measured years after quitting, a different quantity.", WATERMARK)
    k = p.k
    ax = chart_area(p, right=0.5, pad=0.6)
    bare(ax)
    xmax = 21.5
    for i, (r, lab) in enumerate([(f, "Women"), (m, "Men")]):
        y = (1 - i) * 3.4
        ax.text(0, y + 1.05, f"{lab} ({r.life_exp:.1f} years of life left at 65)", fontsize=18 * k, color=INK, va="bottom")
        ax.barh(y, r.years_driving, height=1.5, color=LIGHT, edgecolor=LIGHT)
        ax.barh(y, r.years_not_driving, left=r.years_driving, height=1.5, color=COPPER, edgecolor=COPPER)
        e = Z90 * r.se
        ax.plot([r.years_driving - e, r.years_driving + e], [y, y], color=INK, lw=1.4, solid_capstyle="butt")
        ax.text(r.years_driving / 2, y, f"{r.years_driving:.1f} years driving", fontsize=15 * k, color=INK, va="center", ha="center")
        nd = f"{r.years_not_driving:.1f} years\nnot driving"
        if r.years_not_driving > 4:
            ax.text(r.years_driving + r.years_not_driving / 2, y, nd, fontsize=15 * k, color=BG, va="center", ha="center", linespacing=1.1)
        else:
            ax.text(r.life_exp + 0.3, y, nd, fontsize=15 * k, color=COPPER, va="center", ha="left", linespacing=1.1)
    ax.set_xlim(0, xmax); ax.set_ylim(-2.5, 5.7)
    for t in [0, 5, 10, 15, 20]:
        ax.text(t, -1.25, str(t), fontsize=13 * k, color=GREY, ha="center", va="top")
        ax.plot([t, t], [-1.05, -0.9], color=GREY, lw=1)
    ax.text(0, -1.95, "Years of life remaining at 65", fontsize=13 * k, color=GREY, va="top")
    p.save(OUT / name)


# ---------------------------------------------------------------- og image
def og_image(name):
    d = pd.read_csv(DATA / "chart_years_not_driving.csv").set_index("sex")
    fig = plt.figure(figsize=(8, 4.2), dpi=DPI, facecolor=BG)
    fig.text(0.05, 0.88, "The years\nAmericans\noutlive driving", fontproperties=font("serif", 31), color=INK, va="top", linespacing=1.15)
    fig.text(0.05, 0.4, "Older drivers mostly endanger\nthemselves. Many then live\nyears without driving.", fontsize=13.5,
             color=COPPER, va="top", linespacing=1.3)
    fig.text(0.05, 0.06, WATERMARK, fontsize=11, color=GREY, va="bottom")
    ax = fig.add_axes([0.53, 0.25, 0.43, 0.5]); bare(ax)
    for i, (s, lab) in enumerate([("F", "Women"), ("M", "Men")]):
        r = d.loc[s]; y = 1 - i
        ax.barh(y, r.years_driving, height=0.5, color=LIGHT)
        ax.barh(y, r.years_not_driving, left=r.years_driving, height=0.5, color=COPPER)
        ax.text(0, y + 0.33, lab, fontsize=12, color=INK, va="bottom")
        ax.text(r.life_exp + 0.3, y, f"~{r.years_not_driving:.0f} yrs" if s == "F" else "~2.5 yrs", fontsize=12, color=COPPER, va="center")
    ax.set_xlim(0, 24); ax.set_ylim(-0.5, 1.8)
    fig.text(0.53, 0.8, "Life after 65: years not driving", fontsize=10.5, color=GREY)
    fig.savefig(OUT / name, facecolor=BG); plt.close(fig)


CHARTS = [("per-mile", per_mile), ("years-not-driving", years)]

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
