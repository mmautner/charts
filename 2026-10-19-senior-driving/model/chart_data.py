"""The series the charts draw -> data/chart_*.csv. Run after model/estimates.py and model/crash_risk.py.
usage (from the post folder): python -I model/chart_data.py"""
import pandas as pd

D = "data"
c = pd.read_csv(f"{D}/crash_risk_by_age_2017.csv").set_index("driver_age")
groups = [("16-24", "Under 25"), ("25-64", "25-64"), ("65-74", "65-74"), ("75+", "75 and older")]
rows = []
for g, lab in groups:
    r = c.loc[g]
    rows.append({"driver_age": g, "label": lab,
                 "crashes_per_100M_miles": r.involvements_per_100M_miles, "crashes_se": r.involvements_per_100M_miles_se,
                 "others_killed_per_100M_miles": r.others_killed_per_100M_miles, "others_killed_se": r.others_killed_per_100M_miles_se,
                 "driver_deaths_per_100M_miles": r.driver_deaths_per_100M_miles,
                 "fatal_crash_involvements": int(r.involvements), "others_killed": int(r.others_killed),
                 "drivers_killed": int(r.driver_killed), "share_of_others_killed": r.share_of_others_killed,
                 "share_of_miles": r.share_of_all_miles, "miles_per_driver": r.miles_per_driver,
                 "miles_per_driver_se": r.miles_per_driver_se, "n_driver_trips": int(r.n_driver_trips), "n_drivers": int(r.n_drivers)})
cp = pd.DataFrame(rows)
cp["teen_16_19_crashes_per_100M_miles"] = c.loc["16-19", "involvements_per_100M_miles"]
cp.to_csv(f"{D}/chart_crash_per_mile.csv", index=False)

y = pd.read_csv(f"{D}/years_not_driving.csv")
y = y[(y.spec == "incl_nursing_homes") & (y.survey == 2017) & (y.from_age == 65)]
y = y[["sex", "life_exp", "years_not_driving", "se", "years_driving", "share_of_remaining_life", "n", "n_not_driving"]]
m = pd.read_csv(f"{D}/nondrivers_65plus_modes_2017.csv")
tpd = m[m.measure == "trips per person per day"].set_index("group")
y["trips_per_day_drivers_65plus"] = tpd.loc["65+, drives", "estimate"]
y["trips_per_day_nondrivers_65plus"] = tpd.loc["65+, does not drive", "estimate"]
y.to_csv(f"{D}/chart_years_not_driving.csv", index=False)
print(cp.round(3).to_string(index=False)); print(y.round(3).to_string(index=False))
