# maxmautner.com charts

Code, inputs, and data behind the charts on [maxmautner.com](https://maxmautner.com).
Each folder is one post. `style.py` holds the shared look.

## Posts

| Post | Folder |
|---|---|
| [When we talk about traffic violence](https://maxmautner.com/crashes) | [`2026-09-28-traffic-violence`](2026-09-28-traffic-violence) |
| [1 in 4 new California homes is in someone's backyard](https://maxmautner.com/adus) | [`2026-10-02-backyard-homes`](2026-10-02-backyard-homes) |
| [Driving 5 mph slower beats driving 5% less](https://maxmautner.com/slower) | [`2026-10-03-speed-and-miles`](2026-10-03-speed-and-miles) |
| [How fast is a car, after you pay for it?](https://maxmautner.com/howfast) | [`2026-10-12-car-speed`](2026-10-12-car-speed) |
| [Things I wish I had known about kickscooters](https://maxmautner.com/kickscooter) | [`2026-10-13-kickscooters`](2026-10-13-kickscooters) |
| [Who lives without a car in the Bay Area](https://maxmautner.com/sf-car-free) | [`2026-10-17-car-free`](2026-10-17-car-free) |
| [The years Americans outlive driving](https://maxmautner.com/senior-driving) | [`2026-10-19-senior-driving`](2026-10-19-senior-driving) |
| [The Bay Area will pay more to bail out America's highways than to keep its own trains and buses running](https://maxmautner.com/bay-area-highway-bill) | [`2026-10-24-bay-area-highway-bill`](2026-10-24-bay-area-highway-bill) |
| [Burlingame's city government collects 1.7x as much revenue per resident as San Mateo's](https://maxmautner.com/burlingame-vs-san-mateo) | [`2026-10-27-city-finances`](2026-10-27-city-finances) |

## Running a post's charts

```
pip install -r requirements.txt
cd <post folder>
python charts.py          # posts through 2026-10-13
python charts/charts.py   # posts from 2026-10-17 on
```

Newer post folders split into `inputs/` (download/fetch scripts), `model/` (estimates),
`charts/`, `data/` (the committed CSVs the charts read), and `output/` (PNGs). Their charts
re-render from `data/` alone; raw downloads aren't committed.

Each post folder has its own README listing its inputs, sources, method, and limitations.

## Conventions

- Every published post is tagged (for example `2026-09-28-traffic-violence`), and the post
  links to that tag. Changes after publication show up in the history.
- Data fetched from the web is committed under the post's `data/` folder with its fetch
  date, so charts reproduce exactly as published even after the source is revised.
- Hand-entered numbers live in each post's `inputs.py`, next to their citations.
