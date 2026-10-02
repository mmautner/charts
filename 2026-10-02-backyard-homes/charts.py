"""Render this post's charts into output/."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # repo root, for style.py

from style import BG, INK, GREY, LIGHT, COPPER, Page, setup_font, style_axes
from model import YEARS, load_hcd

WATERMARK = "maxmautner.com"
OUT = HERE / "output"
SOURCES_APR = "HCD Housing Element Annual Progress Reports, Table A2"

def plot_area(p, right=1.9):
    pad = 0.65
    ax = p.fig.add_axes([0.95 / p.W, (p.bottom + pad) / p.H, (p.W - 0.95 - right) / p.W,
                         (p.H - p.top - p.bottom - pad) / p.H])
    style_axes(ax, p.k)
    return ax

def adu_vs_houses(fmt, name, adu, sfd, mf5, fetched):
    """ADUs vs detached houses and units in buildings of 5+, all from the same APR reports."""
    ys = [y for y in YEARS if y in adu]
    a, h, m = ([d[y] for y in ys] for d in (adu, sfd, mf5))
    last, r = ys[-1], adu[ys[-1]] / sfd[ys[-1]]
    if r >= 1:
        title = "California now permits\nmore backyard homes\nthan houses"
    else:
        assert r >= 0.9, f"Title says 'nearly as many' but ADUs/houses = {r:.2f}"
        title = "California now permits\nnearly as many backyard\nhomes as houses"
    p = Page(fmt, title, "Units permitted per year",
             f"In {last}: {a[-1]:,} ADUs, {h[-1]:,} detached houses.",
             f"Source: {SOURCES_APR}\n(fetched {fetched}). All 3 lines come from the same city reports.", WATERMARK)
    ax = plot_area(p, right=2.1)
    ax.plot(ys, m, color=GREY, lw=2.5)
    ax.plot(ys, h, color=INK, lw=4)
    ax.plot(ys, a, color=COPPER, lw=4)
    top = max(m + h + a) * 1.15
    ax.set_ylim(0, top); ax.set_xlim(ys[0], last)
    ax.set_xticks(ys[::2] if fmt == "social" else ys)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v/1000:.0f}k")
    k = p.k
    # end labels, nudged apart where lines finish close together
    ya, yh = a[-1], h[-1]
    need = top * 0.07
    if abs(ya - yh) < need:
        mid, sign = (ya + yh) / 2, (1 if ya >= yh else -1)
        ya, yh = mid + sign * need / 2, mid - sign * need / 2
    for y, text, color in [(ya, "ADUs", COPPER), (yh, "Detached\nhouses", INK),
                           (m[-1], "Buildings of\n5+ units", GREY)]:
        ax.text(last + 0.25, y, text, color=color, fontsize=17 * k, va="center",
                clip_on=False, linespacing=1.2)
    p.save(OUT / name)

def adu_share(fmt, name, adu, total, fetched):
    ys = [y for y in YEARS if y in adu]
    s = [100 * adu[y] / total[y] for y in ys]
    p = Page(fmt, f"ADUs were {s[-1]:.0f}% of new\nCalifornia homes in {ys[-1]}",
             "ADU share of all units permitted statewide",
             f"Up from {s[0]:.0f}% in {ys[0]}.",
             f"Source: {SOURCES_APR}\n(fetched {fetched}).", WATERMARK)
    ax = plot_area(p, right=0.5)
    ax.bar(ys, s, color=COPPER, width=0.65)
    for y, v in zip(ys, s):
        ax.text(y, v + 0.8, f"{v:.0f}%", ha="center", va="bottom", fontsize=14 * p.k, color=INK)
    ax.set_ylim(0, max(s) * 1.2); ax.set_yticks([]); ax.grid(False)
    ax.set_xticks(ys)
    ax.tick_params(axis="x", labelsize=(14 if fmt == "blog" else 11) * p.k)
    p.save(OUT / name)

if __name__ == "__main__":
    import json
    setup_font()
    OUT.mkdir(exist_ok=True)
    adu, total, _, mf5, sfd = load_hcd()
    fetched = json.loads((HERE / "data" / "hcd_a2_meta.json").read_text())["fetched_on"]
    adu_vs_houses("blog", "adu-vs-houses.png", adu, sfd, mf5, fetched)
    adu_vs_houses("social", "social-adu-vs-houses-4x5.png", adu, sfd, mf5, fetched)
    adu_share("blog", "adu-share.png", adu, total, fetched)
    adu_share("social", "social-adu-share-4x5.png", adu, total, fetched)
    print(f"Wrote 4 charts to {OUT}")
