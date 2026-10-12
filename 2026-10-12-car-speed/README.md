# How fast is a car, after you pay for it?

Code and data behind the charts in ["How fast is a car, after you pay for it?"](https://maxmautner.com/howfast) on maxmautner.com.

The charts redo Ivan Illich's "effective speed" arithmetic from *Energy and Equity* (1974) with current US data: miles divided by the hours spent travelling plus the after-tax hours worked to pay for the vehicle. They compare a new car, a used car, and a $999 e-bike at 20 mph and 28 mph assist on trips under 8 miles.

## Reproduce

From this folder, after `pip install -r ../requirements.txt`:

```
python fetch_nhts.py       # 2022 NHTS trip file, summarized to data/nhts2022_short_trips.csv
python model.py            # prints every number the charts use
python charts.py           # writes the PNGs to output/
python calculator.py       # writes output/howfast-calculator.html, the interactive chart (a Jekyll include)
```

To reuse an unzipped copy of the NHTS csv files: `python fetch_nhts.py --dir path/to/csv`.

## Inputs

| Input | Source |
|---|---|
| Driver trips under 8 miles: 14.8 mph, 3.26 miles average, 18% of driver miles | [2022 National Household Travel Survey](https://nhts.ornl.gov/) trip file, fetched |
| New car: $12,863 a year at 15,000 miles | [AAA Your Driving Costs 2026](https://www.repairerdrivennews.com/?p=248248); per-mile split from the [2025 fact sheet](https://newsroom.aaa.com/wp-content/uploads/2025/09/UPDATE-AAA-Fact-Sheet-Your-Driving-Cost-9.2025-1.pdf) |
| Used car: $37,905 over 5 years for a 2022 VW Passat | [Edmunds True Cost to Own](https://www.edmunds.com/volkswagen/passat/2022/cost-to-own/) |
| 10,900 miles per light-duty vehicle per year | [FHWA Highway Statistics 2022, VM-1](https://www.fhwa.dot.gov/policyinformation/statistics/2022/pdf/vm1.pdf) |
| Home parking: $1,700 a year | [Gabbe & Pierce 2016](https://accessmagazine.org/spring-2017/the-hidden-cost-of-bundled-parking/) |
| Parking search: 17 hours a year per driver; 2.43 trips a day | [INRIX](https://inrix.com/press-releases/parking-pain-us/); [AAA Foundation](https://aaafoundation.org/wp-content/uploads/2024/08/202408-AAAFTS-American-Driving-Survey-2023.pdf) |
| E-bike: $999; battery $575 for 672 Wh | [Lectric XP Lite2](https://lectricebikes.com/products/xp-lite-arctic-white-long-range-ebike); [battery](https://lectricebikes.com/products/xp-long-range-battery) |
| Battery life: 500 full charges | [Bosch](https://www.bosch-ebike.com/ca/news/11-questions-about-the-ebike-battery) |
| E-bike energy: 12.5 Wh/km | [Evtimov et al. 2015](https://yadda.icm.edu.pl/baztech/element/bwmeta1.element.baztech-fa13d23a-83be-4330-a51f-8812ae9e8a86/c/Evtimov.pdf) |
| E-bike moving speeds: 17.4 and 24.5 km/h | [Schleinitz et al. 2017](https://redundancy.webcms.tu-dresden.de/bu/verkehr/ivs/vpsy/ressourcen/dateien/publikationen/Schleinitz-et-al-2017-authors.pdf) |
| Cyclist signal wait: 15 s per signal | [Findings, 2019 (Enschede)](https://findingspress.org/article/9636-perceived-versus-actual-waiting-time-a-case-study-among-cyclists-in-enschede-the-netherlands) |
| Median wage $23.80; 2026 federal tax | BLS OEWS May 2024; IRS Rev. Proc. 2025-32 |

Every hand-entered number and its citation is in `inputs.py`.

## Method

**Effective speed** = miles / (hours travelling + hours worked to pay). Hours worked use average after-tax pay for a full-time single filer: federal income tax, 7.65% FICA, and a flat 5% state tax.

**Door to door.** NHTS car times are self-reported departure to arrival. Each car trip adds 2.2 minutes for parking search and the walk from the space. The German e-bike speeds exclude standstill, so each bike trip adds 1 minute to lock and unlock plus 15 seconds per signal at 2 signals a mile.

**Costs.** Car costs split into fixed (depreciation, insurance, finance, fees, plus home parking) and per-mile (fuel, maintenance, repairs, tires). Fixed costs are spread over 10,900 miles a year. The e-bike is written off to zero over 5 years at 3,000 miles a year, plus battery wear, $150 a year upkeep, and electricity at 18 cents per kWh.

## Limitations

- **Self-reported vs. measured.** Car speeds are self-reported; e-bike speeds come from sensors on German riders. The 28 mph figure rests on 9 riders.
- **Assumptions without a source:** 1 minute walking from a parking space, 1 minute to lock a bike, 2 signals a mile, 30 Wh a mile at 28 mph.
- **Short trips only.** Trips over 8 miles are 82% of driving miles. A household with no car pays for those some other way, which this does not price.
- **Left out:** e-bike theft and insurance, e-bike resale value, crash risk, and time saved on exercise.
- **One model each.** The used car is one Edmunds example and the e-bike is one Lectric model. Neither is a market average.
- **US data.** Costs, wages, taxes and car speeds are US figures; e-bike speeds and signal waits are European.
