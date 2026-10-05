#!/usr/bin/env bash
# Compare two OpenAPI snapshots and report what moved.
#
#   tools/diff-spec.sh old.json [new.json]      # new defaults to spec/openapi.json
#
# Exists because the API has no changelog. A removed path is the dangerous case — a generated
# client keeps compiling against a method the service no longer answers — so removals are reported
# first and the exit status is non-zero when there are any.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
old="${1:?usage: diff-spec.sh OLD_SPEC [NEW_SPEC]}"
new="${2:-$root/spec/openapi.json}"

paths() { jq -r '.paths | keys[]' "$1" | sort; }
schemas() { jq -r '.components.schemas | keys[]' "$1" | sort; }

removed_paths="$(comm -23 <(paths "$old") <(paths "$new"))"
added_paths="$(comm -13 <(paths "$old") <(paths "$new"))"
removed_schemas="$(comm -23 <(schemas "$old") <(schemas "$new"))"
added_schemas="$(comm -13 <(schemas "$old") <(schemas "$new"))"

count() {
    # `comm` yields an empty string for "nothing", and a here-string of "" is still one empty line,
    # so grep -c would say 1. Hence the explicit case.
    if [[ -z "$1" ]]; then
        echo 0
    else
        grep -c '' <<<"$1"
    fi
}

printf 'old: %s\n' "$old"
printf 'new: %s\n\n' "$new"

printf 'paths   %s -> %s  (+%s / -%s)\n' \
    "$(jq '.paths | length' "$old")" "$(jq '.paths | length' "$new")" \
    "$(count "$added_paths")" "$(count "$removed_paths")"
printf 'schemas %s -> %s  (+%s / -%s)\n\n' \
    "$(jq '.components.schemas | length' "$old")" "$(jq '.components.schemas | length' "$new")" \
    "$(count "$added_schemas")" "$(count "$removed_schemas")"

section() {
    local title="$1" body="$2"

    if [[ -n "$body" ]]; then
        printf '## %s\n' "$title"

        while IFS= read -r line; do
            printf '  %s\n' "$line"
        done <<<"$body"

        printf '\n'
    fi
}

section 'REMOVED paths — a client calling one of these now gets a 404' "$removed_paths"
section 'REMOVED schemas' "$removed_schemas"
section 'Added paths' "$added_paths"
section 'Added schemas' "$added_schemas"

# Deliberately not `[[ -z … ]] && exit 0`: as the last statement of a script that is a non-zero
# exit when the condition is false, which would report a clean diff as a failure.
if [[ -n "$removed_paths$removed_schemas" ]]; then
    exit 1
fi
