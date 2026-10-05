# Caveats

Things the API description does not tell you, found by building a client against the live service.
Each one cost somebody an afternoon; they are written down so it is only the one afternoon.

> **Most of what belongs to a specific endpoint is not here — it is in the spec.**
> The description has a `description` on exactly **1 of its 240 operations**, and all 240 `summary`
> fields are generated from function names, so there was nowhere for any of this to live. It is
> therefore written *into* the document: [`overlay/annotations.json`](../overlay/annotations.json)
> holds the notes, `tools/annotate-spec.py` applies them to `spec/openapi.annotated.json`, and a
> generated client carries them in its docblocks — where somebody reads them at the call site rather
> than after the bug.
>
> What stays in this file is what has no operation or schema to hang on: how the document is
> published, how it drifts, and how the gift tables behave. If a caveat below could be attached to a
> route or a field, it belongs in the overlay instead.

The provenance is [`synchra-php`](https://github.com/Bluscream/synchra-php) unless noted — a
generated PHP client, which is why so much of this is about where the description and the service
disagree.

---

## 1. The description is published only by the running service

There is no versioned download, no release feed and no changelog. `GET /openapi.json` and
`GET /api/2/ws-docs` return whatever is deployed right now. If the service is down, or a route
changes shape, there is nothing to compare against.

That is the reason this repository exists. `tools/fetch-spec.sh` writes the document with
`jq --sort-keys`, because the API does **not** guarantee a stable key order — without normalising,
every refresh produces a diff of thousands of lines in which the real change is invisible.

### …and do not sort the copy your generator reads

Sorting is right for *this* repository, where the document is the artifact. It is wrong for a client
that generates code from it, because key order leaks into the generated API: a generator naturally
names an inline enum after the first property that references it, and emits constructor parameters in
the order the properties appear.

Measured on `synchra-php`: sorting the keys renamed two enums, dropped a union, and reordered the
constructors of **290** models — a breaking change for any caller constructing a model positionally.

The unsorted order is the server's own declaration order, which is at least meaningful. But it is not
*promised*, so an upstream reorder can do all of that on its own, silently, on an ordinary refresh.
If you generate code, pin the ordering in your **generator** (sort properties yourself, required
first) rather than relying on the document's.

[`synchra-ts`](https://github.com/Bluscream/synchra-ts) does exactly that and is therefore free to
sort: an inline enum becomes an inline literal union with no name, every method takes one options
object rather than positional arguments, and the emitters sort what they write. Its
`test/generator.test.ts` generates the whole tree from a key-sorted and a key-reversed copy of this
document and asserts the output is byte-identical — which is the only way to know the property holds
rather than assuming it. Use `tools/diff-spec.sh` to see what changed; it
compares sets, so it is key-order independent either way.

A smaller trap in the same area: `60.0` and `100` both appear as bounds, and a decode/encode
round-trip in a language that has one numeric type — PHP, for instance — rewrites `60.0` as `60`.
Harmless for a JSON Schema number, but it means that pipeline cannot reproduce its own committed
file, and the resulting few hundred lines of diff noise hide real changes. `jq` preserves the
literal.

## 2. Routes get removed, not just added

Between a snapshot taken 2026-04-02 and one taken 2026-10-05:

```
paths   101 -> 172  (+102 / -31)
schemas 179 -> 465  (+318 / -32)
```

Removals are the dangerous direction: a generated client keeps compiling against a method whose
route now 404s, and a hand-written one keeps a dead code path nobody notices. Run
`tools/diff-spec.sh OLD` after a refresh; it reports removals first and exits non-zero when there
are any, so it works as a CI gate.

Among the 31 that disappeared, two are worth knowing about specifically:

- **All six `emulate` endpoints.** `…/chat-messages/emulate`, `…/chat-events/emulate/progress` and
  the five `twitch/eventsub/emulate-*` routes existed in April and are gone. There is no longer a
  supported way to make the API generate a synthetic gift, cheer, sub or raid, so **testing a chat
  renderer against realistic events means capturing real ones** (or injecting them client-side,
  below).
- **`register-provider/{tiktok,streamelements}`** and the Kick `connect-url` family. Provider
  linking moved into the dashboard's own flow.

## 3. It is current, and it is not complete

The copy in `spec/` is byte-identical to what the service serves — that part is easy to keep true,
and `tools/fetch-spec.sh` plus a `git diff` is the whole mechanism. "Complete" is a different claim,
and it is false in specific, checkable ways.

> Everything in this section is **repaired in `spec/openapi.annotated.json`**: the missing routes and
> schemas are added, the error responses are supplied by rule, the security schemes are filled in and
> the public operations are marked `security: []`. The list below is what the *published* document
> omits — read it to know what you are relying on the overlay for, and what a client built straight
> from `openapi.json` will not know.

**No errors are described.** Across all 240 operations the documented responses are only successes
plus `422` — one operation also documents `413`, and that is the lot:

```
200: 165    201: 16    202: 1    204: 58    413: 1    422: 240
```

There is **no `401`, `403`, `404`, `409`, `429` or `5xx` anywhere in the document**, and every one of
those happens: an anonymous call to a private endpoint answers 401, `/activities` answers 403, the
service rate-limits with 429 and `Retry-After`. A client generated faithfully from this description
has no error model at all, which is why `synchra-php` hand-writes its exception mapping instead of
generating it. Do not read "not documented" as "does not occur".

**Live routes are missing from it.** `GET /health` answers 200 and is not in the document — it *was*
in the April snapshot, so it was removed from the description and not from the service. `GET
/api/2/ws` is absent too, though that one is deliberate: the socket is specified in
`spec/websocket.md` instead.

**Four gateway payloads have no schema.** `KvEventData`, `ChannelGiveawaysEventData`, `QueueEvent`
and `ActivityAlertWidgetTest` appear only in the WebSocket reference — see §5.

**Authentication is not described.** `securitySchemes` is `{"OAuth2": {"flows": {}}}`, and the two
other credential types the API accepts — channel ingest API keys and the widget `x-kv-token` header
— appear in no scheme at all.

**Almost nothing is explained.** One operation of 240 carries a `description`, and that one is the
entire 61 KB WebSocket reference repeated inside it. Every `summary` is generated from a function
name. That is what [`overlay/annotations.json`](../overlay/annotations.json) exists to patch.

### How thoroughly this was checked

Honestly: partially. The REST surface was compared against the paths the real dashboard calls, taken
from two HAR captures, and **every REST path in them is in the document** — so there is no evidence
of a hidden route behind the dashboard. But those captures cover the chat, activity and channel
views only, not settings, giveaways, commands or the admin pages. A route used only by a page nobody
captured would not show up. The absence of evidence here is thin evidence of absence.

## 4. Unknown enum values happen

The description models some fields as a union of several platforms' enums; the service will send a
value that is not in the union. Decide up front whether an unknown value throws or passes through —
`synchra-php` throws, naming the field, on the grounds that silently handing back a value outside
the declared type is worse. Either way, do not assume the enum is closed.

Relatedly: a handful of fields (`KvEntry.value`, `DashboardProfileData.layout`) are genuinely "any
JSON value" in the description. They cannot be modelled; document them in prose.

## 5. Four gateway payloads are documented nowhere but the WS reference

`KvEventData`, `ChannelGiveawaysEventData` and `QueueEvent` appear in `spec/websocket.md` and never
in `openapi.json`, so a generator driven only by the OpenAPI document will not produce them.
`ActivityAlertWidgetTest` exists only as a JSON example, with no schema at all.

Also in the WebSocket protocol: the socket accepts the bare text `ping` as well as
`{"command":"ping"}`, and replies with bare text `pong` — not JSON. A client that pipes everything
through a JSON parser will throw on its own keepalive.

# TikTok gift tables

`data/tiktok_gifts.json` and `data/tiktok_gifts_coinvertify.json` are **not** from the Synchra API.
They were collected on the assumption that rendering a gift notice means turning an id into a name, a
price and an image. **That assumption was wrong**, and it is worth saying so here rather than leaving
the tables looking load-bearing.

Synchra resolves a gift server-side. A notice's `gift` part arrives with `name`, `image_url`, `count`
and `count_display_name` already filled, so a renderer needs no table at all — see
[`GiftPart`](ANNOTATIONS.md#giftpart), which was written from live data.

Worse for the tables: **the ids do not reliably join.** Synchra's `gift.id` is its own
cross-platform identifier — non-TikTok gifts use string ids like `rose`, `super_chat` and
`cheer-1000` — and of five TikTok gifts sampled from live chat, exactly one had an id present in
`data/tiktok_gifts.json`. Two of them (`Popular Vote`, id `13651`; `Imperator Herz`, id `1157212`)
appear in the table under no id and no name, in any locale.

What the tables are still good for:

- **Consistent language.** Synchra passes through whatever locale the platform sent, and it varies
  within one channel: `Imperator Herz` arrived alongside `Popular Vote`, `Heart Me` and `Rose`. There
  is no parameter to ask for a language, so a UI that wants one has to translate the name itself.
- **A direct TikTok integration** that reads the webcast stream without Synchra, which gets ids and
  no names.

TikTok's own `webcast/gift/list` endpoint would be the authoritative source for both, but it needs a
room id and a signed session — unauthenticated it answers `200` with an empty body — so it is not a
drop-in replacement for the scrape.

A sample of five gifts is thin evidence, and the join rate above should be read as "do not assume
this works" rather than as a measurement.

## 6. The same gift exists under several ids

TikTok reissues gifts: same name, same artwork, a new id — and sometimes a different price.

```
Gift Box:         6834=1999◆, 6835=3999◆
Tennis:           9818=1◆,    9834=10◆
Ellie the Elephant: 6845=5000◆, 6922=5000◆
```

So **a name is not a key, and neither is a slug** (the slug is derived from the name). Only `id` is.
`tools/check_gifts.py` reports these for information rather than as errors.

This has a direct consequence for merging: `tools/merge_gifts.py` matches on slug first and id
second, so where two rows share a slug it can only ever update the later of them. Matching on id
alone would be wrong too — the scraped sources sometimes carry a slug and no usable id. If you need
one canonical row per gift, pick by id and accept the duplicates.

## 7. Each source is authoritative for different fields

| Source | Good for | Weak on |
| :--- | :--- | :--- |
| TikTok webcast payload (via the Alberand gist) | `id`, `diamond_count`, `duration` | names — `en` only |
| coinvertify.com (scraped) | `names` in 10 locales (`ar ba de en es fr id pt ru tr`) | a point-in-time scrape; ids drift |

Merge in that order and let the gist win on numbers, the scrape win on names. `merge_gifts.py`
unions the `names` map key by key rather than replacing it, which is the only reason the combined
table has 236 of 289 gifts localised.

## 8. The scraper is the most fragile thing here

coinvertify.com is a Nuxt 3 app, and Nuxt serialises its payload with structural sharing: every
nested value is replaced by an **index into one flat array**. The JSON has to be rehydrated before
it means anything, and the gift list sits under a generated, opaque key — so the scraper looks for
the *shape* of the data rather than its name.

**It already broke once, mid-session, on 2026-10-05.** A scrape at one point returned 235 gifts with
ten locales each; twenty minutes later the same code against the same URLs returned 247 rows whose
`translations` and `diamond_count` were *all* null, and the page's server-rendered payload no longer
contained the word `translations` at all. Whether that is a deploy, an A/B bucket or anti-scraping
behaviour is unknown.

That is the argument for vendoring the table rather than fetching it: `data/tiktok_gifts.json` may
now be the only copy of those names outside TikTok. The tool refuses to write a table where fewer
than half the rows carry more than one locale, so the run above failed loudly and changed nothing
instead of replacing ten locales with none and reporting success.

It also skips the stub rows the site uses to disambiguate a reissued gift — `gift-box-1999` beside
`gift-box` — which carry neither a name nor a price, and are the same gift under an id the webcast
payload already has.

A Nuxt upgrade on their side breaks this silently, yielding zero gifts rather than an error. The
tool now fails loudly and leaves the existing table alone instead of writing an empty one.

## 9. The old gift tooling never worked

`check_dups.py` in the original Python tree could not report anything: it read
`data.get("gifts", [])` from a file that is a bare JSON array, so it always saw zero gifts, and it
grouped on `g["name"]` where the field is a `names` map. Both failures were silent — it printed
"No redundant entries found" on every run. Its replacement is `tools/check_gifts.py`.

All four original scripts also had absolute Windows paths (`p:/Python/synchra/…`) hardcoded in
`__main__` and took no arguments.
