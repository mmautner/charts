"""Hand-entered numbers, with the exact place each comes from.

Weights are as each manufacturer (or, for Xootr, its current US distributor)
lists them, in the unit they list them. model.py converts kg to lb.
All pages accessed 2026-10-13.
"""

# (model, weight, unit, wheel diameter mm, hand-operated brake, source)
SCOOTERS = [
    # Razor product page: 8.38 lb, 8" (200 mm) wheels, rear-fender brake.
    ("Razor A5 Lux", 8.38, "lb", 200, False, "https://razor.com/?p=17024"),
    # Razor product page: 10.93 lb, 10" (254 mm) wheels, rear-fender brake.
    ("Razor A6", 10.93, "lb", 254, False, "https://razor.com/?p=17038"),
    # Scooter4US spec tables. All Xootrs: 180 mm wheels, front hand brake + rear fender.
    ("Xootr Dash", 9.9, "lb", 180, True, "https://scooter4us.com/products/xootr-kick-scooter-dash-red"),
    # MG spec table says 10.8 lb; the same page's description says 10.9 lb.
    ("Xootr MG", 10.8, "lb", 180, True, "https://scooter4us.com/products/xootr-kick-scooter-mg"),
    ("Xootr Cruz", 11.0, "lb", 180, True, "https://scooter4us.com/products/xootr-kick-scooter-cruz"),
    ("Xootr Street", 11.5, "lb", 180, True, "https://scooter4us.com/products/xootr-kick-scooter-street"),
    # Micro (Switzerland) Technical Details tables. Each page also shows a looser
    # "Product Weight" range (e.g. 3-5 kg); the specific "Weight" row is used.
    # Metropolitan hand brake: feature bullet on https://www.micro-scooter.com/ch_en/adults
    ("Micro Metropolitan", 4.9, "kg", 200, True, "https://www.micro-scooter.com/ch_en/micro-metropolitan-schwarz"),
    ("Micro Classic", 4.95, "kg", 200, False, "https://www.micro-scooter.com/ch_en/micro-black-white"),
    # 6.1 kg; US retailer KidslandUSA lists 13.5 lb, consistent.
    ("Micro Suspension", 6.1, "kg", 200, False, "https://www.micro-scooter.com/ch_en/micro-suspension"),
    # Decathlon UAE (the regional page that loaded): 7.4 kg, 200 mm, handlebar brake.
    ("Oxelo Town 9 EF", 7.4, "kg", 200, True, "https://decathlon.ae/products/town-9-ef-v2-adult-scooter"),
]
# Excluded: Micro Speed (3.75 kg) and other models with wheels under 180 mm,
# and the Hudora BigWheel 205 (no manufacturer-listed weight found).

# The "pick 2" cutoffs, printed on the chart.
LIGHT_LB = 10
BIG_WHEEL_MM = 200
