#!/usr/bin/env python3
"""Merge the Alberand gist's gift list into a gift table.

    tools/fetch_alberand.py data/tiktok_gifts.json

The gist is a dump of TikTok's own webcast gift payload, so it is the most authoritative source
for ``id``, ``diamond_count`` and ``duration`` — but it carries only an English ``name`` and uses
TikTok's own shape (``image.url_list[]``), which this maps onto the table's shape.

An existing row is never overwritten from here, only filled where it is missing. The gist is a
point-in-time dump by a third party; the live webcast payload wins where the two disagree.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

GIST_URL = (
    "https://gist.githubusercontent.com/alberand/ce890338db1a97af07802d5d59c72309"
    "/raw/9909d89eb2b5e00c8c9bb2c4d1793afbbf8e4d50/tiktok-gifts-list.json"
)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def first_url(item: dict) -> str | None:
    for key in ("image", "icon"):
        urls = item.get(key, {}).get("url_list") or []

        if urls:
            return urls[0]

    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("table", type=Path, help="the gift table to merge into")
    parser.add_argument("--url", default=GIST_URL, help="raw gist url (default: the pinned revision)")
    args = parser.parse_args()

    print(f"fetching {args.url}")

    if not args.url.startswith("https://"):
        raise SystemExit("--url must be https")

    with urllib.request.urlopen(args.url, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    incoming = payload.get("gifts", payload) if isinstance(payload, dict) else payload
    table = json.loads(args.table.read_text(encoding="utf-8"))

    by_id = {g["id"]: g for g in table if g.get("id")}
    by_slug = {g["slug"]: g for g in table if g.get("slug")}

    added = updated = 0

    for item in incoming:
        gift_id = item.get("id")
        name = (item.get("name") or "").strip()

        if not gift_id or not name:
            continue

        slug = slugify(name)
        mapped = {
            "id": gift_id,
            "names": {"en": name},
            "diamond_count": item.get("diamond_count", 0),
            "image_url": first_url(item),
            "slug": slug,
            "duration": item.get("duration", 0),
        }

        existing = by_id.get(gift_id) or by_slug.get(slug)

        if existing is None:
            table.append(mapped)
            by_id[gift_id] = mapped
            by_slug[slug] = mapped
            added += 1

            continue

        updated += 1
        existing.setdefault("names", {}).setdefault("en", name)

        for field in ("diamond_count", "image_url", "duration", "slug", "id"):
            if not existing.get(field) and mapped.get(field):
                existing[field] = mapped[field]

    table.sort(key=lambda g: (g.get("id") or 0, g.get("slug") or ""))
    args.table.write_text(
        json.dumps(table, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"updated {updated}, added {added}, total {len(table)} -> {args.table}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
