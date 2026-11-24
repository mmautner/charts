"""Japan rail passenger-km and freight ton-km (fiscal years April-March), from MLIT.

Sources (all MLIT, 国土交通省):
  A. 鉄道統計年報 [令和5年度] (22) 運輸成績の推移, sheet (ii): JR (JNR before FY1987) and 民鉄 (all
     non-JR operators, including municipal 公営 subways and trams) passenger-km and ton-km,
     FY1960, 1965, 1970, then annually FY1975-FY2023; Tokyo Metro's passenger-km given FY2004+.
  B. 鉄道統計年報 (2) 運輸成績表 by operator, FY2019 and FY2023: used to split out urban transit.
  C. 鉄道輸送統計年報 2024年度 (e-Stat 00600350): FY2017-FY2024 totals (JR, 民鉄, freight).

"mainline" = JR + non-JR railways, excluding: Tokyo Metro, Osaka Metro (大阪市高速電気軌道), all
municipal 公営 operators (their subways and trams), and named monorail / AGT / tram operators.
Japan's subways through-run onto suburban railways, so any split by operator is approximate.

Usage: python -I model/japan.py raw/japan data
"""
import csv, re, sys
from pathlib import Path
import openpyxl, xlrd

ERA = {"昭和": 1925, "平成": 1988, "令和": 2018}
URBAN = re.compile(r"モノレール|新交通|ゆりかもめ|シーサイドライン|ニューシャトル|ライトレール|軌道線|電気軌道|"
                   r"とさでん|愛知高速交通|広島高速交通|スカイレール|山万|舞浜リゾートライン|山口線|世田谷線|"
                   r"大阪高速鉄道|北九州高速鉄道|埼玉新都市交通|万葉線|福井鉄道|筑豊電気鉄道|ポートライナー")
URBAN_SKIP = ("大阪市高速電気軌道",)           # counted separately as a subway
SRC_A = "https://www.mlit.go.jp/tetudo/content/001977439.xls"
SRC_B = {2019: "https://www.mlit.go.jp/tetudo/content/001460060.xlsx",
         2023: "https://www.mlit.go.jp/tetudo/content/001977414.xlsx"}
SRC_C = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040366428&fileKind=0"


def trend(path):
    """Sheet (ii): FY, minkan pkm, minkan tkm, ote pkm, JR pkm, JR tkm (thousands); Tokyo Metro in the next row."""
    ws = xlrd.open_workbook(path).sheet_by_index(1)
    era, out, last = None, {}, None
    for i in range(3, ws.nrows):
        r = ws.row_values(i)
        if isinstance(r[4], float) and r[4] < 0 and last:      # (Tokyo Metro) row under its year
            out[last]["tokyo_metro_pkm"] = -r[4]
            continue
        if r[0] in ERA:
            era = r[0]
        if r[1] in ("", None) or not isinstance(r[2], float):
            continue
        n = 1 if r[1] == "元" else int(r[1])
        fy = ERA[era] + n
        out[fy] = dict(minkan_pkm=r[2], minkan_tkm=r[3], ote_pkm=r[4], jr_pkm=r[5], jr_tkm=r[6])
        last = fy
    return out


def operators(path):
    """Rows of table (2): (group, name, total pkm in thousands), group in 大手/中小/公営/JR. Operator and
    line rows both appear. Rows are assigned to a group by the subtotal row (大手計, 中小計, 公営計) that
    closes them, since not every year's file has section headers."""
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0]
    rows, buf, hdr = [], [], None
    for i, r in enumerate(ws.iter_rows(values_only=True)):
        if i < 6:
            continue
        cells = [c for c in r if c is not None]
        if len(cells) == 1:     # section header such as （公営） in files that have them
            m = re.fullmatch(r"（(大手|中小|公営)）", str(cells[0]).strip())
            hdr = m.group(1) if m else hdr
        if len(cells) < 2:
            continue
        name = str(cells[0]).strip()
        vals = [c for c in cells[1:] if isinstance(c, (int, float))]
        pkm = vals[6] if len(vals) > 6 else 0
        m = re.fullmatch(r"(大手|中小|公営)計", name)
        if m:
            rows += [(m.group(1), n, p) for n, p in buf]
            buf = []
        elif name.endswith("計"):
            rows.append(("total", name, pkm))
            buf = [] if "運輸局" in name else buf
        elif name.startswith("総合計（民鉄"):
            rows.append(("total", name, pkm))
            hdr = "JR"         # the JR block follows the non-JR grand total
        elif hdr:
            rows.append((hdr, name, pkm))
        else:
            buf.append((name, pkm))
    rows += [("JR", n, p) for n, p in buf]
    return rows


def split(path):
    rows = operators(path)
    get = lambda name: next(p for g, n, p in rows if n == name)
    total_min = next(p for g, n, p in rows if n.startswith("総合計（民鉄"))
    total_jr = get("総合計（ＪＲ）")
    koei = get("公営合計")
    metro = get("東京地下鉄") + get("大阪市高速電気軌道")
    other = [(n, p) for g, n, p in rows
             if g in ("大手", "中小") and URBAN.search(n) and n not in URBAN_SKIP]
    other_pkm = sum(p for _, p in other)
    return dict(all_rail=total_min + total_jr, jr=total_jr, minkan=total_min, koei=koei, metro=metro,
                other_urban=other_pkm, mainline=total_jr + total_min - koei - metro - other_pkm,
                other_list=other)


def survey(path):
    ws = xlrd.open_workbook(path).sheet_by_index(0)
    out = {}
    for i in range(ws.nrows):
        r = ws.row_values(i)
        m = re.match(r"(\d{4})\s*年度$", str(r[0]).strip())
        if m:
            out[int(m.group(1))] = dict(all_rail=r[1], jr=r[3], minkan=r[5])
    return out


def main(raw, out):
    raw, out = Path(raw), Path(out)
    t = trend(raw / "nenpo_fy2023/001977439.xls")
    sp = {2019: split(raw / "nenpo_fy2019/001460060.xlsx"), 2023: split(raw / "nenpo_fy2023/001977414.xlsx")}
    sv = survey(raw / "fy2024/000040366428.xls")
    fr = survey(raw / "fy2024/000040366700.xls")   # same layout: total, container, wagonload (thousand tkm)
    rows = []
    for fy in sorted(set(t) | set(sv)):
        a = t.get(fy)
        row = dict(fiscal_year=fy, jr_pkm=None, minkan_pkm=None, tokyo_metro_pkm=None, all_rail_pkm=None,
                   mainline_pkm=None, urban_excluded_pkm=None, freight_tkm=None, source_pax="", source_freight="")
        if a:
            row.update(jr_pkm=a["jr_pkm"], minkan_pkm=a["minkan_pkm"], tokyo_metro_pkm=a.get("tokyo_metro_pkm"),
                       all_rail_pkm=a["jr_pkm"] + a["minkan_pkm"], freight_tkm=a["jr_tkm"] + a["minkan_tkm"],
                       source_pax=SRC_A, source_freight=SRC_A)
        elif fy in sv:
            row.update(jr_pkm=sv[fy]["jr"], minkan_pkm=sv[fy]["minkan"], all_rail_pkm=sv[fy]["all_rail"],
                       freight_tkm=fr[fy]["all_rail"], source_pax=SRC_C, source_freight=SRC_C)
        if fy in sp:
            s = sp[fy]
            row.update(mainline_pkm=s["mainline"], urban_excluded_pkm=s["koei"] + s["metro"] + s["other_urban"],
                       source_pax=SRC_A + " ; " + SRC_B[fy])
        rows.append(row)
    with open(out / "japan_rail.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:   # thousands -> millions
            w.writerow({k: (round(v / 1000, 1) if isinstance(v, float) or (isinstance(v, int) and k != "fiscal_year") else v)
                        for k, v in r.items()})
    for fy, s in sp.items():
        print(f"FY{fy}: all {s['all_rail']/1e6:.1f}bn, JR {s['jr']/1e6:.1f}, municipal {s['koei']/1e6:.1f}, "
              f"Tokyo+Osaka Metro {s['metro']/1e6:.1f}, monorail/AGT/tram {s['other_urban']/1e6:.2f} "
              f"[{', '.join(n for n, _ in s['other_list'])}] -> mainline {s['mainline']/1e6:.1f}bn "
              f"({s['mainline']/s['all_rail']:.1%} of all)")
    for fy in (2019, 2023):
        print(f"FY{fy} cross-check, trend table vs survey all-rail pkm: {t[fy]['jr_pkm']+t[fy]['minkan_pkm']:,.0f} vs {sv[fy]['all_rail']:,.0f}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
