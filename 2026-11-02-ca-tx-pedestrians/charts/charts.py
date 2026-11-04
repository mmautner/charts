"""Render this post's charts into output/ from data/ (ca_tx_pedestrian_rates.csv, acs_walk_commute.csv).
usage (from the post folder): python charts/charts.py [--social]"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
POST = HERE.parent
sys.path.insert(0, str(POST.parent))  # repo root, for style.py

import matplotlib.pyplot as plt
import pandas as pd
from style import BG, INK, GREY, LIGHT, COPPER, BODY, DPI, Page, font, setup_font, style_axes, text_block

WATERMARK = "maxmautner.com/walking-deaths"
DATA, OUT = POST / "data", POST / "output"
NEUTRAL = "#cfc8b8"
YEAR = 2023                            # latest final FARS year

rates = pd.read_csv(DATA / "ca_tx_pedestrian_rates.csv", dtype={"year": str})


def val(geo, year, measure):
    r = rates[(rates.geo == geo) & (rates.year == str(year)) & (rates.measure == measure)]
    assert len(r) == 1, (geo, year, measure)
    return float(r.value.iloc[0])


def pct(a, b):
    return round(100 * (a / b - 1))


def hbars(ax, k, labels, values, colors, fmt, xmax, xlabel, ticks, tickfmt, fs=17):
    """Horizontal bars, top to bottom in the given order, values labeled at the bar ends."""
    style_axes(ax, k)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=LIGHT, lw=1)
    ys = list(range(len(labels)))[::-1]
    ax.barh(ys, values, color=colors, height=0.62, zorder=2)
    for y, v, c in zip(ys, values, colors):
        ax.text(v + xmax * 0.015, y, fmt(v), va="center", ha="left", color=INK, zorder=3,
                bbox=dict(fc=BG, ec="none", pad=2),
                fontproperties=font("serif", 22 * k) if c == COPPER else font("sans", fs * k))
    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=fs * k, color=INK)
    ax.set_xlim(0, xmax)
    ax.set_xticks(ticks)
    ax.set_xticklabels([tickfmt(t) for t in ticks])
    ax.set_xlabel(xlabel, color=GREY, fontsize=13 * k, labelpad=10)


# ---------------------------------------------------------------- 1. deaths and traffic since 2010
START, LA = 2010, "California excl. Los Angeles metro"
SPAN = range(START, YEAR + 1)


def change(series, a=START, b=YEAR):
    return 100 * (series[b] / series[a] - 1)


def trend_numbers():
    deaths = {y: val("California", y, "pedestrian_deaths") for y in SPAN}
    traffic = {y: val("California", y, "vmt_per_resident") for y in SPAN}
    n = dict(deaths=round(change(deaths)), traffic=round(change(traffic)))
    assert (n["deaths"], n["traffic"]) == (91, -7), n
    # footer claims, checked against the data
    rate = {y: val("California", y, "deaths_per_100k_residents") for y in SPAN}
    avg = lambda d, ys: sum(d[y] for y in ys) / len(ys)
    n["rate"] = round(change(rate))
    n["avg"] = round(100 * (avg(deaths, range(2021, 2024)) / avg(deaths, range(2010, 2013)) - 1))
    n["no_la"] = round(100 * (val(LA, YEAR, "deaths_per_100k_residents") / val(LA, START, "deaths_per_100k_residents") - 1))
    n["tx_traffic"] = round(100 * (val("Texas", YEAR, "vmt_per_resident") / val("Texas", START, "vmt_per_resident") - 1))
    n["tx_rate"] = round(100 * (val("Texas", YEAR, "deaths_per_100k_residents") / val("Texas", START, "deaths_per_100k_residents") - 1))
    n["prelim"] = int(val("California", 2024, "pedestrian_deaths"))
    assert (n["rate"], n["avg"], n["no_la"], n["tx_traffic"], n["tx_rate"]) == (82, 88, 94, 5, 89), n
    return deaths, traffic, n


def signed(v):
    return f"+{v:.0f}%" if v > 0 else (f"\u2212{-v:.0f}%" if v < 0 else "0%")


def trend(fmt, name):
    deaths, traffic, n = trend_numbers()
    p = Page(fmt, f"Since {START}, California\u2019s roads carry {-n['traffic']}% less traffic per resident and kill "
                  f"{n['deaths']}% more people on\u00a0foot",
             f"Change since {START} in the number of people killed while walking in California each year, and in "
             f"miles driven on California roads per resident.",
             "",
             f"Sources: NHTSA Fatality Analysis Reporting System, final files {START}-{YEAR} (people killed while walking "
             f"or using a wheelchair, which NHTSA counts as pedestrians, in the state where the crash happened); FHWA "
             f"Highway Statistics, table VM-2; Census Bureau population estimates. Miles driven include trucks and "
             f"visitors. Per resident, the death rate rose {n['rate']}%. Comparing {START}-{START + 2} with "
             f"{YEAR - 2}-{YEAR} averages, deaths rose {n['avg']}%. Without Los Angeles and Orange counties, the death "
             f"rate per resident rose {n['no_la']}%. Preliminary {YEAR + 1} data show {n['prelim']:,} deaths. In Texas, "
             f"miles driven per resident rose {n['tx_traffic']}% and the death rate per resident rose {n['tx_rate']}%. "
             f"California deaths: {deaths[START]:,.0f} in {START}, {deaths[YEAR]:,.0f} in {YEAR}; miles driven per "
             f"resident: {traffic[START]:,.0f} and {traffic[YEAR]:,.0f}.",
             WATERMARK)
    k = p.k
    left, right, bottom_gap = 0.95 * k + 0.4, 0.45, 0.85
    ax = p.fig.add_axes([left / p.W, (p.bottom + bottom_gap) / p.H, (p.W - left - right) / p.W,
                         (p.H - p.top - p.bottom - bottom_gap - 0.35) / p.H])
    style_axes(ax, k)
    xs = list(SPAN)
    d = [change(deaths, START, y) for y in xs]
    t = [change(traffic, START, y) for y in xs]
    ax.axhline(0, color=GREY, lw=1.2, zorder=1)
    ax.plot(xs, t, color=NEUTRAL, lw=3.2, solid_capstyle="round", zorder=2)
    ax.plot(xs, d, color=COPPER, lw=3.6, solid_capstyle="round", zorder=3)
    for ys, c in [(d, COPPER), (t, NEUTRAL)]:
        ax.plot([YEAR], [ys[-1]], "o", color=c, ms=9 * k, mec=BG, mew=2, zorder=4)
    ax.text(YEAR + 0.35, d[-1], signed(d[-1]), fontproperties=font("serif", 24 * k), color=INK, va="center")
    ax.text(YEAR + 0.35, t[-1], signed(t[-1]), fontproperties=font("serif", 24 * k), color=INK, va="center")
    # labels sit next to their own lines, in the line's color; the background box keeps gridlines out of the text
    box = dict(fc=BG, ec="none", pad=2)
    ax.text(2014.7, 50, "People killed\nwhile walking", color=COPPER, fontsize=17 * k, ha="right", va="center",
            linespacing=1.15, bbox=box, zorder=1.5)
    ax.text(START + 0.2, -5, "Miles driven per resident", color=GREY, fontsize=17 * k, ha="left", va="top",
            bbox=box, zorder=1.5)
    ax.set_xlim(START - 0.4, YEAR + 1.9)
    ax.set_xticks([2010, 2013, 2016, 2019, 2023])
    ax.set_ylim(-52, 110)
    ticks = range(-20, 101, 20)
    ax.set_yticks(ticks)
    ax.set_yticklabels([signed(v) for v in ticks])
    ax.set_xlabel("Year", color=GREY, fontsize=13 * k, labelpad=10)
    ax.set_ylabel(f"Change since {START}", color=GREY, fontsize=13 * k, labelpad=8)
    p.save(OUT / name)


# ---------------------------------------------------------------- 2. driving and walking, California vs. Texas
acs = pd.read_csv(DATA / "acs_walk_commute.csv")
STATES = [("California", COPPER), ("Texas", GREY)]
ACS_N2010 = {"California": "470,000", "Texas": "315,000"}   # B00001 unweighted persons, 2010 (raw/census/acs_series)


def walk_share(st):
    r = acs[(acs.geo == st) & (acs.measure == "walk_share_of_commuters") & acs.year.between(START, YEAR)]
    return r.set_index("year")


def drive_walk(fmt, name):
    drive = {st: {y: val(st, y, "vmt_per_resident") for y in SPAN} for st, _ in STATES}
    walk = {st: walk_share(st) for st, _ in STATES}
    gap = {y: round(100 * (drive["Texas"][y] / drive["California"][y] - 1)) for y in (START, YEAR)}
    assert gap == {START: 7, YEAR: 21}, gap
    ratio = {y: walk["California"].value[y] / walk["Texas"].value[y] for y in (START, YEAR)}
    assert (round(ratio[START], 1), round(ratio[YEAR], 1)) == (1.6, 1.8), ratio
    for st, _ in STATES:   # walking "barely changed": end points within about 0.2 points of each other
        w = walk[st].value
        assert abs(w[YEAR] - w[START]) < 0.002, (st, w[START], w[YEAR])
    p = Page(fmt, f"Texas\u2019s lead over California in driving per resident grew from {gap[START]}% to "
                  f"{gap[YEAR]}% since {START}. Walking to work held steady in\u00a0both.",
             "Miles driven on each state\u2019s roads per resident, and the share of commuters who walk to work. "
             "Shading shows the 90% margin of error.",
             "",
             f"Sources: FHWA Highway Statistics, table VM-2 (all vehicle miles, including trucks and visitors); Census "
             f"Bureau population estimates; American Community Survey 1-year, table B08301 (about "
             f"{ACS_N2010['California']} people sampled in California and {ACS_N2010['Texas']} in Texas in {START}). "
             f"Commuters leave out people who work from home. No standard 2020 survey.",
             WATERMARK)
    k = p.k
    left, right = 1.0 * k + 0.4, 1.0 * k + 0.2
    gap_in, top_gap, bottom_gap = 0.85 + 0.15 * (k == 1), 0.45, 0.85
    h = (p.H - p.top - p.bottom - top_gap - bottom_gap - gap_in) / 2
    w = (p.W - left - right) / p.W
    ax1 = p.fig.add_axes([left / p.W, (p.bottom + bottom_gap + h + gap_in) / p.H, w, h / p.H])
    ax2 = p.fig.add_axes([left / p.W, (p.bottom + bottom_gap) / p.H, w, h / p.H])
    xs = list(SPAN)
    for ax in (ax1, ax2):
        style_axes(ax, k)
        ax.set_xlim(START - 0.3, YEAR + 0.3)
        ax.set_xticks([2010, 2013, 2016, 2019, 2023])
    def ends(ax, items, min_pts=22):
        """End-of-line value labels, nudged apart so they never overlap (min_pts between centers)."""
        to_pts = lambda y: ax.transData.transform((0, y))[1] * 72 / DPI
        from_pts = lambda q: ax.transData.inverted().transform((0, q * DPI / 72))[1]
        items = sorted(items)
        ys = [to_pts(y) for y, _ in items]
        need = min_pts * k
        if len(ys) == 2 and ys[1] - ys[0] < need:
            mid = (ys[0] + ys[1]) / 2
            ys = [mid - need / 2, mid + need / 2]
        for q, (_, txt) in zip(ys, items):
            ax.text(YEAR + 0.5, from_pts(q), txt, color=INK, fontproperties=font("serif", 19 * k), va="center", ha="left")
    end1, end2 = [], []
    name_at = lambda ax, y, st, c, up: ax.annotate(st, (START + 0.1, y), xytext=(0, 9 if up else -9), textcoords="offset points",
                                                   color=c if c == COPPER else BODY, fontsize=16 * k, ha="left",
                                                   va="bottom" if up else "top", fontweight="bold")
    for st, c in STATES:
        ys = [drive[st][y] for y in xs]
        ax1.plot(xs, ys, color=c, lw=3.4 if c == COPPER else 3.0, solid_capstyle="round", zorder=3)
        ax1.plot([YEAR], [ys[-1]], "o", color=c, ms=8 * k, mec=BG, mew=2, zorder=4)
        end1.append((ys[-1], f"{ys[-1]:,.0f}"))
        name_at(ax1, ys[0], st, c, up=(st == "Texas"))
        wv = walk[st]
        for seg in (wv[wv.index <= 2019], wv[wv.index >= 2021]):
            ax2.fill_between(seg.index, 100 * (seg.value - seg.moe90), 100 * (seg.value + seg.moe90), color=c, alpha=0.18, lw=0, zorder=2)
            ax2.plot(seg.index, 100 * seg.value, color=c, lw=3.4 if c == COPPER else 3.0, solid_capstyle="round", zorder=3)
        ax2.plot([YEAR], [100 * wv.value[YEAR]], "o", color=c, ms=8 * k, mec=BG, mew=2, zorder=4)
        end2.append((100 * wv.value[YEAR], f"{100 * wv.value[YEAR]:.1f}%"))
        name_at(ax2, 100 * wv.value[START], st, c, up=(st == "California"))
    ax1.set_ylim(0, 12800)
    ax1.set_yticks(range(0, 10001, 2500))
    ax1.set_yticklabels([f"{t:,}" for t in range(0, 10001, 2500)])
    ax1.set_ylabel("Miles per resident", color=GREY, fontsize=13 * k, labelpad=8)
    ax2.set_ylim(0, 4.0)
    ax2.set_yticks([0, 1, 2, 3])
    ax2.set_yticklabels(["0%", "1%", "2%", "3%"])
    ax2.set_ylabel("Share of commuters", color=GREY, fontsize=13 * k, labelpad=8)
    ends(ax1, end1)
    ends(ax2, end2)
    ax2.set_xlabel("Year", color=GREY, fontsize=13 * k, labelpad=10)
    ax2.text(2020, 0.2, "No 2020\nsurvey", color=GREY, fontsize=12 * k, ha="center", va="bottom", linespacing=1.1)
    for ax, head in [(ax1, "Miles driven per resident"), (ax2, "Commuters who walk to work")]:
        ax.text(0, 1.06, head, transform=ax.transAxes, color=INK, fontproperties=font("sans", 17 * k),
                va="bottom", fontweight="bold")
    p.save(OUT / name)


# ---------------------------------------------------------------- og image
def og_image(name):
    deaths, traffic, n = trend_numbers()
    fig = plt.figure(figsize=(8, 4.2), dpi=DPI, facecolor=BG)
    text_block(fig, 0.05, 0.86, f"Since {START}, California\u2019s\nroads carry {-n['traffic']}% less\ntraffic per resident and\n"
               f"kill {n['deaths']}% more people\non foot.", font("serif", 25), INK, linespacing=1.15)
    fig.text(0.05, 0.06, WATERMARK, fontsize=11, color=GREY, va="bottom")
    ax = fig.add_axes([0.58, 0.16, 0.30, 0.62])
    style_axes(ax, 0.75)
    xs = list(SPAN)
    d = [change(deaths, START, y) for y in xs]
    t = [change(traffic, START, y) for y in xs]
    ax.axhline(0, color=GREY, lw=1, zorder=1)
    ax.plot(xs, t, color=NEUTRAL, lw=2.6, solid_capstyle="round", zorder=2)
    ax.plot(xs, d, color=COPPER, lw=3, solid_capstyle="round", zorder=3)
    for ys, c in [(d, COPPER), (t, NEUTRAL)]:
        ax.plot([YEAR], [ys[-1]], "o", color=c, ms=7, mec=BG, mew=1.5, zorder=4)
        ax.text(YEAR + 0.6, ys[-1], signed(ys[-1]), fontproperties=font("serif", 17), color=INK, va="center")
    ax.text(START, 104, "People killed\nwhile walking", fontsize=9.5, color=INK, va="top", linespacing=1.25)
    ax.text(START, -14, "Miles driven\nper resident", fontsize=9.5, color=BODY, va="top", linespacing=1.25)
    ax.set_xlim(START - 0.3, YEAR + 0.3); ax.set_ylim(-40, 110)
    ax.set_xticks([START, YEAR]); ax.set_yticks([0]); ax.set_yticklabels(["0%"])
    ax.tick_params(labelsize=10)
    ax.text(START - 0.3, 116, f"Change since {START}", fontsize=10, color=GREY, va="bottom")
    fig.savefig(OUT / name, facecolor=BG); plt.close(fig)


CHARTS = [("deaths-and-traffic", trend), ("driving-and-walking", drive_walk)]

if __name__ == "__main__":
    setup_font()
    plt.rcParams["text.parse_math"] = False
    OUT.mkdir(exist_ok=True)
    for name, fn in CHARTS:
        fn("blog", f"{name}.png")
        if "--social" in sys.argv:
            fn("social", f"social-{name}-4x5.png")
    og_image("og-image.png")
    print("wrote", sorted(q.name for q in OUT.glob("*.png")))
