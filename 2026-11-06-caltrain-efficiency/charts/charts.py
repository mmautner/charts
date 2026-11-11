"""Render this post's chart into output/ from data/estimates.csv.
usage (from the post folder): python charts/charts.py [--social]

3 stacked columns on one scale, each from zero: the 6 strategies Caltrain adopted, the 3 options its own
documents point to that it left out, and the average yearly deficit Measure RTM's ~$75 million is meant to
cover. Segments are the midpoint of each estimate range; segment labels give each full range."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
POST = HERE.parent
sys.path.insert(0, str(POST.parent))  # repo root, for style.py

import matplotlib.pyplot as plt
import pandas as pd
from style import BG, INK, GREY, LIGHT, COPPER, BODY, Page, font, setup_font, style_axes, text_width

WATERMARK = "maxmautner.com/caltrain-efficiency"
DATA, OUT = POST / "data", POST / "output"
BLUE = "#2f6fb0"           # adopted strategies; validated against BG with copper (dataviz validate_palette.js)
DEFICIT_COLOR = "#8a8680"  # neutral: a reference amount, not a category; carries a direct label
RTM = 75                   # Caltrain's ~$75M a year from Measure RTM (JPB resolution, June 4, 2026, packet p. 94)
DEFICIT = 75               # average yearly deficit Caltrain projects FY27-FY34 (Hatch/JPB deck, Apr. 2025);
                           # ~equal to Caltrain's ~$75M a year from Measure RTM (JPB resolution, June 4, 2026)

SMALL = ["More GoPass employers", "Parking revenue", "Fiber leasing", "Station retail study", "Energy storage study"]
NAMES = {                  # (name line, suffix after the range on the second line)
    "Operator contract efficiencies": ("Operator contract", ""),
    "small": ("5 smaller items", ""),
    "Engineer plus 1 conductor in 2029 rebid": ("2-person crews", ""),
    "Tie 10 extra trains to measured crowding": ("Federal waiver", ""),
    "Ground leases on surplus lots and Diridon": ("Ground leases", ", 2030s"),
}

# Sizes in points before the format's scale k. Big on purpose: the blog image shows ~3x smaller on a phone.
SIZE = {"label": 22, "column": 26, "deficit": 20, "tick": 19}
LEFT_IN = 0.95             # inches from the page edge to the plot; the y ticks carry the units, no axis title


def chart_area(p, top_gap=0.35, bottom_gap=0.85, left=LEFT_IN, right=0.4):
    return p.fig.add_axes([left / p.W, (p.bottom + bottom_gap) / p.H, (p.W - left - right) / p.W,
                           (p.H - p.top - p.bottom - top_gap - bottom_gap) / p.H])


def fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def rng(lo, hi):
    return f"${fmt(lo)}–{fmt(hi)}M"


def segments(d):
    """Column segments, bottom to top: (key, low, high, color, hatched)."""
    a = d[d.group == "adopted"].set_index("item")
    o = d[d.group == "option"].set_index("item")
    small = a.loc[SMALL]
    adopted = [("Operator contract efficiencies", *a.loc["Operator contract efficiencies", ["low_millions", "high_millions"]],
                BLUE, False),
               ("small", small.low_millions.sum(), small.high_millions.sum(), BLUE, False)]
    left_out = [(k, *o.loc[k, ["low_millions", "high_millions"]], COPPER, "Ground leases" in k) for k in o.index]
    return adopted, left_out


def label_text(key, lo, hi):
    name, suffix = NAMES[key]
    return f"{name}\n{rng(lo, hi)}{suffix}"


def spread(ys, min_gap):
    """Nudge label y positions apart (bottom to top) so none sit closer than min_gap."""
    out = []
    for y in ys:
        out.append(max(y, out[-1] + min_gap) if out else y)
    return out


def estimates(fmt_name, name):
    d = pd.read_csv(DATA / "estimates.csv")
    adopted, left_out = segments(d)
    a_lo, a_hi = sum(s[1] for s in adopted), sum(s[2] for s in adopted)
    o_lo, o_hi = sum(s[1] for s in left_out), sum(s[2] for s in left_out)
    assert (round(a_lo), round(a_hi)) == (5, 11), "column totals: ~$5-11 million"
    assert (round(o_lo), round(o_hi)) == (20, 32), "column totals: ~$20-32 million"

    p = Page(fmt_name,
             f"Caltrain gets ~${RTM} million a year from Measure RTM. Its cost cutting skips the biggest savings.",
             "My estimates of yearly savings or new revenue by fiscal 2030. Neither Caltrain nor MTC put a dollar "
             "figure on any strategy.",
             "",
             "Sources: author's estimates from Caltrain board packets (2025–2026), Hatch non-fare revenue study "
             "(2025) and MTC's Phase 1 efficiency review (2026). Segments are range midpoints. 5 smaller items: "
             "parking, GoPass, fiber leasing, station retail, energy storage. Federal waiver: tying 10 extra trains "
             "to crowding, a cost avoided from 2028 if the FTA agrees. Deficit: Caltrain's projected yearly "
             "average, fiscal 2027–2034. Measure RTM: Caltrain budget resolution, June 4, 2026. Each estimate's "
             "basis is in the chart data.",
             WATERMARK)
    k = p.k
    blog = fmt_name == "blog"
    ax = chart_area(p)
    style_axes(ax, k)
    ax.tick_params(axis="y", labelsize=SIZE["tick"] * k)
    pos = ax.get_position()
    w_in, h_in = pos.width * p.W, pos.height * p.H
    ymax = 85
    per_in = ymax / h_in                   # $M per inch
    lab_size = (SIZE["label"] if blog else 20) * k
    lab_fp = font("sans", lab_size)
    lab_h = 2 * 1.4 * lab_size / 72                    # a 2-line label's rendered height, inches
    half = lab_h / 2 * per_in                           # ... in $M

    # x positions in inches from the plot's left edge, sized to the labels so the larger text always fits
    col_w = (0.65 if blog else 0.58) * k
    pad = (0.25 if blog else 0.42) * k
    widest = lambda segs: max(text_width(line, lab_fp) for s in segs for line in label_text(*s[:3]).split("\n"))
    x1 = 0.05 + col_w / 2
    lx1 = x1 + col_w / 2 + pad
    x2 = lx1 + widest(adopted) + 0.12 * k + col_w / 2
    lx2 = x2 + col_w / 2 + pad
    assert lx2 + widest(left_out) <= w_in + 0.01, f"labels overflow: {lx2 + widest(left_out):.2f} > {w_in:.2f}"
    ax.set_xlim(0, w_in)
    ax.set_ylim(0, ymax)
    gap = 0.03 * per_in                    # thin background gap between stacked segments

    def column(x, lx, segs):
        base, mids = 0, []
        for key, lo, hi, color, hatched in segs:
            mid = (lo + hi) / 2
            ax.bar(x, mid - gap, bottom=base, width=col_w, color=BG if hatched else color, edgecolor=color,
                   hatch="///" if hatched else None, lw=1.6 if hatched else 0, zorder=2)
            mids.append((base + (mid - gap) / 2, key, lo, hi))
            base += mid
        # labels to the right, spaced well apart (there is room above the columns); leaders where they moved
        # labels sit beside their own segment when there's room; only a label pushed clear of its segment
        # gets a leader. With several leaders, the lowest bends farthest out so no lines cross.
        ys = spread([max(m[0], half) for m in mids], 2 * half + (0.2 if blog else 0.12) * per_in)
        edge = x + col_w / 2
        # every label gets a leader: a reader (Adam, Nov. 2026) found an unleadered label beside its own
        # segment harder to match than the leadered ones
        moved = list(range(len(mids)))
        for n, i in enumerate(moved):
            ymid, y = mids[i][0], ys[i]
            name_y = y + half / 2          # the label's first (name) line
            elbow = edge + (lx - edge) * (0.75 - 0.4 * n / max(len(moved) - 1, 1))
            ax.plot([edge, elbow, elbow, lx - 0.05], [ymid, ymid, name_y, name_y], color=BODY, lw=1.3,
                    zorder=3, solid_joinstyle="miter")
            ax.plot([edge], [ymid], "o", color=BODY, ms=5 * k, zorder=4)
        for (ymid, key, lo, hi), y in zip(mids, ys):
            ax.text(lx, y, label_text(key, lo, hi), ha="left", va="center", color=BODY, linespacing=1.12,
                    fontproperties=lab_fp)

    column(x1, lx1, adopted)
    column(x2, lx2, left_out)
    ax.axhline(DEFICIT, color=INK, lw=1.6, ls=(0, (5, 3)), zorder=3)
    if blog:
        ax.text(w_in - 0.02, DEFICIT - 0.12 * per_in, f"Caltrain's average yearly deficit\nthrough 2034: ~${DEFICIT}M, "
                "about\nwhat Measure RTM gives it", ha="right", va="top", color=INK, fontsize=SIZE["deficit"] * k,
                linespacing=1.2)
    else:                                  # the social plot is short: 1 line
        ax.text(w_in - 0.02, DEFICIT - 0.1 * per_in, f"Average yearly deficit through 2034: ~${DEFICIT}M",
                ha="right", va="top", color=INK, fontsize=SIZE["deficit"] * k)

    # column names left-aligned with each column's left edge
    ax.set_xticks([])
    for x, label in zip([x1, x2], ["Adopted strategies", "Options left out"]):
        ax.annotate(label, xy=(x - col_w / 2, 0), xycoords=("data", "axes fraction"), xytext=(0, -10 * k),
                    textcoords="offset points", ha="left", va="top", color=INK,
                    fontproperties=font("serif", SIZE["column"] * k))
    ax.set_yticks(range(0, 81, 20))
    ax.set_yticklabels(["0"] + [f"${t}M" for t in range(20, 81, 20)])
    p.save(OUT / name)


CHARTS = [("caltrain-strategies", estimates)]

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
