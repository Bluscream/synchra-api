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

    for page in range(1, args.pages + 1):
        print(f"scraping page {page}")

        for gift in scrape_page(page):
            slug = gift.get("slug")

            if not slug or slug in seen:
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
            "scraped 0 gifts — the site's markup or Nuxt payload format has changed; "
            "the existing table was left alone"
        )

    gifts.sort(key=lambda g: (g.get("id") or 0, g.get("slug") or ""))
    args.output.write_text(
        json.dumps(gifts, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"scraped {len(gifts)} gifts -> {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
