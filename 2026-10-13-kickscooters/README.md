# Things I wish I had known about kickscooters

Code and data behind the chart in ["Things I wish I had known about kickscooters"](https://maxmautner.com/kickscooter) on maxmautner.com.

The chart compares 10 popular unpowered adult kickscooters on manufacturer-listed weight, wheel size, and whether they have a hand-operated brake. With cutoffs of under 10 lb and 200 mm wheels, none has all 3, and each pair of 2 exists.

## Reproduce

From this folder, after `pip install -r ../requirements.txt`:

```
python model.py     # prints every scooter's weight and traits, and checks the pick-2 claim
python charts.py    # writes the PNGs to output/
```

`model.py` fails if a data change breaks the chart's title: a model with all 3 traits, or a pair with no model.

## Inputs

| Model | Listed weight | Wheels | Hand brake | Source |
|---|---|---|---|---|
| Razor A5 Lux | 8.38 lb | 200 mm | No | [Razor](https://razor.com/?p=17024) |
| Xootr Dash | 9.9 lb | 180 mm | Yes | [Scooter4US](https://scooter4us.com/products/xootr-kick-scooter-dash-red) |
| Xootr MG | 10.8 lb | 180 mm | Yes | [Scooter4US](https://scooter4us.com/products/xootr-kick-scooter-mg) |
| Micro Metropolitan | 4.9 kg | 200 mm | Yes | [Micro](https://www.micro-scooter.com/ch_en/micro-metropolitan-schwarz) |
| Micro Classic | 4.95 kg | 200 mm | No | [Micro](https://www.micro-scooter.com/ch_en/micro-black-white) |
| Razor A6 | 10.93 lb | 254 mm | No | [Razor](https://razor.com/?p=17038) |
| Xootr Cruz | 11.0 lb | 180 mm | Yes | [Scooter4US](https://scooter4us.com/products/xootr-kick-scooter-cruz) |
| Xootr Street | 11.5 lb | 180 mm | Yes | [Scooter4US](https://scooter4us.com/products/xootr-kick-scooter-street) |
| Micro Suspension | 6.1 kg | 200 mm | No | [Micro](https://www.micro-scooter.com/ch_en/micro-suspension) |
| Oxelo Town 9 EF | 7.4 kg | 200 mm | Yes | [Decathlon](https://decathlon.ae/products/town-9-ef-v2-adult-scooter) |

All pages accessed 2026-10-13. Every number and its citation is in `inputs.py`.

## Limitations

- **Listed, not weighed.** Weights are as manufacturers list them. Micro's pages also show a looser "Product Weight" range that conflicts with the specific figure, and Scooter4US lists the Xootr MG at both 10.8 and 10.9 lb.
- **The cutoffs are a choice.** The Xootr Dash sits 0.1 lb under the 10 lb line, and 180 mm Xootr wheels count as not big. Other cutoffs give a different grid.
- **Xootr via a distributor.** Xootr weights come from Scooter4US, its current US seller, not a Xootr-run site.
- **Hand brakes from feature lists.** The Micro Metropolitan's hand brake comes from a feature bullet on Micro's category page, not its spec table.
- **Selection.** Models with wheels under 180 mm (such as the 3.75 kg Micro Speed) are excluded. The Hudora BigWheel 205 is left out for lack of a listed weight.
