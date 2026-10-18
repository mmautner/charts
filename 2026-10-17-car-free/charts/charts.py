"""Render this post's charts into output/ from the data/chart_*.csv files."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
POST = HERE.parent
sys.path.insert(0, str(POST.parent))  # repo root, for style.py

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from style import BG, INK, GREY, LIGHT, COPPER, BODY, DPI, Page, font, setup_font, style_axes

WATERMARK = "maxmautner.com/sf-car-free"
DATA, OUT = POST / "data", POST / "output"
TAN = "#e3c9ad"     # light copper, for the earlier period
Z90 = 1.645         # 90% interval, the ACS convention
SRC = "Source: U.S. Census Bureau, American Community Survey PUMS,\n"
BAY = "households in the 9 Bay Area counties."


def chart_area(p, pad=0.35, left=0.4, right=0.4, bottom_extra=0.0):
    return p.fig.add_axes([left / p.W, (p.bottom + pad + bottom_extra) / p.H, (p.W - left - right) / p.W,
                           (p.H - p.top - p.bottom - pad - bottom_extra) / p.H])


def split(p, n, gap=0.35, top_extra=0.0, **kw):
    """n stacked axes filling the chart area, top first."""
    full = chart_area(p, **kw); x0, y0, w, h = full.get_position().bounds; full.remove()
    h -= top_extra / p.H
    g = gap / p.H
    each = (h - g * (n - 1)) / n
    return [p.fig.add_axes([x0, y0 + (n - 1 - i) * (each + g), w, each]) for i in range(n)]


def bare(ax):
    ax.set_facecolor(BG); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)


def pct(v, d=0):
    return f"{100 * v:.{d}f}%"


def paired_bars(ax, k, groups, a, b, labels_ab, colors_ab, xmax, fmt, err_a=None, err_b=None, label_group=0):
    """For each group: a caption line, then bar a and bar b, values at the bar ends."""
    bare(ax)
    n = len(groups)
    for i, g in enumerate(groups):
        y = (n - 1 - i) * 3.0
        ax.text(0, y + 1.55, g, fontsize=17 * k, color=INK, va="bottom")
        for dy, vals, errs, c, lab in [(0.9, a, err_a, colors_ab[0], labels_ab[0]), (0, b, err_b, colors_ab[1], labels_ab[1])]:
            v = vals[i]
            ax.barh(y + dy, v, height=0.78, color=c, edgecolor=COPPER if c == TAN else c, lw=1)
            end = v
            if errs is not None:
                e = errs[i]
                ax.plot([v - e, v + e], [y + dy] * 2, color=GREY if c != INK else BODY, lw=1.4, solid_capstyle="butt")
                end = v + e
            ax.text(end + xmax * 0.015, y + dy, fmt(v), fontsize=16 * k, color=INK, va="center")
            if i == label_group:
                ax.text(xmax * 0.012, y + dy, lab, fontsize=12.5 * k, color=INK if c == TAN else BG, va="center")
    ax.set_xlim(0, xmax); ax.set_ylim(-0.6, (n - 1) * 3.0 + 2.4)


# ---------------------------------------------------------------- 1. stage mix
def stage_mix(fmt, name):
    d = pd.read_csv(DATA / "chart_stage_mix.csv")
    bay = d[d.scope == "Bay Area"]
    rest = d[d.scope == "Rest of Bay"]
    order = ["Seniors", "Young adults", "Midlife, no kids", "Families"]
    cf = [bay[(bay.stage == s) & (bay.carfree == 1)].est.item() for s in order]
    car = [bay[(bay.stage == s) & (bay.carfree == 0)].est.item() for s in order]
    n_cf = int(bay.n_cf.max())
    rest_sen = rest[(rest.stage == "Seniors") & (rest.carfree == 1)].est.item()
    assert cf[0] == max(cf), "title says seniors are the largest group"
    p = Page(fmt, f"{pct(cf[0])} of Bay Area car-free households are headed by someone 65+",
             "How car-free households and households with a car divide by life stage, 2020-24. Each color adds to 100%.",
             f"Outside San Francisco, {pct(rest_sen)} of car-free households are headed by someone 65+.",
             SRC + "2020-24 5-year sample, " + BAY + f" {n_cf:,} car-free sample households. Families have someone "
             "under 18; young adults are householders under 35.", WATERMARK)
    ax = chart_area(p, right=0.9)
    labels = ["Seniors (householder 65+)", "Young adults (under 35, no kids)", "Midlife (35-64, no kids)", "Families with kids"]
    paired_bars(ax, p.k, labels, cf, car, ["Car-free households", "Households with a car"], [COPPER, INK], 0.45, pct)
    p.save(OUT / name)


# ---------------------------------------------------------------- 2. income profile
INC = ["<25k", "25-50k", "50-75k", "75-100k", "100-150k", "150-200k", "200-300k", "300k+"]
INC_TICK = ["<25", "25-\n50", "50-\n75", "75-\n100", "100-\n150", "150-\n200", "200-\n300", "300+"]


def band_line(ax, k, x, est, se, color, label, at, ha="center"):
    """Line with a shaded 90% band and a direct label placed at data point `at` (x, y),
    chosen by hand to sit in clear space off the line."""
    ax.fill_between(x, est - Z90 * se, est + Z90 * se, color=color, alpha=0.16 if color != INK else 0.1, lw=0)
    ax.plot(x, est, color=color, lw=2.4, marker="o", ms=6, mec=BG, mew=1.5, zorder=3)
    ax.text(*at, label, color=INK, fontsize=15 * k, va="center", ha=ha, zorder=4)


def income_profile(fmt, name):
    d = pd.read_csv(DATA / "chart_income_profile.csv")
    s = lambda series, cf=None: d[(d.series == series) & ((d.carfree == cf) if cf is not None else True)].set_index("inc_band").loc[INC]
    sen, yng = s("Seniors"), s("Young adults")
    dcf, dcar = s("Disability", 1.0), s("Disability", 0.0)
    x = np.arange(len(INC))
    p = Page(fmt, "Lower-income car-free households are older and more often disabled",
             "Bay Area households by household income, 2020-24",
             "At $150k+, car-free households and households with a car report mobility disabilities at the same rate (outside San Francisco, ~4 points apart).",
             SRC + "2020-24 5-year sample, " + BAY + " Shading shows the 90% margin of error. Disability: difficulty walking or "
             f"climbing stairs, or living independently. Smallest cell: {int(dcf.n_cf.min())} car-free sample households.", WATERMARK)
    k = p.k
    top, bot = split(p, 2, gap=0.8, left=0.95, right=0.45, bottom_extra=0.75, top_extra=0.45)
    for ax, title in [(top, "Share of car-free households headed by:"), (bot, "Share of households with an adult who has a mobility disability")]:
        style_axes(ax, k)
        ax.set_xticks(x); ax.set_xticklabels(INC_TICK if ax is bot else [""] * len(x), fontsize=12.5 * k, linespacing=1.0)
        ax.set_ylim(0, 0.62); ax.set_yticks([0, 0.2, 0.4, 0.6]); ax.set_yticklabels(["0%", "20%", "40%", "60%"])
        ax.set_xlim(-0.35, len(x) - 0.65)
        ax.text(-0.35, 0.66, title, transform=ax.transData, fontsize=16 * k, color=INK, va="bottom")
    bot.set_xlabel("Household income ($\u00a0thousands)", fontsize=13 * k, color=GREY, labelpad=8)
    band_line(top, k, x, sen.est.values, sen.se.values, COPPER, "A senior (65+)", (5.6, 0.035))
    band_line(top, k, x, yng.est.values, yng.se.values, INK, "A young adult (under 35)", (6, 0.5))
    band_line(bot, k, x, dcf.est.values, dcf.se.values, COPPER, "Car-free households", (1.15, 0.45), ha="left")
    band_line(bot, k, x, dcar.est.values, dcar.se.values, INK, "Households with a car", (2, 0.09))
    p.save(OUT / name)


# ---------------------------------------------------------------- 3. income shift
def income_shift(fmt, name):
    d = pd.read_csv(DATA / "chart_income_shift.csv")
    order = ["Under $50k", "$50-100k", "$100k+"]
    g = lambda per: d[d.period == per].set_index("inc3").loc[order]
    a, b = g("2015-19"), g("2020-24")
    up = b.est["$100k+"] - a.est["$100k+"]
    up_se = np.hypot(a.se["$100k+"], b.se["$100k+"])
    lo = b.est["Under $50k"] - a.est["Under $50k"]
    lo_se = np.hypot(a.se["Under $50k"], b.se["Under $50k"])
    p = Page(fmt, f"Outside San Francisco, ~{round(up, -2):,.0f} more car-free households earn $100k+ than in 2015-19",
             "Number of car-free households in the other 8 Bay Area counties, by household income (2024 dollars)",
             f"Those earning under $50k fell by\u00a0~{-round(lo, -2):,.0f}.",
             SRC + "2015-19 and 2020-24 5-year samples, housing-unit households, incomes in 2024 dollars (CPI-U). "
             f"Thin lines show the 90% margin of error. Changes: $100k+ +{round(up, -2):,.0f} (±{round(Z90 * up_se, -2):,.0f}), "
             f"under $50k \u2212{-round(lo, -2):,.0f} (±{round(Z90 * lo_se, -2):,.0f}). Car-free sample households: "
             f"{int(a.n_cf.sum()):,} (2015-19), {int(b.n_cf.sum()):,} (2020-24).", WATERMARK)
    ax = chart_area(p, right=0.9)
    paired_bars(ax, p.k, order, a.est.values, b.est.values, ["2015-19", "2020-24"], [TAN, COPPER], 115000,
                lambda v: f"~{v / 1000:.0f}k", err_a=Z90 * a.se.values, err_b=Z90 * b.se.values)
    p.save(OUT / name)


# ---------------------------------------------------------------- 4. commute swap
def commute(fmt, name):
    d = pd.read_csv(DATA / "chart_commute.csv")
    modes = ["Transit", "Work from home", "Car", "Walk", "Bike"]
    # the 4:5 crop has no room for a 2-line label; its footer explains the car category
    mode_lab = {"Car": "Car (as a passenger\nor work vehicle)"} if fmt == "blog" else {}
    other = 1 - d.groupby(["region", "period"]).est.sum()
    p = Page(fmt, "Workers in car-free households moved from transit to working from home",
             "How workers in car-free households get to work, 2015-19 vs. 2020-24",
             "Outside San Francisco, the share commuting by car went from "
             + "{:.0%} to {:.0%}.".format(*[d[(d.region == "Rest of Bay") & (d["mode"] == "Car") & (d.period == per)].est.item()
                                            for per in ("2015-19", "2020-24")]),
             SRC + "2015-19 and 2020-24 5-year samples, workers 16+ in car-free " + BAY
             + " Car includes riding as a passenger; the survey can't separate it from driving a work vehicle. "
             f"Taxi, motorcycle and other modes ({pct(other.min())}-{pct(other.max())}) not shown. "
             f"Sample workers: {int(d.n.min()):,}-{int(d.n.max()):,} per region and period.", WATERMARK)
    k = p.k
    axes = split(p, 2, gap=0.55, left=2.75, right=0.55, top_extra=0.2 if fmt == "social" else 0.0)
    for ax, region, title in [(axes[0], "Rest of Bay", "Other 8 Bay Area counties"), (axes[1], "SF", "San Francisco")]:
        bare(ax)
        r = d[d.region == region]
        for i, m in enumerate(modes):
            y = len(modes) - 1 - i
            v0 = r[(r["mode"] == m) & (r.period == "2015-19")].est.item()
            v1 = r[(r["mode"] == m) & (r.period == "2020-24")].est.item()
            ax.plot([0, 0.6], [y, y], color=LIGHT, lw=1, zorder=0)
            ax.annotate("", xy=(v1, y), xytext=(v0, y), arrowprops=dict(arrowstyle="-", color=GREY, lw=2), zorder=1)
            ax.scatter([v0], [y], s=95, color=BG, edgecolor=INK, lw=1.8, zorder=2)
            ax.scatter([v1], [y], s=110, color=COPPER, edgecolor=BG, lw=1.5, zorder=3)
            lo, hi = sorted([v0, v1])
            near = hi - lo < 0.05
            ax.text(lo - 0.015, y, pct(v0 if v0 <= v1 else v1), ha="right", va="center", fontsize=13.5 * k,
                    color=BODY if v0 <= v1 else COPPER)
            ax.text(hi + 0.015, y, pct(v1 if v0 <= v1 else v0), ha="left", va="center", fontsize=13.5 * k,
                    color=COPPER if v0 <= v1 else BODY)
            ax.text(-0.04, y, mode_lab.get(m, m), ha="right", va="center", fontsize=15 * k,
                    color=INK, linespacing=1.1, transform=ax.get_yaxis_transform())
        ax.text(-(2.75 - 0.4) / (ax.get_position().width * p.W), len(modes) - 0.25, title, ha="left", va="bottom",
                fontsize=17 * k, color=INK, transform=ax.get_yaxis_transform())
        ax.set_xlim(-0.05, 0.6); ax.set_ylim(-0.6, len(modes) - 0.1)
    ax = axes[0]
    ly = len(modes) - 0.05
    ax.scatter([0.30], [ly], s=95, color=BG, edgecolor=INK, lw=1.8, clip_on=False)
    ax.text(0.32, ly, "2015-19", va="center", fontsize=13.5 * k, color=BODY)
    ax.scatter([0.45], [ly], s=110, color=COPPER, edgecolor=BG, lw=1.5, clip_on=False)
    ax.text(0.47, ly, "2020-24", va="center", fontsize=13.5 * k, color=COPPER)
    p.save(OUT / name)


# ---------------------------------------------------------------- 5. 12-year trend
def trend(fmt, name):
    d = pd.read_csv(DATA / "chart_trend.csv")
    bay, sf = d[d.region == "Bay Area"].set_index("year"), d[d.region == "SF"].set_index("year")
    assert round(bay.est[2024], 2) == round(bay.est[2012], 2) == 0.10, "title says 1 in 10 in both years"
    p = Page(fmt, "1 in 10 Bay Area households has no car, the same share as in 2012",
             "Share of households with no car, by year",
             f"San Francisco's share fell to ~{pct(sf.est[[2021, 2022]].mean())} in 2021 and 2022 "
             f"and was {pct(sf.est[2024])} in 2024.",
             SRC + "1-year samples 2012-2024, " + BAY + " No standard 1-year release for 2020. Shading shows the 90% margin of error. "
             + f"Car-free sample households per year: {int(d[d.region == 'SF'].n_cf.min())}-{int(d[d.region == 'SF'].n_cf.max()):,} (SF), "
             f"{int(d[d.region == 'Rest of Bay'].n_cf.min()):,}-{int(d[d.region == 'Rest of Bay'].n_cf.max()):,} (rest).", WATERMARK)
    k = p.k
    ax = chart_area(p, pad=0.7, left=0.95, right=1.95)
    style_axes(ax, k)
    for region, color, lab in [("SF", COPPER, "San Francisco"), ("Rest of Bay", GREY, "Other 8 counties"), ("Bay Area", INK, "All 9 counties")]:
        r = d[d.region == region].sort_values("year")
        for seg in (r[r.year <= 2019], r[r.year >= 2021]):
            ax.fill_between(seg.year, seg.est - Z90 * seg.se, seg.est + Z90 * seg.se, color=color, alpha=0.16, lw=0)
            ax.plot(seg.year, seg.est, color=color, lw=3.4 if region == "Bay Area" else 2.0)
        last = r.iloc[-1]
        nudge = {"Bay Area": 0.022, "Rest of Bay": -0.02}.get(region, 0)
        ax.text(2024.35, last.est + nudge, f"{lab}\n{pct(last.est)}", color=INK, fontsize=14 * k, va="center", linespacing=1.15)
    ax.text(2020, 0.17, "no 2020\nrelease", ha="center", fontsize=12 * k, color=GREY, va="center")
    ax.set_ylim(0, 0.4); ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4]); ax.set_yticklabels(["0%", "10%", "20%", "30%", "40%"])
    ax.set_xlim(2011.6, 2024.3); ax.set_xticks([2012, 2015, 2018, 2021, 2024])
    p.save(OUT / name)


# ---------------------------------------------------------------- og image
def og_image(name):
    d = pd.read_csv(DATA / "chart_income_profile.csv")
    s = lambda series: d[d.series == series].set_index("inc_band").loc[INC]
    sen, yng = s("Seniors"), s("Young adults")
    fig = plt.figure(figsize=(8, 4.2), dpi=DPI, facecolor=BG)
    fig.text(0.05, 0.88, "Who lives without\na car in the\nBay Area", fontproperties=font("serif", 31), color=INK, va="top", linespacing=1.15)
    fig.text(0.05, 0.36, "The poorest car-free households\nare mostly seniors. The richest\nskew young.",
             fontsize=13.5, color=COPPER, va="top", linespacing=1.3)
    fig.text(0.05, 0.06, WATERMARK, fontsize=11, color=GREY, va="bottom")
    ax = fig.add_axes([0.56, 0.2, 0.4, 0.62]); style_axes(ax, 0.75)
    x = np.arange(len(INC))
    ax.plot(x, sen.est, color=COPPER, lw=2.6); ax.plot(x, yng.est, color=INK, lw=2.6)
    ax.text(0.2, sen.est.iloc[0] + 0.06, "Seniors", fontsize=12, color=INK)
    ax.text(4.6, yng.est.iloc[-1] + 0.05, "Young adults", fontsize=12, color=INK)
    ax.set_ylim(0, 0.62); ax.set_yticks([0, 0.2, 0.4, 0.6]); ax.set_yticklabels(["0%", "20%", "40%", "60%"])
    ax.set_xticks([0, 7]); ax.set_xticklabels(["<$25k", "$300k+"])
    ax.text(-0.3, 0.7, "Share of car-free households, by income", fontsize=10.5, color=GREY, transform=ax.transData)
    fig.savefig(OUT / name, facecolor=BG); plt.close(fig)


CHARTS = [("trend", trend), ("stage-mix", stage_mix), ("income-profile", income_profile),
          ("income-shift", income_shift), ("commute", commute)]

if __name__ == "__main__":
    setup_font()
    plt.rcParams["text.parse_math"] = False   # dollar signs are dollars
    OUT.mkdir(exist_ok=True)
    social = "--social" in sys.argv
    for slug, f in CHARTS:
        f("blog", f"{slug}.png")
        if social:
            f("social", f"social-{slug}-4x5.png")
    og_image("og-image.png")
    print(f"Wrote {len(CHARTS) * (2 if social else 1) + 1} charts to {OUT}")
