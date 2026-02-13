# API Reference

> **Interactive docs** (when the service is running):
> - Swagger UI: http://localhost:8080/docs
> - ReDoc: http://localhost:8080/redoc

---

## POST /nl/execute

The main entry point. Accepts a free-text command, runs NLP, and executes the appropriate security action — all in one call.

**Request**
```json
{ "text": "string" }
```

**Response**
```json
{
  "ok": true,
  "parsed": {
    "text": "arm the system",
    "intent": "arm",
    "entities": { "mode": "away" },
    "api": {
      "method": "POST",
      "path": "/api/arm-system",
      "payload": { "mode": "away" }
    },
    "source": "rule"
  },
  "api_result": { "ok": true, "state": { "armed": true, "mode": "away" } },
  "error": null
}
```

| Field | Description |
|-------|-------------|
| `parsed.intent` | Classified intent: `arm`, `disarm`, `add_user`, `remove_user`, `list_users`, or `null` |
| `parsed.source` | `"rule"` — matched by regex engine; `"llm"` — matched by LLM fallback |
| `parsed.entities` | Extracted entities (name, PIN masked, mode, times, permissions) |
| `parsed.api` | The API call that was dispatched |
| `api_result` | The response from the dispatched endpoint |
| `error` | Non-null when something failed (bad command, validation error, etc.) |

**Errors**
- `400` — empty text
- `200 ok:false` — command not understood or downstream API error (error field populated)

---

## POST /api/arm-system

Arm the security system.

**Request**
```json
{ "mode": "away" }
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `mode` | `"away" \| "home" \| "stay"` | No | `"away"` | Away = full perimeter; Home/Stay = interior zones disabled |

**Response**
```json
{ "ok": true, "state": { "armed": true, "mode": "away" } }
```

**Errors** — `422` invalid mode value

---

## POST /api/disarm-system

Disarm the security system.

**Request** — empty body `{}`

**Response**
```json
{ "ok": true, "state": { "armed": false, "mode": "away" } }
```

---

## POST /api/add-user

Add a user with a PIN and optional time window.

**Request**
```json
{
  "name": "Sarah",
  "pin": "5678",
  "start_time": "2025-06-01T17:00:00Z",
  "end_time": "2025-06-03T10:00:00Z",
  "permissions": ["arm", "disarm"]
}
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | Yes | — | User display name |
| `pin` | string | Yes | — | 4–6 digit numeric PIN |
| `start_time` | ISO 8601 UTC | No | `null` | Start of access window |
| `end_time` | ISO 8601 UTC | No | `null` | End of access window |
| `permissions` | `["arm","disarm"]` | No | `["arm","disarm"]` | Allowed operations |

**Response**
```json
{
  "ok": true,
  "user": {
    "name": "Sarah",
    "pin": "**78",
    "start_time": "2025-06-01T17:00:00Z",
    "end_time": "2025-06-03T10:00:00Z",
    "permissions": ["arm", "disarm"]
  }
}
```

> PINs are **always masked** in responses: only the last 2 digits are shown (`**78`).

**Errors** — `422` invalid PIN (not 4-6 digits / non-numeric)

---

## POST /api/remove-user

Remove a user by name or PIN.

**Request**
```json
{ "name": "Sarah" }
```
or
```json
{ "pin": "5678" }
```

**Response**
```json
{ "ok": true, "removed": { "name": "Sarah", "pin": "**78", ... } }
```

**Errors**
- `400` — neither `name` nor `pin` provided
- `404` — user not found

---

## GET /api/list-users

List all registered users. PINs are masked.

**Response**
```json
{
  "ok": true,
  "count": 2,
  "users": [
    { "name": "John", "pin": "**21", "permissions": ["arm", "disarm"], "start_time": null, "end_time": null },
    { "name": "Sarah", "pin": "**78", "permissions": ["arm", "disarm"], "start_time": "...", "end_time": "..." }
  ]
}
```

---

## GET /healthz

Service health check.

**Response**
```json
{
  "ok": true,
  "uptime_seconds": 42.3,
  "system_state": { "armed": false, "mode": "away" }
}
```

---

## Correlation IDs

Every request/response carries a `X-Correlation-ID` header for distributed tracing.

- If you send a `X-Correlation-ID` header, it is echoed back in the response.
- If you don't send one, the backend generates a UUID4 and returns it.

```bash
curl -H "X-Correlation-ID: my-trace-123" localhost:8080/healthz
# Response will include: X-Correlation-ID: my-trace-123
```

---

## Error Response Format

All errors return a consistent JSON body:

```json
{
  "ok": false,
  "error": "error_type",
  "detail": "Human-readable description"
}
```

Validation errors (422) use FastAPI's standard format with a `detail` array.
