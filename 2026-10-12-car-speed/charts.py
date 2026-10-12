"""Render this post's charts into output/."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # repo root, for style.py

import matplotlib.pyplot as plt
from style import BG, INK, GREY, LIGHT, COPPER, BODY, DPI, Page, setup_font, style_axes
from model import (VEHICLES, MEDIAN_WAGE, SHORT_TRIP_MILES_PER_YEAR, CAR_MILES_PER_YEAR,
                   hours_split, effective_mph, take_home, fetched_on)

WATERMARK = "maxmautner.com/howfast"
OUT = HERE / "output"
TAN = "#e3c9ad"
SHORT = {"New car": "New car", "Used car": "Used car",
         "E-bike, Class 2": "20 mph e-bike", "E-bike, Class 3": "28 mph e-bike"}

LINE_LABEL = {"New car": "New car", "Used car": "Used car",
              "E-bike, Class 2": "20 mph e-bike", "E-bike, Class 3": "28 mph e-bike"}

def chart_area(p, pad=0.35, left=0.4, right=0.4):
    return p.fig.add_axes([left / p.W, (p.bottom + pad) / p.H, (p.W - left - right) / p.W,
                           (p.H - p.top - p.bottom - pad) / p.H])

def bare(ax):
    ax.set_facecolor(BG); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

SOURCES_HOURS = (
    "Sources: 2022 National Household Travel\n"
    "Survey (fetched {f}); AAA 2026; Edmunds;\n"
    "Lectric XP Lite2 ($999); Schleinitz et al. 2017.\n"
    "US data. Method: github.com/mmautner/charts")

def hours_chart(fmt, name):
    rows = [(k, t / 52, p / 52) for k, t, p in hours_split()]
    r = {k: (t, p) for k, t, p in rows}
    saved = r["E-bike, Class 2"][0] - r["Used car"][0]
    spent = r["Used car"][1] - r["E-bike, Class 2"][1]
    assert spent > saved > 0, "Title claims the car's road-time savings are spent at work"
    p = Page(fmt, "The time a car saves\ngoes to paying for it",
             f"To cover {SHORT_TRIP_MILES_PER_YEAR:,} miles a year of trips under\n"
             f"8 miles, at the median wage",
             f"Work hours at ${take_home(MEDIAN_WAGE):.2f} an hour, a median earner's\ntake-home pay after tax.",
             SOURCES_HOURS.format(f=fetched_on()), WATERMARK)
    k = p.k
    ax = chart_area(p, pad=0.85, right=0.6)
    style_axes(ax, k); ax.grid(axis="y", visible=False); ax.grid(axis="x", color=LIGHT, lw=1)
    xmax = 10
    n = len(rows)
    for i, (veh, t, w) in enumerate(rows):
        y = n - 1 - i
        ax.barh(y, t, height=0.42, color=INK)
        ax.barh(y, w, left=t, height=0.42, color=COPPER)
        ax.text(0, y + 0.29, SHORT[veh], fontsize=17 * k, color=BODY, va="bottom")
        ax.text(t + w + xmax * 0.015, y, f"{t + w:.1f}", fontsize=19 * k, color=INK, va="center")
    t0, w0 = rows[0][1], rows[0][2]
    ax.text(xmax * 0.015, n - 1, "On the road", fontsize=14 * k, color=BG, va="center")
    ax.text(t0 + xmax * 0.015, n - 1, "At work paying", fontsize=14 * k, color=BG, va="center")
    ax.set_xlim(0, xmax); ax.set_ylim(-0.5, n - 0.25)
    ax.set_xticks(range(0, xmax + 1, 2)); ax.set_yticks([])
    per_in = (n - 0.25 + 0.5) / (ax.get_position().height * p.H)
    ax.text(xmax / 2, -0.5 - per_in * 0.42, "Hours a week", fontsize=13 * k, color=GREY, ha="center", va="top")
    p.save(OUT / name)

SOURCES_SPEED = (
    "Speed = miles / (hours travelling + hours worked\n"
    "to pay, after tax). Door to door. Cars driven {m:,}\n"
    "mi a year (US avg), incl. home parking. Sources:\n"
    "2022 NHTS (fetched {f}); AAA; Edmunds; Lectric.\n"
    "Method: github.com/mmautner/charts")

def speed_chart(fmt, name):
    wages = [w / 4 for w in range(8 * 4, 80 * 4 + 1)]
    lines = {v: [effective_mph(v, w) for w in wages] for v in VEHICLES}
    at = {v: effective_mph(v, MEDIAN_WAGE) for v in VEHICLES}
    p = Page(fmt, "How fast a car goes\ndepends on your wage",
             "Miles per hour on trips under 8 miles,\ncounting the hours worked to pay for it",
             f"At the median wage, ${MEDIAN_WAGE:.2f}: new car {at['New car']:.1f},\n"
             f"used car {at['Used car']:.1f}, e-bike {at['E-bike, Class 2']:.1f} or {at['E-bike, Class 3']:.1f} mph.",
             SOURCES_SPEED.format(m=CAR_MILES_PER_YEAR, f=fetched_on()), WATERMARK)
    k = p.k
    ax = chart_area(p, pad=0.85, left=0.9, right=1.65)
    style_axes(ax, k)
    look = {"New car": (INK, "-"), "Used car": (INK, (0, (5, 3))),
            "E-bike, Class 2": (COPPER, (0, (5, 3))), "E-bike, Class 3": (COPPER, "-")}
    for v in VEHICLES:
        c, ls = look[v]
        ax.plot(wages, lines[v], color=c, ls=ls, lw=2.6, solid_capstyle="round")
    ymax = 13
    ax.axvline(MEDIAN_WAGE, color=GREY, lw=1, ls=(0, (1, 3)))
    ax.text(MEDIAN_WAGE + 1, ymax * 0.03, "Median\nwage", fontsize=12 * k, color=GREY, va="bottom", linespacing=1.1)
    per_in = ymax / (ax.get_position().height * p.H)          # data units per inch
    ends = sorted(((lines[v][-1], v) for v in VEHICLES))
    placed = []
    for y, v in ends:
        y2 = max(y, placed[-1] + per_in * 0.27 * k) if placed else y
        placed.append(y2)
        ax.text(wages[-1] + 1.5, y2, LINE_LABEL[v], fontsize=14 * k, color=look[v][0], va="center",
                clip_on=False, linespacing=1.1)
    ax.set_xlim(8, 80); ax.set_ylim(0, ymax)
    ax.set_xticks([10, 20, 30, 40, 50, 60, 70, 80])
    ax.set_xticklabels([f"${x}" for x in [10, 20, 30, 40, 50, 60, 70, 80]])
    ax.set_yticks(range(0, ymax + 1, 2)); ax.set_yticklabels([f"{y} mph" if y == 12 else str(y) for y in range(0, ymax + 1, 2)])
    ax.text(44, -per_in * 0.42, "Hourly wage, before tax", fontsize=13 * k, color=GREY, ha="center", va="top")
    p.save(OUT / name)

def commute_chart(fmt, name):
    from inputs import COMMUTE_DECENNIAL, COMMUTE_ACS
    first, last = min(COMMUTE_DECENNIAL), max(COMMUTE_ACS)
    gain = COMMUTE_ACS[last] - COMMUTE_DECENNIAL[first]
    p = Page(fmt, f"US commutes are {gain:.1f}\nminutes longer than in {first}",
             "Average one-way travel time to work, minutes",
             f"{COMMUTE_ACS[2019]} minutes in 2019 was the record; it fell when\nremote work peaked and was {COMMUTE_ACS[last]} by {last}.",
             "Sources: Census 2000 Brief C2KBR-33 (1980-2000 census);\n"
             "American Community Survey 1-year (2006-2024; none for\n"
             "2020). Excludes people who work from home.", WATERMARK)
    k = p.k
    ax = chart_area(p, pad=0.5, left=0.75, right=0.6)
    style_axes(ax, k)
    xs, ys = list(COMMUTE_DECENNIAL), list(COMMUTE_DECENNIAL.values())
    ax.plot(xs, ys, color=GREY, lw=2, ls=(0, (2, 3)))
    ax.plot([2000, 2006], [COMMUTE_DECENNIAL[2000], COMMUTE_ACS[2006]], color=GREY, lw=2, ls=(0, (2, 3)))
    ax.scatter(xs, ys, color=INK, s=36 * k, zorder=3)
    pre = [y for y in COMMUTE_ACS if y <= 2019]; post = [y for y in COMMUTE_ACS if y >= 2021]
    for seg in (pre, post):
        ax.plot(seg, [COMMUTE_ACS[y] for y in seg], color=COPPER, lw=2.8, solid_capstyle="round")
    ax.plot([2019, 2021], [COMMUTE_ACS[2019], COMMUTE_ACS[2021]], color=COPPER, lw=1.5, ls=(0, (2, 3)))
    for yr, v in [(first, COMMUTE_DECENNIAL[first]), (2019, COMMUTE_ACS[2019]), (last, COMMUTE_ACS[last])]:
        ax.text(yr, v + 0.9, f"{v}", fontsize=15 * k, color=INK, ha="center", va="bottom")
    ax.text(1985, 19.6, "Census, every\n10 years", fontsize=13 * k, color=GREY, ha="center", va="top", linespacing=1.15)
    ax.text(2013, 23.4, "Annual survey", fontsize=13 * k, color=COPPER, ha="center", va="top")
    ax.set_xlim(1977, 2027); ax.set_ylim(0, 30)
    ax.set_xticks([1980, 1990, 2000, 2010, 2020]); ax.set_yticks(range(0, 31, 5))
    p.save(OUT / name)

def og_image(name):
    """1200 x 630 link-preview image."""
    rows = [(k, t / 52, w / 52) for k, t, w in hours_split()]
    fig = plt.figure(figsize=(8, 4.2), dpi=DPI, facecolor=BG)
    fig.text(0.05, 0.88, "How fast is a car,\nafter you pay for it?", fontsize=28, color=INK, va="top", linespacing=1.15)
    fig.text(0.05, 0.50, "Hours a week on the road,\nplus hours at work paying\nfor the vehicle.",
             fontsize=15, color=COPPER, va="top", linespacing=1.3)
    fig.text(0.05, 0.08, WATERMARK, fontsize=12, color=GREY, va="bottom")
    ax = fig.add_axes([0.58, 0.1, 0.36, 0.78]); bare(ax)
    xmax = max(t + w for _, t, w in rows) * 1.3
    for i, (veh, t, w) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.barh(y, t, height=0.4, color=INK); ax.barh(y, w, left=t, height=0.4, color=COPPER)
        ax.text(0, y + 0.27, SHORT[veh], fontsize=11, color=BODY, va="bottom")
        ax.text(t + w + xmax * 0.02, y, f"{t + w:.1f}", fontsize=12, color=INK, va="center")
    ax.set_xlim(0, xmax); ax.set_ylim(-0.4, len(rows) - 0.3)
    fig.savefig(OUT / name, facecolor=BG); plt.close(fig)

if __name__ == "__main__":
    setup_font()
    OUT.mkdir(exist_ok=True)
    hours_chart("blog", "hours-on-road-and-at-work.png")
    hours_chart("social", "social-hours-on-road-and-at-work-4x5.png")
    speed_chart("blog", "speed-by-wage.png")
    speed_chart("social", "social-speed-by-wage-4x5.png")
    commute_chart("blog", "commute-time.png")
    commute_chart("social", "social-commute-time-4x5.png")
    og_image("og-image.png")
    print(f"Wrote 7 charts to {OUT}")
