# When we talk about traffic violence

Code and inputs behind the charts in
["When we talk about traffic violence"](https://maxmautner.com/crashes) on maxmautner.com.

The charts answer 2 questions: among the people the average American knows, how many
will be killed or seriously injured in a crash over a lifetime, and by what age is it
likely that someone they know has been killed in one.

## Reproduce

From this folder, after `pip install -r ../requirements.txt`:

```
python fetch_census.py   # downloads the Census estimate to data/
python model.py          # prints every number the charts use
python charts.py         # writes the PNGs to output/
```

Run `fetch_census.py` once and commit `data/`. After that, the charts reproduce from the
committed file, and `fetch_census.py` is only needed to compare against a newer release.

## Inputs

| Input | Value | Source |
|---|---|---|
| Lifetime odds of dying in a motor vehicle crash | 1 in 101 | [NSC Injury Facts, Odds of Dying](https://injuryfacts.nsc.org/all-injuries/preventable-death-overview/odds-of-dying/) |
| US motor vehicle crash deaths, 2024 | 39,254 | [NSC Injury Facts, Motor Vehicle Introduction](https://injuryfacts.nsc.org/motor-vehicle/overview/introduction/) |
| US resident population, July 1, 2024 | fetched (340,003,797 in Vintage 2025) | [Census NST-EST2025-ALLDATA](https://www.census.gov/data/datasets/time-series/demo/popest/2020s-national-total.html) |
| Mean personal network size | 611 (median 472) | [McCormick, Salganik & Zheng 2010](https://www.princeton.edu/~mjs3/mccormick_salganik_zheng10.pdf), Section 4.1, p. 64 |
| Crash injuries by severity, 2019 | 36,500 deaths; 141,167 MAIS 3; 19,285 MAIS 4; 7,187 MAIS 5 | [NHTSA DOT HS 813 403](https://crashstats.nhtsa.dot.gov/Api/Public/ViewPublication/813403), Table 1-3, p. 16 |

All hand-entered values live in `inputs.py` with their citations. Only the population is
fetched, because it is the only input published as a machine-readable file.

## Method

**Lifetime counts (dot grid).** Expected acquaintances killed = network size × lifetime
odds = 611 / 101 ≈ 6. Serious injuries use NHTSA's ratio of MAIS 3 to 5 injuries to
deaths in 2019 (167,639 / 36,500 ≈ 4.6), so ≈ 28.

**Chance by age (curve).** Each acquaintance's annual chance of dying in a crash is
p = 2024 deaths / 2024 population ≈ 1 in 8,662. With n = 611 acquaintances from age 18
and independent events, the chance of knowing at least 1 person killed by age a is
1 − (1 − p)^(n × (a − 18)).

## Assumptions and limitations

- **Mean vs. median network.** The paper reports a mean of 611 and a median of 472. Using
  the median gives ~5 killed, ~22 seriously injured, and ~70% by age 40 instead of ~79%.
  `model.py` prints both.
- **What "know" means.** The paper counts people you have had contact with in the past
  2 years. The curve holds that network fixed from age 18, which overstates it at young
  ages. Real networks also turn over, so over a lifetime a person knows more than 611
  people, which pushes the other way.
- **Average risk and independence.** Crash risk varies by age, sex, place, and how much
  someone drives, and people's acquaintances are not a random sample of the country.
- **Years.** The injury ratio is from 2019; deaths and population are from 2024.
