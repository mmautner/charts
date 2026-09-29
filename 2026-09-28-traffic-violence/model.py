"""The arithmetic behind both charts. Run it on its own to print every number."""
import json
from pathlib import Path
import numpy as np
from inputs import *

HERE = Path(__file__).resolve().parent

def load_population():
    path = HERE / "data" / "census_population.json"
    if not path.exists():
        raise SystemExit("data/census_population.json is missing. Run fetch_census.py first.")
    return json.loads(path.read_text())["population"]

# Chart 1: lifetime outcomes among the people the average American knows.
# Expected deaths = network size x lifetime odds of crash death.
# Serious injuries scale deaths by NHTSA's ratio of MAIS 3-5 injuries to deaths.
SERIOUS_PER_DEATH = (MAIS3_2019 + MAIS4_2019 + MAIS5_2019) / FATALITIES_2019

def lifetime_counts(network=NETWORK_SIZE_MEAN):
    killed = network * LIFETIME_ODDS_CRASH_DEATH
    return killed, killed * SERIOUS_PER_DEATH

# Chart 2: chance of knowing at least 1 person killed in a crash, by age.
# Each acquaintance dies in a crash in a given year with probability
# p = deaths / population. With n acquaintances held from age 18 and
# independent events, P(at least 1 by age a) = 1 - (1 - p)^(n * (a - 18)).
def p_know_killed(age, population, network=NETWORK_SIZE_MEAN):
    p = CRASH_DEATHS_2024 / population
    years = np.clip(np.asarray(age, dtype=float) - 18, 0, None)
    return 1 - (1 - p) ** (network * years)

if __name__ == "__main__":
    pop = load_population()
    for label, n in [("mean", NETWORK_SIZE_MEAN), ("median", NETWORK_SIZE_MEDIAN)]:
        k, s = lifetime_counts(n)
        print(f"Network {label} ({n}): ~{k:.1f} killed, ~{s:.1f} seriously injured")
        print("   " + ", ".join(f"by {a}: {100*p_know_killed(a, pop, n):.0f}%" for a in (30, 40, 50)))
    print(f"Serious injuries per death: {SERIOUS_PER_DEATH:.2f}")
    print(f"Annual crash death risk per person: 1 in {pop/CRASH_DEATHS_2024:,.0f}")
