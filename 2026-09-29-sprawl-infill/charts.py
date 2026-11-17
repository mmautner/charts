"""Render this post's charts into output/."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # repo root, for style.py

import numpy as np
from style import BG, INK, GREY, LIGHT, COPPER, BODY, Page, setup_font, style_axes
from model import (load, infill_by_decade, core_series, loop_area_sqmi, state, per_1000_residents,
                   residents_per_home)
from inputs import (URBAN_CORE_HU_PER_SQMI, HOUSTON_REFORM_YEAR, CA_FIPS, CA_POPULATION,
                    US_POPULATION, CA_OCCUPIED, US_OCCUPIED, CA_CROWDED_SHARE,
                    CA_HH_POPULATION, US_HH_POPULATION, CA_MEDIAN_VALUE, US_MEDIAN_VALUE,
                    LA_ZONED_CAPACITY, LA_REZONING_START, LA_POPULATION)

WATERMARK = "maxmautner.com/infill"
OUT = HERE / "output"
SOURCES = ("Sources: Census ACS 2020–2024 5-year, table B25034;\n"
           "Census 2024 tract gazetteer. Counts exclude demolished\n"
           "homes, which understates older decades.")

DEFINITION = ("New homes built each decade that are still standing.\n"
              "Infill: in areas already built up, with "
              f"{URBAN_CORE_HU_PER_SQMI}+ homes\n"
              "per square mile. Greenfield: in areas that weren't.")

def complete_decades(t):
    return [r for r in infill_by_decade(t) if r["decade"] != "2020s"]  # partial decade

def infill_bars(fmt, name, t):
    rows = complete_decades(t)
    since70 = [r for r in rows if r["decade"] >= "1970s"]
    inf_lo, inf_hi = min(r["infill"] for r in since70), max(r["infill"] for r in since70)
    gf_lo, gf_hi = min(r["greenfield"] for r in since70), max(r["greenfield"] for r in since70)
    assert 6e6 <= inf_lo and inf_hi <= 8e6, "Title says ~7 million; check the infill range"
    p = Page(fmt, "US infill has held at ~7 million\nhomes a decade since the 1970s", DEFINITION,
             f"Over the same decades, greenfield building\n"
             f"ranged from {gf_lo/1e6:.1f} million to {gf_hi/1e6:.1f} million homes.",
             SOURCES, WATERMARK)
    mirrored_bars(p, rows, 1e6, lambda v: f"{v:.1f}M")
    p.save(OUT / name)

def california_bars(fmt, name, t):
    rows = complete_decades(state(t, CA_FIPS))
    infill = {r["decade"]: r["infill"] for r in rows}
    ratio = infill["2010s"] / infill["1970s"]
    assert 0.45 <= ratio <= 0.55, "Title says half; check the 1970s and 2010s infill"
    per_k = per_1000_residents(rows, CA_POPULATION)
    p = Page(fmt, "California builds half as many homes\nin its existing neighborhoods as\nit did in the 1970s",
             DEFINITION,
             f"Per resident, infill fell from {per_k['1970s']:.0f} homes per 1,000\n"
             f"Californians in the 1970s to {per_k['2010s']:.0f} in the 2010s.",
             SOURCES + "\nPopulation: decennial census.", WATERMARK)
    mirrored_bars(p, rows, 1e3, lambda v: f"{v:,.0f}K")
    p.save(OUT / name)

def california_per_resident(fmt, name, t):
    rows = complete_decades(state(t, CA_FIPS))
    inf = per_1000_residents(rows, CA_POPULATION, "infill")
    gf = per_1000_residents(rows, CA_POPULATION, "greenfield")
    labels = list(inf)
    tot = {d: inf[d] + gf[d] for d in labels}
    ratio = tot["2010s"] / tot["1970s"]
    assert 0.18 <= ratio <= 0.22, "Title says a fifth; check the 1970s and 2010s totals"
    p = Page(fmt, "California builds a fifth as many homes per resident as it did in the 1970s",
             "New homes built each decade that are still standing, per 1,000 Californians "
             "when the decade began. Infill: in areas already built up, with "
             f"{URBAN_CORE_HU_PER_SQMI}+ homes per square mile. Greenfield: in areas that weren't.",
             f"{tot['1970s']:.0f} homes per 1,000 residents in the 1970s, {tot['2010s']:.0f} in the 2010s.",
             SOURCES + " Population: decennial census.", WATERMARK)
    k, pad = p.k, 0.5
    ax = p.fig.add_axes([0.95 / p.W, (p.bottom + pad) / p.H, (p.W - 1.35) / p.W,
                         (p.H - p.top - p.bottom - pad - 0.5) / p.H])
    style_axes(ax, k)
    x = np.arange(len(labels))
    a = np.array([inf[d] for d in labels]); b = np.array([gf[d] for d in labels])
    ax.bar(x, a, color=INK, width=0.68)
    ax.bar(x, b, bottom=a, color=COPPER, width=0.68)
    for xi, v in zip(x, a + b):
        ax.text(xi, v + 2, f"{v:.0f}", ha="center", va="bottom", fontsize=15 * k, color=INK)
    peak = (a + b).max()
    step = 25
    ticks = np.arange(0, peak + step, step)            # gridlines stop below the legend
    top = ticks[-1] + 1.4 * step
    ax.set_yticks(ticks)
    ax.text(x[-1] + 0.4, top, "Greenfield", ha="right", va="top", fontsize=16 * k, color=COPPER)
    ax.text(x[-1] + 0.4, top - 0.55 * step, "Infill", ha="right", va="top", fontsize=16 * k, color=INK)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylim(0, top); ax.set_xlim(-0.6, x[-1] + 0.6)
    ax.set_ylabel("Homes built per 1,000 residents", color=GREY, fontsize=14 * k, labelpad=8)
    p.save(OUT / name)

def residents_per_home_lines(fmt, name):
    ca, us = residents_per_home(CA_HH_POPULATION, CA_OCCUPIED), residents_per_home(US_HH_POPULATION, US_OCCUPIED)
    years = list(ca)
    assert ca[1980] < ca[2020] and us[1980] > us[2020], "Title says CA rose and the US fell after 1980"
    p = Page(fmt, "Since 1980, California homes have held more people while the US average fell",
             "Residents per occupied home at each census, not counting dorms, prisons and nursing homes.",
             "",
             "Source: Census Bureau decennial censuses, 1960–2020 (household population and occupied units).",
             WATERMARK)
    k, pad, right = p.k, 0.65, 1.6
    ax = p.fig.add_axes([0.95 / p.W, (p.bottom + pad) / p.H, (p.W - 0.95 - right) / p.W,
                         (p.H - p.top - p.bottom - pad) / p.H])
    style_axes(ax, k)
    for label, series, color, lw in (("California", ca, COPPER, 4.5), ("US", us, INK, 2.5)):
        v = [series[y] for y in years]
        ax.plot(years, v, color=color, lw=lw, marker="o", ms=7 * k)
        ax.text(years[-1] + 2, v[-1], label, fontsize=16 * k, color=color, va="center", ha="left",
                clip_on=False, weight="bold" if label == "California" else "normal")
    ax.axvline(1980, color=LIGHT, lw=1.5, zorder=0)
    ax.set_xticks(years); ax.set_ylim(2.4, 3.5); ax.set_xlim(years[0] - 3, years[-1] + 1)
    ax.set_ylabel("Residents per occupied home", color=GREY, fontsize=14 * k, labelpad=8)
    p.save(OUT / name)

def mirrored_bars(p, rows, unit, label):
    """Infill bars to the left of a center line, greenfield to the right, one row per decade."""
    k = p.k
    ax = p.fig.add_axes([0.4 / p.W, p.bottom / p.H, (p.W - 0.8) / p.W, (p.H - p.top - p.bottom) / p.H])
    ax.set_facecolor(BG); ax.axis("off")
    inf = np.array([r["infill"] for r in rows]) / unit
    gf = np.array([r["greenfield"] for r in rows]) / unit
    n, m = len(rows), max(inf.max(), gf.max())
    left, right = inf.max() + 0.55 * m, gf.max() + 0.22 * m   # room for decade labels, values
    y = np.arange(n)[::-1]
    ax.barh(y, -inf, color=INK, height=0.68)
    ax.barh(y, gf, color=COPPER, height=0.68)
    ax.axvline(0, color=GREY, lw=1)
    pad = 0.02 * m
    for yi, r, a, b in zip(y, rows, inf, gf):
        ax.text(-left, yi, r["decade"], ha="left", va="center", fontsize=17 * k, color=INK)
        inside = a > 0.2 * m  # short bars get their label outside
        ax.text(-a + pad if inside else -a - pad, yi, label(a), ha="left" if inside else "right",
                va="center", fontsize=15 * k, color=BG if inside else INK)
        ax.text(b + pad, yi, label(b), ha="left", va="center", fontsize=15 * k, color=COPPER)
    ax.text(-3 * pad, n - 0.35, "Infill\nin built-up areas", ha="right", va="bottom", fontsize=16 * k,
            color=INK, linespacing=1.2)
    ax.text(3 * pad, n - 0.35, "Greenfield\nin areas not yet built up", ha="left", va="bottom", fontsize=16 * k,
            color=COPPER, linespacing=1.2)
    ax.set_xlim(-left, right); ax.set_ylim(-0.6, n + 0.9)

def texas_cores(fmt, name, t):
    labels, series = core_series(t)
    base, last = labels.index("1990s"), len(labels) - 1
    ratio = {c: v[last] / v[base] for c, v in series.items()}
    assert min(ratio.values()) >= 2.0, "Title says at least doubled; check the ratios"
    p = Page(fmt, "Downtown homebuilding at least\ndoubled in 3 Texas cities, with or\nwithout Houston's 1998 small-lot rule",
             "New homes built each decade that are still standing.\n"
             "Houston: inside its I-610 highway loop. Dallas and\n"
             f"San Antonio: the same area (~{loop_area_sqmi():.0f} sq mi) around downtown.",
             f"From the 1990s to the 2010s, building grew {ratio['Houston']:.1f} times\n"
             f"in Houston, {ratio['Dallas']:.1f} in Dallas, {ratio['San Antonio']:.1f} in San Antonio.",
             SOURCES, WATERMARK)
    k, pad, right = p.k, 0.65, 2.0
    ax = p.fig.add_axes([0.95 / p.W, (p.bottom + pad) / p.H, (p.W - 0.95 - right) / p.W,
                         (p.H - p.top - p.bottom - pad) / p.H])
    style_axes(ax, k)
    x = np.arange(len(labels))
    look = {"Houston": (COPPER, 4.5), "Dallas": (INK, 2.5), "San Antonio": (GREY, 2.5)}
    for c, v in series.items():
        color, lw = look[c]
        ax.plot(x, v / 1e3, color=color, lw=lw, marker="o", ms=7 * k)
        ax.text(x[-1] + 0.2, v[-1] / 1e3, c, fontsize=16 * k, color=color, va="center",
                ha="left", clip_on=False, weight="bold" if c == "Houston" else "normal")
    ymax = max(v.max() for v in series.values()) / 1e3 * 1.1
    ax.axvline(base + 0.5, color=LIGHT, lw=1.5, zorder=0)  # between the 1990s and 2000s points
    ax.text(base + 0.45, ymax, f"{HOUSTON_REFORM_YEAR}: Houston\nallows smaller lots", fontsize=14 * k,
            color=GREY, va="top", ha="right")  # left of the line, where the chart is empty
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylim(0, ymax); ax.set_xlim(-0.3, x[-1] + 0.1)
    ax.set_ylabel("Homes built per decade (thousands)", color=GREY, fontsize=14 * k, labelpad=8)
    p.save(OUT / name)

def price_ratio_line(fmt, name):
    """California's median home value as a multiple of the US median."""
    years = [y for y in CA_MEDIAN_VALUE if y in US_MEDIAN_VALUE]
    r = {y: CA_MEDIAN_VALUE[y] / US_MEDIAN_VALUE[y] for y in years}
    assert 1.3 <= r[1970] <= 1.4 and r[2024] >= 2.0, "Title says ~1/3 more in 1970, twice in 2024"
    p = Page(fmt, "A California home is worth twice the US median, up from a third more in 1970",
             "Median value of owner-occupied homes in California,\nas a multiple of the US median.",
             "",
             "Sources: Census Bureau, Historical Census of Housing Tables (home values, 1940–2000); "
             "ACS 1-year, table B25077 (2005–2024; no standard 2020 release).",
             WATERMARK)
    k, pad, right = p.k, 0.65, 1.5
    ax = p.fig.add_axes([0.95 / p.W, (p.bottom + pad) / p.H, (p.W - 0.95 - right) / p.W,
                         (p.H - p.top - p.bottom - pad) / p.H])
    style_axes(ax, k)
    ax.axhline(1, color=GREY, lw=1.2, zorder=1)
    ax.text(1941, 1.03, "US median", fontsize=13 * k, color=GREY, va="bottom")
    # A gap where 2000-2005 has no annual data and 2020 is missing: plot decades and ACS years
    # as separate runs so the line never implies values that weren't measured.
    for run in ([y for y in years if y <= 2000], [y for y in years if 2005 <= y <= 2019],
                [y for y in years if y >= 2021]):
        ax.plot(run, [r[y] for y in run], color=COPPER, lw=4.5, solid_capstyle="round")
    dec = [y for y in years if y <= 2000]
    ax.plot(dec, [r[y] for y in dec], "o", color=COPPER, ms=7 * k)
    ax.text(1970, r[1970] - 0.06, f"{r[1970]:.2f}×", fontsize=16 * k, color=INK, ha="center",
            va="top", weight="bold")
    ax.text(2025.5, r[2024], f"{r[2024]:.2f}×", fontsize=16 * k, color=INK, ha="left",
            va="center", weight="bold", clip_on=False)
    ax.set_ylim(0.8, 3.1); ax.set_xlim(1938, 2027)
    ax.set_yticks([1, 1.5, 2, 2.5, 3]); ax.set_yticklabels(["1×", "1.5×", "2×", "2.5×", "3×"])
    ax.set_xticks([1940, 1960, 1980, 2000, 2020])
    p.save(OUT / name)

def la_capacity_lines(fmt, name):
    """City of Los Angeles zoned capacity against its census population."""
    cap, pop = LA_ZONED_CAPACITY, LA_POPULATION
    assert cap[1990] / pop[1990] < 1.2 and cap[1960] / pop[1960] > 3.5, \
        "Title says zoning went from room for 4x the residents to barely more than lived there"
    p = Page(fmt, "Los Angeles cut its zoning from room for 4 times its residents to barely more "
             "than already lived there",
             "Residents the city's zoning could hold if every lot\nwere built to the limit, and actual population.",
             "The plans behind the rezoning called for \u201cpopulation control\u201d\nand to "
             "\u201cprotect the City\u2019s suburbia.\u201d",
             "Sources: Monkkonen, Lens & Manville, Built-Out Cities?, Terner Center 2020 (1960, 2020, "
             "citing Morrow 2013); City of Los Angeles, Historic Housing and Land Use Study "
             "(early 1970s, 1981 rezoning, plan language); Census Bureau (population).",
             WATERMARK)
    k, pad, right = p.k, 0.65, 1.9
    ax = p.fig.add_axes([0.95 / p.W, (p.bottom + pad) / p.H, (p.W - 0.95 - right) / p.W,
                         (p.H - p.top - p.bottom - pad) / p.H])
    style_axes(ax, k)
    cy, py = list(cap), list(pop)
    # Measured before and after the rezoning; the path between isn't known year by year, so no
    # line is drawn across the gap.
    for run in ([y for y in cy if y < LA_REZONING_START], [y for y in cy if y > LA_REZONING_START]):
        ax.plot(run, [cap[y] / 1e6 for y in run], color=COPPER, lw=4.5, marker="o", ms=8 * k)
    ax.plot(py, [pop[y] / 1e6 for y in py], color=INK, lw=2.5, marker="o", ms=6 * k)
    ax.axvline(LA_REZONING_START, color=LIGHT, lw=1.5, zorder=0)
    ax.text(LA_REZONING_START + 1, 11.3, f"Rezoning\nbegins {LA_REZONING_START}", fontsize=12 * k,
            color=GREY, va="top")
    ax.text(2022, cap[2020] / 1e6 + 0.35, "Zoned\ncapacity", fontsize=15 * k, color=COPPER,
            va="bottom", ha="left", weight="bold", clip_on=False)
    ax.text(2022, pop[2020] / 1e6 - 0.35, "Population", fontsize=15 * k, color=INK, va="top",
            ha="left", clip_on=False)
    ax.set_ylim(0, 12); ax.set_xlim(1956, 2021)
    ax.set_yticks([0, 2, 4, 6, 8, 10]); ax.set_yticklabels(["0", "2M", "4M", "6M", "8M", "10M"])
    ax.set_xticks([1960, 1970, 1980, 1990, 2000, 2010, 2020])
    p.save(OUT / name)

if __name__ == "__main__":
    setup_font()
    OUT.mkdir(exist_ok=True)
    t = load()
    infill_bars("blog", "infill-vs-greenfield-by-decade.png", t)
    infill_bars("social", "social-infill-vs-greenfield-4x5.png", t)
    texas_cores("blog", "texas-cores-by-decade.png", t)
    texas_cores("social", "social-texas-cores-4x5.png", t)
    california_bars("blog", "california-infill-by-decade.png", t)
    california_bars("social", "social-california-infill-4x5.png", t)
    california_per_resident("blog", "california-homes-per-resident.png", t)
    california_per_resident("social", "social-california-homes-per-resident-4x5.png", t)
    residents_per_home_lines("blog", "residents-per-home.png")
    residents_per_home_lines("social", "social-residents-per-home-4x5.png")
    price_ratio_line("blog", "california-price-ratio.png")
    price_ratio_line("social", "social-california-price-ratio-4x5.png")
    la_capacity_lines("blog", "la-zoned-capacity.png")
    la_capacity_lines("social", "social-la-zoned-capacity-4x5.png")
    print(f"Wrote 14 charts to {OUT}")
