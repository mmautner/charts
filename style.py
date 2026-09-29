"""Shared visual style for maxmautner.com charts.

Theme colors, font setup, and a portrait page layout (title, subtitle, grey note,
chart area, sources footer, watermark). Per-post chart code imports from here.
"""
import os, urllib.request
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

ROOT = Path(__file__).resolve().parent
BG, INK, GREY, LIGHT, COPPER, DOT, BODY = "#f9f7f2", "#1c1c1c", "#8a8680", "#dedad0", "#b5763c", "#d9d5cb", "#333333"
DPI = 150
FORMATS = {                 # width in, height in (at 150 dpi), font scale
    "blog": (8, 12, 1.0),   # 1200 x 1800, 2:3, for the post itself
    "social": (7.2, 9, 0.9),  # 1080 x 1350, 4:5, the tallest Instagram allows
}
LH = 1 / 72 * 1.3           # inches of line height per point of font size

FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/lora/Lora%5Bwght%5D.ttf"
FONT_PATH = ROOT / "fonts" / "Lora.ttf"

def setup_font():
    if not FONT_PATH.exists():
        FONT_PATH.parent.mkdir(exist_ok=True)
        try:
            urllib.request.urlretrieve(FONT_URL, FONT_PATH)
        except Exception:
            print("Could not download Lora; falling back to the default serif.")
            plt.rcParams["font.family"] = "serif"
            return
    fm.fontManager.addfont(str(FONT_PATH))
    plt.rcParams["font.family"] = "Lora"

class Page:
    """Portrait page. After construction, self.top and self.bottom are the inches
    reserved above and below the chart area."""
    def __init__(self, fmt, title, subtitle, note, sources, watermark):
        self.W, self.H, self.k = FORMATS[fmt]
        k = self.k
        self.fig = plt.figure(figsize=(self.W, self.H), dpi=DPI, facecolor=BG)
        x0 = 0.4 / self.W
        y = 0.35
        for txt, size, color, gap in [(title, 34 * k, INK, 0.18), (subtitle, 17 * k, BODY, 0.14), (note, 15 * k, GREY, 0.25)]:
            self.fig.text(x0, 1 - y / self.H, txt, fontsize=size, color=color, va="top", ha="left", linespacing=1.2)
            y += (txt.count("\n") + 1) * size * LH * 1.02 + gap
        self.top = y
        self.bottom = 0.3 + (sources.count("\n") + 1) * 10 * k * LH * 1.1 + 0.2
        self.fig.text(x0, 0.25 / self.H, sources, fontsize=10 * k, color=GREY, va="bottom", ha="left", linespacing=1.4)
        self.fig.text(1 - x0, 0.25 / self.H, watermark, fontsize=13 * k, color=GREY, va="bottom", ha="right")

    def yf(self, inches_from_top):
        return 1 - inches_from_top / self.H

    def save(self, path):
        self.fig.savefig(path, facecolor=BG)
        plt.close(self.fig)

def style_axes(ax, k):
    """Line-chart axes: no spines, light horizontal grid, grey ticks."""
    ax.set_facecolor(BG)
    ax.tick_params(colors=GREY, labelsize=14 * k, length=0, pad=8)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.grid(axis="y", color=LIGHT, lw=1)
    ax.set_axisbelow(True)
