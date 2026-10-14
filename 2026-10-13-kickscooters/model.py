"""The arithmetic behind the chart. Run it on its own to print every number."""
from inputs import *

LB_PER_KG = 1 / 0.45359237
TRAITS = ["Under 10 lb", "200 mm+ wheels", "Hand brake"]

def scooters():
    """Rows sorted lightest first: (model, lb, wheel_mm, traits)."""
    rows = []
    for model, w, unit, wheel, hand, _ in SCOOTERS:
        lb = w * LB_PER_KG if unit == "kg" else w
        rows.append((model, lb, wheel, [lb < LIGHT_LB, wheel >= BIG_WHEEL_MM, hand]))
    return sorted(rows, key=lambda r: r[1])

def check_pick_2(rows):
    """The chart's title claim: no model has all 3, and every pair exists."""
    assert not any(all(t) for *_, t in rows), "a model has all 3 traits"
    for skip in range(3):
        assert any(all(t[i] for i in range(3) if i != skip) for *_, t in rows), f"no model has the pair without {TRAITS[skip]}"

if __name__ == "__main__":
    rows = scooters()
    check_pick_2(rows)
    for m, lb, wheel, t in rows:
        print(f"{m:20s} {lb:5.2f} lb  {wheel} mm  " + "  ".join(n for n, on in zip(TRAITS, t) if on))
    print(f"Heaviest / lightest: {rows[-1][1] / rows[0][1]:.2f}x")
