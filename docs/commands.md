# Supported Commands

All commands are sent to `POST /nl/execute` as `{ "text": "..." }`.

---

## English — Standard

### Arm System

| Command | Mode |
|---------|------|
| `arm the system` | away (default) |
| `please activate the alarm to stay mode` | stay |
| `activate alarm in home mode` | home |
| `lock it down` | away |
| `turn on the alarm` | away |
| `enable the security system` | away |
| `arm it in away mode` | away |
| `start the alarm` | away |

### Disarm System

| Command |
|---------|
| `disarm the system` |
| `turn off the alarm now` |
| `deactivate the alarm` |
| `disable the security` |
| `unlock the system` |
| `shut off the alarm` |


### Add User

| Command | Notes |
|---------|-------|
| `add user John with pin 4321` | Basic user |
| `create a user Bob with passcode 9999` | Synonym |
| `add a temporary user Sarah, pin 5678 from today 5pm to Sunday 10am` | Time-bounded |
| `give John access` | Requires PIN in follow-up (or use with PIN in same sentence) |
| `My mother-in-law is coming to stay for the weekend, make sure she can arm and disarm our system using passcode 1234` | Complex natural language (heuristic or LLM) |

### Remove User

| Command |
|---------|
| `remove user John` |
| `delete user Alice` |
| `revoke user access for Bob` |

### List Users

| Command |
|---------|
| `show me all users` |
| `list all users` |
| `who has access` |
| `show the user list` |

---

## English — Creative Aliases

These fun/tactical phrases are understood out of the box:

| Command | Intent |
|---------|--------|
| `open sesame` | disarm |
| `sesame open` | disarm |
| `sesame close` | arm |
| `close sesame` | arm |
| `all clear` | disarm |
| `stand down` | disarm |
| `at ease` | disarm |
| `code red` | arm |
| `red alert` | arm |
| `go hot` | arm |
| `high alert` | arm |
| `go live` | arm |

---

## Spanish (Español)

| Command | Intent |
|---------|--------|
| `armar el sistema` | arm |
| `activar el sistema` | arm |
| `desarmar el sistema` | disarm |
| `desactivar el sistema` | disarm |
| `mostrar usuarios` | list_users |

---

## French (Français)

| Command | Intent |
|---------|--------|
| `armer le système` | arm |
| `activer le système` | arm |
| `désarmer le système` | disarm |
| `désactiver le système` | disarm |

---

## German (Deutsch)

| Command | Intent |
|---------|--------|
| `Anlage scharf` | arm |
| `scharf schalten` | arm |
| `Anlage unscharf` | disarm |
| `unscharf schalten` | disarm |

---

## Arabic (Romanized)

| Command | Meaning | Intent |
|---------|---------|--------|
| `aghliq` / `aghleq` | close/lock | arm |
| `iftah` / `aftah` | open | disarm |

---

## Hindi (Romanized)

| Command | Meaning | Intent |
|---------|---------|--------|
| `band karo` | lock it / close it | arm |
| `kholo` / `khol do` | open it | disarm |

---

## Japanese (Romanized)

| Command | Meaning | Intent |
|---------|---------|--------|
| `kagi kakete` | lock it | arm |
| `akete` | open/unlock | disarm |

---

## Portuguese (Português)

| Command | Intent |
|---------|--------|
| `armar o sistema` | arm |
| `ativar o sistema` | arm |
| `desarmar o sistema` | disarm |
| `desativar o sistema` | disarm |

---

## Hebrew (Romanized)

| Command | Meaning | Intent |
|---------|---------|--------|
| `pe'al` / `pa'al` | activate | arm |
| `batel` / `battel` | cancel | disarm |

---

## NLP Pipeline

```
Input text
    │
    ▼
Creative aliases check (sesame, multilingual)
    │ match → intent
    ▼
Standard rule engine (regex patterns)
    │ match → intent + entity extraction
    ▼
Heuristic (PIN + passcode keyword present)
    │ match → add_user
    ▼
LLM fallback (if LLM_PROVIDER configured)
    │
    ▼
Intent + entities → API call
```

For commands not listed here that are still security-related, the LLM fallback
(if configured) will attempt to understand them. Enable it by setting `LLM_PROVIDER`
and the appropriate credentials in your `.env` file.
