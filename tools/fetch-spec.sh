#!/usr/bin/env bash
# Refresh the API description from the live service.
#
# Synchra publishes the OpenAPI document and the WebSocket reference from the running API, and
# nowhere else — there is no versioned download, no release feed, and no changelog. So the snapshot
# in spec/ is the only record of what the API looked like at a point in time, and `git diff` after
# running this is the only way to see what changed.
#
# That has caught removals as well as additions: between the April 2026 and October 2026 snapshots
# 102 paths appeared and 31 disappeared. See docs/CAVEATS.md.
set -euo pipefail

host="${SYNCHRA_API_HOST:-https://api.synchra.net}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Pretty-printed and with sorted keys, so a diff shows what actually changed rather than a
# re-serialisation of the whole document. jq --sort-keys is what makes two fetches comparable:
# the API does not guarantee a stable key order.
curl --fail --show-error --silent "$host/openapi.json" \
    | jq --sort-keys . \
    > "$root/spec/openapi.json"

curl --fail --show-error --silent "$host/api/2/ws-docs" > "$root/spec/websocket.md"

printf 'Fetched %s into spec/.\n' "$host"
printf 'paths=%s schemas=%s version=%s\n' \
    "$(jq '.paths | length' "$root/spec/openapi.json")" \
    "$(jq '.components.schemas | length' "$root/spec/openapi.json")" \
    "$(jq -r '.info.version' "$root/spec/openapi.json")"
