"""Shared visual style for maxmautner.com charts.

Theme colors, fonts, and a portrait page layout (title, subtitle, grey italic note,
chart area, sources footer, watermark). Per-post chart code imports from here.

Fonts match the blog: Newsreader (serif) for titles and the note, IBM Plex Sans for
everything else. Page wraps its text to the full content width itself, so callers
pass plain strings; a non-breaking space (\\u00a0) keeps 2 words on one line.
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
MARGIN = 0.4                # inches of left and right page margin

_GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
FONTS = {                   # role: (file in fonts/, Google Fonts source)
    "serif": ("Newsreader.ttf", _GF + "newsreader/Newsreader%5Bopsz,wght%5D.ttf"),
    "serif_italic": ("Newsreader-Italic.ttf", _GF + "newsreader/Newsreader-Italic%5Bopsz,wght%5D.ttf"),
    "sans": ("IBMPlexSans.ttf", _GF + "ibmplexsans/IBMPlexSans%5Bwdth,wght%5D.ttf"),
}
SANS = "IBM Plex Sans"


def font_path(role):
    return ROOT / "fonts" / FONTS[role][0]


def setup_font():
    """Download the fonts if needed and make IBM Plex Sans the default. Titles and notes
    use the serif files by path (both Newsreader files share one family name)."""
    for role, (name, url) in FONTS.items():
        path = font_path(role)
        if not path.exists():
            path.parent.mkdir(exist_ok=True)
            try:
                urllib.request.urlretrieve(url, path)
            except Exception:
                print(f"Could not download {name}; falling back to a default font.")
                continue
        fm.fontManager.addfont(str(path))
    plt.rcParams["font.family"] = SANS if font_path("sans").exists() else "sans-serif"


def font(role, size):
    """FontProperties for a role at a size, falling back to the default font."""
    path = font_path(role)
    return fm.FontProperties(fname=str(path), size=size) if path.exists() else fm.FontProperties(size=size)


_MEASURE = {}


def text_width(s, fp):
    """Rendered width of s in inches."""
    if "r" not in _MEASURE:
        fig = plt.figure(dpi=DPI)
        _MEASURE.update(fig=fig, r=fig.canvas.get_renderer())
    t = _MEASURE["fig"].text(0, 0, s, fontproperties=fp)
    w = t.get_window_extent(renderer=_MEASURE["r"]).width / DPI
    t.remove()
    return w


def _greedy(words, fp, width):
    lines, line = [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if line and text_width(trial, fp) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line]


def wrap(s, fp, width, last_width=None, balance=False):
    """Word-wrap s to width inches, ignoring line breaks already in s.

    balance: lines of near-equal length on as few lines as fit (for titles).
    last_width: keep the last line this narrow (room for the watermark).
    A last line is never a single word when the line before it can spare one."""
    words = [w for w in s.replace("\n", " ").split(" ") if w]
    if not words:
        return ""
    lines = _greedy(words, fp, width)
    if balance and len(lines) > 1:
        lo, hi = 0.0, width
        for _ in range(12):        # narrowest width that still fits on the same number of lines
            mid = (lo + hi) / 2
            if len(_greedy(words, fp, mid)) > len(lines):
                lo = mid
            else:
                hi = mid
        lines = _greedy(words, fp, hi)
    if last_width is not None and text_width(lines[-1], fp) > last_width and " " in lines[-1]:
        head, tail = lines[-1].rsplit(" ", 1)
        while " " in head and text_width(head, fp) > last_width:
            head, moved = head.rsplit(" ", 1)
            tail = f"{moved} {tail}"
        lines[-1:] = [head, tail]
    if len(lines) > 1 and " " not in lines[-1] and " " in lines[-2]:
        head, moved = lines[-2].rsplit(" ", 1)
        lines[-2:] = [head, f"{moved} {lines[-1]}"]
    return "\n".join(lines)


class Page:
    """Portrait page. After construction, self.top and self.bottom are the inches
    reserved above and below the chart area. Text spans the full content width
    (the same width the chart gets); pass wrap_text=False to keep the strings' own breaks."""
    def __init__(self, fmt, title, subtitle, note, sources, watermark, wrap_text=True):
        self.W, self.H, self.k = FORMATS[fmt]
        k = self.k
        self.fig = plt.figure(figsize=(self.W, self.H), dpi=DPI, facecolor=BG)
        x0 = MARGIN / self.W
        full = self.W - 2 * MARGIN
        f_wm = font("sans", 13 * k)
        f_src = font("sans", 10 * k)
        rows = [(title, font("serif", 34 * k), INK, 0.18, dict(balance=True)),
                (subtitle, font("sans", 16 * k), BODY, 0.14, {}),
                (note, font("serif_italic", 16 * k), GREY, 0.25, {})]
        y = 0.35
        for txt, fp, color, gap, opts in rows:
            if wrap_text:
                txt = wrap(txt, fp, full, **opts)
            t = self.fig.text(x0, 1 - y / self.H, txt, fontproperties=fp, color=color, va="top", ha="left", linespacing=1.2)
            y += self._height(t) + gap
        self.top = y
        if wrap_text:
            sources = wrap(sources, f_src, full, last_width=full - text_width(watermark, f_wm) - 0.3)
        self.bottom = 0.3 + (sources.count("\n") + 1) * f_src.get_size() * LH * 1.1 + 0.2
        self.fig.text(x0, 0.25 / self.H, sources, fontproperties=f_src, color=GREY, va="bottom", ha="left", linespacing=1.4)
        self.fig.text(1 - x0, 0.25 / self.H, watermark, fontproperties=f_wm, color=GREY, va="bottom", ha="right")

    def _height(self, t):
        """Rendered height of a text artist in inches, so spacing follows the font's real metrics."""
        return t.get_window_extent(renderer=self.fig.canvas.get_renderer()).height / DPI

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
