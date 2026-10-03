"""Render this post's charts into output/."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # repo root, for style.py

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from style import BG, INK, GREY, LIGHT, COPPER, BODY, DPI, Page, setup_font
from model import (LABELS, MILES_CUT, EXAMPLE_TRIP_MILES, speed_rows, extra_minutes,
                   load_nhts, fetched_on, exposure_rows, driving_rows)

WATERMARK = "maxmautner.com/slower"
OUT = HERE / "output"
TAN = "#e3c9ad"   # light copper, for the third category
FILL = {"MSA 1M+": INK, "MSA under 1M": COPPER, "Not in MSA": TAN}
TEXT_ON = {"MSA 1M+": BG, "MSA under 1M": BG, "Not in MSA": INK}

def chart_area(p, pad=0.35, left=0.4, right=0.4):
    """Axes filling the space between the header and the sources footer."""
    return p.fig.add_axes([left / p.W, (p.bottom + pad) / p.H, (p.W - left - right) / p.W,
                           (p.H - p.top - p.bottom - pad) / p.H])

def bare(ax):
    ax.set_facecolor(BG); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

def hbars(ax, k, labels, values, colors, fmt, xmax, gap_before_last=0.0, inside=False):
    """Horizontal bars with the value at the right end, labeled above the bar or inside it."""
    bare(ax)
    n = len(values)
    ys = [n - 1 - i for i in range(n)]
    ys[-1] -= gap_before_last
    for y, lab, v, c in zip(ys, labels, values, colors):
        ax.barh(y, v, height=0.62 if inside else 0.42, color=c, edgecolor=COPPER if c == TAN else c, lw=1)
        if inside:
            ax.text(xmax * 0.015, y, lab, fontsize=15 * k, color=INK if c == TAN else BG, va="center")
        else:
            ax.text(0, y + 0.31, lab, fontsize=17 * k, color=BODY, va="bottom")
        ax.text(v + xmax * 0.015, y, fmt(v), fontsize=19 * k, color=INK, va="center")
    ax.set_xlim(0, xmax); ax.set_ylim(min(ys) - 0.4, max(ys) + 0.85)

def speed_vs_miles(fmt, name):
    rows = speed_rows()
    v0, v1 = rows[0][1], rows[0][2]
    mins, fwy = extra_minutes(v0, v1), rows[0][3]
    p = Page(fmt, "5 mph slower beats\ndriving 5% less",
             "Estimated drop in fatal crashes",
             f"On a freeway, 5 mph slower adds ~{mins:.1f} minutes\nper {EXAMPLE_TRIP_MILES} miles.",
             "Source: Elvik (2009), The Power Model of the relationship between\n"
             "speed and road safety, TØI Report 1034/2009. Fatal-crash exponents\n"
             "4.1 (rural roads, freeways) and 2.6 (urban roads). *Likely high:\n"
             "a given % cut matters less at low speeds (Elvik 2013).", WATERMARK)
    labels = [r[0] for r in rows] + ["Drive 5% fewer miles, same speed"]
    labels[3] += "*"
    values = [r[3] for r in rows] + [MILES_CUT]
    ax = chart_area(p, right=0.6)
    hbars(ax, p.k, labels, values, [COPPER] * len(rows) + [INK], lambda v: f"{v:.0%}", 0.5, gap_before_last=0.3)
    p.save(OUT / name)

def exposure_area(fmt, name, nhts):
    rows = exposure_rows(nhts)
    big, rural = rows[0], rows[-1]
    more_miles, deaths_x, per_mile_x = rural[1] / big[1] - 1, rural[2] / big[2], rural[3] / big[3]
    p = Page(fmt, f"Rural residents drive\n{more_miles:.0%} more and die in\ntraffic at {deaths_x:.1f}× the rate",
             "Width is miles driven per resident, height is\ndeaths per mile, area is deaths per resident.",
             f"Each rural mile comes with ~{per_mile_x:.1f}× the deaths of\na big-metro mile. 2017, by home county.",
             f"Sources: 2017 National Household Travel Survey (fetched\n{fetched_on()}); NCHS Data Brief 343, age-adjusted traffic deaths by\n"
             "county of residence. Height is deaths ÷ miles and counts all\nresidents' traffic deaths, including pedestrians.", WATERMARK)
    k = p.k
    ax = chart_area(p, pad=1.3, left=0.95, right=0.4)
    bare(ax)
    xmax, ymax = max(r[1] for r in rows) * 1.06, max(r[3] for r in rows) * 1.06
    per_in = ymax / (ax.get_position().height * p.H)   # data units per inch, for offsets below the axis
    for g, mi, d, h in reversed(rows):   # largest box first, smaller ones on top
        ax.add_patch(Rectangle((0, 0), mi, h, facecolor=FILL[g], edgecolor=COPPER if g == "Not in MSA" else FILL[g], lw=1.2))
    heights = [r[3] for r in rows]
    bands = [(0, heights[0]), (heights[0], heights[1]), (heights[1], heights[2])]
    for (g, mi, d, h), (lo, hi) in zip(rows, bands):
        ax.text(xmax * 0.025, (lo + hi) / 2, LABELS[g].replace(" (", "\n("), fontsize=17 * k,
                color=TEXT_ON[g], va="center", linespacing=1.15)
        ax.text(mi - xmax * 0.025, (lo + hi) / 2, f"{d:.1f} deaths per 100,000", fontsize=15 * k,
                color=TEXT_ON[g], va="center", ha="right", linespacing=1.15)
        ax.text(-xmax * 0.015, h, f"{h:.2f}", fontsize=14 * k, color=GREY, va="center", ha="right")
    for i, (g, mi, *_) in enumerate(rows):   # stagger the close-together width labels
        drop = per_in * (0.1 + 0.28 * i)
        ax.plot([mi, mi], [0, -drop + per_in * 0.03], color=LIGHT, lw=1, clip_on=False)
        ax.text(mi, -drop, f"{mi:,.0f}", fontsize=14 * k, color=GREY, ha="center", va="top")
    ax.text(xmax / 2, -per_in * 0.95, "Miles driven per resident per year", fontsize=14 * k, color=GREY, ha="center", va="top")
    ax.text(-xmax * 0.1, ymax / 2, "Deaths per 100 million miles", fontsize=14 * k, color=GREY,
            rotation=90, ha="center", va="center")
    ax.set_xlim(0, xmax); ax.set_ylim(0, ymax)
    p.save(OUT / name)

def time_vs_miles(fmt, name, nhts):
    rows = driving_rows(nhts)
    big, rural = rows[0], rows[-1]
    more = rural[2] / big[2] - 1
    assert rural[1] < big[1], "Title says rural drivers spend less time driving"
    p = Page(fmt, f"Rural drivers spend less\ntime driving and cover\n{more:.0%} more miles",
             "Per licensed driver per day, by the\ndriver's home county, 2017",
             f"Big-metro drivers average {big[3]:.0f} mph; rural drivers\naverage {rural[3]:.0f} mph.",
             f"Source: 2017 National Household Travel Survey, travel-day\ndriving (fetched {fetched_on()}). "
             "Includes drivers who did not drive\nthat day. Big metros 1 million+; smaller metros under\n1 million; rural not in a metro area.", WATERMARK)
    k = p.k
    full = chart_area(p, pad=0.2, right=0.9); full.remove()
    x0, y0, w, h = full.get_position().bounds
    for i, (title, idx, xmax, f) in enumerate([("Minutes driving per day", 1, 70, lambda v: f"{v:.0f} min"),
                                              ("Miles driven per day", 2, 35, lambda v: f"{v:.1f} mi")]):
        ax = p.fig.add_axes([x0, y0 + h * (0.52 if i == 0 else 0), w, h * 0.46])
        hbars(ax, k, [LABELS[r[0]] for r in rows], [r[idx] for r in rows],
              [FILL[r[0]] for r in rows], f, xmax, inside=True)
        ax.set_ylim(-0.45, 2.95)
        ax.text(0, 2.5, title, fontsize=15 * k, color=GREY, va="bottom")
    p.save(OUT / name)

def og_image(name):
    """1200 x 630 link-preview image for the post's og:image."""
    rows = speed_rows()
    fwy = rows[0][3]
    fig = plt.figure(figsize=(8, 4.2), dpi=DPI, facecolor=BG)
    fig.text(0.05, 0.88, "5 mph slower beats\ndriving 5% less", fontsize=30, color=INK, va="top", linespacing=1.15)
    fig.text(0.05, 0.50, f"On a freeway: ~{fwy:.0%} fewer fatal\ncrashes, ~{extra_minutes(65, 60):.1f} extra minutes\nper {EXAMPLE_TRIP_MILES} miles.",
             fontsize=16, color=COPPER, va="top", linespacing=1.3)
    fig.text(0.05, 0.08, WATERMARK, fontsize=12, color=GREY, va="bottom")
    ax = fig.add_axes([0.66, 0.14, 0.26, 0.68]); bare(ax)
    vals, labs, cols = [fwy, MILES_CUT], ["5 mph\nslower", "5% fewer\nmiles"], [COPPER, INK]
    ax.bar([0, 1], vals, width=0.62, color=cols)
    for x, v, lab in zip([0, 1], vals, labs):
        ax.text(x, v + 0.012, f"{v:.0%}", ha="center", va="bottom", fontsize=17, color=INK)
        ax.text(x, -0.02, lab, ha="center", va="top", fontsize=12, color=BODY, linespacing=1.15)
    ax.text(0.5, max(vals) * 1.42, "Fewer fatal crashes", ha="center", va="top", fontsize=12, color=GREY)
    ax.set_xlim(-0.55, 1.55); ax.set_ylim(0, max(vals) * 1.42)
    fig.savefig(OUT / name, facecolor=BG); plt.close(fig)

if __name__ == "__main__":
    setup_font()
    OUT.mkdir(exist_ok=True)
    nhts = load_nhts()
    speed_vs_miles("blog", "speed-vs-miles.png")
    speed_vs_miles("social", "social-speed-vs-miles-4x5.png")
    exposure_area("blog", "miles-and-deaths-by-home.png", nhts)
    exposure_area("social", "social-miles-and-deaths-by-home-4x5.png", nhts)
    time_vs_miles("blog", "time-vs-miles.png", nhts)
    time_vs_miles("social", "social-time-vs-miles-4x5.png", nhts)
    og_image("og-image.png")
    print(f"Wrote 7 charts to {OUT}")
