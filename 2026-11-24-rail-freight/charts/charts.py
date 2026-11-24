"""Candidate charts for the rail freight vs. passenger post, rendered from data/rail_freight_passenger.csv.
usage (from the post folder): python charts/charts.py [--social]
Writes output/<name>.png (and output/social-<name>-4x5.png with --social)."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
POST = HERE.parent
sys.path.insert(0, str(POST.parent))  # repo root, for style.py

import numpy as np
import pandas as pd
import matplotlib.ticker as mt
from style import BG, INK, GREY, LIGHT, COPPER, BODY, Page, font, setup_font, style_axes

WATERMARK = "maxmautner.com/rail-freight"
DATA, OUT = POST / "data", POST / "output"
NEUTRAL, DARK = "#cfc8b8", "#6f6a62"
d = pd.read_csv(DATA / "rail_freight_passenger.csv")
# data/ keeps the sources' metric units; the charts show US units for a US audience. After this,
# "freight_tkm" holds millions of short ton-miles and every pkm_* column millions of passenger-miles.
TKM_PER_TON_MILE, KM_PER_MILE = 1.45997, 1.609344
d["freight_tkm"] = d["freight_tkm"] / TKM_PER_TON_MILE
for _c in ("pkm_mainline", "pkm_all_rail", "pkm_reported"):
    d[_c] = d[_c] / KM_PER_MILE

NAME = {"USA": "United States", "DEU": "Germany", "JPN": "Japan", "FRA": "France", "GBR": "Britain",
        "CHN": "China", "RUS": "Russia", "IND": "India", "CAN": "Canada", "AUS": "Australia",
        "CHE": "Switzerland", "NLD": "Netherlands", "KOR": "South Korea", "ITA": "Italy", "ESP": "Spain"}
HEADLINE = {"USA", "JPN", "DEU"}
YEAR = 2024
YEAR_OVERRIDE = {   # (iso, column): year, where 2024 is missing or distorted
    ("JPN", "pkm_mainline"): 2023,                                     # operator split only for FY2019 and FY2023
    ("RUS", "pkm_reported"): 2019, ("IND", "pkm_reported"): 2019,      # World Bank ends 2021, COVID-distorted
    ("KOR", "pkm_reported"): 2023,
}


def cell(iso, col):
    """(year, freight tkm, pkm, population) for one country and passenger column, or None."""
    y = YEAR_OVERRIDE.get((iso, col), YEAR)
    r = d[(d.iso3 == iso) & (d.year == y)]
    if r.empty or pd.isna(r[col].iloc[0]) or pd.isna(r.freight_tkm.iloc[0]):
        return None
    r = r.iloc[0]
    pop = r.population if pd.notna(r.population) else d[(d.iso3 == iso) & d.population.notna()].sort_values("year").population.iloc[-1]
    return int(y), r.freight_tkm, r[col], pop


def snapshot(defn):
    """One row per country. defn 'mainline' or 'all_rail'; falls back to the next definition, flagged."""
    order = {"mainline": ["pkm_mainline", "pkm_reported"], "all_rail": ["pkm_all_rail", "pkm_mainline", "pkm_reported"]}[defn]
    rows = []
    for iso in NAME:
        for col in order:
            c = cell(iso, col)
            if c:
                y, f, p, pop = c
                rows.append(dict(iso=iso, col=col, exact=(col == order[0]), year=y, freight=f, pax=p, pop=pop,
                                 ratio=f / p, f_pc=f * 1e6 / (pop * 1e6), p_pc=p * 1e6 / (pop * 1e6)))
                break
    return pd.DataFrame(rows)


SHORT_SOURCES = "Sources: national statistics agencies, Eurostat, ITF/OECD, World Bank; full list and method at the post's source link."


def src(fmt):
    return SHORT_SOURCES if fmt == "social" else SOURCES


def ratio_label(r):
    return f"{r:,.0f}" if r >= 10 else (f"{r:.1f}" if r >= 0.95 else f"1/{1 / r:,.0f}")


DEFN_TEXT = {
    "mainline": "Intercity, regional and commuter trains; subways, light rail and trams aren't counted.",
    "all_rail": "All trains, including subways, light rail and trams.",
}
SOURCES = ("Sources: US Census Historical Statistics and Statistical Abstract, BTS National Transportation Statistics, "
           "STB R-1 reports; MLIT (Japan); "
           "Verkehr in Zahlen, Destatis, Eurostat (Germany, Italy, Spain, Netherlands, Switzerland); SDES (France); "
           "ORR and DfT (Britain); NBS (China); ITF/OECD and World Bank (Canada, Australia, South Korea, Russia, India).")


# ---------------------------------------------------------------- 1. ratio bars
def chart_ratio_bars(fmt, defn):
    s = snapshot(defn).sort_values("ratio", ascending=True)
    dropped = s[~s.exact] if fmt == "social" else s.iloc[0:0]
    if defn == "all_rail" or fmt == "social":   # social: only countries with a verified definition, to fit
        s = s[s.exact]
    us, jp = s.set_index("iso").loc["USA"], s.set_index("iso").loc["JPN"]
    title = (f"US railroads move {us.ratio:,.0f} times as much freight as passengers. "
             f"Japan's move {1 / jp.ratio:,.0f} times as many passengers as freight.")
    sub = ("Freight ton-miles divided by passenger-miles, latest year. Bars right of the line carry more freight than passengers. "
           + DEFN_TEXT[defn])
    omitted = (" Not shown, for lack of a comparable passenger count: " + ", ".join(NAME[i] for i in dropped.iso) + ".") if len(dropped) else ""
    fallback = s[~s.exact]
    note = "Only countries whose statistics count subways, light rail and trams." if defn == "all_rail" else ""
    if len(fallback):
        note = ("Grey bars use a broader or less certain passenger count where this definition isn't available: "
                + ", ".join(NAME[i] for i in fallback.iso) + ".")
    years = ", ".join(f"{NAME[i]} {y}" for i, y in zip(s.iso, s.year) if y != YEAR)
    footer = (f"Year {YEAR} unless noted: {years}. Japan and Britain use April-March fiscal years. "
              "US freight is Class I railroads' revenue ton-miles (tons of 2,000 lb)."
              + (" Canada's passenger figure covers VIA Rail only, not commuter rail." if "CAN" in set(s.iso) else "") + omitted + " " + src(fmt))
    pg = Page(fmt, title, sub, note, footer, WATERMARK)
    k = pg.k
    ax = pg.fig.add_axes([0.24, pg.bottom / pg.H + 0.075, 0.68, 1 - (pg.top + pg.bottom) / pg.H - 0.095])
    style_axes(ax, k)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=LIGHT, lw=1)
    ys = np.arange(len(s))
    colors = [COPPER if i == "USA" else (DARK if (i in HEADLINE and e) else (NEUTRAL if e else LIGHT))
              for i, e in zip(s.iso, s.exact)]
    ax.set_xscale("log")
    lo = 0.02
    ax.barh(ys, [r - lo for r in s.ratio], left=lo, color=colors, height=0.66, zorder=2)
    ax.axvline(1, color=INK, lw=1.2, zorder=3)
    ax.text(1, len(s) - 0.2, " equal", color=INK, fontsize=12 * k, va="bottom", ha="left")
    for y, r, i in zip(ys, s.ratio, s.iso):
        ax.text(r * 1.12, y, ratio_label(r), va="center", ha="left", color=INK,
                fontproperties=font("serif", 19 * k) if i in HEADLINE else font("sans", 13 * k))
    ax.set_yticks(ys)
    ax.set_yticklabels([NAME[i] for i in s.iso], fontsize=14 * k, color=INK)
    ax.set_xlim(lo, 1500)
    ticks = [0.02, 0.1, 1, 10, 100, 1000]
    ax.set_xticks(ticks)
    ax.xaxis.set_minor_locator(mt.NullLocator())
    ax.set_xticklabels(["1/50", "1/10", "1", "10", "100", "1,000"])
    ax.set_xlabel("Freight ton-miles per passenger-mile (log scale)", color=GREY, fontsize=13 * k, labelpad=10)
    return pg


# ---------------------------------------------------------------- 2. per-capita scatter
OFFSET = {  # label placement (dx, dy in points); dx 0 centers the label
    "USA": (10, -4), "JPN": (10, 0), "DEU": (12, 4), "FRA": (10, 2), "GBR": (-10, 9), "CHN": (10, -8),
    "RUS": (-10, 8), "IND": (10, -6), "CAN": (10, -6), "AUS": (10, 6), "CHE": (10, 4), "NLD": (0, -16),
    "KOR": (-10, 0), "ITA": (6, 14), "ESP": (-10, -9)}
OFFSET["NLD"] = (0, -20); OFFSET["IND"] = (10, -6)
# Italy and the Netherlands nearly coincide, so their labels sit below the cluster with a thin leader line
OFFSET.update({"ESP": (-10, 0), "CHE": (0, 13)})
CLUSTER = {"blog": {"ITA": (22, -32), "NLD": (-4, -30)}, "social": {"ITA": (5, -34), "NLD": (-4, -22), "GBR": (0, 12)}}
LEADER = {"ITA", "NLD"}


def chart_scatter(fmt, defn):
    s = snapshot(defn)
    S = s.set_index("iso")
    us, jp = S.loc["USA"], S.loc["JPN"]
    title = (f"Per person, Americans ride trains 1/{jp.p_pc / us.p_pc:,.0f} as much as the Japanese, "
             f"while US railroads haul {us.f_pc / jp.f_pc:,.0f} times as much freight")
    sub = ("Rail freight ton-miles and passenger-miles per resident, latest year. "
           "Countries above the line move more passengers than freight. " + DEFN_TEXT[defn])
    fallback = s[~s.exact]
    note = ""
    if len(fallback):
        note = "Hollow dots use a broader or less certain passenger count: " + ", ".join(NAME[i] for i in fallback.iso) + "."
    years = ", ".join(f"{NAME[i]} {y}" for i, y in zip(s.iso, s.year) if y != YEAR)
    footer = (f"Year {YEAR} unless noted: {years}. Population: World Bank (2024 used for 2025 rows); "
              "Britain's rail figures cover Great Britain, divided by UK population. " + src(fmt))
    pg = Page(fmt, title, sub, note, footer, WATERMARK)
    k = pg.k
    ax = pg.fig.add_axes([0.14, pg.bottom / pg.H + 0.075, 0.8, 1 - (pg.top + pg.bottom) / pg.H - 0.095])
    style_axes(ax, k)
    ax.grid(axis="x", color=LIGHT, lw=1)
    ax.set_xscale("log"); ax.set_yscale("log")
    lim = (20, 40000)
    ax.set_xlim(*lim); ax.set_ylim(20, 6000)
    ax.plot(lim, lim, color=INK, lw=1, zorder=1)
    ax.text(50, 33, "equal freight and passengers", rotation=0, color=GREY, fontsize=11 * k, ha="left", va="bottom")
    for _, r in s.iterrows():
        c = COPPER if r.iso == "USA" else (DARK if r.iso in HEADLINE else "#9b9488")
        ax.scatter(r.f_pc, r.p_pc, s=(110 if r.iso in HEADLINE else 60) * k, zorder=3,
                   facecolor=c if r.exact else BG, edgecolor=c, linewidth=1.8, )
        dx, dy = CLUSTER[fmt].get(r.iso, OFFSET.get(r.iso, (8, 0)))
        leader = dict(arrowstyle="-", color=GREY, lw=0.8, shrinkA=2, shrinkB=5) if r.iso in LEADER else None
        ax.annotate(NAME[r.iso], (r.f_pc, r.p_pc), xytext=(dx, dy), textcoords="offset points", arrowprops=leader,
                    ha="left" if dx > 0 else ("right" if dx < 0 else "center"), va="center", color=INK,
                    fontproperties=font("serif", 18 * k) if r.iso in HEADLINE else font("sans", 12.5 * k), zorder=4)
    fmt_n = mt.FuncFormatter(lambda v, _: f"{v:,.0f}")
    for a in (ax.xaxis, ax.yaxis):
        a.set_major_formatter(fmt_n); a.set_minor_locator(mt.NullLocator())
    ax.set_xticks([30, 100, 300, 1000, 3000, 10000, 30000])
    ax.set_yticks([30, 100, 300, 1000, 3000])
    ax.set_xlabel("Freight ton-miles per resident per year (log scale)", color=GREY, fontsize=13 * k, labelpad=10)
    ax.set_ylabel("Passenger-miles per resident per year (log scale)", color=GREY, fontsize=13 * k, labelpad=10)
    return pg


# ---------------------------------------------------------------- 3. ratio over time
SERIES = {  # iso: (passenger column, label)
    "USA": "pkm_mainline", "JPN": "pkm_all_rail", "DEU": "pkm_mainline", "FRA": "pkm_mainline",
    "GBR": "pkm_mainline", "CHN": "pkm_mainline"}
EVENTS = [("USA", 1958, "US Transportation Act", 8.5), ("USA", 1971, "Amtrak starts", 40), ("USA", 1980, "Staggers Act", 20),
          ("JPN", 1964, "Shinkansen opens", 0.38), ("JPN", 1987, "JNR breakup", 0.027), ("DEU", 1994, "Bahnreform", 0.16)]


def series(iso, col):
    g = d[(d.iso3 == iso) & d[col].notna() & d.freight_tkm.notna()].sort_values("year")
    return g.year.values, (g.freight_tkm / g[col]).values


def chart_time(fmt):
    yu, ru = series("USA", "pkm_mainline")
    r1920, r1970 = ru[list(yu).index(1920)], ru[list(yu).index(1970)]
    after = min(r for y, r in zip(yu, ru) if y > 1970)
    assert after > r1970 - 1, after
    title = (f"In 1920, US railroads hauled {r1920:.0f} ton-miles of freight for every passenger-mile. "
             f"By 1970 it was {r1970:.0f}, and it has stayed above that ever since.")
    sub = ("Freight ton-miles divided by passenger-miles, each year. "
           "Intercity, regional and commuter trains (Japan also counts subways and trams).")
    note = ""
    footer = ("US passenger counts exist only every 5 years from 1970 to 1990 (dots joined by lines). The 2020-2022 spikes are "
              "COVID-era drops in passengers. "
              "Germany is West Germany through 1990 (decade points only), unified Germany after; breaks in 1996 and 2016 "
              "where the source changes. Britain and Japan use April-March fiscal years. " + src(fmt))
    pg = Page(fmt, title, sub, note, footer, WATERMARK)
    k = pg.k
    ax = pg.fig.add_axes([0.11, pg.bottom / pg.H + 0.075, 0.70, 1 - (pg.top + pg.bottom) / pg.H - 0.095])
    style_axes(ax, k)
    ax.set_yscale("log")
    ax.set_xlim(1915, 2026); ax.set_ylim(0.02, 400)
    ax.axhline(1, color=INK, lw=1)
    last = {}
    for iso, col in SERIES.items():
        y, r = series(iso, col)
        c = COPPER if iso == "USA" else (DARK if iso in HEADLINE else "#a59e92")
        lw = 2.6 if iso == "USA" else (2.0 if iso in HEADLINE else 1.5)
        # break the line where consecutive points are more than 5 years apart
        seg = np.split(np.arange(len(y)), np.where(np.diff(y) > 5)[0] + 1)
        for idx in seg:
            ax.plot(y[idx], r[idx], color=c, lw=lw, zorder=3, marker="o" if len(idx) == 1 else None, ms=4)
        if iso == "USA":   # 5-yearly passenger counts 1970-1990
            m = (y >= 1970) & (y <= 1990)
            ax.plot(y[m], r[m], ls="none", marker="o", ms=4.5, color=c, zorder=4)
        if iso == "DEU":   # decade points for West Germany
            m = y <= 1990
            ax.plot(y[m], r[m], color=c, lw=1, ls=":", marker="o", ms=4, zorder=3)
        last[iso] = (y[-1], r[-1])
    nudge = {"FRA": 1.18, "GBR": 0.85}
    for iso, (x, v) in last.items():
        ax.text(x + 1, v * nudge.get(iso, 1), NAME[iso], va="center", ha="left", color=INK,
                fontproperties=font("serif", 17 * k) if iso in HEADLINE else font("sans", 12.5 * k))
    for iso, year, label, yy in EVENTS:
        ax.axvline(year, color=LIGHT, lw=1, zorder=1)
        ax.text(year + 0.6, yy, f"{label} ({year})", ha="left", va="center", color=GREY, fontsize=10.5 * k,
                bbox=dict(fc=BG, ec="none", pad=1), zorder=2)
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: ratio_label(v)))
    ax.yaxis.set_minor_formatter(mt.NullFormatter())
    ax.set_yticks([0.02, 0.1, 1, 10, 100])
    ax.set_xlabel("Year", color=GREY, fontsize=13 * k, labelpad=10)
    ax.set_ylabel("Ton-miles per passenger-mile (log scale)", color=GREY, fontsize=13 * k, labelpad=10)
    return pg


# ---------------------------------------------------------------- 4. 100% stacked bars
def chart_share(fmt):
    s = snapshot("mainline")
    s["share"] = s.freight / (s.freight + s.pax)
    s = s.sort_values("share")
    us, jp = s.set_index("iso").loc["USA"], s.set_index("iso").loc["JPN"]
    title = (f"{us.share:.1%} of US rail traffic is freight. In Japan it's {jp.share:.0%}.")
    sub = ("Freight ton-miles as a share of freight ton-miles plus passenger-miles, latest year; each bar adds to 100%. "
           + DEFN_TEXT["mainline"])
    note = "Adding tons and passengers treats one ton like one person, so read this as a ranking, not a measure of trains or track."
    footer = "Light bars: passenger count of uncertain definition (" + ", ".join(NAME[i] for i in s[~s.exact].iso) + "). " + src(fmt)
    pg = Page(fmt, title, sub, note, footer, WATERMARK)
    k = pg.k
    ax = pg.fig.add_axes([0.24, pg.bottom / pg.H + 0.075, 0.7, 1 - (pg.top + pg.bottom) / pg.H - 0.095])
    style_axes(ax, k)
    ax.grid(axis="y", visible=False); ax.grid(axis="x", color=LIGHT, lw=1)
    ys = np.arange(len(s))
    fc = [COPPER if i == "USA" else (DARK if e else NEUTRAL) for i, e in zip(s.iso, s.exact)]
    ax.barh(ys, s.share * 100, color=fc, height=0.66, zorder=2)
    ax.barh(ys, (1 - s.share) * 100, left=s.share * 100 + 0.4, color=LIGHT, height=0.66, zorder=2)
    for y, v, c in zip(ys, s.share, fc):
        lab = f"{v:.0%}" if 0.02 < v < 0.98 else f"{v:.1%}"
        inside = v > 0.15
        ax.text(v * 100 - 1.5 if inside else v * 100 + 1.5, y, lab, va="center", ha="right" if inside else "left",
                color=BG if (inside and c != NEUTRAL) else INK, fontsize=12 * k)
    ax.text(1, len(s) - 0.3, "freight", color=COPPER, fontsize=12 * k, va="bottom")
    ax.text(99, len(s) - 0.3, "passengers", color=GREY, fontsize=12 * k, va="bottom", ha="right")
    ax.set_yticks(ys); ax.set_yticklabels([NAME[i] for i in s.iso], fontsize=14 * k, color=INK)
    ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_xlabel("Share of rail traffic (ton-miles + passenger-miles)", color=GREY, fontsize=13 * k, labelpad=10)
    return pg


# ---------------------------------------------------------------- 5. small multiples
def chart_multiples(fmt):
    g = d[d.iso3 == "USA"].set_index("year")
    pax = 100 * (1 - g.pkm_mainline[1970] / g.pkm_mainline[1920])
    fr = 100 * (g.freight_tkm[1970] / g.freight_tkm[1920] - 1)
    title = f"From 1920 to 1970, US rail passenger travel fell {pax:.0f}% while rail freight grew {fr:.0f}%"
    sub = ("Rail freight (billion ton-miles) and rail passengers (billion passenger-miles) per year. Each panel has its own scale. "
           "Intercity, regional and commuter trains; Japan includes subways and trams.")
    footer = "Gaps are years no source covers; nothing is interpolated. " + src(fmt)
    pg = Page(fmt, title, sub, "", footer, WATERMARK)
    k = pg.k
    top, bot = 1 - pg.top / pg.H, pg.bottom / pg.H + 0.05
    isos = ["USA", "JPN", "DEU", "FRA", "GBR", "CHN"]
    h = (top - bot) / 3
    for n, iso in enumerate(isos):
        col = SERIES[iso]
        ax = pg.fig.add_axes([0.1 + (n % 2) * 0.46, top - (n // 2 + 1) * h + 0.035, 0.36, h - 0.07])
        style_axes(ax, k * 0.8)
        g = d[d.iso3 == iso].sort_values("year")
        for c, colname, lab in ((COPPER, "freight_tkm", "freight"), (INK, col, "passengers")):
            gg = g[g[colname].notna()]
            yv, vv = gg.year.values, gg[colname].values / 1000
            for idx in np.split(np.arange(len(yv)), np.where(np.diff(yv) > 5)[0] + 1):
                ax.plot(yv[idx], vv[idx], color=c, lw=1.8, marker="o" if len(idx) == 1 else None, ms=3)
            if len(yv):
                ax.text(yv[-1] + 1.5, vv[-1], lab, color=c, fontsize=10 * k, va="center")
        ax.set_xlim(1915, 2035); ax.set_ylim(0, None)
        ax.set_title(NAME[iso], loc="left", fontproperties=font("serif", 17 * k), color=INK)
        ax.set_xticks([1920, 1950, 1980, 2010])
        if n % 2 == 0:
            ax.set_ylabel("Billions per year", color=GREY, fontsize=10 * k)
        if n >= 4:
            ax.set_xlabel("Year", color=GREY, fontsize=10 * k)
    return pg


CHARTS = {
    "1-ratio-mainline": lambda f: chart_ratio_bars(f, "mainline"),
    "1-ratio-allrail": lambda f: chart_ratio_bars(f, "all_rail"),
    "2-scatter-mainline": lambda f: chart_scatter(f, "mainline"),
    "2-scatter-allrail": lambda f: chart_scatter(f, "all_rail"),
    "3-ratio-over-time": chart_time,
    "4-share": chart_share,
    "5-small-multiples": chart_multiples,
}


def main():
    setup_font()
    OUT.mkdir(parents=True, exist_ok=True)
    fmts = ["blog"] + (["social"] if "--social" in sys.argv else [])
    for name, fn in CHARTS.items():
        for f in fmts:
            out = OUT / (f"{name}.png" if f == "blog" else f"social-{name}-4x5.png")
            fn(f).save(out)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
