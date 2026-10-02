# maxmautner.com charts

Code, inputs, and data behind the charts on [maxmautner.com](https://maxmautner.com).
Each folder is one post. `style.py` holds the shared look.

## Posts

| Post | Folder |
|---|---|
| [When we talk about traffic violence](https://maxmautner.com/crashes) | [`2026-09-28-traffic-violence`](2026-09-28-traffic-violence) |
| [California now permits nearly as many backyard homes as houses](https://maxmautner.com/adus) | [`2026-10-02-california-adus`](2026-10-02-california-adus) |

## Running a post's charts

```
pip install -r requirements.txt
cd <post folder>
python charts.py
```

Each post folder has its own README listing its inputs, sources, method, and limitations.

## Conventions

- Every published post is tagged (for example `2026-09-28-traffic-violence`), and the post
  links to that tag. Changes after publication show up in the history.
- Data fetched from the web is committed under the post's `data/` folder with its fetch
  date, so charts reproduce exactly as published even after the source is revised.
- Hand-entered numbers live in each post's `inputs.py`, next to their citations.
