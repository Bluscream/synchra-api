#!/usr/bin/env python3
"""Validate a gift table: duplicates, missing fields, suspicious values.

    tools/check_gifts.py data/tiktok_gifts.json

Exits non-zero when something is wrong, so it works as a pre-commit or CI gate.

Replaces the earlier check_dups.py, which could never report anything: it read
``data.get("gifts", [])`` from a file that is a bare array (so it always saw zero gifts), and
grouped on ``g["name"]`` where the field is a ``names`` map. Both failures were silent.

Duplicate ids are an error. Duplicate *names* are not: TikTok genuinely reissues a gift under a new
id — same artwork, same name, sometimes a different diamond count — so the same name legitimately
appears several times. Those are reported for information.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

REQUIRED = ("id", "slug", "diamond_count", "image_url", "names")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("table", type=Path, help="the gift table to check")
    args = parser.parse_args()

    data = json.loads(args.table.read_text(encoding="utf-8"))

    if isinstance(data, dict):
        data = data.get("gifts", [])

    errors: list[str] = []
    by_id: dict[int, list[dict]] = defaultdict(list)
    by_slug: dict[str, list[dict]] = defaultdict(list)
    by_name: dict[str, list[dict]] = defaultdict(list)
    locales: set[str] = set()

    for position, gift in enumerate(data):
        where = f"[{position}] {gift.get('slug') or gift.get('id') or '?'}"

        for field in REQUIRED:
            if not gift.get(field):
                errors.append(f"{where}: missing {field}")

        if gift.get("id"):
            by_id[gift["id"]].append(gift)
        if gift.get("slug"):
            by_slug[gift["slug"]].append(gift)

        names = gift.get("names") or {}

        if not isinstance(names, dict):
            errors.append(f"{where}: names is {type(names).__name__}, expected an object")
        else:
            locales.update(names)

            if "en" in names:
                by_name[names["en"].casefold()].append(gift)

        if not str(gift.get("image_url", "")).startswith("https://"):
            errors.append(f"{where}: image_url is not https")

    for gift_id, entries in sorted(by_id.items()):
        if len(entries) > 1:
            errors.append(f"id {gift_id} used by {len(entries)} entries")

    # Both merge tools write the table sorted by id. Checking it here keeps a hand-edit from
    # turning the next merge into a diff of the whole file.
    ids = [g["id"] for g in data if g.get("id")]

    if ids != sorted(ids):
        errors.append("not sorted by id — run tools/merge_gifts.py, or sort with jq 'sort_by(.id)'")

    # A repeated slug is NOT an error, for the same reason a repeated name is not: a reissued gift
    # keeps its name, so slugify() gives it the same slug under a new id. It does matter though —
    # merge_gifts.py matches on slug first, and where two rows share one it can only ever update
    # the later of them. See docs/CAVEATS.md.
    reissued = {slug: entries for slug, entries in by_slug.items() if len(entries) > 1}

    # Caught only when a row has no slug to group by, so it is not already in `reissued`.
    for name, entries in sorted(by_name.items()):
        if len(entries) > 1 and not all(g.get("slug") for g in entries):
            reissued.setdefault(name, entries)

    print(f"{len(data)} gifts, {len(locales)} locales: {' '.join(sorted(locales))}")
    print(f"{sum(1 for g in data if len(g.get('names') or {}) > 1)} with more than one locale")

    if reissued:
        print(f"\n{len(reissued)} gifts exist under several ids (expected — TikTok reissues them):")

        for key, entries in sorted(reissued.items()):
            shown = ", ".join(f"{g.get('id')}={g.get('diamond_count')}◆" for g in entries)
            label = (entries[0].get("names") or {}).get("en") or key
            flag = "" if len({g.get("diamond_count") for g in entries}) == 1 else "  <- differing price"
            print(f"  {label}: {shown}{flag}")

    if errors:
        print(f"\n{len(errors)} problems:", file=sys.stderr)

        for error in errors:
            print(f"  {error}", file=sys.stderr)

        return 1

    print("\nno problems")

    return 0


if __name__ == "__main__":
    sys.exit(main())
