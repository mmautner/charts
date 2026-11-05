"""Render this post's chart into output/ from data/express_lanes_funding.csv.
usage (from the post folder): python charts/charts.py [--social]"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
POST = HERE.parent
sys.path.insert(0, str(POST.parent))  # repo root, for style.py

import matplotlib.pyplot as plt
import pandas as pd
from style import BG, INK, GREY, LIGHT, COPPER, BODY, Page, font, setup_font, style_axes, text_width

WATERMARK = "maxmautner.com/rtm-oversight"
DATA, OUT = POST / "data", POST / "output"
STONE = "#c9c2b4"          # neutral for the money an inspector general can audit


def chart_area(p, top_gap=0.3, bottom_gap=0.85, left=1.0, right=0.4):
    return p.fig.add_axes([left / p.W, (p.bottom + bottom_gap) / p.H, (p.W - left - right) / p.W,
                           (p.H - p.top - p.bottom - top_gap - bottom_gap) / p.H])


def money(v):
    return f"${v:,.1f}".rstrip("0").rstrip(".") + " million"


# ---------------------------------------------------------------- who can audit the 101 express lanes' money
def funding(fmt, name):
    d = pd.read_csv(DATA / "express_lanes_funding.csv")
    total = d.amount_millions.sum()
    by = d.groupby("oversight").amount_millions.sum()
    no_ig = by["no_ig"]
    assert round(total, 1) == 514.3, "subtitle: $514.3 million"
    assert round(no_ig, 1) == 178.5, "title: $178.5 million"
    assert round(by["caltrans_ig"], 1) == 282.8
    segs = (d.groupby(["oversight", "label"], sort=False).amount_millions.sum().reset_index())
    order = ["Bay Area bridge tolls", "Local money",
             "State and federal money", "Private companies"]
    segs = segs.set_index("label").loc[order].reset_index()

    p = Page(fmt, f"{money(no_ig)} of public money in the 101 express lanes answers to no inspector general",
             f"Where the {money(total)} budget for the US 101 express lanes in San Mateo County came from. Caltrans' "
             "Inspector General can audit the state and federal money; no inspector general covers the bridge toll "
             "or local money.",
             "",
             "Source: San Mateo County Express Lanes Joint Powers Authority, application for toll facility to the "
             "California Transportation Commission, June 28, 2019, Exhibit 14. Planned budget; Streetsblog put the "
             "finished project near $600 million. State and federal: SB 1 Solutions for Congested Corridors $200 "
             "million and Local Partnership Program $21.8 million, state transportation improvement programs $51.5 "
             "million, federal earmark $9.5 million. Local: Measure A sales tax $30.5 million and $53 million the "
             "application says Measure A or other local funds would front, repaid from future tolls. Caltrans' Inspector General audits entities receiving state and federal transportation "
             "money through Caltrans (ig.dot.ca.gov). The bridge toll measure RM3 created an inspector general "
             "for BART only. Private money is shown but is not public.",
             WATERMARK)
    k = p.k
    small = k < 1
    ax = chart_area(p, left=1.2, right=0.25, bottom_gap=0.95 if small else 1.05, top_gap=0.35 if small else 0.5)
    style_axes(ax, k)
    ax.grid(False)                      # gridlines would run through the segment labels
    x, w = 0, 0.5                       # bar centre and width
    x0, x1 = -1.35, 2.6
    ax.set_xlim(x0, x1)
    per_in = 560 / (ax.get_position().height * p.H)          # $ millions per inch of page
    per_in_x = (x1 - x0) / (ax.get_position().width * p.W)   # x data units per inch of page
    gap = 0.03 * per_in                                       # thin background gap between segments
    colors = {"no_ig": COPPER, "caltrans_ig": STONE, "private": LIGHT}
    base = 0
    label_x = x + w / 2 + 0.1
    for _, r in segs.iterrows():
        v = r.amount_millions
        ax.bar(x, v - gap, bottom=base, width=w, color=colors[r.oversight], lw=0, zorder=2,
               hatch="//" if r.oversight == "private" else None, edgecolor=BG if r.oversight == "private" else None)
        mid = base + (v - gap) / 2
        # one line per segment, value then name, so short segments don't need two lines of room
        fv = font("serif", (22 if r.oversight == "no_ig" else 19) * k)
        ax.text(label_x, mid, money(v), fontproperties=fv, color=INK, va="center_baseline", ha="left")
        ax.text(label_x + (text_width(money(v), fv) + 0.1) * per_in_x, mid, r.label, color=BODY,
                fontsize=13 * k, va="center_baseline", ha="left")
        base += v
    # bracket the two segments no inspector general covers
    bx = x - w / 2 - 0.1
    ax.plot([bx + 0.05, bx, bx, bx + 0.05], [0, 0, no_ig - gap, no_ig - gap], color=INK, lw=1.4, zorder=3,
            clip_on=False)
    ax.text(bx - 0.06, (no_ig - gap) / 2, "No inspector\ngeneral", color=INK, fontsize=14 * k, ha="right",
            va="center", linespacing=1.15)
    ax.set_ylim(0, 560)
    ax.set_xticks([x]); ax.set_xticklabels(["US 101 express lanes"], fontsize=15 * k, color=INK)
    ax.set_yticks(range(0, 501, 100)); ax.set_yticklabels(["0" if t == 0 else f"${t}M" for t in range(0, 501, 100)])
    ax.set_ylabel("Funding, millions of dollars", color=GREY, fontsize=13 * k, labelpad=10)
    ax.set_xlabel("Planned budget by source, 2019", color=GREY, fontsize=13 * k, labelpad=12)
    p.save(OUT / name)


CHARTS = [("express-lanes-funding", funding)]

if __name__ == "__main__":
    setup_font()
    plt.rcParams["text.parse_math"] = False
    social = "--social" in sys.argv
    OUT.mkdir(exist_ok=True)
    for slug, f in CHARTS:
        f("blog", f"{slug}.png")
        if social:
            f("social", f"social-{slug}-4x5.png")
    print(f"Wrote {len(CHARTS) * (2 if social else 1)} charts to {OUT}")
