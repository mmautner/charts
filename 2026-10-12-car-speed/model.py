"""The arithmetic behind every chart. Run it on its own to print every number."""
import csv, json
from pathlib import Path
from inputs import *

HERE = Path(__file__).resolve().parent
VEHICLES = ["New car", "Used car", "E-bike, Class 2", "E-bike, Class 3"]

def nhts():
    path = HERE / "data" / "nhts2022_short_trips.csv"
    if not path.exists():
        raise SystemExit("data/nhts2022_short_trips.csv is missing. Run fetch_nhts.py first.")
    return {r["trips"]: r for r in csv.DictReader(open(path))}

def fetched_on():
    return json.loads((HERE / "data" / "nhts2022_meta.json").read_text())["fetched_on"]

def federal_tax(income):
    taxable, tax, floor = max(income - STANDARD_DEDUCTION, 0), 0.0, 0.0
    for top, rate in FEDERAL_BRACKETS:
        tax += max(min(taxable, top) - floor, 0) * rate
        floor = top
    return tax

def take_home(wage):
    """Average after-tax pay per hour for a full-time worker at this gross wage.
    (Average, not marginal: smooth, and slightly kinder to the car.)"""
    gross = wage * HOURS_PER_YEAR
    return (gross - federal_tax(gross)) / HOURS_PER_YEAR - wage * (FICA + STATE_TAX)

def door_to_door_mph():
    """Average short trip, including parking, walking, locking and signal waits."""
    n = nhts()["short"]
    car_moving, trip = float(n["mph"]), float(n["mean_miles"])
    car = trip / (trip / car_moving + CAR_TERMINAL_MIN / 60)
    bike_stop_min = EBIKE_LOCK_MIN + SIGNAL_WAIT_S / 60 * SIGNALS_PER_MILE * trip
    bike = {c: trip / (trip / v + bike_stop_min / 60) for c, v in EBIKE_MOVING_MPH.items()}
    return {"New car": car, "Used car": car, **{f"E-bike, {c}": v for c, v in bike.items()}}

def cost_per_mile(car_miles=CAR_MILES_PER_YEAR):
    """Dollars per mile. Car fixed costs (incl. home parking) spread over the car's annual miles."""
    new_fixed = NEW_CAR_ANNUAL_AT_15K - NEW_CAR_PER_MILE * AAA_MILES
    used_run = USED_CAR_RUNNING_5YR / 5 / EDMUNDS_MILES
    used_fixed = USED_CAR_5YR / 5 - used_run * EDMUNDS_MILES
    out = {"New car": (new_fixed + HOME_PARKING_PER_YEAR) / car_miles + NEW_CAR_PER_MILE,
           "Used car": (used_fixed + HOME_PARKING_PER_YEAR) / car_miles + used_run}
    for c, wh in WH_PER_MILE.items():
        out[f"E-bike, {c}"] = (EBIKE_PRICE / EBIKE_LIFE_YEARS / EBIKE_MILES_PER_YEAR
                               + BATTERY_PRICE / (BATTERY_CYCLES * BATTERY_WH / wh)
                               + EBIKE_UPKEEP_PER_YEAR / EBIKE_MILES_PER_YEAR
                               + wh / 1000 * ELECTRICITY_PER_KWH)
    return out

def effective_mph(vehicle, wage, car_miles=CAR_MILES_PER_YEAR):
    """Miles per hour of travel plus after-tax hours worked to pay for each mile."""
    v, c = door_to_door_mph()[vehicle], cost_per_mile(car_miles)[vehicle]
    return 1 / (1 / v + c / take_home(wage))

def hours_split(wage=MEDIAN_WAGE, miles=SHORT_TRIP_MILES_PER_YEAR):
    """(vehicle, hours travelling, hours working to pay) for a year of short trips."""
    v, c, pay = door_to_door_mph(), cost_per_mile(), take_home(wage)
    return [(k, miles / v[k], miles * c[k] / pay) for k in VEHICLES]

def crossover(a, b, lo=8.0, hi=200.0):
    """Lowest gross wage at which vehicle a's effective speed passes vehicle b's."""
    w = lo
    while w <= hi:
        if effective_mph(a, w) > effective_mph(b, w):
            return w
        w += 0.25
    return None

if __name__ == "__main__":
    n = nhts()
    print(f"NHTS 2022 driver trips <= 8 mi: {float(n['short']['mph']):.1f} mph moving, "
          f"{float(n['short']['mean_miles']):.2f} mi average, {float(n['short']['share_of_driver_miles']):.0%} of driver miles")
    print(f"Take-home per extra hour at the median wage: ${take_home(MEDIAN_WAGE):.2f}")
    for k in VEHICLES:
        print(f"  {k:<16} door-to-door {door_to_door_mph()[k]:5.1f} mph   {cost_per_mile()[k]*100:5.1f} c/mi   "
              f"effective at median {effective_mph(k, MEDIAN_WAGE):4.1f} mph")
    print(f"\nChart 1: {SHORT_TRIP_MILES_PER_YEAR:,} miles of short trips a year, median wage")
    for k, t, p in hours_split():
        print(f"  {k:<16} travel {t:5.0f} h  work {p:5.0f} h  total {t+p:5.0f} h  ({(t+p)/52:.1f} h/week)")
    print("\nChart 2 crossovers (gross wage where the first overtakes the second):")
    for a in ["New car", "Used car"]:
        for b in ["E-bike, Class 2", "E-bike, Class 3"]:
            x = crossover(a, b)
            print(f"  {a} passes {b}: {'above $%.2f' % x if x else 'never below $200'}")
