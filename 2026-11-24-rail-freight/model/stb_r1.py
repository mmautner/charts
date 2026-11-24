"""US Class I revenue ton-miles from STB R-1 annual reports, Schedule 755 line 110.

Line 110 is "Ton-Miles of Freight (thousands), Revenue, TOTAL (lines 108 and 109)": revenue
freight only, excluding non-revenue (company material) ton-miles on line 111. Class I railroads
report US operations only (CN's US lines file as GTC, CPKC's as SOO/KCS).

Usage: python -I model/stb_r1.py raw/stb/files data
Writes data/us_class1_ton_miles.csv (railroad, year, revenue ton-miles, file used).
"""
import csv, sys
from pathlib import Path
import openpyxl

SHORT_TON_MILE_TO_TKM = 1.45997  # 0.90718474 t x 1.609344 km

# (year, railroad): file relative to raw/stb/files. A revision that resubmits Schedule 755 wins.
FILES = {
    (2019, "BNSF"): "R1-BNSF-2019.xlsx",
    (2019, "CSX"): "R1-CSX-2019/2019 Sch 755.xlsx",
    (2019, "GTC"): "R1-GTC-2019.xlsx",
    (2019, "KCS"): "R1-KCS-2019.xlsx",
    (2019, "NS"): "R1-NS-2019.xlsx",
    (2019, "SOO"): "R1-SOO-2019.xlsx",
    (2019, "UP"): "R1-UP-2019.xlsx",
    (2024, "BNSF"): "R1-BNSF-2024.xlsx",
    (2024, "CSX"): "R1-CSX-2024/2024 Sch 755 Final.xlsx",
    (2024, "GTC"): "R1-GTC-2024.xlsx",
    (2024, "NS"): "R1-NS-2024.xlsx",
    (2024, "SOO-KCSR"): "R1-SOO-KCSR-2024.xlsx",
    (2024, "UP"): "R1-UP-2024/2024 Sch 755 Final.xlsx",
    (2025, "BNSF"): "rev/R1-BNSF-2025-REV-SCHEDULES-10-23-2026.xlsx",
    (2025, "CSX"): "R1-CSX-2025/2025 Sch 755 Final.xlsx",
    (2025, "GTC"): "R1-GTC-2025.xlsx",
    (2025, "NS"): "R1-NS-2025.xlsx",
    (2025, "SOO-KCSR"): "R1-SOO-KCSR-2025.xlsx",
    (2025, "UP"): "R1-UP-2025/2025 Sch 755 Final.xlsx",
}


def line110(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheets = [n for n in wb.sheetnames if "755" in n and "nstr" not in n] or wb.sheetnames
    for name in sheets:   # older filings name sheets by page number: find the one with line 8-03
        rows = list(wb[name].iter_rows(values_only=True))
        if not any(str(c).strip().startswith("8-03") for r in rows for c in r if c):
            continue
        for row in rows:      # line 110 is item 8-03, total revenue ton-miles
            cells = [c for c in row if c is not None]
            if len(cells) > 1 and str(cells[0]).strip() == "110" and str(cells[1]).strip().startswith("8-03"):
                nums = [c for c in cells[1:] if isinstance(c, (int, float))]
                if nums:
                    return nums[0]
    raise ValueError(f"line 110 not found in {path} ({sheets})")


def main(raw, out):
    raw, out = Path(raw), Path(out)
    rows = []
    for (year, rr), f in sorted(FILES.items()):
        v = line110(raw / f)
        rows.append(dict(railroad=rr, year=year, revenue_ton_miles_thousands=v, file=f))
    for year in sorted({r["year"] for r in rows}):
        tot = sum(r["revenue_ton_miles_thousands"] for r in rows if r["year"] == year)
        rows.append(dict(railroad="ALL_CLASS_I", year=year, revenue_ton_miles_thousands=tot, file=""))
        print(f"{year}: Class I revenue ton-miles {tot/1e6:,.0f} billion = {tot*SHORT_TON_MILE_TO_TKM/1e6:,.0f} billion tkm")
    with open(out / "us_class1_ton_miles.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main(*sys.argv[1:3])
