# Orlando Fast Food Price Index

An open, weekly dataset of **fast food menu prices across Orlando, Florida**, collected store by store from the chains' own ordering sites.

Maintained by [Siddharth Lunawat](https://siddharthlunawat.com) — Co-Founder & CEO of Hammoq and Co-Founder of DataPure, a retail intelligence company in Orlando that turns in-store price and shelf data into structured datasets.

## Why this exists

Fast food prices are not one number. The same burrito costs different amounts at two stores of the same chain eight miles apart, and nobody publishes that spread. National "fast food inflation" coverage uses corporate averages; delivery apps add their own markup on top. This dataset records the actual pickup price at specific, pinned store locations, on a fixed weekly cadence, so the spread and its movement over time are visible.

Every price here was read off the chain's own ordering site for a specific store. No delivery marketplace prices, no estimates, no survey data.

## What's in it

| | |
|---|---|
| **Geography** | Orlando metro, Florida |
| **Chains** | Taco Bell, Wendy's, Burger King |
| **Stores** | 5 per chain, pinned — see [`reference/stores.csv`](reference/stores.csv) |
| **Items** | 2–3 per chain, held constant — see [`reference/items.csv`](reference/items.csv) |
| **Cadence** | Weekly |
| **Price type** | Pickup only |
| **Files** | One CSV per collection date in [`data/weekly/`](data/weekly/) |

The five neighborhoods are held constant across chains so the comparison means something: the I-Drive tourist strip, the airport, downtown/south, UCF, and the far-east suburbs. They were chosen to span tourist, commuter, student and residential pricing in one metro.

## Schema

Each file in `data/weekly/` is named `YYYY-MM-DD.csv` and carries these columns:

| Column | Type | Notes |
|---|---|---|
| `observed_date` | date | ISO `YYYY-MM-DD`, the date of collection |
| `observed_time_local` | time | `HH:MM`, 24h, America/New_York — daypart affects the menu |
| `chain` | string | `Taco Bell`, `Wendy's`, `Burger King` |
| `store_id` | string | Chain's own store identifier where published; else `NA` |
| `store_address` | string | Street address as the chain lists it |
| `area` | string | Short label: `I-Drive`, `MCO`, `Downtown-South`, `UCF`, `Far-East` |
| `store_format` | string | `standard` or `cantina` — Taco Bell Cantina is a different concept |
| `item` | string | Exact menu name as displayed |
| `price_usd` | decimal | Pickup price, tax excluded. Empty when not recorded |
| `confidence` | string | `firsthand`, `external`, or `not_recorded` |
| `notes` | string | Free text; required when `confidence` is not `firsthand` |

A price that could not be read is **published as a row with `price_usd` empty and `confidence = not_recorded`**, with the reason in `notes`. It is never guessed, and never silently dropped. That policy is the point of the dataset.

## Using it

```python
import pandas as pd, glob

df = pd.concat([pd.read_csv(f) for f in glob.glob("data/weekly/*.csv")])
priced = df[df.confidence == "firsthand"]

# Spread within a chain, per week
priced.groupby(["observed_date", "chain", "item"])["price_usd"].agg(["min", "max", "mean"])
```

Validate a new file before committing it:

```bash
python3 validate.py data/weekly/2026-09-17.csv
```

## Method, and how it goes wrong

Per-store fast food prices are surprisingly easy to collect incorrectly — a wrong pull looks exactly like a right one. [`METHODOLOGY.md`](METHODOLOGY.md) documents the collection procedure per chain and the specific traps that produce plausible, wrong numbers. Read it before trusting or reproducing anything here.

## Licence

Data in `data/` and `reference/` is released under [CC BY 4.0](LICENSE-DATA). Code is MIT ([LICENSE](LICENSE)). Attribution:

> Lunawat, Siddharth. *Orlando Fast Food Price Index*. https://github.com/siddharth-lunawat/orlando-fast-food-price-index

## Contact

Corrections and additional store requests are welcome — open an issue. Siddharth Lunawat, Orlando, Florida — [siddharthlunawat.com](https://siddharthlunawat.com) · [LinkedIn](https://www.linkedin.com/in/sidlunawat/) · [X](https://x.com/LunawatSid)
