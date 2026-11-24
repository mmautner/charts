"""Merge every source into data/rail_freight_passenger.csv and data/source_observations.csv.

Usage: python -I model/assemble.py raw inputs data
Run model/stb_r1.py and model/japan.py first (they write data/us_class1_ton_miles.csv, data/japan_rail.csv).

Units: millions of ton-km and passenger-km. Fiscal-year sources are filed under the year the fiscal
year starts (Japan and Great Britain: April-March). See METHODS.md.
"""
import csv, json, re, sys
from collections import defaultdict
from pathlib import Path
import openpyxl, pandas as pd, pypdf

STM_TO_TKM = 1.45997       # short ton-mile -> metric ton-km (0.90718474 t x 1.609344 km)
MI_TO_KM = 1.609344
ISO = {"USA": "United States", "DEU": "Germany", "JPN": "Japan", "FRA": "France", "GBR": "United Kingdom",
       "CHN": "China", "RUS": "Russia", "IND": "India", "CAN": "Canada", "AUS": "Australia",
       "CHE": "Switzerland", "NLD": "Netherlands", "KOR": "South Korea", "ITA": "Italy", "ESP": "Spain"}
EU2 = {"DE": "DEU", "FR": "FRA", "IT": "ITA", "ES": "ESP", "NL": "NLD", "CH": "CHE", "UK": "GBR"}
WDI_URL = "https://api.worldbank.org/v2/country/{c}/indicator/{i}"
ITF_URL = "https://sdmx.oecd.org/public/rest/data/OECD.ITF,DSD_ST@{f},1.0/all"
EST_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{d}"

OBS = []   # (iso, year, measure, value_mil, source, url, note)


def add(iso, year, measure, value, source, url, note=""):
    if value is None or value != value:
        return
    OBS.append(dict(iso=iso, year=int(year), measure=measure, value=float(value), source=source, url=url, note=note))


# ---------- international compilations (secondary) ----------
def wdi(raw):
    for ind, measure in [("IS.RRS.GOOD.MT.K6", "freight_tkm"), ("IS.RRS.PASG.KM", "pkm_reported"), ("SP.POP.TOTL", "population")]:
        for r in json.load(open(raw / f"wb/{ind}.json"))[1]:
            if r["value"] is not None and r["countryiso3code"] in ISO:
                v = r["value"] if measure != "population" else r["value"] / 1e6
                add(r["countryiso3code"], r["date"], measure, v, "WDI", WDI_URL.format(c=r["countryiso3code"], i=ind))


def itf(raw):
    for f, measure in [("DF_STFREIGHT", "freight_tkm"), ("DF_STPASS", "pkm_reported")]:
        for x in csv.DictReader(open(raw / f"oecd/{f}.csv")):
            if (x["FREQ: Frequency of observation"].startswith("A") and x["OBS_VALUE"]
                    and x["TRANSPORT_MODE: Transport mode"].startswith("RAIL")
                    and x["GEO_COVERAGE: Geographical coverage"].startswith("_T")
                    and x["REF_AREA: Reference area"][:3] in ISO and x["TIME_PERIOD: Time period"] <= "2024"):
                add(x["REF_AREA: Reference area"][:3], x["TIME_PERIOD: Time period"], measure,
                    x["OBS_VALUE"], "ITF", ITF_URL.format(f=f))


def eurostat(raw):
    for d, unit, measure in [("rail_go_total", "MIO_TKM", "freight_tkm"), ("rail_pa_total", "MIO_PKM", "pkm_mainline")]:
        lines = open(raw / f"eurostat/{d}.tsv").read().splitlines()
        years = [y.strip() for y in lines[0].split("\t")[1:]]
        for line in lines[1:]:
            key, *vals = line.split("\t")
            _, u, geo = key.split(",")
            if u != unit or geo not in EU2:
                continue
            for y, v in zip(years, vals):
                m = re.match(r"\s*([\d.]+)", v)
                if m:
                    add(EU2[geo], y, measure, m.group(1), "Eurostat", EST_URL.format(d=d),
                        "Eurostat railway statistics: railways only, no metro or tram" if measure == "pkm_mainline" else "")


# ---------- United States ----------
def usa(raw, inputs, data):
    src = ("Census, Historical Statistics of the U.S., Colonial Times to 1970, series Q 307 / Q 340",
           "https://www2.census.gov/library/publications/1975/compendia/hist_stats_colonial-1970/hist_stats_colonial-1970p2-chQ.pdf")
    for r in csv.DictReader(l for l in open(inputs / "us_hsus_1916_1970.csv") if not l.startswith("#")):
        add("USA", r["year"], "pkm_mainline", float(r["passenger_miles_mil"]) * MI_TO_KM, *src,
            "all line-haul railroads incl. commuter (commutation); excludes street railways and rapid transit")
        add("USA", r["year"], "freight_tkm", float(r["revenue_ton_miles_mil"]) * STM_TO_TKM, *src,
            "revenue ton-miles, class I-III railroads, x1.45997")
    for r in csv.DictReader(open(data / "us_class1_ton_miles.csv")):
        if r["railroad"] == "ALL_CLASS_I":
            add("USA", r["year"], "freight_tkm", float(r["revenue_ton_miles_thousands"]) / 1e3 * STM_TO_TKM,
                "STB R-1 Schedule 755 line 110, sum of Class I railroads",
                "https://www.stb.gov/reports-data/economic-data/annual-report-financial-data/",
                "Class I revenue ton-miles x1.45997; excludes regional and short-line railroads")
    ntd = defaultdict(dict)
    for r in csv.DictReader(open(raw / "ntd/ts21_pmt_by_mode.csv")):
        if r["pmt"]:
            ntd[int(r["report_year"])][r["mode"]] = float(r["pmt"]) / 1e6
    amtrak = {int(r["fiscal_year"]): float(r["passenger_miles_mil"])
              for r in csv.DictReader(l for l in open(inputs / "amtrak.csv") if not l.startswith("#"))}
    url = "https://data.transportation.gov/resource/npsm-38gk (NTD TS2.1, passenger miles by mode)"
    for y, m in ntd.items():
        main_ntd = sum(m.get(k, 0) for k in ("CR", "YR", "AR"))
        urban = sum(m.get(k, 0) for k in ("HR", "LR", "SR", "MG", "CC", "IP"))
        OBS.append(dict(iso="USA", year=y, measure="us_ntd_commuter_pkm", value=main_ntd * MI_TO_KM, source="NTD", url=url, note=""))
        OBS.append(dict(iso="USA", year=y, measure="us_ntd_urban_rail_pkm", value=urban * MI_TO_KM, source="NTD", url=url, note=""))
        if y in amtrak:
            note = (f"NTD commuter+hybrid+Alaska RR (report year {y}) + Amtrak FY{y} {amtrak[y]:,.0f} million passenger-miles "
                    "(rounded to 0.1 billion); fiscal years differ")
            add("USA", y, "pkm_mainline", (main_ntd + amtrak[y]) * MI_TO_KM, "NTD + Amtrak", url + " ; " + "inputs/amtrak.csv", note)
            add("USA", y, "pkm_all_rail", (main_ntd + urban + amtrak[y]) * MI_TO_KM, "NTD + Amtrak", url + " ; inputs/amtrak.csv",
                note + "; plus heavy rail, light rail, streetcar, monorail, cable car, inclined plane")


def usa_bts(raw, inputs):
    """BTS National Transportation Statistics tables 1-40 and 1-50 (downloaded by hand: bts.gov refuses scripts)."""
    url40 = "https://www.bts.gov/content/us-passenger-miles (NTS table 1-40)"
    url50 = "https://www.bts.gov/content/us-ton-miles-freight (NTS table 1-50)"
    def table(path, sheet):
        rows = list(openpyxl.load_workbook(path, read_only=True, data_only=True)[sheet].iter_rows(values_only=True))
        hdr = next(r for r in rows if any(isinstance(c, (int, float)) and 1900 < c < 2100 for c in r[1:]))
        get = lambda name: {int(y): v for y, v in zip(hdr[1:], next(r for r in rows if r[0] and str(r[0]).startswith(name))[1:])
                            if isinstance(y, (int, float)) and isinstance(v, (int, float))}
        return get
    g40 = table(raw / "bts/passenger-miles.xlsx", "1-40")
    amtrak, commuter, heavy, light = g40("Intercity/Amtrak"), g40("Commuter rail"), g40("Heavy rail"), g40("Light rail")
    for y in sorted(set(amtrak) & set(commuter)):
        main = amtrak[y] + commuter[y]
        add("USA", y, "pkm_mainline", main * MI_TO_KM, "BTS NTS 1-40", url40,
            "intercity/Amtrak (FRA) + commuter rail (APTA to 1995, NTD after), passenger-miles x1.609344"
            + ("; before 1971 'intercity' is the private railroads' service" if y < 1971 else ""))
        if y in heavy and y in light:
            add("USA", y, "pkm_all_rail", (main + heavy[y] + light[y]) * MI_TO_KM, "BTS NTS 1-40", url40,
                "mainline + transit heavy rail + light rail (incl. streetcar, hybrid rail); monorail/cable car not included")
    g50 = table(raw / "bts/freight-miles.xlsx", "1-50")
    for y, v in g50("Railroad").items():
        add("USA", y, "freight_tkm", v * STM_TO_TKM, "BTS NTS 1-50", url50,
            "AAR railroad ton-miles (1980-89 from STB waybill sample, incl. some short lines) x1.45997")
    for r in csv.DictReader(l for l in open(inputs / "us_statab.csv") if not l.startswith("#")):
        add("USA", r["year"], "freight_tkm", float(r["class1_ton_miles_bil"]) * 1000 * STM_TO_TKM,
            "Census Statistical Abstract 1987, table 1048", "https://www2.census.gov/library/publications/1986/compendia/statab/107ed/1987-05.pdf",
            "Class I tons carried one mile (AAR) x1.45997")


# ---------- Japan ----------
def japan(data):
    for r in csv.DictReader(open(data / "japan_rail.csv")):
        y = int(r["fiscal_year"])
        src = "MLIT 鉄道統計年報 / 鉄道輸送統計年報"
        add("JPN", y, "pkm_all_rail", float(r["all_rail_pkm"]), src, r["source_pax"],
            "fiscal year Apr-Mar; JR (JNR before FY1987) + all other railways incl. subways, trams, monorails")
        if r["mainline_pkm"]:
            add("JPN", y, "pkm_mainline", float(r["mainline_pkm"]), src, r["source_pax"],
                "excludes Tokyo Metro, Osaka Metro, municipal operators, monorail/AGT/tram operators")
        add("JPN", y, "freight_tkm", float(r["freight_tkm"]), src, r["source_freight"], "fiscal year Apr-Mar")
        if r["jr_pkm"]:
            OBS.append(dict(iso="JPN", year=y, measure="jp_jr_pkm", value=float(r["jr_pkm"]), source=src, url=r["source_pax"], note=""))


# ---------- Germany ----------
def germany(raw, inputs):
    url = "https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/DEHeft_derivate_00054943/FS-8-2-J-2002.pdf"
    for r in csv.DictReader(l for l in open(inputs / "germany_fachserie_1960_2002.csv") if not l.startswith("#")):
        if r["territory"] == "FRG" and r["year"] == "1990":
            continue   # keep unified Germany for 1990
        note = "West Germany" if r["territory"] == "FRG" else "unified Germany"
        add("DEU", r["year"], "pkm_mainline", r["pkm_mil"] or None, "Destatis Fachserie 8 Reihe 2 (2002)", url, note + "; all railways incl. S-Bahn")
        add("DEU", r["year"], "freight_tkm", r["tkm_mil"] or None, "Destatis Fachserie 8 Reihe 2 (2002)", url, note + "; tariff ton-km")
    viz = "https://elib.dlr.de/221967/1/VIZ_2025_2026_Download.pdf (Verkehr in Zahlen 2025/2026, p.54-55)"
    rd = pypdf.PdfReader(raw / "viz/VIZ_2025_2026.pdf")
    for pg in (53, 54):    # zero-based pages 54-55 of the PDF
        lines = rd.pages[pg + 1].extract_text().splitlines()
        years = next([int(y) for y in re.findall(r"\d{4}", l)] for l in lines if len(re.findall(r"\b(?:19|20)\d\d\b", l)) >= 5)
        def num(s):   # "79 107 82 539 ..." -> thousands separated by spaces; every value here is 10,000-999,999
            tok = s.split()
            assert len(tok) == 2 * len(years), (s, years)
            return [float(tok[i] + tok[i + 1]) for i in range(0, len(tok), 2)]
        pkm = next(l for l in lines if l.startswith("Verkehrsleistung 5) Mio. Pkm"))
        tkm = next(l for l in lines if l.startswith("Verkehrsleistung Mio. tkm"))
        for y, p, t in zip(years, num(pkm.split("Pkm", 1)[1]), num(tkm.split("tkm", 1)[1])):
            add("DEU", y, "pkm_mainline", p, "Verkehr in Zahlen 2025/2026", viz, "Eisenbahnen incl. S-Bahn (Nah- + Fernverkehr)")
            add("DEU", y, "freight_tkm_viz", t, "Verkehr in Zahlen 2025/2026", viz,
                "incl. company material, container tare, small-firm estimates; revised upward from 2016")


# ---------- France ----------
def france(raw):
    url_v = "https://www.statistiques.developpement-durable.gouv.fr/media/8866/download (Bilan annuel des transports 2024, F3 / F2.a)"
    url_m = "https://www.statistiques.developpement-durable.gouv.fr/media/8865/download (Bilan annuel des transports 2024, E3.a1)"
    def table(path, sheet, block_end=None):
        rows = list(openpyxl.load_workbook(path, read_only=True, data_only=True)[sheet].iter_rows(values_only=True))
        hdr = next(r for r in rows if r and any(isinstance(c, int) and c > 1900 for c in r))
        years = [int(str(c)[:4]) if c else None for c in hdr]
        out = {}
        for r in rows[rows.index(hdr) + 1:]:
            if not r or not r[0]:
                continue
            if block_end and str(r[0]).startswith(block_end):
                break
            out.setdefault(str(r[0]).strip(), {y: v for y, v in zip(years, r) if y and isinstance(v, (int, float))})
        return out
    f3 = table(raw / "france/voyageurs.xlsx", "F3")
    f2 = table(raw / "france/voyageurs.xlsx", "F2.a")
    e3 = table(raw / "france/marchandises.xlsx", "E3.a", block_end="E3.a2")
    metro_idf, tram_idf = f2["Métro"], f2["Tramways (2)"]
    metro_prov = f2["Métros (4)"]
    for y, v in f3["Ensemble"].items():
        add("FRA", y, "pkm_mainline", v, "SDES", url_v, "TGV + intercity + TER + Île-de-France trains and RER (incl. RATP RER); metropolitan France")
        if y in metro_idf and y in metro_prov:
            add("FRA", y, "pkm_all_rail", v + metro_idf[y] + tram_idf[y] + metro_prov[y], "SDES", url_v,
                "mainline + Paris Métro + Île-de-France trams + provincial metros; provincial trams are not "
                "separable from buses in SDES and are left out")
    for y, v in e3["Total"].items():
        add("FRA", y, "freight_tkm", v, "SDES", url_m, "national + international + transit; SNCF data to 2005, all operators from 2006")


# ---------- Great Britain ----------
def uk(raw):
    url_p = "https://dataportal.orr.gov.uk/media/1477/table-1230-passenger-kilometres.ods"
    url_f = "https://dataportal.orr.gov.uk/media/1998/table-1310-freight-moved-by-commodity.ods"
    url_t1 = "https://assets.publishing.service.gov.uk/media/69395b7e6a12691d48491d13/tsgb0101.ods"
    url_t4 = "https://assets.publishing.service.gov.uk/media/69398beecfacd5e888491d46/tsgb0401.ods"
    yr = lambda s: int(re.search(r"(\d{4})", str(s)).group(1))
    p = pd.read_excel(raw / "uk/table-1230.ods", sheet_name="1230_Passenger_kilometres", engine="odf", header=None)
    for _, r in p.iloc[5:].iterrows():
        if isinstance(r[1], (int, float)):
            add("GBR", yr(r[0]), "pkm_mainline", r[1] * 1000, "ORR table 1230", url_p,
                "Great Britain National Rail; calendar year to 1983, April-March from 1984; excludes Eurostar, Underground, light rail")
    f = pd.read_excel(raw / "uk/table-1310.ods", sheet_name="1310_Freight_moved_by_commodity", engine="odf", header=None)
    for _, r in f.iloc[6:].iterrows():
        if str(r[0]).startswith("Apr") and "Jun" not in str(r[0]) and isinstance(r[13], (int, float)):
            if re.match(r"Apr \d{4} to Mar \d{4}", str(r[0])):
                add("GBR", yr(r[0]), "freight_tkm", r[13], "ORR table 1310", url_f, "Great Britain; April-March; excludes infrastructure (engineering) trains")
        if str(r[0]).startswith("Table 1310b"):
            break
    t1 = pd.read_excel(raw / "uk/tsgb0101.ods", sheet_name="TSGB0101a", engine="odf", header=None)
    for _, r in t1.iloc[5:].iterrows():
        if isinstance(r[6], (int, float)):
            add("GBR", yr(r[0]), "pkm_all_rail", r[6] * 1000, "DfT TSGB0101", url_t1,
                "National Rail + London Underground + other metros and trams; rail on April-March years")
    t4 = pd.read_excel(raw / "uk/tsgb0401.ods", sheet_name="TSGB0401b", engine="odf", header=None)
    for _, r in t4.iloc[6:].iterrows():
        if isinstance(r[2], (int, float)) and yr(r[0]) < 1982:
            add("GBR", yr(r[0]), "freight_tkm", r[2] * 1000, "DfT TSGB0401", url_t4, "Great Britain rail goods moved (billion tkm, rounded)")


# ---------- China ----------
def china(inputs):
    url = "https://www.stats.gov.cn/sj/ndsj/2025/html/C16-06.jpg ; https://www.stats.gov.cn/sj/ndsj/2025/html/C16-08.jpg"
    for r in csv.DictReader(l for l in open(inputs / "china_nbs_1978_2024.csv") if not l.startswith("#")):
        add("CHN", r["year"], "pkm_mainline", float(r["rail_pkm_100mil"]) * 100, "NBS China Statistical Yearbook 2025, tables 16-6/16-8", url,
            "railways only; urban rail transit not included")
        add("CHN", r["year"], "freight_tkm", float(r["rail_tkm_100mil"]) * 100, "NBS China Statistical Yearbook 2025, tables 16-6/16-8", url, "")


# ---------- choose one value per cell ----------
PRIORITY = {   # first available wins; Eurostat preferred over national for EU freight (harmonised definition)
    "freight_tkm": {"USA": ["STB R-1", "BTS NTS", "Census, Historical", "Census Statistical", "ITF", "WDI"], "DEU": ["Eurostat", "Destatis", "ITF", "WDI"],
                    "_": ["MLIT", "SDES", "ORR", "DfT", "NBS", "Eurostat", "ITF", "WDI"]},
    "pkm_mainline": {"_": ["Census", "BTS NTS", "NTD + Amtrak", "MLIT", "Verkehr in Zahlen", "Destatis", "SDES", "ORR", "NBS", "Eurostat"]},
    "pkm_all_rail": {"_": ["BTS NTS", "NTD + Amtrak", "MLIT", "SDES", "DfT"]},
    "pkm_reported": {"_": ["ITF", "WDI"]},
    "population": {"_": ["WDI"]},
}


EXCLUDE = {   # (iso, year, measure): reason. Kept in source_observations.csv, left out of the main table.
    ("JPN", 1987, "freight_tkm"): "MLIT trend table gives JR 10.0 billion tkm for FY1987, half of FY1986 (20.1) and FY1988 "
                                  "(23.0), the year JNR was split up; looks like a partial year, so left blank",
}


NOTE = {(("USA", y, "pkm_reported")): "ITF counts Amtrak only for 2004-2013 (8.7-11.0 billion pkm) and adds commuter "
         "rail from 2014 (36 billion); not comparable with other years" for y in range(2004, 2014)}


def pick(obs, measure, iso):
    order = PRIORITY[measure].get(iso, PRIORITY[measure]["_"])
    for pre in order:
        for o in obs:
            if o["source"].startswith(pre):
                return o
    return None


def main(raw, inputs, data):
    raw, inputs, data = Path(raw), Path(inputs), Path(data)
    wdi(raw); itf(raw); eurostat(raw); usa(raw, inputs, data); usa_bts(raw, inputs); japan(data); germany(raw, inputs); france(raw); uk(raw); china(inputs)
    with open(data / "source_observations.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["iso", "country", "year", "measure", "value", "source", "url", "note"])
        w.writeheader()
        for o in sorted(OBS, key=lambda o: (o["iso"], o["measure"], o["year"], o["source"])):
            w.writerow(dict(o, country=ISO[o["iso"]], value=round(o["value"], 3)))
    cells = defaultdict(list)
    for o in OBS:
        cells[(o["iso"], o["year"], o["measure"])].append(o)
    keys = sorted({(o["iso"], o["year"]) for o in OBS})
    out = []
    for iso, y in keys:
        row = dict(country=ISO[iso], iso3=iso, year=y)
        notes, srcs = [], {}
        for m in ("freight_tkm", "pkm_mainline", "pkm_all_rail", "pkm_reported", "population"):
            o = pick(cells.get((iso, y, m), []), m, iso)
            if (iso, y, m) in NOTE:
                notes.append(f"{m}: {NOTE[(iso, y, m)]}")
            if (iso, y, m) in EXCLUDE:
                notes.append(f"{m}: {EXCLUDE[(iso, y, m)]}")
                o = None
            row[m] = round(o["value"], 3) if o else None
            if o and m != "population":
                srcs[m] = f'{o["source"]} <{o["url"]}>'
                if o["note"]:
                    notes.append(f'{m}: {o["note"]}')
        if not any(row[m] is not None for m in ("freight_tkm", "pkm_mainline", "pkm_all_rail", "pkm_reported")):
            continue
        row["source_freight"] = srcs.get("freight_tkm", "")
        row["source_pax"] = " | ".join(f"{m}: {srcs[m]}" for m in ("pkm_mainline", "pkm_all_rail", "pkm_reported") if m in srcs)
        row["notes"] = "; ".join(notes)
        out.append(row)
    cols = ["country", "iso3", "year", "freight_tkm", "pkm_mainline", "pkm_all_rail", "pkm_reported", "population",
            "source_freight", "source_pax", "notes"]
    with open(data / "rail_freight_passenger.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} country-years, {len(OBS)} source observations")


if __name__ == "__main__":
    main(*sys.argv[1:4])
