"""Bay Area (5-county transit measure district) share of federal income tax, by tax year, from IRS
Statistics of Income county data -> data/bay_area_tax_share.csv.
usage (from the post folder): python -I model/bay_area_share.py raw data

IRS SOI county data (https://www.irs.gov/statistics/soi-tax-stats-county-data), files YYincyallagi.csv.
A10300 = total tax liability (thousands of dollars); A06500 = income tax after credits; N1 = returns.
County totals: the agi_stub == 0 rows if present, else the sum over AGI classes. County FIPS 0 rows
(state totals) are excluded from the U.S. sum.
"""
import glob, re, sys
import pandas as pd

raw, out = sys.argv[1], sys.argv[2]
BAY = {1: 'Alameda', 13: 'Contra Costa', 75: 'San Francisco', 81: 'San Mateo', 85: 'Santa Clara'}
rows = []
for path in sorted(glob.glob(f'{raw}/irs/*incyallagi.csv')):
    yy = int(re.search(r'(\d\d)incyallagi', path).group(1))
    d = pd.read_csv(path, encoding='latin-1', usecols=['STATEFIPS', 'STATE', 'COUNTYFIPS', 'agi_stub', 'N1',
                                                      'A00100', 'A06500', 'A10300'])
    d = d[d.agi_stub == 0] if (d.agi_stub == 0).any() else \
        d.groupby(['STATEFIPS', 'STATE', 'COUNTYFIPS'], as_index=False)[['N1', 'A00100', 'A06500', 'A10300']].sum()
    cty = d[d.COUNTYFIPS != 0]
    bay = cty[(cty.STATE == 'CA') & cty.COUNTYFIPS.isin(BAY)]
    assert len(bay) == 5
    us = cty[['N1', 'A00100', 'A06500', 'A10300']].sum()
    b = bay[['N1', 'A00100', 'A06500', 'A10300']].sum()
    rows.append({'tax_year': 2000 + yy, 'bay_returns': b.N1, 'us_returns': us.N1,
                 'share_total_tax': b.A10300 / us.A10300, 'share_income_tax': b.A06500 / us.A06500,
                 'share_agi': b.A00100 / us.A00100, 'share_returns': b.N1 / us.N1})
s = pd.DataFrame(rows).sort_values('tax_year')
s.round(5).to_csv(f'{out}/bay_area_tax_share.csv', index=False)
print(s.round(4).to_string(index=False))
