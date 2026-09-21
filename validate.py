#!/usr/bin/env python3
"""Validate a weekly Orlando Fast Food Price Index file against the schema.

Usage:
    python3 validate.py data/weekly/2026-09-17.csv
    python3 validate.py            # validates every file in data/weekly/

Exits non-zero if any file fails. No third-party dependencies.
"""

import csv
import glob
import os
import re
import sys
from datetime import datetime

COLUMNS = [
    "observed_date", "observed_time_local", "chain", "store_id", "store_address",
    "area", "store_format", "item", "price_usd", "confidence", "notes",
]
CONFIDENCE = {"firsthand", "external", "not_recorded"}
FORMATS = {"standard", "cantina"}
HERE = os.path.dirname(os.path.abspath(__file__))


def load_reference():
    def rows(name):
        path = os.path.join(HERE, "reference", name)
        with open(path, newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))

    stores = rows("stores.csv")
    items = rows("items.csv")
    return (
        {(r["chain"], r["store_address"]) for r in stores},
        {(r["chain"], r["item"]) for r in items},
        {r["chain"] for r in stores},
    )


def validate(path, known_stores, known_items, chains):
    errors = []

    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != COLUMNS:
            errors.append(f"header mismatch\n  expected: {COLUMNS}\n  found:    {reader.fieldnames}")
            return errors

        seen = set()
        for n, row in enumerate(reader, start=2):
            def bad(msg):
                errors.append(f"line {n}: {msg}")

            try:
                datetime.strptime(row["observed_date"], "%Y-%m-%d")
            except ValueError:
                bad(f"observed_date {row['observed_date']!r} is not YYYY-MM-DD")

            if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", row["observed_time_local"] or ""):
                bad(f"observed_time_local {row['observed_time_local']!r} is not HH:MM")

            if row["chain"] not in chains:
                bad(f"unknown chain {row['chain']!r}")
            elif (row["chain"], row["store_address"]) not in known_stores:
                bad(f"store not in reference/stores.csv: {row['chain']} / {row['store_address']!r}")

            if row["chain"] in chains and (row["chain"], row["item"]) not in known_items:
                bad(f"item not in reference/items.csv: {row['chain']} / {row['item']!r}")

            if row["store_format"] not in FORMATS:
                bad(f"store_format {row['store_format']!r} not in {sorted(FORMATS)}")

            conf = row["confidence"]
            if conf not in CONFIDENCE:
                bad(f"confidence {conf!r} not in {sorted(CONFIDENCE)}")

            price = (row["price_usd"] or "").strip()
            if conf == "not_recorded":
                if price:
                    bad("confidence is not_recorded but price_usd is populated")
                if not (row["notes"] or "").strip():
                    bad("confidence is not_recorded but notes is empty — the reason is required")
            else:
                if not price:
                    bad(f"price_usd is empty but confidence is {conf!r}")
                else:
                    try:
                        value = float(price)
                    except ValueError:
                        bad(f"price_usd {price!r} is not a number")
                    else:
                        if value <= 0:
                            bad(f"price_usd {value} is not positive")
                        elif value > 50:
                            bad(f"price_usd {value} is implausibly high — check the pull")
                if conf == "external" and not (row["notes"] or "").strip():
                    bad("confidence is external but notes does not name the source")

            key = (row["chain"], row["store_address"], row["item"])
            if key in seen:
                bad(f"duplicate row for {key}")
            seen.add(key)

    return errors


def main():
    known_stores, known_items, chains = load_reference()
    targets = sys.argv[1:] or sorted(
        f for f in glob.glob(os.path.join(HERE, "data", "weekly", "*.csv"))
        if not f.endswith("TEMPLATE.csv")
    )

    if not targets:
        print("no files to validate")
        return 0

    failed = 0
    for path in targets:
        errors = validate(path, known_stores, known_items, chains)
        name = os.path.relpath(path, HERE)
        if errors:
            failed += 1
            print(f"FAIL  {name}")
            for e in errors:
                print(f"      {e}")
        else:
            print(f"ok    {name}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
