#!/usr/bin/env python3
"""Merge one TikTok gift table into another.

    tools/merge_gifts.py data/tiktok_gifts.json data/tiktok_gifts_coinvertify.json
    tools/merge_gifts.py base.json incoming.json -o merged.json

Entries are matched on ``slug`` first and ``id`` second, because neither alone is reliable:
the same gift is reissued under new ids (see docs/CAVEATS.md), and a few scraped rows carry a
slug the webcast CDN does not use.

``names`` is merged key by key rather than replaced — that is the whole point of pulling in the
Coinvertify table, which carries ten locales where the webcast payload carries only ``en``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))

    # Both shapes are in the wild: a bare array, and {"gifts": [...]} from the Alberand gist.
    if isinstance(data, dict):
        data = data.get("gifts", [])

    if not isinstance(data, list):
        raise SystemExit(f"{path}: expected an array of gifts, or an object with a 'gifts' key")

    return data


def merge(base: list[dict], incoming: list[dict]) -> tuple[int, int]:
    by_slug = {g["slug"]: g for g in base if g.get("slug")}
    by_id = {g["id"]: g for g in base if g.get("id")}

    added = updated = 0

    for new in incoming:
        existing = by_slug.get(new.get("slug")) or by_id.get(new.get("id"))

        if existing is None:
            base.append(new)
            added += 1

            if new.get("slug"):
                by_slug[new["slug"]] = new
            if new.get("id"):
                by_id[new["id"]] = new

            continue

        updated += 1
        existing["names"] = {**existing.get("names", {}), **new.get("names", {})}

        # Only fill from the incoming row where it actually has something; a scrape with a missing
        # diamond count must not blank out a known one.
        for field in ("diamond_count", "image_url", "duration"):
            if new.get(field):
                existing[field] = new[field]

        for field in ("id", "slug"):
            if new.get(field) and not existing.get(field):
                existing[field] = new[field]

    return added, updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path, help="the table to merge into")
    parser.add_argument("incoming", type=Path, help="the table to merge from")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="where to write the result (default: overwrite BASE)",
    )
    args = parser.parse_args()

    base = load(args.base)
    incoming = load(args.incoming)
    added, updated = merge(base, incoming)

    # By id, the same order fetch_alberand.py writes, so the two tools do not fight over the file.
    base.sort(key=lambda g: (g.get("id") or 0, g.get("slug") or ""))

    output = args.output or args.base
    output.write_text(
        json.dumps(base, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"updated {updated}, added {added}, total {len(base)} -> {output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
