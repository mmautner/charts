"""Share of older Americans not driving, and expected years lived not driving (Sullivan method).

usage (from the post folder):  python -I model/estimates.py raw data

Inputs (see inputs/fetch.sh, inputs/fetch_census.py):
  raw/nhts17/perpub.csv, raw/nhts17/perwgt.sas7bdat   2017 NHTS persons + 98 jackknife replicate weights
  raw/nhts22/perv2pub.csv                              2022 NHTS persons (no replicate weights published)
  raw/lt*/Table02|03.xlsx                              NCHS U.S. life tables, males|females
  raw/census/{P12,PCO1,PCO5}_us.json                   2020 Census DHC: total, group quarters, nursing facilities
  raw/fhwa/dl20_*.{cfm,xlsx}                           FHWA DL-20 licensed drivers as % of population

Variance:
  2017: SE = sqrt(6/7 * sum_i (REP_i - x)^2), i = 1..98 (2017 NHTS User's Guide sec. 7.12, p. 66;
        JKn with n_h = 7 variance units in each of 14 variance strata, 2017 NHTS Weighting Report sec. 2.2).
  2022: Taylor linearization, strata STRATUMID, PSU = household (HOUSEID), with-replacement approximation.
        The 2022 public files carry no replicate weights.
Census counts (nursing-home adjustment) and life tables are treated as fixed.

Definitions:
  not driving = NHTS derived DRIVER == 2 ("Driver status, derived": No). Persons with DRIVER missing dropped.
  ages: 2017 R_AGE_IMP (top-coded: ages 89+ are coded 92); 2022 R_AGE (same top code).
"""
import json, re, sys
import numpy as np, pandas as pd

RAW = sys.argv[1] if len(sys.argv) > 1 else 'raw'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'data'
G5 = ['65-69', '70-74', '75-79', '80-84', '85+']
B5 = [65, 70, 75, 80, 85, 200]
GS = ['65-69', '70-74', '75-79', '80-84', '85-88', '89+']   # split of 85+ at the NHTS top code
BS = [65, 70, 75, 80, 85, 89, 200]
REPS = [f'WTPERFIN{i}' for i in range(1, 99)]
JK = 6 / 7


# ---------------------------------------------------------------- inputs
def life_table(folder, sex):
    import glob
    f = [p for p in glob.glob(f'{RAW}/{folder}/*.xlsx') if p.lower().endswith(('table02.xlsx' if sex == 'M' else 'table03.xlsx'))][0]
    d = pd.read_excel(f, header=None)
    year = int(re.search(r'(\d{4})\s*$', str(d.iloc[0, 0])).group(1))
    d = d.iloc[3:104, [2, 4, 6]]
    d.columns = ['lx', 'Lx', 'ex']; d.index = range(101)
    return year, d.astype(float)


LT = {}
for folder in ['lt6807', 'lt7019', 'lt7402', 'lt7406', 'lt7505']:
    for s in 'MF':
        y, d = life_table(folder, s)
        LT[(y, s)] = d


def coefs(L, x, bins, labels):
    """c_g = (person-years lived in age group g at ages >= x) / l_x; sum_g c_g = e_x."""
    ages = np.arange(101); m = ages >= x
    g = pd.cut(ages[m], bins, right=False, labels=labels)
    return pd.Series(L.Lx.values[m]).groupby(np.asarray(g), observed=True).sum().reindex(labels).fillna(0) / L.lx[x]


def census():
    out = {}
    for t in ['P12', 'PCO1', 'PCO5']:
        d = json.load(open(f'{RAW}/census/{t}_us.json')); row = dict(zip(d[0], d[1]))
        v = json.load(open(f'{RAW}/census/{t}_vars.json'))['variables']
        for k, val in row.items():
            if not (k.startswith(t + '_') and k.endswith('N')): continue
            lab = v[k]['label']
            sex = 'M' if '!!Male:' in lab else 'F' if '!!Female:' in lab else None
            m = re.search(r'!!(\d+)( and \d+| to \d+)? years$|!!(85) years and over$', lab)
            if not sex or not m: continue
            lo = int(m.group(1) or m.group(3))
            if lo < 65: continue
            g = G5[min((lo - 65) // 5, 4)]
            out[(t, sex, g)] = out.get((t, sex, g), 0) + int(val)
    rows = []
    for s in 'MF':
        for g in G5:
            rows.append(dict(sex=s, group=g, pop2020=out[('P12', s, g)], gq2020=out[('PCO1', s, g)], nursing2020=out[('PCO5', s, g)]))
    c = pd.DataFrame(rows)
    c['f_nursing'] = c.nursing2020 / c.pop2020; c['f_gq'] = c.gq2020 / c.pop2020
    return c


def fhwa():
    """DL-20 'drivers as percent of age group' (FHWA's own Census denominators)."""
    rows = []
    x = pd.read_excel(f'{RAW}/fhwa/dl20_2022.xlsx', header=None)
    for year, f in [(2022, 'dl20_2022.xlsx'), (2023, 'dl20_2023.xlsx')]:
        x = pd.read_excel(f'{RAW}/fhwa/{f}', header=None)
        for i, g in zip(range(30, 35), G5):
            rows.append(dict(year=year, group=g, M=float(x.iloc[i, 3]), F=float(x.iloc[i, 6])))
    txt = open(f'{RAW}/fhwa/dl20_2017.cfm', encoding='latin-1').read()
    toks = [t.strip() for t in re.sub(r'<[^>]+>', '\n', txt).split('\n') if t.strip()]
    for lab, g in zip(['65-69', '70-74', '75-79', '80-84', '85 AND OVER'], G5):
        i = toks.index(lab); v = [float(t.replace(',', '')) for t in toks[i + 1:i + 10]]
        rows.append(dict(year=2017, group=g, M=v[2], F=v[5]))
    f = pd.DataFrame(rows).melt(['year', 'group'], var_name='sex', value_name='pct_licensed')
    return f


def load17():
    cols = ['HOUSEID', 'PERSONID', 'R_AGE_IMP', 'R_SEX_IMP', 'DRIVER', 'URBRUR', 'HHSTATE', 'WTPERFIN', 'CONDRIVE',
            'MEDCOND', 'MEDCOND6', 'CNTTDTR', 'PROXY', 'DRVRCNT', 'HHVEHCNT', 'SMPLSRCE']
    p = pd.read_csv(f'{RAW}/nhts17/perpub.csv', usecols=cols)
    p = p[p.R_AGE_IMP >= 65].copy()
    r = pd.read_sas(f'{RAW}/nhts17/perwgt.sas7bdat')
    for k in ['HOUSEID', 'PERSONID']:
        if r[k].dtype == object: r[k] = r[k].str.decode('ascii')
        r[k] = r[k].astype(np.int64)
    p = p.merge(r[['HOUSEID', 'PERSONID', 'WTPERFIN'] + REPS].rename(columns={'WTPERFIN': 'W_chk'}), on=['HOUSEID', 'PERSONID'], how='left')
    assert np.allclose(p.W_chk, p.WTPERFIN), 'replicate file weight mismatch'
    p = p.rename(columns={'R_AGE_IMP': 'age'})
    return p


def load22():
    cols = ['HOUSEID', 'PERSONID', 'R_AGE', 'R_SEX_IMP', 'DRIVER', 'URBRUR', 'STRATUMID', 'WTPERFIN', 'CONDRIVE',
            'MEDCOND', 'MEDCOND6', 'CNTTDTR', 'PROXY', 'DRVRCNT', 'HHVEHCNT']
    p = pd.read_csv(f'{RAW}/nhts22/perv2pub.csv', usecols=cols)
    p = p[p.R_AGE >= 65].copy().rename(columns={'R_AGE': 'age'})
    return p


def prep(p):
    p['all_ages_n'] = len(p)
    p = p[p.DRIVER.isin([1, 2])].copy()
    p['sex'] = p.R_SEX_IMP.map({1: 'M', 2: 'F'})
    p['y'] = (p.DRIVER == 2).astype(float)
    p['g5'] = pd.cut(p.age, B5, right=False, labels=G5).astype(str)
    p['gs'] = pd.cut(p.age, BS, right=False, labels=GS).astype(str)
    p['w'] = p.WTPERFIN
    return p


# ---------------------------------------------------------------- variance engines
class Rep17:
    """Evaluate any statistic f(df, weight_col) on the full weight and 98 replicates."""
    def __init__(self, p): self.p = p
    def __call__(self, f, d=None):
        d = self.p if d is None else d
        full = np.asarray(f(d, 'w'), float)
        reps = np.array([np.asarray(f(d, r), float) for r in REPS])
        return full, np.sqrt(JK * ((reps - full) ** 2).sum(0))


def taylor_se(d, z):
    """d: frame with STRATUMID, HOUSEID; z: linearized values (one column per statistic)."""
    z = np.atleast_2d(np.asarray(z, float).T).T if np.ndim(z) == 1 else np.asarray(z, float)
    t = pd.DataFrame(z, index=d.index); t['h'] = d.STRATUMID.values; t['psu'] = d.HOUSEID.values
    tot = t.groupby(['h', 'psu']).sum()
    v = np.zeros(z.shape[1])
    for h, x in tot.groupby(level=0):
        n = len(x)
        if n > 1: v += n / (n - 1) * ((x - x.mean()) ** 2).sum().values
    return np.sqrt(v)


def wmean(d, wc, y='y'):
    return np.average(d[y], weights=d[wc]) if len(d) else np.nan


# ---------------------------------------------------------------- estimators
def shares(d, wc, gcol, groups, adj=None):
    """weighted non-driving share by group; adj = (a_g, b_g) applies pi' = a + b*pi."""
    out = []
    for g in groups:
        x = d[d[gcol] == g]; pi = wmean(x, wc)
        if adj is not None: pi = adj[0][g] + adj[1][g] * pi
        out.append(pi)
    return np.array(out)


def lin_share(d, gcol, g):
    """linearized values of the weighted share in group g (2022)."""
    I = (d[gcol] == g).values; W = d.w[I].sum(); pi = np.average(d.y[I], weights=d.w[I])
    return np.where(I, d.w.values * (d.y.values - pi) / W, 0.0), pi


def sullivan_stat(c, gcol, groups, adj=None):
    def f(d, wc):
        return float((c.values * shares(d, wc, gcol, groups, adj)).sum())
    return f


def sullivan22(d, c, gcol, groups, adj=None):
    z = np.zeros(len(d)); est = 0.0
    for g in groups:
        zg, pi = lin_share(d, gcol, g)
        b = 1.0 if adj is None else adj[1][g]; a = 0.0 if adj is None else adj[0][g]
        est += c[g] * (a + b * pi); z += c[g] * b * zg
    return est, float(taylor_se(d, z)[0])


def share_se(year, d, gcol, g, eng=None, adj=None):
    x = d[d[gcol] == g]
    if year == 2017:
        f = lambda dd, wc: shares(dd, wc, gcol, [g], adj)[0]
        e, se = eng(f, d)
        return float(e), float(se)
    zg, pi = lin_share(d, gcol, g)
    b = 1.0 if adj is None else adj[1][g]; a = 0.0 if adj is None else adj[0][g]
    return a + b * pi, b * float(taylor_se(d, zg)[0])


# ---------------------------------------------------------------- main
cen = census()
fh = fhwa()
p17 = prep(load17()); p22 = prep(load22())
E17 = Rep17(p17)
cen.to_csv(f'{OUT}/census_2020_nursing.csv', index=False)


def adj_for(sex, kind):
    if kind is None: return None
    f = cen[cen.sex == sex].set_index('group')['f_nursing' if kind == 'nursing' else 'f_gq']
    return (f, 1 - f)   # pi' = f + (1-f) pi


rows_age5, rows_sul = [], []
for year, P in [(2017, p17), (2022, p22)]:
    for sex in ['M', 'F', 'All']:
        d = P if sex == 'All' else P[P.sex == sex]
        for gcol, groups in [('g5', G5)] + ([('gs', GS[4:])] if year == 2017 else []):
            for g in groups:
                x = d[d[gcol] == g]
                e, se = share_se(year, d, gcol, g, E17)
                r = dict(survey=year, sex=sex, age_group=g, share_not_driving=e, se=se, moe90=1.645 * se,
                         n=len(x), n_not_driving=int(x.y.sum()), flag_lt50=bool(len(x) < 50 or x.y.sum() < 50))
                if sex != 'All' and gcol == 'g5':
                    ea, sea = share_se(year, d, gcol, g, E17, adj_for(sex, 'nursing'))
                    r.update(share_incl_nursing=ea, se_incl_nursing=sea, moe90_incl_nursing=1.645 * sea,
                             nursing_share_of_pop2020=float(cen[(cen.sex == sex) & (cen.group == g)].f_nursing.iloc[0]))
                    lic = fh[(fh.year == year) & (fh.sex == sex) & (fh.group == g)].pct_licensed
                    if len(lic): r['fhwa_pct_not_licensed'] = 100 - float(lic.iloc[0])
                rows_age5.append(r)

A5 = pd.DataFrame(rows_age5)
A5.to_csv(f'{OUT}/not_driving_by_age5.csv', index=False)

# single-year ages, 2017 (ages 89+ are top-coded together)
rows1 = []
p17['a1'] = p17.age.clip(upper=89).astype(int).astype(str).replace({'89': '89+'})
A1G = [str(a) for a in range(65, 89)] + ['89+']
for sex in ['M', 'F']:
    d = p17[p17.sex == sex]
    est, se = E17(lambda dd, wc: shares(dd, wc, 'a1', A1G), d)
    for g, e, s in zip(A1G, est, se):
        x = d[d.a1 == g]
        rows1.append(dict(survey=2017, sex=sex, age=g, share_not_driving=e, se=s, moe90=1.645 * s, n=len(x),
                          n_not_driving=int(x.y.sum()), flag_lt50=bool(len(x) < 50 or x.y.sum() < 50)))
pd.DataFrame(rows1).to_csv(f'{OUT}/not_driving_by_age1_2017.csv', index=False)


# Sullivan estimates
def sul(spec, year, P, lt_year, sex, x, gcol='g5', groups=G5, bins=B5, adj=None, subset=None, note=''):
    d = P[P.sex == sex]
    if subset is not None: d = d[subset(d)]
    L = LT[(lt_year, sex)]; c = coefs(L, x, bins, groups)
    a = adj_for(sex, adj)
    if year == 2017:
        e, se = E17(sullivan_stat(c, gcol, groups, a), d); e, se = float(e), float(se)
    else:
        e, se = sullivan22(d, c, gcol, groups, a)
    rows_sul.append(dict(spec=spec, survey=year, lifetable=lt_year, sex=sex, from_age=x, life_exp=L.ex[x],
                         years_not_driving=e, se=se, moe90=1.645 * se, years_driving=L.ex[x] - e,
                         share_of_remaining_life=e / L.ex[x], n=int((d.age >= x).sum()),
                         n_not_driving=int(d[d.age >= x].y.sum()), note=note))


for sex in 'MF':
    for x in (65, 70):
        sul('main', 2017, p17, 2017, sex, x, note='household population only')
        sul('incl_nursing_homes', 2017, p17, 2017, sex, x, adj='nursing', note='adds 2020 Census nursing-facility residents as non-drivers')
        sul('incl_all_group_quarters', 2017, p17, 2017, sex, x, adj='gq', note='upper bound: all group-quarters residents as non-drivers')
        sul('split_85', 2017, p17, 2017, sex, x, 'gs', GS, BS, note='85+ split into 85-88 and 89+')
        for ly in (2019, 2022, 2023, 2024):
            sul(f'lifetable_{ly}', 2017, p17, ly, sex, x, note='2017 NHTS shares with a later life table')
        sul('urban', 2017, p17, 2017, sex, x, subset=lambda q: q.URBRUR == 1, note='self-selected; not causal')
        sul('rural', 2017, p17, 2017, sex, x, subset=lambda q: q.URBRUR == 2, note='self-selected; not causal')
        sul('excl_california', 2017, p17, 2017, sex, x, subset=lambda q: q.HHSTATE != 'CA')
        sul('excl_new_york', 2017, p17, 2017, sex, x, subset=lambda q: q.HHSTATE != 'NY')
        sul('main', 2022, p22, 2022, sex, x, note='2022 NHTS; see survey comparison')
        sul('incl_nursing_homes', 2022, p22, 2022, sex, x, adj='nursing')
        sul('nhts2022_lifetable_2017', 2022, p22, 2017, sex, x, note='isolates survey change from life-table change')
S = pd.DataFrame(rows_sul)


# FHWA unlicensed-share Sullivan (no SE: administrative counts)
for year, ly in [(2017, 2017), (2022, 2022)]:
    for sex in 'MF':
        L = LT[(ly, sex)]
        for x in (65, 70):
            c = coefs(L, x, B5, G5)
            pi = 1 - fh[(fh.year == year) & (fh.sex == sex)].set_index('group').pct_licensed.reindex(G5) / 100
            e = float((c * pi).sum())
            S = pd.concat([S, pd.DataFrame([dict(spec='fhwa_not_licensed', survey=year, lifetable=ly, sex=sex, from_age=x,
                life_exp=L.ex[x], years_not_driving=e, se=np.nan, moe90=np.nan, years_driving=L.ex[x] - e,
                share_of_remaining_life=e / L.ex[x], n=np.nan, n_not_driving=np.nan,
                note='FHWA DL-20 licensed share; licence records overstate active drivers at old ages')])])
S.to_csv(f'{OUT}/years_not_driving.csv', index=False)


# ---------------------------------------------------------------- 65+ totals and household context
rows = []
def add(year, measure, est, se, n, n_cases, denom, note=''):
    rows.append(dict(survey=year, measure=measure, estimate=est, se=se, moe90=1.645 * se if se == se else np.nan,
                     n=n, n_cases=n_cases, denominator=denom, note=note))

nh65 = cen.nursing2020.sum(); pop65 = cen.pop2020.sum()
for year, P in [(2017, p17), (2022, p22)]:
    nd = P[P.y == 1]
    if year == 2017:
        e, se = E17(lambda d, wc: [wmean(d, wc), (d[wc] * d.y).sum(), d[wc].sum()])
        share, cnt, tot = e; s_share, s_cnt, s_tot = se
    else:
        W = P.w.sum(); share = (P.w * P.y).sum() / W; cnt = (P.w * P.y).sum(); tot = W
        s_share = taylor_se(P, P.w * (P.y - share) / W)[0]; s_cnt = taylor_se(P, P.w * P.y)[0]; s_tot = np.nan
    add(year, 'share of people 65+ (households) who do not drive', share, s_share, len(P), len(nd), 'people 65+ in households')
    add(year, 'people 65+ in households who do not drive (count)', cnt, s_cnt, len(P), len(nd), 'count')
    add(year, 'people 65+ in households (weighted total)', tot, s_tot, len(P), len(P), 'count')
    adj_share = (cnt + nh65) / (tot + nh65)
    add(year, 'share of people 65+ incl. nursing-home residents who do not drive', adj_share,
        s_share * tot / (tot + nh65), len(P), len(nd), 'people 65+ in households + 2020 nursing-facility residents',
        'nursing-home count from 2020 Census, survey from NHTS year')
    add(year, 'people 65+ not driving incl. nursing-home residents (count)', cnt + nh65, s_cnt, len(P), len(nd), 'count')
    # context among non-drivers
    for lab, cond in [('non-drivers 65+ living in a household with no driver', lambda d: d.DRVRCNT == 0),
                      ('non-drivers 65+ living in a household with no vehicle', lambda d: d.HHVEHCNT == 0),
                      ('non-drivers 65+ who report a medical condition made them give up driving', lambda d: d.CONDRIVE == 1),
                      ('non-drivers 65+ reporting a travel-limiting medical condition', lambda d: d.MEDCOND == 1),
                      ('non-drivers 65+ with a travel-limiting condition all their life', lambda d: d.MEDCOND6 == 3)]:
        for sex in ['All', 'M', 'F']:
            q = nd if sex == 'All' else nd[nd.sex == sex]
            q = q.assign(z=cond(q).astype(float))
            if year == 2017:
                e, se = E17(lambda d, wc: wmean(d, wc, 'z'), q); e, se = float(e), float(se)
            else:
                W = q.w.sum(); e = (q.w * q.z).sum() / W; se = taylor_se(q, q.w * (q.z - e) / W)[0]
            add(year, f'{lab} ({sex})', e, se, len(q), int(q.z.sum()), 'non-drivers 65+ in households')
    # all people 65+ with no driver in household (larger group affected)
    q = P.assign(z=(P.DRVRCNT == 0).astype(float))
    if year == 2017:
        e, se = E17(lambda d, wc: wmean(d, wc, 'z'), q); e, se = float(e), float(se)
    else:
        W = q.w.sum(); e = (q.w * q.z).sum() / W; se = taylor_se(q, q.w * (q.z - e) / W)[0]
    add(year, 'people 65+ living in a household with no driver', e, se, len(q), int(q.z.sum()), 'people 65+ in households')
T = pd.DataFrame(rows)
T.to_csv(f'{OUT}/not_driving_65plus_totals.csv', index=False)


# ---------------------------------------------------------------- 2017 vs 2022 diagnostics
rows = []
for year, P in [(2017, p17), (2022, p22)]:
    for sex in ['M', 'F']:
        d = P[P.sex == sex]
        for g in G5:
            x = d[d.g5 == g]
            rows.append(dict(survey=year, sex=sex, age_group=g, n=len(x),
                             unweighted_share_of_65plus_sample=len(x) / len(d),
                             weighted_share_of_65plus=x.w.sum() / d.w.sum(),
                             census2020_share_of_65plus=float(cen[(cen.sex == sex) & (cen.group == g)].pop2020.iloc[0] / cen[cen.sex == sex].pop2020.sum()),
                             unweighted_share_not_driving=x.y.mean(), weighted_share_not_driving=wmean(x, 'w'),
                             zero_trip_rate_drivers=wmean(x[x.y == 0].assign(z=(x.CNTTDTR == 0).astype(float)), 'w', 'z'),
                             zero_trip_rate_nondrivers=wmean(x[x.y == 1].assign(z=(x.CNTTDTR == 0).astype(float)), 'w', 'z') if x.y.sum() else np.nan,
                             self_report_rate=float(np.average((x.PROXY == 1), weights=x.w)),
                             mean_weight_nondriver_over_driver=(x[x.y == 1].w.mean() / x[x.y == 0].w.mean()) if x.y.sum() else np.nan))
D = pd.DataFrame(rows)
D.to_csv(f'{OUT}/survey_2017_vs_2022.csv', index=False)

pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
print(A5.round(4).to_string())
print(S[['spec', 'survey', 'lifetable', 'sex', 'from_age', 'life_exp', 'years_not_driving', 'se', 'n', 'n_not_driving']].round(3).to_string())
print(T.round(4).to_string())
print(D.round(3).to_string())
