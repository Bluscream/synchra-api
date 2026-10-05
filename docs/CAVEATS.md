# Caveats

Things the API description does not tell you, found by building a client against the live service.
Each one cost somebody an afternoon; they are written down so it is only the one afternoon.

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
first) rather than relying on the document's. Use `tools/diff-spec.sh` to see what changed; it
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

## 3. Scopes are not the same thing as access

A token can hold `channel_activity:read` and still get **403** on
`GET /api/2/channels/{id}/activities`. The scope set says what *kind* of call the token may make;
whether it may make it *against that channel* is separate, and granted per channel in the
dashboard. A token minted by one account for another account's channel reads chat happily and
refuses activities.

So `403` here means "not granted on this channel", not "scope missing" — and the fix is in the
dashboard, not in the token. Nothing in the description expresses this.

## 4. A large part of the API is public

No token at all is needed for a channel's `providers`, `provider-streams` (status, title,
`viewer_count`, `peak_viewer_count`, `started_at`), `chat-messages`, `chat-events`,
`random-chat-messages`, and the global reference lists (`currencies.json`, `activity-types`,
`stream-categories`, `subscription/plans`, `link-tracking/config`).

The channel record itself, `streams`, `activities`, `links`, `widgets` and everything that writes
need one; an anonymous call answers 401.

Widget endpoints are public but keyed by `widget_id`, which **is** the capability — treat a widget
id like a secret, because anyone holding one can read that widget.

`components.securitySchemes` is only `{"OAuth2": {"type": "oauth2", "flows": {}}}` — the flows are
empty, so the description states *that* it is OAuth2 without documenting an authorize or token URL.
There is no token endpoint; tokens come from the dashboard by hand. A generator that trusts
`securitySchemes` to build an auth layer will produce nothing usable.

Concretely: `POST /api/2/auth/token` **does not exist** and answers 404. It is a plausible-looking
guess, and `synchra.py` shipped it as the default `token_url` for its refresh flow, which therefore
cannot work. If you need a token to change while a process runs, resolve it from the outside — a
callable, a file, a secrets manager — rather than expecting a refresh grant.

## 5. A notice puts its content somewhere else

A chat message normally carries an ordered list of typed parts in `message_parts`. A **notice** does
not: it fills `notice_message_parts` and leaves `message_parts` **empty**.

A TikTok gift is the common case — `type: notice`, `sub_type: tiktok_gift`, with the gift and its
image in the notice parts. A renderer that reads only `message_parts` draws every gift, sub and raid
as a blank row, and because gifts cluster, a busy stream's chat log appears to go dead.

Worth deciding deliberately whether a notice is a "message" or an "event" in your own UI: the API
delivers it through `chat-messages`, not through `activities`, so a notification filter built around
"messages vs events" will put gifts on the wrong side of the line unless you single them out.

## 6. Viewer avatars are missing for some providers, present for others

`viewer_profile_picture_url` is filled for TikTok and null for Twitch and YouTube, so a chat log
rendered straight from the API shows pictures for some people and blanks for the rest.

The picture does exist, at `GET /channels/{id}/viewers/{provider}/{id}/info` — one request per
viewer, which is why no client should resolve them eagerly. Cache per **viewer** rather than per
message, and cache the negative answer too, or every refresh retries everyone who has not set one.
That endpoint needs a token that can read the channel's viewers; see §3.

## 7. There is no public profile URL

The API identifies a viewer by handle and provider id and carries no link to their profile. Building
one is per-provider: YouTube is addressed by **channel id**, everyone else by **handle**, and some
providers have no public profile page at all.

## 8. Unknown enum values happen

The description models some fields as a union of several platforms' enums; the service will send a
value that is not in the union. Decide up front whether an unknown value throws or passes through —
`synchra-php` throws, naming the field, on the grounds that silently handing back a value outside
the declared type is worse. Either way, do not assume the enum is closed.

Relatedly: a handful of fields (`KvEntry.value`, `DashboardProfileData.layout`) are genuinely "any
JSON value" in the description. They cannot be modelled; document them in prose.

## 9. Three WebSocket payloads are documented nowhere but the WS reference

`KvEventData`, `ChannelGiveawaysEventData` and `QueueEvent` appear in `spec/websocket.md` and never
in `openapi.json`, so a generator driven only by the OpenAPI document will not produce them.
`ActivityAlertWidgetTest` exists only as a JSON example, with no schema at all.

Also in the WebSocket protocol: the socket accepts the bare text `ping` as well as
`{"command":"ping"}`, and replies with bare text `pong` — not JSON. A client that pipes everything
through a JSON parser will throw on its own keepalive.

## 10. `POST` and `PATCH` must not be retried blindly

The API rate-limits with 429 and sends `Retry-After`. Retrying `GET`/`HEAD`/`OPTIONS`/`PUT`/`DELETE`
is safe; retrying a `POST` that already succeeded sends the chat message twice. Idempotency keys are
not offered, so this cannot be papered over at the transport layer.

## 11. Two other credential types exist

Besides the bearer token: channel **ingest API keys** (passed as an ordinary parameter, not a
header) and the widget **`x-kv-token`** header. Neither appears in `securitySchemes`.

---

# TikTok gift tables

`data/tiktok_gifts.json` and `data/tiktok_gifts_coinvertify.json` are **not** from the Synchra API.
They are here because rendering a gift notice (§5) means turning a gift id into a name, a price and
an image, and the API does not provide a lookup table for that.

## 12. The same gift exists under several ids

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

## 13. Each source is authoritative for different fields

| Source | Good for | Weak on |
| :--- | :--- | :--- |
| TikTok webcast payload (via the Alberand gist) | `id`, `diamond_count`, `duration` | names — `en` only |
| coinvertify.com (scraped) | `names` in 10 locales (`ar ba de en es fr id pt ru tr`) | a point-in-time scrape; ids drift |

Merge in that order and let the gist win on numbers, the scrape win on names. `merge_gifts.py`
unions the `names` map key by key rather than replacing it, which is the only reason the combined
table has 236 of 289 gifts localised.

## 14. The scraper is the most fragile thing here

coinvertify.com is a Nuxt 3 app, and Nuxt serialises its payload with structural sharing: every
nested value is replaced by an **index into one flat array**. The JSON has to be rehydrated before
it means anything, and the gift list sits under a generated, opaque key — so the scraper looks for
the *shape* of the data rather than its name.

A Nuxt upgrade on their side breaks this silently, yielding zero gifts rather than an error. The
tool now fails loudly and leaves the existing table alone instead of writing an empty one.

## 15. The old gift tooling never worked

`check_dups.py` in the original Python tree could not report anything: it read
`data.get("gifts", [])` from a file that is a bare JSON array, so it always saw zero gifts, and it
grouped on `g["name"]` where the field is a `names` map. Both failures were silent — it printed
"No redundant entries found" on every run. Its replacement is `tools/check_gifts.py`.

All four original scripts also had absolute Windows paths (`p:/Python/synchra/…`) hardcoded in
`__main__` and took no arguments.
