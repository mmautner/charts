"""Fetch 2020 Census DHC national tables: P12 (total pop by sex x age), PCO1 (group quarters pop
by sex x age), PCO5 (nursing facility pop by sex x age).
usage: CENSUS_API_KEY=... python -I inputs/fetch_census.py raw/census
The key is read from the environment only; it is never written to disk."""
import json, os, sys, urllib.request

out = sys.argv[1] if len(sys.argv) > 1 else 'raw/census'
os.makedirs(out, exist_ok=True)
key = os.environ['CENSUS_API_KEY']
for table in ['P12', 'PCO1', 'PCO5']:
    url = f'https://api.census.gov/data/2020/dec/dhc?get=NAME,group({table})&for=us:*'
    with urllib.request.urlopen(url + f'&key={key}', timeout=60) as r:
        data = json.load(r)
    with open(f'{out}/{table}_us.json', 'w') as f:
        json.dump(data, f)
    meta = f'https://api.census.gov/data/2020/dec/dhc/groups/{table}.json'
    with urllib.request.urlopen(meta, timeout=60) as r:
        with open(f'{out}/{table}_vars.json', 'wb') as f:
            f.write(r.read())
    print(table, len(data[0]), 'columns')

# ACS 1-year households by vehicles available (B25044) and by age of householder (B25045), U.S.
for year in [2017, 2022]:
    for table in ['B25044', 'B25045']:
        url = f'https://api.census.gov/data/{year}/acs/acs1?get=NAME,group({table})&for=us:*'
        with urllib.request.urlopen(url + f'&key={key}', timeout=60) as r:
            data = json.load(r)
        with open(f'{out}/{table}_{year}_us.json', 'w') as f:
            json.dump(data, f)
        print(table, year, 'ok')
