# Apply overlay/annotations.json to the published API description.
#
#   jq --argjson overlay "$(cat overlay/annotations.json)" -f tools/annotate.jq < spec/openapi.json
#
# tools/annotate-spec.py wraps this; synchra-php vendors a copy and runs it during its own fetch.
# This file is the single implementation, so the two stay honest.
#
# What the overlay may do:
#
#   info                  prose appended to info.description
#   operations            prose appended to an operation's description, keyed "GET /api/2/..."
#   schemas               prose for a schema or one of its properties, keyed "Name" or "Name.field"
#   public                operations verified to answer without a token -> security: []
#   errors                error responses added by rule, since the description documents none
#   add.paths             routes the service answers but the description omits
#   add.schemas           schemas only the WebSocket reference defines
#   add.securitySchemes   replaces the empty OAuth2 stub with what the API actually accepts
#
# Two classes of failure, both fatal and both deliberate:
#
#   - a note whose target does not exist. Something was renamed or removed upstream.
#   - an addition whose target DOES exist. Synchra documented it; drop it from the overlay rather
#     than shadowing theirs with ours.
#
# Key order is never sorted. A generator takes class names and constructor parameter order from it.

def attribution:
    "> The notes below are not from Synchra. They were added by https://github.com/Bluscream/synchra-api."
;

# Overlay prose is written as a list of lines so it stays reviewable in a diff.
def text: if type == "array" then join("\n") else . end;

def methods: ["get", "post", "put", "delete", "patch"];

# "GET /api/2/x" -> ["paths", "/api/2/x", "get"]
def operation_path:
    split(" ") as $parts | ["paths", $parts[1], ($parts[0] | ascii_downcase)]
;

# "ChatMessage" -> [..., "ChatMessage"];  "ChatMessage.field" -> [..., "ChatMessage", "properties", "field"]
def schema_path:
    split(".") as $parts
    | if ($parts | length) == 1
      then ["components", "schemas", $parts[0]]
      else ["components", "schemas", $parts[0], "properties", $parts[1]]
      end
;

# Keep whatever the service said; the note goes after it.
def annotate($note; $attributed):
    (if $attributed then attribution + "\n\n" + $note else $note end) as $block
    | .description = (
        if (.description // "") == ""
        then $block
        else (.description | sub("\\s+$"; "")) + "\n\n---\n\n" + $block
        end
      )
;

def note_targets:
    [($overlay.operations // {} | keys_unsorted[] | {at: operation_path, note: $overlay.operations[.], attributed: true, target: .})]
    + [($overlay.schemas // {} | keys_unsorted[] | {at: schema_path, note: $overlay.schemas[.], attributed: true, target: .})]
;

# Every [path, method] pair in the document, after any additions.
def operations:
    [ .paths
      | to_entries[]
      | .key as $path
      | .value
      | keys_unsorted[]
      | . as $method
      | select(methods | index($method))
      | {path: $path, method: $method}
    ]
;

. as $spec

# ---- validation, before anything is written ----------------------------------------------------

| ([note_targets[] | . as $t | select(($spec | getpath($t.at) | type) != "object") | $t.target]) as $missing
| ([($overlay.public // [])[] | . as $t | select(($spec | getpath($t | operation_path) | type) != "object")]) as $missing_public
| ([($overlay.add.paths // {} | keys_unsorted[]) | select(. as $p | $spec.paths | has($p))]) as $existing_paths
| ([($overlay.add.schemas // {} | keys_unsorted[]) | select(. as $s | $spec.components.schemas | has($s))]) as $existing_schemas

| if (($missing + $missing_public) | length) > 0
  then
      error(
          "The overlay refers to \((($missing + $missing_public) | length)) thing(s) this description does not have:\n  "
          + (($missing + $missing_public) | join("\n  "))
          + "\nSomething was renamed or removed upstream. Check each note is still true, then update"
          + "\noverlay/annotations.json."
      )
  else .
  end

| if (($existing_paths + $existing_schemas) | length) > 0
  then
      error(
          "The overlay adds \((($existing_paths + $existing_schemas) | length)) thing(s) the description now defines itself:\n  "
          + (($existing_paths + $existing_schemas) | join("\n  "))
          + "\nSynchra documented these. Remove them from overlay/annotations.json rather than"
          + "\nshadowing the published definition."
      )
  else .
  end

# ---- additions ---------------------------------------------------------------------------------
# First, so that error responses and notes can apply to what was added.

| if ($overlay.add.paths // {}) != {} then .paths += $overlay.add.paths else . end
| if ($overlay.add.schemas // {}) != {} then .components.schemas += $overlay.add.schemas else . end
| if ($overlay.add.securitySchemes // {}) != {}
  then .components.securitySchemes = $overlay.add.securitySchemes
  else .
  end

# ---- public operations -------------------------------------------------------------------------
# `security: []` is OpenAPI's way of saying "this one needs no credential". The description cannot be
# used to infer it: admin routes carry a security entry with no scopes, and 36 operations omit the
# key altogether, so each entry in `public` was verified with an unauthenticated request instead.

| ($overlay.public // []) as $public
| reduce $public[] as $entry (
      .;
      setpath(($entry | operation_path) + ["security"]; [])
  )

# ---- error responses ---------------------------------------------------------------------------
# The description documents successes and 422 and nothing else, though 401, 403, 404 and 429 all
# occur. These are added by rule rather than listed per operation: 240 operations' worth of identical
# response objects would be unreviewable, and every one of them would be a guess the moment the API
# changed. An existing response is never replaced.

| reduce operations[] as $op (
      .;
      . as $doc
      # Read "needs no credential" off the document rather than off the overlay's `public` list: an
      # added route can declare `security: []` itself, and this way one rule covers both. (An earlier
      # version tested `$public_pairs | index($pair)`, which silently never matched — jq's `index`
      # searches an array for a *subsequence*, not for an element.)
      | (($doc | getpath(["paths", $op.path, $op.method, "security"])) == []) as $public
      | (
          ($overlay.errors.always // {})
          + (if $public then {} else ($overlay.errors.authenticated // {}) end)
          + (if ($op.path | test("\\{")) then ($overlay.errors.identified // {}) else {} end)
        ) as $add
      | reduce ($add | keys_unsorted[]) as $status (
            $doc;
            if (getpath(["paths", $op.path, $op.method, "responses", $status]) | type) == "object"
            then .
            else setpath(["paths", $op.path, $op.method, "responses", $status]; $add[$status])
            end
        )
  )

# ---- prose -------------------------------------------------------------------------------------

| reduce note_targets[] as $t (
      .;
      setpath($t.at; getpath($t.at) | annotate(($t.note | text); $t.attributed))
  )
| if ($overlay.info // null) != null
  then .info |= annotate(($overlay.info | text); false)
  else .
  end
