"""Render this post's chart into output/ from data/estimates.csv.
usage (from the post folder): python charts/charts.py [--social]

2 stacked columns on one scale, from zero: the 9 strategies BART adopted (grouped into revenue and cost
items), and the same strategies with 3 options BART's 2027 union contracts will decide stacked on top, against a
dashed line at the $57 million deficit BART projects for fiscal 2028 even with Measure RTM. Segments are the
midpoint of each estimate range; segment labels give each full range."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
POST = HERE.parent
sys.path.insert(0, str(POST.parent))  # repo root, for style.py

import matplotlib.pyplot as plt
import pandas as pd
from style import BG, INK, GREY, LIGHT, COPPER, BODY, Page, font, setup_font, style_axes, text_width

WATERMARK = "maxmautner.com/bart-efficiency"
DATA, OUT = POST / "data", POST / "output"
BLUE = "#2f6fb0"           # adopted strategies; validated against BG with copper (dataviz validate_palette.js)
DEFICIT_COLOR = "#8a8680"  # neutral: a reference amount, not a category; carries a direct label
RTM = 310                  # BART's ~$310M a year from Measure RTM (BART response to grand jury report 2608, F16)
DEFICIT = 57               # FY28 net result with Measure RTM, BART five-year outlook (June 11, 2026 budget deck, p. 7)

NAMES = {                  # (name line, suffix after the range on the second line)
    "revenue": ("5 revenue items", ""),
    "cost": ("4 cost items", ""),
    "overtime": ("Overtime rules", ""),
    "staffing": ("Station staffing", ""),
    "automation": ("Driverless trains", ", 2030s"),
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
    a = d[d.group == "adopted"].groupby("segment", sort=False)[["low_millions", "high_millions"]].sum()
    o = d[d.group == "option"].set_index("segment")
    adopted = [(k, a.loc[k, "low_millions"], a.loc[k, "high_millions"], BLUE, False) for k in ["revenue", "cost"]]
    left_out = [(k, o.loc[k, "low_millions"], o.loc[k, "high_millions"], COPPER, k == "automation")
                for k in ["overtime", "staffing", "automation"]]
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
    assert (round(a_lo), round(a_hi)) == (5, 18), "column totals: ~$5-18 million"
    assert (round(o_lo), round(o_hi)) == (69, 105), "column totals: ~$69-105 million"

    p = Page(fmt_name,
             "Driverless trains could save BART ~$50–75 million a year, about the size of its deficit after "
             "Measure RTM.",
             # social: the caveat joins the subtitle, since a separate note squeezed the plot until labels collided
             "My estimates of yearly savings or new revenue. Neither BART nor MTC put a dollar figure on any "
             "strategy." + ("" if fmt_name == "blog" else " Driverless trains: 2030s, before equipment costs."),
             "Driverless trains: not before the 2030s, and before the cost of platform doors and other equipment."
             if fmt_name == "blog" else "",
             "Sources: author's estimates from BART budgets (2025–2026), BART's Inspector General overtime audit "
             "(2025), Contra Costa grand jury report 2608 and BART's response (2026), and MTC's Phase 1 efficiency "
             "review (2026). Segments are range midpoints. Revenue items: parking, fare gates, fiber and cell "
             "leasing, BayPass, station retail. Cost items: shorter trains, insurance and paratransit contracts, "
             "SFO lease, speed and reliability study. Driverless trains: after the new train control system, "
             "capital costs not included. Deficit: BART's fiscal 2028 forecast with Measure RTM, June 11, 2026. "
             "Each estimate's basis is in the chart data.",
             WATERMARK)
    k = p.k
    blog = fmt_name == "blog"
    ax = chart_area(p)
    style_axes(ax, k)
    ax.tick_params(axis="y", labelsize=SIZE["tick"] * k)
    pos = ax.get_position()
    w_in, h_in = pos.width * p.W, pos.height * p.H
    ymax = 115
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

    def column(x, lx, segs, under=()):
        """Stack `under` first, unlabeled, then `segs` with labels on top of it."""
        base, mids = 0, []
        for key, lo, hi, color, hatched in under:
            mid = (lo + hi) / 2
            ax.bar(x, mid - gap, bottom=base, width=col_w, color=color, lw=0, zorder=2)
            base += mid
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
            # a background box knocks the dashed deficit line out behind any label it crosses (social format)
            ax.text(lx, y, label_text(key, lo, hi), ha="left", va="center", color=BODY, linespacing=1.12,
                    fontproperties=lab_fp, zorder=5, bbox=dict(facecolor=BG, edgecolor="none", pad=1))

    column(x1, lx1, adopted)
    # the options left out stack on top of the adopted strategies: they would add to them, not replace them
    # (2 readers, Nov. 2026, read separate columns as alternatives rather than cumulative)
    column(x2, lx2, left_out, under=adopted)
    ax.axhline(DEFICIT, color=INK, lw=1.6, ls=(0, (5, 3)), zorder=3)
    # the line's label sits at its left end, just above it, so readers learn what the line is as they meet it
    # (a reader, John, Nov. 2026, took a moment to read the line when its label was at the far right, below it)
    # the line's label sits at its left end, just above it, in the clear space left of the second column
    # (2 lines: on 1 line it ran through the second column and its labels)
    line_label = f"${DEFICIT}M deficit left in\nfiscal 2028, after RTM"
    line_fp = font("sans", SIZE["deficit"] * k)
    room = x2 - col_w / 2 - 0.15 * k
    assert 0.05 + max(text_width(l, line_fp) for l in line_label.split("\n")) <= room, "deficit label overflows"
    ax.text(0.05, DEFICIT + 0.08 * per_in, line_label, ha="left", va="bottom", color=INK, linespacing=1.1,
            fontproperties=line_fp)

    # column names left-aligned with each column's left edge
    ax.set_xticks([])
    for x, label in zip([x1, x2], ["Adopted strategies", "Plus contract options"]):
        ax.annotate(label, xy=(x - col_w / 2, 0), xycoords=("data", "axes fraction"), xytext=(0, -10 * k),
                    textcoords="offset points", ha="left", va="top", color=INK,
                    fontproperties=font("serif", SIZE["column"] * k))
    ax.set_yticks([0, 20, 40, 100])  # no $60M or $80M ticks: they would run through the deficit label
    ax.set_yticklabels(["0", "$20M", "$40M", "$100M"])
    p.save(OUT / name)


CHARTS = [("bart-strategies", estimates)]

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
