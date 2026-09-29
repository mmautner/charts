"""Render this post's charts into output/."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # repo root, for style.py

import matplotlib.pyplot as plt
import numpy as np
from style import BG, INK, GREY, LIGHT, COPPER, DOT, BODY, DPI, Page, setup_font, style_axes
from model import lifetime_counts, p_know_killed, p_know_killed_rate, load_population
from inputs import NETWORK_SIZE_MEAN, ROAD_DEATHS_PER_100K

WATERMARK = "maxmautner.com/crashes"
OUT = HERE / "output"

def dot_colors(n, killed, serious):
    return [INK if i < killed else (COPPER if i < killed + serious else DOT) for i in range(n)]

def icon_array(fmt, name):
    killed, serious = (round(x) for x in lifetime_counts())
    n = NETWORK_SIZE_MEAN
    cols = 20 if fmt == "blog" else 24
    rows = int(np.ceil(n / cols))
    p = Page(fmt, f"~{killed} people you know\nwill die in a crash",
             f"Lifetime outcomes among the ~{n} people the\naverage American knows. Each dot is 1 person.",
             "Assumes each acquaintance faces average risk.",
             "Sources: NSC Injury Facts, lifetime odds of crash death 1 in 101;\n"
             "McCormick, Salganik & Zheng (2010), network size;\n"
             "NHTSA DOT HS 813 403, MAIS 3+ injuries per death, 2019.", WATERMARK)
    grid_w = min(p.W * 0.55, (p.H - p.top - p.bottom) * cols / rows)
    grid_h = grid_w * rows / cols
    ax = p.fig.add_axes([0.4 / p.W, p.yf(p.top + grid_h), grid_w / p.W, grid_h / p.H])
    ax.set_facecolor(BG)
    ax.scatter([i % cols for i in range(n)], [-(i // cols) for i in range(n)],
               c=dot_colors(n, killed, serious), s=62 if fmt == "blog" else 44, linewidths=0)
    ax.set_xlim(-0.8, cols - 0.2); ax.set_ylim(-rows + 0.2, 0.8); ax.axis("off")
    cx, k, y = (0.4 + grid_w + 0.35) / p.W, p.k, p.top - 0.05
    for big, color, small in [(f"~{killed}", INK, "Killed in a crash."),
                              (f"~{serious}", COPPER, "Survive a serious\ninjury, like a\nfractured skull or\nspinal cord injury.")]:
        p.fig.text(cx, p.yf(y), big, fontsize=48 * k, color=color, va="top"); y += 48 * k / 72 * 1.15
        p.fig.text(cx, p.yf(y), small, fontsize=17 * k, color=BODY, va="top", linespacing=1.3); y += 0.75
    p.save(OUT / name)

def curve(fmt, name, pop):
    age = np.linspace(18, 80, 500)
    at40 = 100 * p_know_killed(40, pop)
    assert 77 <= at40 <= 82, f"Title says ~4 in 5 but the model gives {at40:.0f}% at 40"
    p = Page(fmt, "By 40, ~4 in 5 Americans\nhave lost someone they\nknow to a crash",
             "Chance an American knows at least 1 person\nkilled in a crash, by age",
             f"Assumes a network of ~{NETWORK_SIZE_MEAN} people from age 18.",
             "Sources: NSC Injury Facts, crash deaths (2024); Census Vintage\n"
             f"2025, population {pop/1e6:.1f}M (2024); McCormick, Salganik & Zheng (2010),\n"
             f"network ~{NETWORK_SIZE_MEAN}. Assumes average risk and independent events.", WATERMARK)
    k, pad = p.k, 0.65
    ax = p.fig.add_axes([0.95 / p.W, (p.bottom + pad) / p.H, (p.W - 1.35) / p.W,
                         (p.H - p.top - p.bottom - pad) / p.H])
    style_axes(ax, k)
    ax.plot(age, 100 * p_know_killed(age, pop), color=INK, lw=4)
    ax.set_xlim(18, 80); ax.set_ylim(0, 104)
    ax.set_yticks([0, 25, 50, 75, 100]); ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_xticks(range(20, 81, 10))
    ax.set_xlabel("Age", color=GREY, fontsize=14 * k, labelpad=6)
    for a in (30, 40):
        v = 100 * p_know_killed(a, pop)
        ax.plot([a], [v], "o", color=COPPER, ms=11 * k)
        ax.text(a + 1.5, v - 3, f"~{v:.0f}% by {a}", fontsize=19 * k, color=COPPER, va="top")
    p.save(OUT / name)

def country_curves(fmt, name):
    """International variant of the curve: same model, each country's death rate."""
    age = np.linspace(18, 80, 500)
    at40 = {c: 100 * p_know_killed_rate(40, r) for c, r in ROAD_DEATHS_PER_100K.items()}
    us, jp = round(at40["United States"] / 10), round(at40["Japan"] / 10)
    p = Page(fmt, f"By 40, ~{us} in 10 Americans\nhave lost someone they know\nto a crash. In Japan, ~{jp} in 10.",
             "Chance of knowing at least 1 person killed\nin a crash, by age",
             f"Assumes the same ~{NETWORK_SIZE_MEAN}-person network in every country.",
             "Sources: BITRE, Road Safety International Comparisons 2023 (IRTAD),\n"
             "road deaths per 100,000, 2023; ITF Mexico country profile, 2022;\n"
             "McCormick, Salganik & Zheng (2010), US network ~611.", WATERMARK)
    k, pad = p.k, 0.65
    right = 2.3 if fmt == "blog" else 2.1   # room for end-of-line labels
    ax = p.fig.add_axes([0.95 / p.W, (p.bottom + pad) / p.H, (p.W - 0.95 - right) / p.W,
                         (p.H - p.top - p.bottom - pad) / p.H])
    style_axes(ax, k)
    style = {"United States": (COPPER, "-", 4.5), "Mexico": (GREY, (0, (2, 2)), 2.5),
             "Canada": (INK, "-", 2.5), "Germany": (INK, "-", 2.5), "Japan": (INK, "-", 2.5)}
    for c, r in ROAD_DEATHS_PER_100K.items():
        color, ls, lw = style[c]
        ax.plot(age, 100 * p_know_killed_rate(age, r), color=color, ls=ls, lw=lw)
    ax.axvline(40, color=LIGHT, lw=1.5, zorder=0)
    ax.set_xlim(18, 80); ax.set_ylim(0, 104)
    ax.set_yticks([0, 25, 50, 75, 100]); ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_xticks(range(20, 81, 10))
    ax.set_xlabel("Age", color=GREY, fontsize=14 * k, labelpad=6)
    # country names at the right end of each line
    ends = {c: 100 * p_know_killed_rate(80, r) for c, r in ROAD_DEATHS_PER_100K.items()}
    names = [("United States", COPPER, ends["United States"] + 1),
             ("Mexico (dashed)", GREY, ends["Mexico"] - 7),
             ("Canada", INK, ends["Canada"]), ("Germany", INK, ends["Germany"]), ("Japan", INK, ends["Japan"])]
    for text, color, y in names:
        ax.text(81, y, text, fontsize=15 * k, color=color, va="center", ha="left", clip_on=False)
    # values at age 40, on the lines
    box = dict(boxstyle="square,pad=0.15", fc=BG, ec="none")
    marks = [("United States", COPPER, f"~{at40['United States']:.0f}% (US and Mexico)", 0),
             ("Canada", INK, f"~{at40['Canada']:.0f}%", 0),
             ("Germany", INK, f"~{at40['Germany']:.0f}%", 1.5),
             ("Japan", INK, f"~{at40['Japan']:.0f}%", -3.5)]
    for c, color, text, dy in marks:
        v = at40[c]
        ax.plot([40], [v], "o", color=color, ms=9 * k, zorder=5)
        ax.text(41.5, v + dy - 2.5, text, fontsize=15 * k, color=color, va="top", ha="left", bbox=box, zorder=6)
    p.save(OUT / name)

def og_image(name):
    """1200 x 630 link-preview image for the post's og:image."""
    killed, serious = (round(x) for x in lifetime_counts())
    n, cols = NETWORK_SIZE_MEAN, 26
    rows = int(np.ceil(n / cols))
    fig = plt.figure(figsize=(8, 4.2), dpi=DPI, facecolor=BG)
    fig.text(0.05, 0.88, f"~{killed} people you know\nwill die in a crash", fontsize=30, color=INK, va="top", linespacing=1.15)
    fig.text(0.05, 0.50, f"~{serious} more will survive a\nserious injury.", fontsize=17, color=COPPER, va="top", linespacing=1.3)
    fig.text(0.05, 0.08, WATERMARK, fontsize=12, color=GREY, va="bottom")
    ax = fig.add_axes([0.60, 0.08, 0.36, 0.84]); ax.set_facecolor(BG)
    ax.scatter([i % cols for i in range(n)], [-(i // cols) for i in range(n)],
               c=dot_colors(n, killed, serious), s=14, linewidths=0)
    ax.set_xlim(-0.8, cols - 0.2); ax.set_ylim(-rows + 0.2, 0.8); ax.axis("off")
    fig.savefig(OUT / name, facecolor=BG); plt.close(fig)

if __name__ == "__main__":
    setup_font()
    OUT.mkdir(exist_ok=True)
    pop = load_population()
    icon_array("blog", "acquaintances-sorted.png")
    icon_array("social", "social-acquaintances-4x5.png")
    curve("blog", "knowing-a-victim-by-age.png", pop)
    curve("social", "social-knowing-a-victim-4x5.png", pop)
    og_image("og-image.png")
    country_curves("blog", "knowing-a-victim-by-country.png")
    country_curves("social", "social-knowing-a-victim-by-country-4x5.png")
    print(f"Wrote 7 charts to {OUT}")
