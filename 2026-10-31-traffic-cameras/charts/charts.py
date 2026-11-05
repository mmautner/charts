"""Render this post's charts into output/ from data/ (speed_cameras_chicago.csv, red_light_cameras.csv,
camera_communities.csv, chicago_ticket_burden.csv).
usage (from the post folder): python charts/charts.py [--social]"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
POST = HERE.parent
sys.path.insert(0, str(POST.parent))  # repo root, for style.py

import matplotlib.pyplot as plt
import pandas as pd
from style import BG, INK, GREY, LIGHT, COPPER, BODY, Page, font, setup_font, style_axes

WATERMARK = "maxmautner.com/traffic-cameras"
DATA, OUT = POST / "data", POST / "output"
BLUE = "#2f6c9e"                              # pair with COPPER checked with the dataviz validator
MINUS = "−"


def chart_area(p, top_gap=0.3, bottom_gap=0.85, left=1.0, right=0.4):
    return p.fig.add_axes([left / p.W, (p.bottom + bottom_gap) / p.H, (p.W - left - right) / p.W,
                           (p.H - p.top - p.bottom - top_gap - bottom_gap) / p.H])


def pct(x):
    return (MINUS if x < 0 else "+") + f"{abs(x):g}%"


# ---------------------------------------------------------------- 1. Chicago speed cameras
def speed(fmt, name):
    d = pd.read_csv(DATA / "speed_cameras_chicago.csv").set_index("measure").value
    exp, obs, cut = d.all_injury_expected, d.all_injury_observed, d.all_injury_pct
    assert exp - obs == d.all_injury_reduction == 204, "title: about 200 fewer"
    assert round(cut) == 12, "title: 12%"
    p = Page(fmt, "Chicago's speed cameras cut injury crashes nearby by 12%, about 200 fewer crashes in three years",
             "Crashes that injured or killed someone within 250 meters of 101 Chicago speed cameras, 2015 to 2017. "
             f"Crashes that killed someone or caused a serious injury fell {d.ka_pct:g}% "
             f"({d.ka_observed:,.0f} vs. {d.ka_expected:,.0f} expected).",
             "",
             "Source: Stacey Sutton and Nebiyou Tilahun, \"Red-Light and Speed Cameras: Analyzing the Equity and "
             "Efficacy of Chicago's Automated Camera Enforcement Program,\" University of Illinois Chicago, report "
             "to the City of Chicago, Jan. 30, 2022, Table 1; published as Tilahun, Transportation Research Record "
             "2677(1), 2023. Actual crashes are a raw count of Illinois DOT crash records. Crashes expected without "
             "cameras are a modeled estimate (empirical Bayes) built from 146 similar streets without cameras and "
             "each site's 2010-12 crash record, so it accounts for cameras going where crashes were already high and "
             "for citywide trends. Cameras were installed in 2013-14. The drop is statistically significant "
             "(standard error from FHWA's crash modification factor database). Results varied by site: 16 of the 101 had clearly more crashes than expected.",
             WATERMARK)
    k = p.k
    small = k < 1                                           # social 4:5: less height for the plot
    ax = chart_area(p, left=1.15, right=0.4, bottom_gap=1.6 if small else 1.85, top_gap=0.45 if small else 0.6)
    style_axes(ax, k)
    w = 0.52
    ax.bar(0, exp, width=w, color=LIGHT, edgecolor=GREY, lw=1.6, ls=(0, (4, 3)), zorder=2)
    ax.bar(1, obs, width=w, color=COPPER, edgecolor=BG, lw=0, zorder=2)
    for x, v in ((0, exp), (1, obs)):
        ax.text(x, v + 40, f"{v:,.0f}", fontproperties=font("serif", 30 * k), color=INK, ha="center", va="bottom")
    # the gap between the two bars
    xb = 1 + w / 2 + 0.08
    ax.plot([xb, xb + 0.06, xb + 0.06, xb], [exp, exp, obs, obs], color=INK, lw=1.4, zorder=3)
    ax.plot([0 + w / 2, xb], [exp, exp], color=GREY, lw=1, ls=(0, (2, 2)), zorder=1)
    ax.text(xb + 0.12, (exp + obs) / 2, f"{exp - obs:,.0f} fewer\n({round(cut)}%)", color=INK, fontsize=16 * k,
            va="center", linespacing=1.15)
    ax.set_xlim(-0.5, 1.95); ax.set_ylim(0, 2000)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Expected without\ncameras\n(modeled estimate)", "What actually\nhappened\n(raw count)"],
                       fontsize=15 * k, color=INK, linespacing=1.15)
    ax.set_yticks(range(0, 2001, 500)); ax.set_yticklabels([f"{t:,}" for t in range(0, 2001, 500)])
    ax.set_ylabel("Injury crashes, 2015 to 2017", color=GREY, fontsize=13 * k, labelpad=10)
    ax.set_xlabel("Near Chicago's speed cameras", color=GREY, fontsize=13 * k, labelpad=12)
    p.save(OUT / name)


# ---------------------------------------------------------------- 2. red light cameras on and off
def red_light(fmt, name):
    d = pd.read_csv(DATA / "red_light_cameras.csv")
    get = lambda g, o: d[(d.group == g) & (d.outcome == o)].value.iloc[0]
    assert get("off", "red_light_running") == 30, "title: 30%"
    assert get("on", "red_light_running") == -21, "subtitle: 21%"
    p = Page(fmt, "Cities that turned off red light cameras had 30% more fatal red light running crashes than "
                  "expected",
             "Fatal crashes per resident compared with what a model predicted if nothing had changed, in U.S. cities "
             f"of 200,000 people or more. Cities that turned cameras on had {abs(get('on', 'red_light_running')):g}% "
             "fewer.",
             "",
             "Source: Wen Hu and Jessica B. Cicchino, \"Effects of turning on and off red light cameras on fatal "
             "crashes in large U.S. cities,\" Journal of Safety Research 61 (2017): 141-148, Insurance Institute for "
             "Highway Safety. All bars are modeled estimates comparing actual fatal crash rates with the rates "
             "expected had cameras not changed, controlling for trends over time, population density and "
             "unemployment. All four are statistically significant. Cameras on: 57 cities that started cameras in "
             "1992-2014, compared with 33 cities that never had them. Cameras off: 14 cities that ended cameras in 2010-14, compared with 29 cities in the "
             "same regions that kept them. Counting all 19 cities that turned cameras off, including those that "
             f"stopped before 2010, the increases were {get('off_all19', 'red_light_running'):g}% and "
             f"{get('off_all19', 'signalized_all'):g}% and not statistically significant.",
             WATERMARK)
    k = p.k
    small = k < 1
    ax = chart_area(p, left=1.15, right=0.4, bottom_gap=1.35 if small else 1.55, top_gap=0.35 if small else 0.5)
    style_axes(ax, k)
    ax.axhline(0, color=INK, lw=1.2, zorder=3)
    lo, hi = (-34, 42) if small else (-30, 40)
    per_in = (hi - lo) / (ax.get_position().height * p.H)     # axis percent points per inch of page
    w = 0.36
    names = {"red_light_running": "Red light\nrunning crashes", "signalized_all": "All crashes at\ntraffic lights"}
    cols = {"red_light_running": COPPER, "signalized_all": BLUE}
    for gx, g in enumerate(("on", "off")):
        for j, o in enumerate(("red_light_running", "signalized_all")):
            x = gx + (j - 0.5) * (w + 0.04)
            v = get(g, o)
            ax.bar(x, v, width=w, color=cols[o], alpha=1 if g == "off" else 0.5, lw=0, zorder=2)
            s = 1 if v > 0 else -1
            va = "bottom" if v > 0 else "top"
            size = (30 if (g, o) == ("off", "red_light_running") else 24) * k
            ax.text(x, v + s * 0.08 * per_in, pct(v), color=INK, ha="center", va=va,
                    fontproperties=font("serif", size))
            # the bar's name sits across the zero line from it, in the empty space
            ax.text(x, -s * 0.1 * per_in, names[o], color=BODY, fontsize=12.5 * k, ha="center",
                    va="top" if v > 0 else "bottom", linespacing=1.1)
    ax.set_ylim(lo, hi)
    ax.set_xlim(-0.6, 1.6)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["57 cities that\nturned cameras on", "14 cities that\nturned cameras off"],
                       fontsize=15 * k, color=INK, linespacing=1.15)
    ticks = range(-30, 41, 10)
    ax.set_yticks(ticks); ax.set_yticklabels(["0" if t == 0 else pct(t) for t in ticks])
    ax.set_ylabel("Fatal crash rate vs. expected", color=GREY, fontsize=13 * k, labelpad=10)
    ax.set_xlabel("U.S. cities of 200,000 people or more", color=GREY, fontsize=13 * k, labelpad=12)
    p.save(OUT / name)


# ---------------------------------------------------------------- 3. communities with each kind of camera
def adoption(fmt, name):
    d = pd.read_csv(DATA / "camera_communities.csv")
    rl = d[d.camera == "red light"].set_index("year").communities
    sp = d[d.camera == "speed"].set_index("year").communities
    peak = rl.idxmax()
    assert peak == 2012 and 0.32 < 1 - rl[2025] / rl[peak] < 0.35, "title: fallen by a third since 2012"
    assert sp[2025] / sp[2018] > 2, "title: more than doubled since 2018"
    p = Page(fmt, "U.S. communities with red light cameras fell by a third after 2012, while those with speed "
                  "cameras more than doubled after 2018",
             "Cities, towns and counties operating each kind of camera program, by year.",
             "",
             "Source: Insurance Institute for Highway Safety, \"Red light running\" and \"Speed\" research pages "
             "(updated July 2026), counts tracked from media reports and other public information. Raw counts. IIHS "
             "does not report speed camera counts for 1996-2002 or 2004-06; the dotted line spans those gaps. "
             "Communities with both kinds of camera are counted in each line.",
             WATERMARK)
    k = p.k
    small = k < 1
    ax = chart_area(p, left=1.15, right=1.75, bottom_gap=0.95, top_gap=0.5 if small else 0.6)
    style_axes(ax, k)
    ax.plot(rl.index, rl.values, color=COPPER, lw=3.4, solid_capstyle="round", zorder=3)
    cont = sp[sp.index >= 2007]
    ax.plot(cont.index, cont.values, color=BLUE, lw=2.4, solid_capstyle="round", zorder=3)
    gap = sp[sp.index <= 2007]
    ax.plot(gap.index, gap.values, color=BLUE, lw=1.4, ls=(0, (1.5, 2)), zorder=2)
    ax.plot(gap.index[:-1], gap.values[:-1], "o", color=BLUE, ms=5 * k, mec=BG, mew=1.5, zorder=4)
    ax.plot([peak], [rl[peak]], "o", color=COPPER, ms=8 * k, mec=BG, mew=2, zorder=4)
    ax.text(peak, rl[peak] + 22, f"{rl[peak]} in {peak}", color=INK, fontsize=15 * k, ha="center", va="bottom")
    last = 2025
    for s, col, lab, va in ((rl, COPPER, "Red light\ncameras", "bottom"), (sp, BLUE, "Speed\ncameras", "top")):
        ax.plot([last], [s[last]], "o", color=col, ms=8 * k, mec=BG, mew=2, zorder=4)
        ax.text(last + 0.8, s[last] + (8 if va == "bottom" else -8), f"{lab}: {s[last]}", color=INK,
                fontsize=15 * k, va=va, linespacing=1.1)
    ax.set_xlim(1991, 2026); ax.set_ylim(0, 620)
    ax.set_xticks(range(1995, 2026, 5))
    ax.set_yticks(range(0, 601, 100))
    ax.set_ylabel("Communities with cameras", color=GREY, fontsize=13 * k, labelpad=10)
    ax.set_xlabel("Year", color=GREY, fontsize=13 * k, labelpad=10)
    p.save(OUT / name)


# ---------------------------------------------------------------- 4. who pays late fees in Chicago
def who_pays(fmt, name):
    d = pd.read_csv(DATA / "chicago_ticket_burden.csv")
    get = lambda m, g: d[(d.measure == m) & (d.group == g)].value.iloc[0]
    lo, up = "low-income tracts", "upper-income tracts"
    fee_lo, fee_up = get("tickets_late_fees", lo), get("tickets_late_fees", up)
    assert 2.5 < fee_lo / fee_up < 3, "title: nearly 3 times"
    p = Page(fmt, "Camera tickets in Chicago's low-income neighborhoods were nearly 3 times as likely to end up "
                  "with a late fee",
             "Share of each neighborhood group's red light and speed camera tickets, 2016 to 2019. Paying late can "
             "double the $100 fine.",
             "",
             "Source: Stacey Sutton and Nebiyou Tilahun, \"Red-Light and Speed Cameras: Analyzing the Equity and "
             "Efficacy of Chicago's Automated Camera Enforcement Program,\" University of Illinois Chicago, report to "
             "the City of Chicago, Jan. 30, 2022, pp. 25 and 27. Raw counts of 2.4 million camera tickets with a "
             "fine, matched to the census tract where the vehicle's owner lives. Low- and upper-income groups are "
             "the report's; it does not state the income cutoffs. Middle-income neighborhoods are not shown. "
             f"Low-income neighborhoods received {get('share_of_all_tickets', lo):g}% of all camera tickets and "
             f"upper-income neighborhoods {get('share_of_all_tickets', up):g}%.",
             WATERMARK)
    k = p.k
    ax = chart_area(p, left=1.15, right=0.4, bottom_gap=1.1, top_gap=0.6)
    style_axes(ax, k)
    top = 65
    per_in = top / (ax.get_position().height * p.H)          # axis percent points per inch of page
    w = 0.36
    groups = [("tickets_late_fees", "Got a late fee"), ("tickets_unpaid", "Never paid")]
    cols = {lo: COPPER, up: "#c9c2b4"}
    names = {lo: "Low-income\nneighborhoods", up: "Upper-income\nneighborhoods"}
    for gx, (m, _) in enumerate(groups):
        for j, g in enumerate((lo, up)):
            x = gx + (j - 0.5) * (w + 0.04)
            v = get(m, g)
            ax.bar(x, v, width=w, color=cols[g], lw=0, zorder=2)
            size = (30 if g == lo else 24) * k
            ax.text(x, v + 0.08 * per_in, f"{v:g}%", color=INK, ha="center", va="bottom",
                    fontproperties=font("serif", size))
            if gx == 0:      # name each bar once, above its value
                ax.text(x, v + (0.14 + size / 72) * per_in, names[g], color=BODY, fontsize=12.5 * k, ha="center",
                        va="bottom", linespacing=1.1)
    ax.set_xlim(-0.6, 1.6); ax.set_ylim(0, top)
    ax.set_xticks([0, 1]); ax.set_xticklabels([lab for _, lab in groups], fontsize=16 * k, color=INK)
    ax.set_yticks(range(0, 51, 10)); ax.set_yticklabels([f"{t}%" for t in range(0, 51, 10)])
    ax.set_ylabel("Share of camera tickets", color=GREY, fontsize=13 * k, labelpad=10)
    ax.set_xlabel("Chicago camera tickets by the owner's neighborhood", color=GREY, fontsize=13 * k, labelpad=12)
    p.save(OUT / name)


CHARTS = [("speed-cameras", speed), ("red-light-cameras", red_light), ("camera-communities", adoption),
          ("who-pays", who_pays)]

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
