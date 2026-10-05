# synchra-api

Machine-readable descriptions of the [Synchra](https://synchra.net) API, the reference data a client
needs alongside them, and the tools that keep both current.

Synchra publishes its API description from the running service and nowhere else — no versioned
download, no release feed, no changelog. This repository is the missing part: a snapshot you can
diff, plus the findings that the description itself does not carry.

| | |
| :--- | :--- |
| `spec/openapi.json` | OpenAPI 3.1.0 — **172 paths, 465 schemas**, API version 2.0, as published |
| **`spec/openapi.annotated.json`** | **the same document with what it leaves unsaid written into it** |
| `spec/websocket.md` | the WebSocket reference, from `/api/2/ws-docs` |
| `overlay/annotations.json` | the notes, and the only copy of them |
| `data/tiktok_gifts.json` | 289 TikTok gifts: id, slug, price in diamonds, image, names in up to 10 locales |
| `data/tiktok_gifts_coinvertify.json` | the localised-names source, kept separate so a re-scrape is reviewable |
| [`docs/ANNOTATIONS.md`](docs/ANNOTATIONS.md) | the notes, rendered (generated — do not edit) |
| [`docs/CAVEATS.md`](docs/CAVEATS.md) | what has no endpoint to hang on: how the document is published, how it drifts, and [where it is incomplete](docs/CAVEATS.md#3-it-is-current-and-it-is-not-complete) |

## Why an annotated spec

The published description has a `description` on **1 of its 240 operations**, and all 240 `summary`
fields are generated from function names — `"Get Activities"`. So there is nowhere in it for the
things that actually cost you an afternoon:

- a **403** on `/activities` usually means the token is not granted on *that channel*, not that a
  scope is missing;
- a **notice** — a gift, a sub, a raid — leaves `message_parts` **empty** and puts its content in
  `notice_message_parts`, so a reader that knows only the first field renders every gift as a blank
  row;
- `POST /api/2/auth/token` **does not exist**, so the OAuth2 refresh flow the empty
  `securitySchemes.flows` implies cannot be built.

Keeping those in prose next to the spec means nobody reads them at the moment they matter. So they
are written *into* the document instead:

```bash
tools/annotate-spec.py --docs docs/ANNOTATIONS.md    # overlay -> spec/openapi.annotated.json
tools/annotate-spec.py --check                       # is the committed annotated file current?
tools/annotate-spec.py --targets-only                # do all the notes still point at something?
```

Generate your client from `spec/openapi.annotated.json` and the notes land in its docblocks, where
they are read at the call site rather than after the bug. `synchra-php` does this — its
`tools/fetch-spec.sh` pulls `overlay/annotations.json` from here and applies it with
`tools/annotate.jq` while fetching.

Two properties worth knowing:

- **A stale note is a hard error.** Every target is resolved before anything is written, so when
  Synchra renames or removes something a note depends on, the run fails and names it. That makes the
  overlay a drift detector as well as documentation — it caught a wrong target on its first run.
- **Key order is never changed**, by either tool. A generator takes class names and constructor
  parameter order from it; see [caveat 1](docs/CAVEATS.md#1-the-description-is-published-only-by-the-running-service).

## Clients

| | |
| :--- | :--- |
| [synchra-php](https://github.com/Bluscream/synchra-php) | PHP, generated from this spec |
| [synchra.py](https://github.com/Bluscream/synchra.py) | Python, async (`aiohttp` + `pydantic` v2) |
| [synchra.cli](https://github.com/Bluscream/synchra.cli) | terminal client, on top of synchra.py |

## Using the spec

**Fetch it live and cache.** The service is the source of truth, so a client that wants to be
current should read from the API and keep a local copy for when it cannot:

```bash
curl --fail --silent https://api.synchra.net/openapi.json | jq --sort-keys . > openapi.json
```

`jq --sort-keys` matters. The API does not guarantee a stable key order, so without normalising,
two fetches of an *unchanged* document produce a diff thousands of lines long and a real change
hides in it.

The snapshot in `spec/` is the cache-of-last-resort and the thing to diff against:

```bash
tools/fetch-spec.sh                     # refresh spec/ from the live API
tools/diff-spec.sh old-openapi.json     # what moved; non-zero exit if anything was REMOVED
```

A removal is the case to watch for — a generated client keeps compiling against a route that now
404s. Between April and October 2026, 102 paths appeared and **31 disappeared**. See
[caveat 2](docs/CAVEATS.md#2-routes-get-removed-not-just-added).

`SYNCHRA_API_HOST` points either tool at a different instance.

## Using the gift tables

A gift arrives in chat as a *notice*, and the API gives you an id, not a price or a localised name —
hence these tables. They are plain JSON arrays:

```json
{
  "id": 5487,
  "slug": "finger-heart",
  "diamond_count": 5,
  "image_url": "https://p16-webcast.tiktokcdn.com/img/maliva/webcast-va/a4c4…webp",
  "names": { "en": "Finger Heart", "de": "Fingerherz", "ru": "Сердечко", "…": "…" }
}
```

Key them by **`id`**. The same gift is reissued under new ids — sometimes at a different price — so
neither the name nor the slug is unique ([caveat 6](docs/CAVEATS.md#6-the-same-gift-exists-under-several-ids)).

```bash
pip install -r tools/requirements.txt

tools/check_gifts.py data/tiktok_gifts.json              # duplicates, missing fields, bad urls
tools/fetch_alberand.py data/tiktok_gifts.json           # ids, prices, durations from TikTok's own payload
tools/scrape_coinvertify.py -o data/tiktok_gifts_coinvertify.json   # localised names
tools/merge_gifts.py data/tiktok_gifts.json data/tiktok_gifts_coinvertify.json
```

Merge in that order: the webcast payload is authoritative for numbers, the scrape for names, and
`merge_gifts.py` unions the `names` map key by key rather than replacing it. Both merge tools sort
by id, so the committed file stays diffable.

`check_gifts.py` exits non-zero on a real problem and merely reports the legitimate duplicates, so
it works as a CI or pre-commit gate.

## Contributing

A refresh is a pull request with the regenerated file and the `diff-spec.sh` output in the
description — that way the change to the API is reviewable even though the API has no changelog. If
a refresh teaches you something the description does not say: if it belongs to an endpoint or a
field, add it to `overlay/annotations.json` and regenerate; if it is about the document or the
tooling, it goes in `docs/CAVEATS.md`.

## Provenance and licensing

The MIT licence here covers **this repository's own tooling and documentation** only.

`spec/` is Synchra's own published API description, reproduced for interoperability; it belongs to
Synchra and is not the authors' to license. The gift tables are compiled from TikTok's public
webcast payload (via [this gist](https://gist.github.com/alberand/ce890338db1a97af07802d5d59c72309))
and from [coinvertify.com](https://coinvertify.com/tiktok-gifts); gift names and artwork are
TikTok's.

No credentials are in this repository and none belong here. HAR captures of the dashboard — the
original source of several caveats — carry live bearer tokens and are deliberately **not** included;
`.gitignore` excludes `*.har` so one cannot be added by accident.
