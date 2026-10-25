"""Bay Area taxpayers' share of Highway Trust Fund bailouts, past and projected, vs. the Nov 3, 2026
regional transit sales tax -> data/bay_area_bailout.csv, data/bay_area_bailout_summary.csv.
usage (from the post folder): python -I model/bay_area_bailout.py raw data

Method: general-fund transfers into the Highway Trust Fund are paid for out of general federal revenue.
Each transfer is attributed to Bay Area taxpayers (Alameda, Contra Costa, San Francisco, San Mateo, Santa
Clara: the measure district) in proportion to their share of all federal income tax liability that year
(IRS SOI county data, A10300). Years before 2011 use 2011's share (the earliest year fetched, and lower
than later years); 2012 is interpolated. Projections use CBO's June 2026 baseline highway-account
shortfall with the 2022-2023 share (low), the 2018-2023 mean (central) and the 2018-2023 maximum (high).
This treats the transfers as if paid from current income taxes; in practice they were largely borrowed,
so the bill falls on the same tax base later.
"""
import sys
import numpy as np
import pandas as pd

raw, out = sys.argv[1], sys.argv[2]
share = pd.read_csv(f'{out}/bay_area_tax_share.csv').set_index('tax_year').share_total_tax
yrs = range(2008, 2024)
sh = share.reindex(yrs).interpolate(limit_area='inside')
sh.loc[:2010] = share.loc[2011]

t = pd.read_csv(f'{out}/crs_general_fund_transfers.csv')
t['bay_share'] = t.fiscal_year.map(lambda y: sh.loc[min(y, 2023)])
t['bay_highway'] = t.highway_account * t.bay_share
t['bay_total'] = t.total * t.bay_share
t.round(4).to_csv(f'{out}/bay_area_bailout.csv', index=False)

c = pd.read_csv(f'{out}/cbo_htf_baseline_2026_06.csv').set_index('fiscal_year')
hw_gap = (c.highway_outlays - c.highway_receipts).loc[2028:2036]          # $B a year, highway account
all_gap = (c.highway_outlays + c.transit_outlays - c.highway_receipts - c.transit_receipts).loc[2028:2036]
recent = share.loc[2018:2023]
cases = {'low (2022-23)': share.loc[2022:2023].min(), 'central (2018-23 mean)': recent.mean(),
         'high (2018-23 max)': recent.max()}
MEASURE = 0.980              # $B a year, district counsel's impartial analysis (Aug 2026)
ret = pd.read_csv(f'{out}/bay_area_tax_share.csv').set_index('tax_year').bay_returns.loc[2023]
# Households: ACS 2024 1-year, table B11001 (summary file acsdt1y2024-b11001.dat), the 5 counties
acs = pd.read_csv(f'{raw}/census/acsdt1y2024-b11001.dat', sep='|', dtype={'GEO_ID': str})
hh = acs[acs.GEO_ID.isin([f'0500000US06{c:03d}' for c in (1, 13, 75, 81, 85)])].B11001_E001.sum()
assert 2.2e6 < hh < 2.5e6

rows = [{'item': 'Transit sales tax on the Nov 3 ballot, per year', 'billions': MEASURE,
         'per_return': MEASURE * 1e9 / ret}]
rows.append({'item': 'Transit sales tax, all 14 years', 'billions': MEASURE * 14, 'per_return': np.nan})
rows.append({'item': 'Bay Area share of highway-account bailouts, FY2008-2022', 'billions': t.bay_highway.sum(),
             'per_return': np.nan})
rows.append({'item': 'Bay Area share of all trust fund bailouts, FY2008-2022', 'billions': t.bay_total.sum(),
             'per_return': np.nan})
for name, s in cases.items():
    rows.append({'item': f'Bay Area share of projected highway-account gap, avg FY2028-36, {name}',
                 'billions': hw_gap.mean() * s, 'per_return': hw_gap.mean() * s * 1e9 / ret, 'share': s})
    rows.append({'item': f'Bay Area share of projected highway-account gap, FY2029, {name}',
                 'billions': hw_gap.loc[2029] * s, 'per_return': hw_gap.loc[2029] * s * 1e9 / ret, 'share': s})
    rows.append({'item': f'Bay Area share of projected whole-fund gap, avg FY2028-36, {name}',
                 'billions': all_gap.mean() * s, 'per_return': all_gap.mean() * s * 1e9 / ret, 'share': s})
summ = pd.DataFrame(rows)
summ['per_household'] = summ.billions * 1e9 / hh
summ['households'] = hh
summ.round(4).to_csv(f'{out}/bay_area_bailout_summary.csv', index=False)

if __name__ == '__main__':
    pd.set_option('display.width', 200)
    print(t[['public_law', 'fiscal_year', 'highway_account', 'total', 'bay_share', 'bay_highway', 'bay_total']].round(3).to_string(index=False))
    print(f'\nhighway-account gap FY2028-36: mean {hw_gap.mean():.2f}B, FY2029 {hw_gap.loc[2029]:.2f}B; whole fund mean {all_gap.mean():.2f}B')
    print(f'Bay returns 2023: {ret:,.0f}')
    print(summ.round(3).to_string(index=False))

# Bay Area shares of U.S. driving, people and federal income tax -> data/chart_bay_area_shares.csv.
# Driving: Caltrans California Public Road Data 2024, Table 6 county totals (daily vehicle-miles, thousands)
# x 365, over FHWA Highway Statistics 2024 VM-2 U.S. total (data/bay_area_vmt_2024.csv, transcribed).
v = pd.read_csv(f'{out}/bay_area_vmt_2024.csv').set_index('area')
bay_vmt = v.loc[['Alameda', 'Contra Costa', 'San Francisco', 'San Mateo', 'Santa Clara'], 'daily_vmt_thousands'].sum() * 365 / 1e3
pop = pd.read_csv(f'{raw}/census/NST-EST2025-ALLDATA.csv', encoding='latin-1')
co = pd.read_csv(f'{raw}/census/co-est2025-alldata.csv', encoding='latin-1')
co = co[(co.SUMLEV == 50) & (co.STNAME == 'California') &
        co.CTYNAME.isin([f'{c} County' for c in ('Alameda', 'Contra Costa', 'San Francisco', 'San Mateo', 'Santa Clara')])]
assert len(co) == 5
shares = pd.DataFrame([
    {'measure': 'Share of U.S. population, 2025', 'share': co.POPESTIMATE2025.sum() / pop[pop.SUMLEV == 10].POPESTIMATE2025.iloc[0]},
    {'measure': 'Share of U.S. vehicle-miles driven, 2024', 'share': bay_vmt / v.loc['United States', 'annual_vmt_millions']},
    {'measure': 'Share of federal income tax, 2023', 'share': share.loc[2023]},
])
shares.round(5).to_csv(f'{out}/chart_bay_area_shares.csv', index=False)
if __name__ == '__main__':
    print(shares.round(4).to_string(index=False))
