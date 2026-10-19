"""Crash risk by driver age, per mile and per person, 2017: FARS fatal crashes / NHTS 2017 miles driven.
Also: how people 65+ who don't drive get around (NHTS 2017 trips).

usage (from the post folder):  python -I model/crash_risk.py raw data

Inputs:
  raw/nhts17/{perpub,trippub}.csv, perwgt.sas7bdat   2017 NHTS (98 jackknife replicate weights)
  raw/fars/FARS2017NationalCSV.zip                    NHTSA FARS 2017 (census of fatal crashes; no sampling error)

Definitions:
  light vehicle  = FARS BODY_TYP 1-49 (cars, SUVs, vans, pickups); NHTS TRPTRANS 3-6 (car, SUV, van, pickup).
  miles driven   = NHTS VMT_MILE on trips where the person drove (DRVR_FLG = 1) a light vehicle; annual = trip
                   weight WTTRDFIN (= 365 x person weight). Replicate trip weights = 365 x WTPERFIN1..98.
  drivers        = NHTS persons with DRIVER = 1 ("driver status, derived"), age 16+.
  FARS age       = driver AGE (unknown 998/999 dropped and reported).
  involvement    = a light-vehicle driver in a fatal crash. Others killed = people killed outside that driver's vehicle
                   (other vehicles' occupants + pedestrians/cyclists); in multi-vehicle crashes each involved driver is
                   credited, so these are "deaths of others in crashes involving drivers of age X", not blame.
  ped/cyclist killed by lone vehicle = non-occupants killed in crashes with exactly one motor vehicle (a light vehicle),
                   credited to that vehicle's driver: the cleanest attribution FARS allows.
Variance: SE of NHTS totals = sqrt(6/7 * sum (rep_i - est)^2); FARS counts treated as fixed, so SE(rate) =
rate * SE(miles)/miles. NHTS covers household residents' travel; commercial and visitor miles are excluded, as are
their FARS counterparts only partly (FARS counts every crash), which raises every age group's rate by a similar factor.
"""
import os, sys, zipfile
import numpy as np, pandas as pd

RAW = sys.argv[1] if len(sys.argv) > 1 else 'raw'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'data'
REPS = [f'WTPERFIN{i}' for i in range(1, 99)]
JK = 6 / 7
BINS = [16, 20, 25, 30, 40, 50, 60, 65, 70, 75, 80, 85, 200]
LABS = ['16-19', '20-24', '25-29', '30-39', '40-49', '50-59', '60-64', '65-69', '70-74', '75-79', '80-84', '85+']
ROLLUP = {'16-24': ['16-19', '20-24'], '25-64': ['25-29', '30-39', '40-49', '50-59', '60-64'],
          '65+': ['65-69', '70-74', '75-79', '80-84', '85+'], '65-74': ['65-69', '70-74'], '75+': ['75-79', '80-84', '85+'], '80+': ['80-84', '85+'],
          'All 16+': LABS}
grp = lambda a: pd.cut(a, BINS, right=False, labels=LABS).astype(str)

# ------------------------------------------------------------------ NHTS 2017
r = pd.read_sas(f'{RAW}/nhts17/perwgt.sas7bdat')
for k in ['HOUSEID', 'PERSONID']:
    if r[k].dtype == object:
        r[k] = r[k].str.decode('ascii')
    r[k] = r[k].astype(np.int64)
p = pd.read_csv(f'{RAW}/nhts17/perpub.csv', usecols=['HOUSEID', 'PERSONID', 'R_AGE_IMP', 'DRIVER', 'WTPERFIN'])
p = p.merge(r[['HOUSEID', 'PERSONID'] + REPS], on=['HOUSEID', 'PERSONID'], how='left')
assert p[REPS[0]].notna().all()
p = p[p.R_AGE_IMP >= 16].copy()
p['g'] = grp(p.R_AGE_IMP)
W = ['WTPERFIN'] + REPS

t = pd.read_csv(f'{RAW}/nhts17/trippub.csv', usecols=['HOUSEID', 'PERSONID', 'TRPTRANS', 'DRVR_FLG', 'VMT_MILE', 'TRPMILES',
                                                      'WTTRDFIN', 'R_AGE_IMP'])
t = t[t.R_AGE_IMP >= 16]
assert np.allclose(t.merge(p[['HOUSEID', 'PERSONID', 'WTPERFIN']], on=['HOUSEID', 'PERSONID']).eval('WTTRDFIN / WTPERFIN'), 365)
drv = t[(t.DRVR_FLG == 1) & t.TRPTRANS.isin([3, 4, 5, 6])].copy()
n_vmt_missing = int((drv.VMT_MILE < 0).sum())
drv = drv[drv.VMT_MILE >= 0].merge(p[['HOUSEID', 'PERSONID', 'g'] + W], on=['HOUSEID', 'PERSONID'])


def totals(df, val, gcol='g'):
    """weighted totals (full + 98 replicates) by group; val is a column (sum of val*w*365 for trips) or None (count)"""
    out = {}
    for c in W:
        x = df[c] * (365 if val else 1) * (df[val] if val else 1)
        out[c] = x.groupby(df[gcol]).sum()
    return pd.DataFrame(out)


def with_rollups(T):
    for k, v in ROLLUP.items():
        T.loc[k] = T.loc[v].sum()
    return T


miles = with_rollups(totals(drv, 'VMT_MILE'))
drv_cap = drv.assign(VMT_MILE=drv.VMT_MILE.clip(upper=500))
miles_cap = with_rollups(totals(drv_cap, 'VMT_MILE'))
drivers = with_rollups(totals(p[p.DRIVER == 1], None))
persons = with_rollups(totals(p, None))
se = lambda T: np.sqrt(JK * T[REPS].sub(T.WTPERFIN, axis=0).pow(2).sum(axis=1))


def ratio(N, D):  # per-person ratio with replicate SE
    R = N[W] / D[W]
    return R.WTPERFIN, np.sqrt(JK * R[REPS].sub(R.WTPERFIN, axis=0).pow(2).sum(axis=1))


mpd, mpd_se = ratio(miles, drivers)
n_trips = drv.groupby('g').size(); n_drv = p[p.DRIVER == 1].groupby('g').size(); n_per = p.groupby('g').size()
for k, v in ROLLUP.items():
    n_trips[k] = n_trips[v].sum(); n_drv[k] = n_drv[v].sum(); n_per[k] = n_per[v].sum()

# ------------------------------------------------------------------ FARS 2017
z = zipfile.ZipFile(f'{RAW}/fars/FARS2017NationalCSV.zip')
rd = lambda n, cols: pd.read_csv(z.open(n), usecols=cols, encoding='latin-1', low_memory=False)
per = rd('Person.CSV', ['ST_CASE', 'VEH_NO', 'PER_TYP', 'AGE', 'INJ_SEV', 'BODY_TYP'])
acc = rd('accident.CSV', ['ST_CASE', 'VE_TOTAL', 'FATALS'])
veh = rd('Vehicle.CSV', ['ST_CASE', 'VEH_NO', 'BODY_TYP'])
light_veh = veh[veh.BODY_TYP.between(1, 49)]
dr = per[(per.PER_TYP == 1) & (per.VEH_NO > 0)].merge(light_veh[['ST_CASE', 'VEH_NO']], on=['ST_CASE', 'VEH_NO'])
n_dr_unknown_age = int((~dr.AGE.between(16, 120)).sum())
n_dr_under16 = int(dr.AGE.between(0, 15).sum())
dr = dr[dr.AGE.between(16, 120)].copy()
dr['g'] = grp(dr.AGE)
killed = per[per.INJ_SEV == 4]
# deaths outside each driver's vehicle, per crash
kc = killed.groupby('ST_CASE').size().rename('k_all')
kv = killed[killed.VEH_NO > 0].groupby(['ST_CASE', 'VEH_NO']).size().rename('k_own')
dr = dr.merge(kc, on='ST_CASE', how='left').merge(kv, on=['ST_CASE', 'VEH_NO'], how='left').fillna({'k_all': 0, 'k_own': 0})
dr['driver_killed'] = (dr.INJ_SEV == 4).astype(int)
dr['others_killed'] = dr.k_all - dr.k_own
dr['passengers_killed'] = dr.k_own - dr.driver_killed
nonocc = killed[killed.VEH_NO == 0].groupby('ST_CASE').size().rename('k_nonocc')
dr = dr.merge(nonocc, on='ST_CASE', how='left').fillna({'k_nonocc': 0}).merge(acc[['ST_CASE', 'VE_TOTAL']], on='ST_CASE')
dr['ped_killed_lone_vehicle'] = np.where(dr.VE_TOTAL == 1, dr.k_nonocc, 0)
F = dr.groupby('g')[['driver_killed', 'passengers_killed', 'others_killed', 'ped_killed_lone_vehicle']].sum()
F['involvements'] = dr.groupby('g').size()
F = F.reindex(LABS)
for k, v in ROLLUP.items():
    F.loc[k] = F.loc[v].sum()

# ------------------------------------------------------------------ table
rows = []
for g in LABS + list(ROLLUP):
    m, mse = miles.loc[g, 'WTPERFIN'], se(miles).loc[g]
    o = {'driver_age': g, 'is_rollup': g in ROLLUP,
         'population_household': persons.loc[g, 'WTPERFIN'], 'n_persons': int(n_per[g]),
         'drivers': drivers.loc[g, 'WTPERFIN'], 'drivers_se': se(drivers).loc[g], 'n_drivers': int(n_drv[g]),
         'share_who_drive': drivers.loc[g, 'WTPERFIN'] / persons.loc[g, 'WTPERFIN'],
         'miles_billion': m / 1e9, 'miles_billion_se': mse / 1e9, 'n_driver_trips': int(n_trips[g]),
         'miles_per_driver': mpd[g], 'miles_per_driver_se': mpd_se[g],
         'share_of_all_miles': m / miles.loc['All 16+', 'WTPERFIN']}
    for c in ['involvements', 'driver_killed', 'passengers_killed', 'others_killed', 'ped_killed_lone_vehicle']:
        o[c] = int(F.loc[g, c])
    o['share_of_involvements'] = F.loc[g, 'involvements'] / F.loc['All 16+', 'involvements']
    o['share_of_others_killed'] = F.loc[g, 'others_killed'] / F.loc['All 16+', 'others_killed']
    o['share_of_ped_killed_lone_vehicle'] = F.loc[g, 'ped_killed_lone_vehicle'] / F.loc['All 16+', 'ped_killed_lone_vehicle']
    for c, lab in [('involvements', 'involvements'), ('others_killed', 'others_killed'), ('driver_killed', 'driver_deaths'),
                   ('ped_killed_lone_vehicle', 'ped_killed_lone_vehicle')]:
        rate = F.loc[g, c] / (m / 1e8)
        o[f'{lab}_per_100M_miles'] = rate
        o[f'{lab}_per_100M_miles_se'] = rate * mse / m
    rcap = F.loc[g, 'involvements'] / (miles_cap.loc[g, 'WTPERFIN'] / 1e8)
    o['involvements_per_100M_miles_tripcap500'] = rcap
    o['involvements_per_100k_drivers'] = F.loc[g, 'involvements'] / drivers.loc[g, 'WTPERFIN'] * 1e5
    o['others_killed_per_100k_people'] = F.loc[g, 'others_killed'] / persons.loc[g, 'WTPERFIN'] * 1e5
    o['involvements_per_100k_people'] = F.loc[g, 'involvements'] / persons.loc[g, 'WTPERFIN'] * 1e5
    rows.append(o)
T = pd.DataFrame(rows)
T['note'] = ('2017. FARS light-vehicle drivers (BODY_TYP 1-49) in fatal crashes / NHTS 2017 miles driven in household light '
             'vehicles by household residents. Population = household population (NHTS). Others killed counts deaths outside '
             'the driver\'s vehicle in any crash the driver was in (multi-vehicle crashes credit every driver). FARS counts '
             f'have no sampling error. Dropped: {n_dr_unknown_age} drivers with unknown age, {n_dr_under16} under 16; '
             f'{n_vmt_missing} NHTS driver trips with missing miles.')
os.makedirs(OUT, exist_ok=True)
T.to_csv(f'{OUT}/crash_risk_by_age_2017.csv', index=False)

# ------------------------------------------------------------------ how non-drivers 65+ get around
tt = t.merge(p[['HOUSEID', 'PERSONID', 'DRIVER'] + W], on=['HOUSEID', 'PERSONID'])
tt = tt[tt.R_AGE_IMP >= 65]
# NHTS 2017 TRPTRANS: 1 walk, 2 bicycle, 3-6 car/SUV/van/pickup, 18 rental car, 12 paratransit/dial-a-ride,
# 11/14/15/16/20 public bus, intercity bus, Amtrak/commuter rail, subway/light rail, ferry, 17 taxi incl. Uber/Lyft
MODE = {1: 'walk', 2: 'bike', 3: 'car', 4: 'car', 5: 'car', 6: 'car', 18: 'car', 11: 'public transit', 14: 'public transit',
        15: 'public transit', 16: 'public transit', 20: 'public transit', 12: 'paratransit', 17: 'taxi or ride-hailing'}
mode = tt.TRPTRANS.map(MODE).fillna('other')
tt['mode'] = np.where(mode == 'car', np.where(tt.DRVR_FLG == 1, 'car, driving', 'car, riding'), mode)
pp = p[p.R_AGE_IMP >= 65]
rows = []
for dname, dcode in [('drives', 1), ('does not drive', 2)]:
    x = tt[tt.DRIVER == dcode]
    tot = pd.Series({c: (x[c] * 365).sum() for c in W})
    ppl = pd.Series({c: pp.loc[pp.DRIVER == dcode, c].sum() for c in W})
    trips_per_day = tot / 365 / ppl
    rows.append({'group': f'65+, {dname}', 'measure': 'trips per person per day', 'estimate': trips_per_day.WTPERFIN,
                 'se': np.sqrt(JK * ((trips_per_day[REPS] - trips_per_day.WTPERFIN) ** 2).sum()),
                 'n_persons': int((pp.DRIVER == dcode).sum()), 'n_trips': len(x)})
    for mname, mx in x.groupby('mode'):
        sh = pd.Series({c: (mx[c]).sum() / x[c].sum() for c in W})
        rows.append({'group': f'65+, {dname}', 'measure': f'share of trips: {mname}', 'estimate': sh.WTPERFIN,
                     'se': np.sqrt(JK * ((sh[REPS] - sh.WTPERFIN) ** 2).sum()),
                     'n_persons': int((pp.DRIVER == dcode).sum()), 'n_trips': len(mx)})
M = pd.DataFrame(rows)
M['moe90'] = 1.645 * M.se
M['flag_lt50'] = M.n_trips < 50
M.to_csv(f'{OUT}/nondrivers_65plus_modes_2017.csv', index=False)

pd.set_option('display.width', 250, 'display.max_columns', 40)
show = ['driver_age', 'drivers', 'share_who_drive', 'miles_per_driver', 'miles_per_driver_se', 'share_of_all_miles', 'involvements',
        'involvements_per_100M_miles', 'involvements_per_100M_miles_se', 'involvements_per_100M_miles_tripcap500',
        'driver_deaths_per_100M_miles', 'others_killed_per_100M_miles', 'share_of_involvements', 'share_of_others_killed',
        'ped_killed_lone_vehicle', 'share_of_ped_killed_lone_vehicle', 'involvements_per_100k_people', 'others_killed_per_100k_people',
        'n_driver_trips', 'n_drivers']
print(T[show].round(3).to_string(index=False))
print(T.note.iloc[0])
print(M.round(3).to_string(index=False))
