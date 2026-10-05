#!/usr/bin/env python3
"""Scrape coinvertify.com for the localised TikTok gift names.

    tools/scrape_coinvertify.py -o data/tiktok_gifts_coinvertify.json

This is the only source found that carries gift names in more than one language — ten locales,
against the single ``en`` that TikTok's own webcast payload and the Alberand gist provide. That is
what it is here for; for ids, diamond counts and durations prefer fetch_alberand.py.

The page is Nuxt 3, which serialises its payload with structural sharing: every value is an index
into one flat array, so the JSON has to be rehydrated before it means anything. That makes this the
most fragile tool in the repository — a Nuxt upgrade on their side breaks it silently, returning
zero gifts rather than an error. It checks for that and fails loudly instead.

Requires: requests, beautifulsoup4 (see tools/requirements.txt).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ModuleNotFoundError as missing:  # pragma: no cover - dependency guard
    raise SystemExit(
        f"missing dependency {missing.name}: pip install -r tools/requirements.txt"
    ) from missing

PAGE_URL = "https://coinvertify.com/tiktok-gifts?page={page}"


def rehydrate(flat: list, index: int = 1):
    """Resolve a Nuxt 3 de-duplicated payload back into ordinary JSON.

    Nuxt replaces every nested value with its position in one flat array, so `{"a": 4}` means
    "the value at index 4". Resolving is therefore a lookup per node, and a cycle would recurse
    forever — hence `seen`.
    """
    seen: set[int] = set()

    def resolve(node):
        if isinstance(node, int) and 0 <= node < len(flat):
            if node in seen:
                return None

            seen.add(node)
            resolved = resolve(flat[node])
            seen.discard(node)

            return resolved

        if isinstance(node, dict):
            return {key: resolve(value) for key, value in node.items()}

        if isinstance(node, list):
            return [resolve(value) for value in node]

        return node

    return resolve(index)


def scrape_page(page: int) -> list[dict]:
    url = PAGE_URL.format(page=page)
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    script = BeautifulSoup(response.text, "html.parser").find("script", id="__NUXT_DATA__")

    if script is None:
        print(f"  page {page}: no __NUXT_DATA__ — the page layout changed", file=sys.stderr)

        return []

    resolved = rehydrate(json.loads(script.string))
    found: list[dict] = []

    # The gift list is under an opaque, generated key, so look for the shape rather than the name.
    for value in (resolved or {}).get("data", {}).values():
        if isinstance(value, list) and value and isinstance(value[0], dict) and "slug" in value[0]:
            found.extend(value)

    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", type=Path, required=True, help="where to write the table")
    parser.add_argument("--pages", type=int, default=15, help="how many pages to walk (default 15)")
    args = parser.parse_args()

    gifts: list[dict] = []
    seen: set[str] = set()
    skipped: list[str] = []

    for page in range(1, args.pages + 1):
        print(f"scraping page {page}")

        for gift in scrape_page(page):
            slug = gift.get("slug")

            if not slug or slug in seen:
                continue

            # The site disambiguates a reissued gift by appending the price to the slug —
            # `gift-box-1999` beside `gift-box` — and those extra rows carry neither translations nor
            # a diamond count. They are the same gift under an id the webcast payload already has, so
            # they would add nothing and fail the table's own validation. Skipped, and counted, rather
            # than dropped silently: if the real rows ever start arriving empty, the count says so.
            if not gift.get("translations") and not gift.get("diamond_count"):
                skipped.append(slug)

                continue

            seen.add(slug)
            gifts.append(
                {
                    "id": gift.get("id"),
                    "slug": slug,
                    "diamond_count": gift.get("diamond_count"),
                    "image_url": gift.get("gift_image"),
                    "names": gift.get("translations", {}),
                }
            )

    if not gifts:
        raise SystemExit(
            f"scraped 0 usable gifts of {len(skipped)} rows seen — the site's payload no longer "
            "carries what this reads. The existing table was left alone; see docs/CAVEATS.md §7."
        )

    # The localised names are the only reason this tool exists, so a scrape that returns gifts
    # without them is a failure even though it returned gifts. Observed 2026-10-05: the page stopped
    # carrying `translations` in its server-rendered payload partway through a session, and a run
    # without this check would have replaced ten locales with none and called it success.
    localised = sum(1 for gift in gifts if len(gift.get("names") or {}) > 1)

    if localised < len(gifts) // 2:
        raise SystemExit(
            f"only {localised} of {len(gifts)} scraped gifts carry more than one locale. The page's "
            "payload has probably stopped including translations — writing this would discard the "
            "names the existing table already has. Left alone; see docs/CAVEATS.md §7."
        )

    if skipped:
        print(f"skipped {len(skipped)} price-disambiguated stub rows: {', '.join(sorted(skipped))}")

    gifts.sort(key=lambda g: (g.get("id") or 0, g.get("slug") or ""))
    args.output.write_text(
        json.dumps(gifts, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"scraped {len(gifts)} gifts -> {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
