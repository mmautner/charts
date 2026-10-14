"""Render this post's charts into output/."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # repo root, for style.py

import matplotlib.pyplot as plt
from style import BG, INK, GREY, COPPER, DOT, BODY, DPI, Page, setup_font
from model import scooters, check_pick_2, TRAITS

WATERMARK = "maxmautner.com/kickscooter"
OUT = HERE / "output"
HEADS = ["Under\n10 lb", "200 mm+\nwheels", "Hand\nbrake"]
SOURCES = (
    "Weights as listed by Razor, Micro, Decathlon, and\n"
    "Scooter4US (Xootr), Oct 2026; kg converted to lb.\n"
    "Method: github.com/mmautner/charts")

def bare(ax):
    ax.set_facecolor(BG); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

def grid(ax, rows, k, name_fs, val_fs, head_fs, dot, bar_h=0.42):
    """Weight bars on the left, one dot column per trait on the right."""
    xmax, cols = 34, [24.2, 28.4, 32.4]
    n = len(rows)
    for i, (m, lb, _, traits) in enumerate(rows):
        y = n - 1 - i
        ax.barh(y, lb, height=bar_h, color=INK)
        ax.text(0, y + bar_h / 2 + 0.08, m, fontsize=name_fs * k, color=BODY, va="bottom")
        ax.text(lb + 0.3, y, f"{lb:.1f} lb", fontsize=val_fs * k, color=INK, va="center")
        for x, on in zip(cols, traits):
            ax.scatter(x, y, s=dot * k, color=COPPER if on else DOT, zorder=3, clip_on=False)
    for x, h in zip(cols, HEADS):
        ax.text(x, n - 0.15, h, fontsize=head_fs * k, color=INK, ha="center", va="bottom", linespacing=1.05)
    ax.set_xlim(0, xmax); ax.set_ylim(-0.5, n + 0.55); bare(ax)

def pick2_chart(fmt, name):
    rows = scooters()
    check_pick_2(rows)
    p = Page(fmt, "Light, big wheels,\nhand brake: pick 2",
             f"None of {len(rows)} popular adult\nkickscooters has all 3",
             "Every pound gets carried up the stairs.",
             SOURCES, WATERMARK)
    ax = p.fig.add_axes([0.4 / p.W, (p.bottom + 0.2) / p.H, (p.W - 0.8) / p.W, (p.H - p.top - p.bottom - 0.2) / p.H])
    grid(ax, rows, p.k, 15, 15, 12, 260, bar_h=0.42 if fmt == "blog" else 0.32)
    p.save(OUT / name)

def og_image(name):
    """1200 x 630 link-preview image: one model for each of the 3 pairs."""
    rows = scooters()
    first_for_pair = []
    for skip in range(3):
        first_for_pair.append(next(r for r in rows if all(r[3][i] for i in range(3) if i != skip)))
    fig = plt.figure(figsize=(8, 4.2), dpi=DPI, facecolor=BG)
    fig.text(0.05, 0.9, "Light, big wheels,\nhand brake: pick 2", fontsize=26, color=INK, va="top", linespacing=1.15)
    fig.text(0.05, 0.08, WATERMARK, fontsize=12, color=GREY, va="bottom")
    ax = fig.add_axes([0.05, 0.2, 0.9, 0.42])
    grid(ax, sorted(first_for_pair, key=lambda r: r[1]), 1, 12, 12, 10, 150)
    fig.savefig(OUT / name, facecolor=BG); plt.close(fig)

if __name__ == "__main__":
    setup_font()
    OUT.mkdir(exist_ok=True)
    pick2_chart("blog", "pick-2.png")
    pick2_chart("social", "social-pick-2-4x5.png")
    og_image("og-image.png")
    print(f"Wrote 3 charts to {OUT}")
