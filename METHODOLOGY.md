# Methodology

How the Orlando Fast Food Price Index is collected, and the specific ways a per-store price pull goes wrong without looking wrong.

## Principles

1. **Pickup prices only.** Delivery marketplace prices carry a platform markup that varies by platform and by store, which would swamp the geographic signal this dataset exists to measure.
2. **Pinned stores.** The same store list every week. A changing store list makes week-over-week movement meaningless.
3. **Fixed daypart.** All stores in a given week are collected inside the same time window, because breakfast and lunch menus are different menus.
4. **Unreadable is published, not dropped.** A price that could not be obtained becomes a row with an empty `price_usd` and `confidence = not_recorded`, with the reason. Dropping it silently biases the series toward whatever was easy to collect.
5. **No estimates.** If a number was not read from the chain's own ordering site for that store, it is not `firsthand`. Prices taken from any other source are marked `external` and the source named in `notes`.

## Collection window

Collect all stores within a single 2-hour window, between **11:00 and 14:00 America/New_York**, on the same weekday each week. Record the actual time per row in `observed_time_local`.

## Per-chain procedure

### Taco Bell

The only chain of the three that pins the store in the URL:

```
https://www.tacobell.com/food/burritos?store={store_id}
```

Store IDs come from `locations.tacobell.com`, which is static and safe to fetch server-side.

### Wendy's

Store lives in session state, so the store picker has to be clicked through each run at `order.wendys.com`. The search field clears if you type before the page hydrates — wait about two seconds after load before typing.

### Burger King

The `bk.com` picker is a bottom sheet, and it has a specific sequence that works:

1. Click the chevron at the right end of the Pickup bar to open the sheet.
2. Click the address field a **second** time once the sheet has expanded to full height. Typing into the collapsed sheet is silently discarded.
3. Type the address, click the autocomplete row, then "Order Here".
4. Deep-link to the section URL, e.g. `/menu/section/section_5596` (Flame Grilled Burgers), with the store held in session.

Note that Burger King runs **two price books** across Orlando — west/central and east — rather than genuinely per-store pricing. Record per store anyway; the grouping is a finding, not an assumption.

### McDonald's — excluded

The McDonald's US web menu shows items and calories but no prices. It is not collectable this way without the app, so it is out of scope rather than half-included.

## Traps

These are the failure modes that produce plausible, wrong data. Each one has actually occurred.

**The header is not proof.** Loading a menu without the store parameter renders default national pricing *while the page header displays the selected store*. Deep-linking straight to a category URL can drop store context the same way. Always click through from the store picker, then confirm both the store address in the header **and** that prices are present before reading anything.

**Server-side fetching does not work.** `curl` and server-side fetchers hold one sticky session, so every store ID — and even a no-store control — returns the same page with identical prices. It looks like a successful pull of many stores. Per-store collection must run in a real browser. The exception is `locations.tacobell.com`, which is static.

**The cross-metro control.** Before trusting a run, request a store in a completely different metro and confirm the prices actually change. If they don't, the session is serving a default price book and the whole run is void.

**Ghost stores.** A store priced far below its neighbors is usually a closed location whose price book stopped updating, not a bargain. Verify the store still appears in the chain's own location directory before publishing anything about it.

**Daypart contamination.** Wendy's and Burger King serve breakfast menus early enough to catch a careless run. Fixing the collection window is what prevents this.

**Format confusion.** Two of the five Taco Bell stores (downtown, UCF) are Taco Bell **Cantina** format, a different concept from a standard Taco Bell. This is recorded in `store_format` and should be flagged in any published comparison.

## Recording

Record the actual figures at the time of the pull, not just the store list and method. A previous collection captured stores and items but no prices, and the numbers had to be collected again from scratch.

## Example row

Illustrative only — not real data. The 0.00 is a placeholder; a real file needs a positive price, and `validate.py` will reject 0.00:

```csv
observed_date,observed_time_local,chain,store_id,store_address,area,store_format,item,price_usd,confidence,notes
2026-01-01,12:15,Taco Bell,039602,7623 International Dr,I-Drive,standard,Bean Burrito,0.00,firsthand,
2026-01-01,12:40,Wendy's,NA,7749 Turkey Lake Rd,I-Drive,standard,Baconator,,not_recorded,store picker would not hold session
```
