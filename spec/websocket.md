# WebSocket API

Connect to `wss://api.synchra.net/api/2/ws`.

Use the WebSocket API to subscribe to live events. Each client message is either the text `ping` or a JSON command object.

## Commands

| Command | Purpose |
| --- | --- |
| `ping` | Keep the connection alive. Send raw text `ping` or `{ "command": "ping" }`; the server replies with raw text `pong`. |
| `authorization` | Authenticate the socket with a bearer token before subscribing to private events. |
| `subscribe` | Subscribe to one event type. `type` and `data` are required. |
| `unsubscribe` | Unsubscribe from one event type, or omit `type` to unsubscribe from everything. |

All JSON commands may include `nonce`. When present, successful `authorization`, `subscribe`, and `unsubscribe` commands receive an acknowledgement event:

```json
{
  "type": "ok",
  "action": "new",
  "data": {},
  "nonce": "client-nonce"
}
```

Errors are sent as events with `type: "error"` and the same `nonce` when available.

```json
{
  "type": "error",
  "action": "new",
  "data": {
    "code": 400,
    "message": "Unknown type chat_messagee",
    "type": "unknown_type",
    "errors": []
  },
  "nonce": "client-nonce"
}
```

## Authentication

Some event data is public and some requires channel access. Send an `authorization` command before subscribing when you need authenticated access.

```json
{
  "command": "authorization",
  "data": {
    "token": "YOUR_ACCESS_TOKEN"
  },
  "nonce": "auth-1"
}
```

## Subscribe

Subscribe with the event `type` and the event-specific `data` shown below.

```json
{
  "command": "subscribe",
  "type": "chat_message",
  "data": {
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d"
  },
  "nonce": "sub-1"
}
```

## Unsubscribe

Unsubscribe from a matching subscription by sending the same `type` and `data` used to subscribe. Omit `type` to remove all subscriptions on the socket.

```json
{
  "command": "unsubscribe",
  "type": "chat_message",
  "data": {
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d"
  },
  "nonce": "unsub-1"
}
```

## Event Types

| Type | Subscribe With |
| --- | --- |
| `activity` | `channel_id` |
| `activity_alert_test` | `widget_id` |
| `channel_giveaway` | `giveaway_id` |
| `channel_giveaway_entries` | `giveaway_id` |
| `channel_giveaways` | `channel_id` |
| `channel_provider` | `channel_id` |
| `channel_provider_stream` | `channel_id` |
| `channel_queue` | `channel_queue_id` |
| `chat_event` | `channel_id` |
| `chat_message` | `channel_id` |
| `obs_remote_command` | `obs_remote_id` |
| `widget` | `widget_id` |
| `widget_value` | `widget_id`, `channel_id`, `key` |

## `activity`

Activity events.

### Subscribe
```json
{
  "command": "subscribe",
  "type": "activity",
  "data": {
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d"
  },
  "nonce": "optional-nonce"
}
```
#### Subscribe Data
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `channel_id` | `uuid` | **Yes** |  |

### Event
```json
{
  "type": "activity",
  "action": "new",
  "data": {
    "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "provider": "twitch",
    "provider_message_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "provider_channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "provider_viewer_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "viewer_name": "string",
    "viewer_display_name": "string",
    "type": "sub",
    "sub_type": "string",
    "count": 0,
    "count_decimal_place": 0,
    "count_currency": "string",
    "created_at": "2026-01-01T12:00:00Z",
    "gifted_viewers": [
      {
        "user_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
        "username": "string",
        "display_name": "string"
      }
    ],
    "system_message": "string",
    "message_parts": [
      {
        "type": "text",
        "text": "string"
      }
    ],
    "read": false,
    "color": "string",
    "font_color": "string",
    "count_name": "string",
    "type_display_name": "string",
    "sub_type_display_name": "string",
    "activity_group": "subscription",
    "contribution_group": "currency_amount"
  }
}
```
#### Event Envelope
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | `string` | **Yes** |  |
| `action` | `new`<br>`updated`<br>`deleted` | **Yes** |  |
| `data` | `Activity` | **Yes** |  |
| `nonce` | `string`<br>`null` | No |  |

---

## `activity_alert_test`

Activity alert test events.

### Subscribe
```json
{
  "command": "subscribe",
  "type": "activity_alert_test",
  "data": {
    "widget_id": "0197465f-c40d-7db8-ad11-dc44b153a32d"
  },
  "nonce": "optional-nonce"
}
```
#### Subscribe Data
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `widget_id` | `uuid` | **Yes** |  |

### Event
```json
{
  "type": "activity_alert_test",
  "action": "new",
  "data": {
    "widget_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "activity": {
      "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
      "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
      "provider": "twitch",
      "provider_message_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
      "provider_channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
      "provider_viewer_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
      "viewer_name": "string",
      "viewer_display_name": "string",
      "type": "sub",
      "sub_type": "string",
      "count": 0,
      "count_decimal_place": 0,
      "count_currency": "string",
      "created_at": "2026-01-01T12:00:00Z",
      "gifted_viewers": [
        {
          "user_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
          "username": "string",
          "display_name": "string"
        }
      ],
      "system_message": "string",
      "message_parts": [
        {
          "type": "text",
          "text": "string"
        }
      ],
      "read": false,
      "color": "string",
      "font_color": "string",
      "count_name": "string",
      "type_display_name": "string",
      "sub_type_display_name": "string",
      "activity_group": "subscription",
      "contribution_group": "currency_amount"
    },
    "settings": {
      "canvas_scale": 0.0,
      "enabled": false,
      "active_group_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
      "themes": [
        {
          "text_color": "string",
          "viewer_color": "string",
          "count_color": "string",
          "count_name_color": "string",
          "max_width": 0,
          "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
          "font_size": 0,
          "media_position": "above",
          "title_offset_x": 0,
          "title_offset_y": 0,
          "title_delay_seconds": 0.0,
          "title_animation_type": "none",
          "message_offset_x": 0,
          "message_offset_y": 0,
          "message_delay_seconds": 0.0,
          "message_animation_type": "none",
          "title_alignment": "left",
          "message_alignment": "left",
          "animation_type": "none",
          "exit_animation_type": "none",
          "celebration_type": "confetti",
          "duration_seconds": 0.0,
          "custom_script_typescript": "string",
          "custom_script_javascript": "string",
          "custom_css": "string",
          "id": "string",
          "name": "string"
        }
      ],
      "media_packs": [
        {
          "id": "string",
          "name": "string",
          "media": [
            {
              "name": "string",
              "enabled": false,
              "url": "string",
              "weight": 0,
              "filter": {
                "min_count": 0.0,
                "max_count": 0.0,
                "sub_types": [
                  "string"
                ],
                "message_keywords": [
                  "string"
                ]
              },
              "volume": 0.0,
              "max_duration_seconds": 0.0,
              "type": "image",
              "sound_url": "string"
            }
          ]
        }
      ],
      "sound_packs": [
        {
          "id": "string",
          "name": "string",
          "sounds": [
            {
              "name": "string",
              "enabled": false,
              "url": "string",
              "weight": 0,
              "filter": {
                "min_count": 0.0,
                "max_count": 0.0,
                "sub_types": [
                  "string"
                ],
                "message_keywords": [
                  "string"
                ]
              },
              "volume": 0.0,
              "max_duration_seconds": 0.0
            }
          ]
        }
      ],
      "tts_packs": [
        {
          "id": "string",
          "name": "string",
          "tts": [
            {
              "name": "string",
              "enabled": false,
              "channel_provider_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
              "provider": "twitch",
              "voice_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
              "voice_trigger": "string",
              "provider_settings": {},
              "weight": 0,
              "filter": {
                "min_count": 0.0,
                "max_count": 0.0,
                "sub_types": [
                  "string"
                ],
                "message_keywords": [
                  "string"
                ]
              },
              "volume": 0.0,
              "delay_seconds": 0.0,
              "max_duration_seconds": 0.0,
              "read_title": false,
              "read_message": false
            }
          ]
        }
      ],
      "variant_packs": [
        {
          "id": "string",
          "name": "string",
          "variants": [
            {
              "text_color": "string",
              "viewer_color": "string",
              "count_color": "string",
              "count_name_color": "string",
              "max_width": 0,
              "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
              "font_size": 0,
              "media_position": "above",
              "title_offset_x": 0,
              "title_offset_y": 0,
              "title_delay_seconds": 0.0,
              "title_animation_type": "none",
              "message_offset_x": 0,
              "message_offset_y": 0,
              "message_delay_seconds": 0.0,
              "message_animation_type": "none",
              "title_alignment": "left",
              "message_alignment": "left",
              "animation_type": "none",
              "exit_animation_type": "none",
              "celebration_type": "confetti",
              "duration_seconds": 0.0,
              "custom_script_typescript": "string",
              "custom_script_javascript": "string",
              "custom_css": "string",
              "id": "string",
              "name": "string",
              "enabled": false,
              "weight": 0,
              "filter": {
                "min_count": 0.0,
                "max_count": 0.0,
                "sub_types": [
                  "string"
                ],
                "message_keywords": [
                  "string"
                ]
              },
              "theme_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
              "variant_pack_ids": [
                "string"
              ],
              "media_pack_ids": [
                "string"
              ],
              "sound_pack_ids": [
                "string"
              ],
              "tts_pack_ids": [
                "string"
              ],
              "title_template": "string",
              "message_template": "string",
              "media": [
                {
                  "name": "string",
                  "enabled": false,
                  "url": "string",
                  "weight": 0,
                  "filter": {
                    "min_count": 0.0,
                    "max_count": 0.0,
                    "sub_types": [
                      "string"
                    ],
                    "message_keywords": [
                      "string"
                    ]
                  },
                  "volume": 0.0,
                  "max_duration_seconds": 0.0,
                  "type": "image",
                  "sound_url": "string"
                }
              ],
              "sounds": [
                {
                  "name": "string",
                  "enabled": false,
                  "url": "string",
                  "weight": 0,
                  "filter": {
                    "min_count": 0.0,
                    "max_count": 0.0,
                    "sub_types": [
                      "string"
                    ],
                    "message_keywords": [
                      "string"
                    ]
                  },
                  "volume": 0.0,
                  "max_duration_seconds": 0.0
                }
              ],
              "tts": [
                {
                  "name": "string",
                  "enabled": false,
                  "channel_provider_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
                  "provider": "twitch",
                  "voice_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
                  "voice_trigger": "string",
                  "provider_settings": {},
                  "weight": 0,
                  "filter": {
                    "min_count": 0.0,
                    "max_count": 0.0,
                    "sub_types": [
                      "string"
                    ],
                    "message_keywords": [
                      "string"
                    ]
                  },
                  "volume": 0.0,
                  "delay_seconds": 0.0,
                  "max_duration_seconds": 0.0,
                  "read_title": false,
                  "read_message": false
                }
              ]
            }
          ]
        }
      ],
      "groups": [
        {
          "text_color": "string",
          "viewer_color": "string",
          "count_color": "string",
          "count_name_color": "string",
          "max_width": 0,
          "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
          "font_size": 0,
          "media_position": "above",
          "title_offset_x": 0,
          "title_offset_y": 0,
          "title_delay_seconds": 0.0,
          "title_animation_type": "none",
          "message_offset_x": 0,
          "message_offset_y": 0,
          "message_delay_seconds": 0.0,
          "message_animation_type": "none",
          "title_alignment": "left",
          "message_alignment": "left",
          "animation_type": "none",
          "exit_animation_type": "none",
          "celebration_type": "confetti",
          "duration_seconds": 0.0,
          "custom_script_typescript": "string",
          "custom_script_javascript": "string",
          "custom_css": "string",
          "id": "string",
          "name": "string",
          "enabled": false,
          "volume": 0.0,
          "theme_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
          "queue_delay_seconds": 0.0,
          "filter_currency": "string",
          "rules": [
            {
              "name": "string",
              "activity_type": "sub"
            }
          ]
        }
      ]
    }
  }
}
```
#### Event Envelope
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | `string` | **Yes** |  |
| `action` | `new`<br>`updated`<br>`deleted` | **Yes** |  |
| `data` | `ActivityAlertWidgetTest` | **Yes** |  |
| `nonce` | `string`<br>`null` | No |  |

---

## `channel_giveaway`

Channel giveaway events.

### Subscribe
```json
{
  "command": "subscribe",
  "type": "channel_giveaway",
  "data": {
    "giveaway_id": "0197465f-c40d-7db8-ad11-dc44b153a32d"
  },
  "nonce": "optional-nonce"
}
```
#### Subscribe Data
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `giveaway_id` | `uuid` | **Yes** |  |

### Event
```json
{
  "type": "channel_giveaway",
  "action": "new",
  "data": {}
}
```
#### Event Envelope
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | `string` | **Yes** |  |
| `action` | `new`<br>`updated`<br>`deleted` | **Yes** |  |
| `data` | `any` | **Yes** |  |
| `nonce` | `string`<br>`null` | No |  |
| `draw` | `GiveawayDraw` | No |  |

---

## `channel_giveaway_entries`

Channel giveaway entries events.

### Subscribe
```json
{
  "command": "subscribe",
  "type": "channel_giveaway_entries",
  "data": {
    "giveaway_id": "0197465f-c40d-7db8-ad11-dc44b153a32d"
  },
  "nonce": "optional-nonce"
}
```
#### Subscribe Data
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `giveaway_id` | `uuid` | **Yes** |  |

### Event
```json
{
  "type": "channel_giveaway_entries",
  "action": "new",
  "data": [
    {
      "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
      "created_at": "2026-01-01T12:00:00Z",
      "channel_giveaway_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
      "provider": "twitch",
      "provider_viewer_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
      "name": "string",
      "display_name": "string"
    }
  ]
}
```
#### Event Envelope
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | `string` | **Yes** |  |
| `action` | `new`<br>`updated`<br>`deleted` | **Yes** |  |
| `data` | `GiveawayEntry`[] | **Yes** |  |
| `nonce` | `string`<br>`null` | No |  |

---

## `channel_giveaways`

Channel giveaways events.

### Subscribe
```json
{
  "command": "subscribe",
  "type": "channel_giveaways",
  "data": {
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d"
  },
  "nonce": "optional-nonce"
}
```
#### Subscribe Data
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `channel_id` | `uuid` | **Yes** |  |

### Event
```json
{
  "type": "channel_giveaways",
  "action": "new",
  "data": {
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "giveaway_id": "0197465f-c40d-7db8-ad11-dc44b153a32d"
  }
}
```
#### Event Envelope
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | `string` | **Yes** |  |
| `action` | `new`<br>`updated`<br>`deleted` | **Yes** |  |
| `data` | `ChannelGiveawaysEventData` | **Yes** |  |
| `nonce` | `string`<br>`null` | No |  |

---

## `channel_provider`

Channel provider events.

### Subscribe
```json
{
  "command": "subscribe",
  "type": "channel_provider",
  "data": {
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d"
  },
  "nonce": "optional-nonce"
}
```
#### Subscribe Data
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `channel_id` | `uuid` | **Yes** |  |

### Event
```json
{
  "type": "channel_provider",
  "action": "new",
  "data": {
    "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "provider": "twitch",
    "provider_channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "provider_channel_name": "string",
    "provider_channel_display_name": "string",
    "state": {},
    "scope_needed": false
  }
}
```
#### Event Envelope
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | `string` | **Yes** |  |
| `action` | `new`<br>`updated`<br>`deleted` | **Yes** |  |
| `data` | `ChannelProviderPublic` | **Yes** |  |
| `nonce` | `string`<br>`null` | No |  |

---

## `channel_provider_stream`

Channel provider stream events.

### Subscribe
```json
{
  "command": "subscribe",
  "type": "channel_provider_stream",
  "data": {
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d"
  },
  "nonce": "optional-nonce"
}
```
#### Subscribe Data
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `channel_id` | `uuid` | **Yes** |  |

### Event
```json
{
  "type": "channel_provider_stream",
  "action": "new",
  "data": {
    "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "channel_provider_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "channel_stream_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "provider": "twitch",
    "provider_channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "provider_stream_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "title": "string",
    "category": "string",
    "tags": [
      "string"
    ],
    "viewer_count": 0,
    "variant_label": "string",
    "provider_logo_variant": "string",
    "status": "pending",
    "started_at": "2026-01-01T12:00:00Z",
    "ended_at": "2026-01-01T12:00:00Z",
    "avg_viewer_count": 0,
    "peak_viewer_count": 0,
    "viewer_watched_minutes": 0,
    "chat_message_count": 0,
    "unique_chatter_count": 0
  }
}
```
#### Event Envelope
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | `string` | **Yes** |  |
| `action` | `new`<br>`updated`<br>`deleted` | **Yes** |  |
| `data` | `ChannelProviderStream` | **Yes** |  |
| `nonce` | `string`<br>`null` | No |  |

---

## `channel_queue`

Channel queue events.

### Subscribe
```json
{
  "command": "subscribe",
  "type": "channel_queue",
  "data": {
    "channel_queue_id": "0197465f-c40d-7db8-ad11-dc44b153a32d"
  },
  "nonce": "optional-nonce"
}
```
#### Subscribe Data
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `channel_queue_id` | `uuid` | **Yes** |  |

### Event
```json
{
  "type": "channel_queue",
  "action": "new",
  "data": {
    "type": "channel_queue_viewer_created"
  }
}
```
#### Event Envelope
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | `string` | **Yes** |  |
| `action` | `new`<br>`updated`<br>`deleted` | **Yes** |  |
| `data` | `QueueEvent` | **Yes** |  |
| `nonce` | `string`<br>`null` | No |  |

---

## `chat_event`

Chat event events.

### Subscribe
```json
{
  "command": "subscribe",
  "type": "chat_event",
  "data": {
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d"
  },
  "nonce": "optional-nonce"
}
```
#### Subscribe Data
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `channel_id` | `uuid` | **Yes** |  |

### Event
```json
{
  "type": "chat_event",
  "action": "new",
  "data": {
    "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "provider": "twitch",
    "provider_channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "provider_event_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "name": "string",
    "type": "poll",
    "status": "open",
    "created_at": "2026-01-01T12:00:00Z",
    "updated_at": "2026-01-01T12:00:00Z"
  }
}
```
#### Event Envelope
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | `string` | **Yes** |  |
| `action` | `new`<br>`updated`<br>`deleted` | **Yes** |  |
| `data` | `ChatEvent` | **Yes** |  |
| `nonce` | `string`<br>`null` | No |  |

---

## `chat_message`

Chat message events.

### Subscribe
```json
{
  "command": "subscribe",
  "type": "chat_message",
  "data": {
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d"
  },
  "nonce": "optional-nonce"
}
```
#### Subscribe Data
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `channel_id` | `uuid` | **Yes** |  |

### Event
```json
{
  "type": "chat_message",
  "action": "new",
  "data": {
    "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "type": "message",
    "sub_type": "string",
    "created_at": "2026-01-01T12:00:00Z",
    "updated_at": "2026-01-01T12:00:00Z",
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "outgoing_group_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "channel_provider_chat_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "channel_provider_stream_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "provider_logo_variant": "string",
    "provider": "twitch",
    "provider_channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "provider_message_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "provider_viewer_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "viewer_name": "string",
    "viewer_display_name": "string",
    "viewer_profile_picture_url": "string",
    "viewer_created_at": "2026-01-01T12:00:00Z",
    "viewer_color": "string",
    "message_parts": [
      {
        "type": "text",
        "text": "string"
      }
    ],
    "badges": [
      {
        "id": "string",
        "type": "string",
        "name": "string"
      }
    ],
    "access_level": 0,
    "notice_message_parts": [
      {
        "type": "text",
        "text": "string"
      }
    ],
    "source_provider_channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "source_provider_channel_name": "string",
    "source_provider_channel_display_name": "string",
    "deleted_at": "2026-01-01T12:00:00Z",
    "deleted_by_provider_viewer_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "deleted_by_name": "string",
    "deleted_by_display_name": "string",
    "parent_provider_thread_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "parent": {
      "provider_message_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
      "message": "string",
      "provider_viewer_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
      "viewer_name": "string",
      "viewer_display_name": "string"
    }
  }
}
```
#### Event Envelope
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | `string` | **Yes** |  |
| `action` | `new`<br>`updated`<br>`deleted` | **Yes** |  |
| `data` | `ChatMessage` | **Yes** |  |
| `nonce` | `string`<br>`null` | No |  |

---

## `obs_remote_command`

Obs remote command events.

### Subscribe
```json
{
  "command": "subscribe",
  "type": "obs_remote_command",
  "data": {
    "obs_remote_id": "0197465f-c40d-7db8-ad11-dc44b153a32d"
  },
  "nonce": "optional-nonce"
}
```
#### Subscribe Data
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `obs_remote_id` | `uuid` | **Yes** |  |

### Event
```json
{
  "type": "obs_remote_command",
  "action": "new",
  "data": {
    "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "obs_remote_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "command": "refresh_state",
    "data": {},
    "created_at": "2026-01-01T12:00:00Z"
  }
}
```
#### Event Envelope
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | `string` | **Yes** |  |
| `action` | `new`<br>`updated`<br>`deleted` | **Yes** |  |
| `data` | `ObsRemoteCommand` | **Yes** |  |
| `nonce` | `string`<br>`null` | No |  |

---

## `widget`

Widget events.

### Subscribe
```json
{
  "command": "subscribe",
  "type": "widget",
  "data": {
    "widget_id": "0197465f-c40d-7db8-ad11-dc44b153a32d"
  },
  "nonce": "optional-nonce"
}
```
#### Subscribe Data
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `widget_id` | `uuid` | **Yes** |  |

### Event
```json
{
  "type": "widget",
  "action": "new",
  "data": {
    "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "name": "string",
    "created_at": "2026-01-01T12:00:00Z",
    "updated_at": "2026-01-01T12:00:00Z",
    "type": "chat_widget"
  }
}
```
#### Event Envelope
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | `string` | **Yes** |  |
| `action` | `new`<br>`updated`<br>`deleted` | **Yes** |  |
| `data` | `ChatWidget`<br>`CustomWidget`<br>`ActivityAlertWidget`<br>`GoalWidget`<br>`GiveawayWidget`<br>`LeaderboardWidget`<br>`StreamathonWidget`<br>`VersusWidget`<br>`ViewerCountWidget`<br>`ValueWidget` | **Yes** |  |
| `nonce` | `string`<br>`null` | No |  |

#### Event Data
Discriminator: `type`

##### `ChatWidget`
```json
{
  "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "type": "chat_widget",
  "name": "string",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z",
  "last_used_at": "2026-01-01T12:00:00Z",
  "settings": {
    "canvas_scale": 0.0,
    "size": "xxs",
    "text_color": "string",
    "text_shadow_color": "string",
    "background_color": "string",
    "background_opacity": 0.0,
    "border_width": 0,
    "border_color": "string",
    "border_radius": 0,
    "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "message_fade_duration_seconds": 0,
    "message_delay_seconds": 0,
    "ignore_names": [
      "string"
    ],
    "provider_logo": false,
    "provider_logo_display": "default",
    "badges": false,
    "username_colon": false,
    "notices": false,
    "message_order": "top",
    "message_alignment": "left",
    "providers": [
      "all"
    ],
    "style_type": "string",
    "entrance_animation_type": "string",
    "themes": [
      {
        "id": "string",
        "name": "string",
        "text_color": "string",
        "text_shadow_color": "string",
        "background_color": "string",
        "background_opacity": 0.0,
        "border_width": 0,
        "border_color": "string",
        "border_radius": 0,
        "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
        "provider_logo_display": "default",
        "custom_css": "string"
      }
    ],
    "custom_css": "string"
  }
}
```
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `uuid` | **Yes** |  |
| `channel_id` | `uuid` | **Yes** |  |
| `type` | `chat_widget` | No |  |
| `name` | `string` | **Yes** |  |
| `created_at` | `date-time` | **Yes** |  |
| `updated_at` | `date-time` | **Yes** |  |
| `last_used_at` | `date-time`<br>`null` | No |  |
| `settings` | `ChatWidgetSettings` | No |  |

##### `CustomWidget`
```json
{
  "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "type": "custom_widget",
  "name": "string",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z",
  "last_used_at": "2026-01-01T12:00:00Z",
  "settings": {
    "build": {
      "javascript": "string",
      "css": "string",
      "html": "string",
      "source_map": "string"
    },
    "settings_values": {},
    "enabled": false,
    "project": {
      "entry": "string",
      "files": {}
    }
  }
}
```
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `uuid` | **Yes** |  |
| `channel_id` | `uuid` | **Yes** |  |
| `type` | `custom_widget` | No |  |
| `name` | `string` | **Yes** |  |
| `created_at` | `date-time` | **Yes** |  |
| `updated_at` | `date-time` | **Yes** |  |
| `last_used_at` | `date-time`<br>`null` | No |  |
| `settings` | `CustomWidgetSettings` | No |  |

##### `ActivityAlertWidget`
```json
{
  "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "type": "activity_alert_widget",
  "name": "string",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z",
  "last_used_at": "2026-01-01T12:00:00Z",
  "settings": {
    "canvas_scale": 0.0,
    "enabled": false,
    "active_group_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "themes": [
      {
        "text_color": "string",
        "viewer_color": "string",
        "count_color": "string",
        "count_name_color": "string",
        "max_width": 0,
        "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
        "font_size": 0,
        "media_position": "above",
        "title_offset_x": 0,
        "title_offset_y": 0,
        "title_delay_seconds": 0.0,
        "title_animation_type": "none",
        "message_offset_x": 0,
        "message_offset_y": 0,
        "message_delay_seconds": 0.0,
        "message_animation_type": "none",
        "title_alignment": "left",
        "message_alignment": "left",
        "animation_type": "none",
        "exit_animation_type": "none",
        "celebration_type": "confetti",
        "duration_seconds": 0.0,
        "custom_script_typescript": "string",
        "custom_script_javascript": "string",
        "custom_css": "string",
        "id": "string",
        "name": "string"
      }
    ],
    "media_packs": [
      {
        "id": "string",
        "name": "string",
        "media": [
          {
            "name": "string",
            "enabled": false,
            "url": "string",
            "weight": 0,
            "filter": {
              "min_count": 0.0,
              "max_count": 0.0,
              "sub_types": [
                "string"
              ],
              "message_keywords": [
                "string"
              ]
            },
            "volume": 0.0,
            "max_duration_seconds": 0.0,
            "type": "image",
            "sound_url": "string"
          }
        ]
      }
    ],
    "sound_packs": [
      {
        "id": "string",
        "name": "string",
        "sounds": [
          {
            "name": "string",
            "enabled": false,
            "url": "string",
            "weight": 0,
            "filter": {
              "min_count": 0.0,
              "max_count": 0.0,
              "sub_types": [
                "string"
              ],
              "message_keywords": [
                "string"
              ]
            },
            "volume": 0.0,
            "max_duration_seconds": 0.0
          }
        ]
      }
    ],
    "tts_packs": [
      {
        "id": "string",
        "name": "string",
        "tts": [
          {
            "name": "string",
            "enabled": false,
            "channel_provider_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
            "provider": "twitch",
            "voice_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
            "voice_trigger": "string",
            "provider_settings": {},
            "weight": 0,
            "filter": {
              "min_count": 0.0,
              "max_count": 0.0,
              "sub_types": [
                "string"
              ],
              "message_keywords": [
                "string"
              ]
            },
            "volume": 0.0,
            "delay_seconds": 0.0,
            "max_duration_seconds": 0.0,
            "read_title": false,
            "read_message": false
          }
        ]
      }
    ],
    "variant_packs": [
      {
        "id": "string",
        "name": "string",
        "variants": [
          {
            "text_color": "string",
            "viewer_color": "string",
            "count_color": "string",
            "count_name_color": "string",
            "max_width": 0,
            "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
            "font_size": 0,
            "media_position": "above",
            "title_offset_x": 0,
            "title_offset_y": 0,
            "title_delay_seconds": 0.0,
            "title_animation_type": "none",
            "message_offset_x": 0,
            "message_offset_y": 0,
            "message_delay_seconds": 0.0,
            "message_animation_type": "none",
            "title_alignment": "left",
            "message_alignment": "left",
            "animation_type": "none",
            "exit_animation_type": "none",
            "celebration_type": "confetti",
            "duration_seconds": 0.0,
            "custom_script_typescript": "string",
            "custom_script_javascript": "string",
            "custom_css": "string",
            "id": "string",
            "name": "string",
            "enabled": false,
            "weight": 0,
            "filter": {
              "min_count": 0.0,
              "max_count": 0.0,
              "sub_types": [
                "string"
              ],
              "message_keywords": [
                "string"
              ]
            },
            "theme_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
            "variant_pack_ids": [
              "string"
            ],
            "media_pack_ids": [
              "string"
            ],
            "sound_pack_ids": [
              "string"
            ],
            "tts_pack_ids": [
              "string"
            ],
            "title_template": "string",
            "message_template": "string",
            "media": [
              {
                "name": "string",
                "enabled": false,
                "url": "string",
                "weight": 0,
                "filter": {
                  "min_count": 0.0,
                  "max_count": 0.0,
                  "sub_types": [
                    "string"
                  ],
                  "message_keywords": [
                    "string"
                  ]
                },
                "volume": 0.0,
                "max_duration_seconds": 0.0,
                "type": "image",
                "sound_url": "string"
              }
            ],
            "sounds": [
              {
                "name": "string",
                "enabled": false,
                "url": "string",
                "weight": 0,
                "filter": {
                  "min_count": 0.0,
                  "max_count": 0.0,
                  "sub_types": [
                    "string"
                  ],
                  "message_keywords": [
                    "string"
                  ]
                },
                "volume": 0.0,
                "max_duration_seconds": 0.0
              }
            ],
            "tts": [
              {
                "name": "string",
                "enabled": false,
                "channel_provider_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
                "provider": "twitch",
                "voice_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
                "voice_trigger": "string",
                "provider_settings": {},
                "weight": 0,
                "filter": {
                  "min_count": 0.0,
                  "max_count": 0.0,
                  "sub_types": [
                    "string"
                  ],
                  "message_keywords": [
                    "string"
                  ]
                },
                "volume": 0.0,
                "delay_seconds": 0.0,
                "max_duration_seconds": 0.0,
                "read_title": false,
                "read_message": false
              }
            ]
          }
        ]
      }
    ],
    "groups": [
      {
        "text_color": "string",
        "viewer_color": "string",
        "count_color": "string",
        "count_name_color": "string",
        "max_width": 0,
        "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
        "font_size": 0,
        "media_position": "above",
        "title_offset_x": 0,
        "title_offset_y": 0,
        "title_delay_seconds": 0.0,
        "title_animation_type": "none",
        "message_offset_x": 0,
        "message_offset_y": 0,
        "message_delay_seconds": 0.0,
        "message_animation_type": "none",
        "title_alignment": "left",
        "message_alignment": "left",
        "animation_type": "none",
        "exit_animation_type": "none",
        "celebration_type": "confetti",
        "duration_seconds": 0.0,
        "custom_script_typescript": "string",
        "custom_script_javascript": "string",
        "custom_css": "string",
        "id": "string",
        "name": "string",
        "enabled": false,
        "volume": 0.0,
        "theme_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
        "queue_delay_seconds": 0.0,
        "filter_currency": "string",
        "rules": [
          {
            "id": "string",
            "name": "string",
            "activity_type": "sub",
            "enabled": false,
            "variants": [
              {
                "text_color": "string",
                "viewer_color": "string",
                "count_color": "string",
                "count_name_color": "string",
                "max_width": 0,
                "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
                "font_size": 0,
                "media_position": "above",
                "title_offset_x": 0,
                "title_offset_y": 0,
                "title_delay_seconds": 0.0,
                "title_animation_type": "none",
                "message_offset_x": 0,
                "message_offset_y": 0,
                "message_delay_seconds": 0.0,
                "message_animation_type": "none",
                "title_alignment": "left",
                "message_alignment": "left",
                "animation_type": "none",
                "exit_animation_type": "none",
                "celebration_type": "confetti",
                "duration_seconds": 0.0,
                "custom_script_typescript": "string",
                "custom_script_javascript": "string",
                "custom_css": "string",
                "id": "string",
                "name": "string",
                "enabled": false,
                "weight": 0,
                "filter": {
                  "min_count": 0.0,
                  "max_count": 0.0,
                  "sub_types": [
                    "string"
                  ],
                  "message_keywords": [
                    "string"
                  ]
                },
                "theme_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
                "variant_pack_ids": [
                  "string"
                ],
                "media_pack_ids": [
                  "string"
                ],
                "sound_pack_ids": [
                  "string"
                ],
                "tts_pack_ids": [
                  "string"
                ],
                "title_template": "string",
                "message_template": "string",
                "media": [
                  {
                    "name": "string",
                    "enabled": false,
                    "url": "string",
                    "weight": 0,
                    "filter": {
                      "min_count": 0.0,
                      "max_count": 0.0,
                      "sub_types": [
                        "string"
                      ],
                      "message_keywords": [
                        "string"
                      ]
                    },
                    "volume": 0.0,
                    "max_duration_seconds": 0.0,
                    "type": "image",
                    "sound_url": "string"
                  }
                ],
                "sounds": [
                  {
                    "name": "string",
                    "enabled": false,
                    "url": "string",
                    "weight": 0,
                    "filter": {
                      "min_count": 0.0,
                      "max_count": 0.0,
                      "sub_types": [
                        "string"
                      ],
                      "message_keywords": [
                        "string"
                      ]
                    },
                    "volume": 0.0,
                    "max_duration_seconds": 0.0
                  }
                ],
                "tts": [
                  {
                    "name": "string",
                    "enabled": false,
                    "channel_provider_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
                    "provider": "twitch",
                    "voice_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
                    "voice_trigger": "string",
                    "provider_settings": {},
                    "weight": 0,
                    "filter": {
                      "min_count": 0.0,
                      "max_count": 0.0,
                      "sub_types": [
                        "string"
                      ],
                      "message_keywords": [
                        "string"
                      ]
                    },
                    "volume": 0.0,
                    "delay_seconds": 0.0,
                    "max_duration_seconds": 0.0,
                    "read_title": false,
                    "read_message": false
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `uuid` | **Yes** |  |
| `channel_id` | `uuid` | **Yes** |  |
| `type` | `activity_alert_widget` | No |  |
| `name` | `string` | **Yes** |  |
| `created_at` | `date-time` | **Yes** |  |
| `updated_at` | `date-time` | **Yes** |  |
| `last_used_at` | `date-time`<br>`null` | No |  |
| `settings` | `ActivityAlertWidgetSettings` | No |  |

##### `GoalWidget`
```json
{
  "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "type": "goal_widget",
  "name": "string",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z",
  "last_used_at": "2026-01-01T12:00:00Z",
  "settings": {
    "canvas_scale": 0.0,
    "enabled": false,
    "title": "string",
    "display_mode": "points",
    "points_label": "string",
    "currency": "string",
    "base_value": 0.0,
    "goal_value": 0.0,
    "activity_period": "custom",
    "start_at": "2026-01-01T12:00:00Z",
    "end_at": "2026-01-01T12:00:00Z",
    "activity_checkpoint_at": "2026-01-01T12:00:00Z",
    "activity_checkpoint_value": 0.0,
    "goals": [
      {
        "id": "string",
        "title": "string",
        "goal_value": 0.0,
        "image_url": "string"
      }
    ],
    "show_end_date": false,
    "show_title": false,
    "show_current_value": false,
    "show_goal_value": false,
    "theme_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "themes": [
      {
        "id": "string",
        "name": "string",
        "title_color": "string",
        "secondary_text_color": "string",
        "background_color": "string",
        "border_color": "string",
        "progress_track_color": "string",
        "progress_fill_color": "string",
        "goal_amount_color": "string",
        "completed_fill_color": "string",
        "border_width": 0,
        "border_radius": 0,
        "bar_height": 0,
        "padding": 0,
        "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
        "font_size": 0,
        "min_width": 0,
        "max_width": 0,
        "custom_css": "string"
      }
    ],
    "title_color": "string",
    "secondary_text_color": "string",
    "background_color": "string",
    "border_color": "string",
    "progress_track_color": "string",
    "progress_fill_color": "string",
    "goal_amount_color": "string",
    "completed_fill_color": "string",
    "border_width": 0,
    "border_radius": 0,
    "bar_height": 0,
    "padding": 0,
    "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "font_size": 0,
    "min_width": 0,
    "max_width": 0,
    "custom_css": "string",
    "value_per_unit": 0.0,
    "activity_sources": [
      {
        "provider": "twitch",
        "activity_type": "sub",
        "enabled": false,
        "default_multiplier": 0.0,
        "sub_type_multipliers": {}
      }
    ]
  }
}
```
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `uuid` | **Yes** |  |
| `channel_id` | `uuid` | **Yes** |  |
| `type` | `goal_widget` | No |  |
| `name` | `string` | **Yes** |  |
| `created_at` | `date-time` | **Yes** |  |
| `updated_at` | `date-time` | **Yes** |  |
| `last_used_at` | `date-time`<br>`null` | No |  |
| `settings` | `GoalWidgetSettings` | No |  |

##### `GiveawayWidget`
```json
{
  "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "type": "giveaway_widget",
  "name": "string",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z",
  "last_used_at": "2026-01-01T12:00:00Z",
  "settings": {
    "enabled": false,
    "mode": "latest",
    "giveaway_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "title": "string",
    "image_url": "string",
    "show_trigger": false,
    "trigger_label": "string",
    "show_count": false,
    "show_recent": false,
    "recent_count": 0,
    "show_countdown": false,
    "entry_animation_type": "none",
    "exit_animation_type": "none",
    "canvas_scale": 0.0,
    "theme_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "themes": [
      {
        "id": "string",
        "name": "string",
        "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
        "font_size": 0,
        "text_color": "string",
        "muted_color": "string",
        "accent_color": "string",
        "background_color": "string",
        "border_color": "string",
        "border_width": 0,
        "border_radius": 0,
        "padding": 0,
        "min_width": 0,
        "max_width": 0,
        "custom_css": "string"
      }
    ],
    "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "font_size": 0,
    "text_color": "string",
    "muted_color": "string",
    "accent_color": "string",
    "background_color": "string",
    "border_color": "string",
    "border_width": 0,
    "border_radius": 0,
    "padding": 0,
    "min_width": 0,
    "max_width": 0,
    "custom_css": "string"
  }
}
```
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `uuid` | **Yes** |  |
| `channel_id` | `uuid` | **Yes** |  |
| `type` | `giveaway_widget` | No |  |
| `name` | `string` | **Yes** |  |
| `created_at` | `date-time` | **Yes** |  |
| `updated_at` | `date-time` | **Yes** |  |
| `last_used_at` | `date-time`<br>`null` | No |  |
| `settings` | `GiveawayWidgetSettings` | No |  |

##### `LeaderboardWidget`
```json
{
  "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "type": "leaderboard_widget",
  "name": "string",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z",
  "last_used_at": "2026-01-01T12:00:00Z",
  "settings": {
    "canvas_scale": 0.0,
    "enabled": false,
    "title": "string",
    "display_mode": "points",
    "points_label": "string",
    "currency": "string",
    "activity_period": "custom",
    "start_at": "2026-01-01T12:00:00Z",
    "end_at": "2026-01-01T12:00:00Z",
    "places": 0,
    "sort_direction": "desc",
    "show_title": false,
    "show_end_date": false,
    "show_rank": false,
    "show_value": false,
    "show_empty_places": false,
    "theme_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "themes": [
      {
        "id": "string",
        "name": "string",
        "title_color": "string",
        "text_color": "string",
        "secondary_text_color": "string",
        "value_color": "string",
        "background_color": "string",
        "row_background_color": "string",
        "border_color": "string",
        "border_width": 0,
        "border_radius": 0,
        "row_gap": 0,
        "padding": 0,
        "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
        "font_size": 0,
        "min_width": 0,
        "max_width": 0,
        "custom_css": "string"
      }
    ],
    "title_color": "string",
    "text_color": "string",
    "secondary_text_color": "string",
    "value_color": "string",
    "background_color": "string",
    "row_background_color": "string",
    "border_color": "string",
    "border_width": 0,
    "border_radius": 0,
    "row_gap": 0,
    "padding": 0,
    "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "font_size": 0,
    "min_width": 0,
    "max_width": 0,
    "custom_css": "string",
    "value_per_unit": 0.0,
    "activity_sources": [
      {
        "provider": "twitch",
        "activity_type": "sub",
        "enabled": false,
        "default_multiplier": 0.0,
        "sub_type_multipliers": {}
      }
    ]
  }
}
```
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `uuid` | **Yes** |  |
| `channel_id` | `uuid` | **Yes** |  |
| `type` | `leaderboard_widget` | No |  |
| `name` | `string` | **Yes** |  |
| `created_at` | `date-time` | **Yes** |  |
| `updated_at` | `date-time` | **Yes** |  |
| `last_used_at` | `date-time`<br>`null` | No |  |
| `settings` | `LeaderboardWidgetSettings` | No |  |

##### `StreamathonWidget`
```json
{
  "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "type": "streamathon_widget",
  "name": "string",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z",
  "last_used_at": "2026-01-01T12:00:00Z",
  "settings": {
    "canvas_scale": 0.0,
    "enabled": false,
    "title": "string",
    "currency": "string",
    "seconds_per_unit": 0.0,
    "status": "idle",
    "start_seconds": 0.0,
    "manual_adjust_seconds": 0.0,
    "started_at": "2026-01-01T12:00:00Z",
    "end_at": "2026-01-01T12:00:00Z",
    "activity_checkpoint_at": "2026-01-01T12:00:00Z",
    "activity_checkpoint_remaining_seconds": 0.0,
    "pause_started_at": "2026-01-01T12:00:00Z",
    "pause_periods": [
      {
        "started_at": "2026-01-01T12:00:00Z",
        "ended_at": "2026-01-01T12:00:00Z"
      }
    ],
    "show_title": false,
    "show_status": false,
    "show_recent_events": false,
    "theme_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "themes": [
      {
        "id": "string",
        "name": "string",
        "text_color": "string",
        "background_color": "string",
        "border_color": "string",
        "time_left_color": "string",
        "warning_timer_color": "string",
        "ended_timer_color": "string",
        "border_width": 0,
        "border_radius": 0,
        "padding": 0,
        "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
        "font_size": 0,
        "min_width": 0,
        "max_width": 0,
        "custom_css": "string"
      }
    ],
    "text_color": "string",
    "background_color": "string",
    "border_color": "string",
    "time_left_color": "string",
    "warning_timer_color": "string",
    "ended_timer_color": "string",
    "border_width": 0,
    "border_radius": 0,
    "padding": 0,
    "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "font_size": 0,
    "min_width": 0,
    "max_width": 0,
    "custom_css": "string",
    "activity_sources": [
      {
        "provider": "twitch",
        "activity_type": "sub",
        "enabled": false,
        "default_multiplier": 0.0,
        "sub_type_multipliers": {}
      }
    ]
  }
}
```
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `uuid` | **Yes** |  |
| `channel_id` | `uuid` | **Yes** |  |
| `type` | `streamathon_widget` | No |  |
| `name` | `string` | **Yes** |  |
| `created_at` | `date-time` | **Yes** |  |
| `updated_at` | `date-time` | **Yes** |  |
| `last_used_at` | `date-time`<br>`null` | No |  |
| `settings` | `StreamathonWidgetSettings` | No |  |

##### `VersusWidget`
```json
{
  "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "type": "versus_widget",
  "name": "string",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z",
  "last_used_at": "2026-01-01T12:00:00Z",
  "settings": {
    "canvas_scale": 0.0,
    "enabled": false,
    "title": "string",
    "display_mode": "points",
    "points_label": "string",
    "currency": "string",
    "activity_period": "custom",
    "start_at": "2026-01-01T12:00:00Z",
    "end_at": "2026-01-01T12:00:00Z",
    "activity_checkpoint_at": "2026-01-01T12:00:00Z",
    "activity_checkpoint_option_values": {},
    "show_countdown": false,
    "ended_text": "string",
    "show_lead_amount": false,
    "show_title": false,
    "show_option_titles": false,
    "show_values": false,
    "theme_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "themes": [
      {
        "id": "string",
        "name": "string",
        "title_color": "string",
        "text_color": "string",
        "value_color": "string",
        "secondary_text_color": "string",
        "background_color": "string",
        "border_color": "string",
        "border_width": 0,
        "border_radius": 0,
        "bar_height": 0,
        "image_size": 0,
        "padding": 0,
        "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
        "font_size": 0,
        "min_width": 0,
        "max_width": 0,
        "custom_css": "string"
      }
    ],
    "title_color": "string",
    "text_color": "string",
    "value_color": "string",
    "secondary_text_color": "string",
    "background_color": "string",
    "border_color": "string",
    "border_width": 0,
    "border_radius": 0,
    "bar_height": 0,
    "image_size": 0,
    "padding": 0,
    "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "font_size": 0,
    "min_width": 0,
    "max_width": 0,
    "custom_css": "string",
    "value_per_unit": 0.0,
    "options": [
      {
        "id": "string",
        "title": "string",
        "keywords": [
          "string"
        ],
        "color": "string",
        "image_url": "string",
        "base_value": 0.0
      }
    ],
    "activity_sources": [
      {
        "provider": "twitch",
        "activity_type": "sub",
        "enabled": false,
        "default_multiplier": 0.0,
        "sub_type_multipliers": {}
      }
    ]
  }
}
```
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `uuid` | **Yes** |  |
| `channel_id` | `uuid` | **Yes** |  |
| `type` | `versus_widget` | No |  |
| `name` | `string` | **Yes** |  |
| `created_at` | `date-time` | **Yes** |  |
| `updated_at` | `date-time` | **Yes** |  |
| `last_used_at` | `date-time`<br>`null` | No |  |
| `settings` | `VersusWidgetSettings` | No |  |

##### `ViewerCountWidget`
```json
{
  "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "type": "viewer_count_widget",
  "name": "string",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z",
  "last_used_at": "2026-01-01T12:00:00Z",
  "settings": {
    "canvas_scale": 0.0,
    "enabled": false,
    "providers": [
      "all"
    ],
    "theme_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "themes": [
      {
        "id": "string",
        "name": "string",
        "text_color": "string",
        "background_color": "string",
        "border_color": "string",
        "border_width": 0,
        "border_radius": 0,
        "padding": 0,
        "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
        "font_size": 0,
        "min_width": 0,
        "max_width": 0,
        "custom_css": "string"
      }
    ],
    "text_color": "string",
    "background_color": "string",
    "border_color": "string",
    "border_width": 0,
    "border_radius": 0,
    "padding": 0,
    "font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "font_size": 0,
    "min_width": 0,
    "max_width": 0,
    "custom_css": "string"
  }
}
```
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `uuid` | **Yes** |  |
| `channel_id` | `uuid` | **Yes** |  |
| `type` | `viewer_count_widget` | No |  |
| `name` | `string` | **Yes** |  |
| `created_at` | `date-time` | **Yes** |  |
| `updated_at` | `date-time` | **Yes** |  |
| `last_used_at` | `date-time`<br>`null` | No |  |
| `settings` | `ViewerCountWidgetSettings` | No |  |

##### `ValueWidget`
```json
{
  "id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
  "type": "value_widget",
  "name": "string",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z",
  "last_used_at": "2026-01-01T12:00:00Z",
  "settings": {
    "canvas_scale": 0.0,
    "enabled": false,
    "image_url": "string",
    "key": "string",
    "label": "string",
    "show_label": false,
    "fallback_value": "string",
    "format_numbers": false,
    "theme_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "themes": [
      {
        "id": "string",
        "name": "string",
        "label_color": "string",
        "value_color": "string",
        "background_color": "string",
        "border_color": "string",
        "border_width": 0,
        "border_radius": 0,
        "padding": 0,
        "gap": 0,
        "layout": "inline",
        "label_font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
        "value_font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
        "label_font_size": 0,
        "value_font_size": 0,
        "min_width": 0,
        "max_width": 0,
        "custom_css": "string"
      }
    ],
    "label_color": "string",
    "value_color": "string",
    "background_color": "string",
    "border_color": "string",
    "border_width": 0,
    "border_radius": 0,
    "padding": 0,
    "gap": 0,
    "label_font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "value_font_family_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "label_font_size": 0,
    "value_font_size": 0,
    "min_width": 0,
    "max_width": 0,
    "custom_css": "string"
  }
}
```
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `uuid` | **Yes** |  |
| `channel_id` | `uuid` | **Yes** |  |
| `type` | `value_widget` | No |  |
| `name` | `string` | **Yes** |  |
| `created_at` | `date-time` | **Yes** |  |
| `updated_at` | `date-time` | **Yes** |  |
| `last_used_at` | `date-time`<br>`null` | No |  |
| `settings` | `ValueWidgetSettings` | No |  |

---

## `widget_value`

Widget value events.

### Subscribe
```json
{
  "command": "subscribe",
  "type": "widget_value",
  "data": {
    "widget_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "channel_id": "0197465f-c40d-7db8-ad11-dc44b153a32d",
    "key": "string"
  },
  "nonce": "optional-nonce"
}
```
#### Subscribe Data
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `widget_id` | `uuid` | **Yes** |  |
| `channel_id` | `uuid` | **Yes** |  |
| `key` | `string` | **Yes** |  |

### Event
```json
{
  "type": "widget_value",
  "action": "new",
  "data": {
    "key": "string",
    "value": {},
    "expires_at": "2026-01-01T12:00:00Z",
    "revision": 0
  }
}
```
#### Event Envelope
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | `string` | **Yes** |  |
| `action` | `new`<br>`updated`<br>`deleted` | **Yes** |  |
| `data` | `KvEventData` | **Yes** |  |
| `nonce` | `string`<br>`null` | No |  |

---
