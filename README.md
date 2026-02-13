# NL Security Control

A Dockerized natural language security system controller. Type commands in plain English — the system interprets them and executes the appropriate security actions.

**Features:**
- Natural language command processing (arm, disarm, manage users)
- Multi-language support (English, Spanish, French, German, Arabic, Hindi, Japanese, Portuguese)
- Rule-based NLP (works 100% offline by default)
- Optional LLM fallback (Azure, GitHub Models)
- PIN masking in all responses and logs
- Structured JSON logging with correlation IDs
- React + Vite frontend with real-time feedback
- Fully Dockerized with health checks

---

## Quick Start

### Run with Docker

```bash
git clone <your-repo>
cd nlp_security_control
docker compose up --build
```

- **API:** http://localhost:8080
- **UI:** http://localhost:3005
- **API Docs:** http://localhost:8080/docs
- **Health:** http://localhost:8080/healthz

### Quick Test

```bash
# Health check
curl localhost:8080/healthz

# Arm the system
curl -X POST localhost:8080/nl/execute \
  -H "Content-Type: application/json" \
  -d '{"text":"arm the system"}'

# Add a user
curl -X POST localhost:8080/nl/execute \
  -H "Content-Type: application/json" \
  -d '{"text":"add user John with pin 4321"}'

# Open the UI
open http://localhost:3005
```

---

## System Architecture

```
┌─────────────────────────────────┐
│   Frontend                      │
│   React + Vite (nginx :3005)    │
└──────────────┬──────────────────┘
               │
               │ HTTP
               ▼
┌─────────────────────────────────────────────────────────┐
│             FastAPI Backend (:8080)                     │
│                                                         │
│  ┌────────────────────────────────────────┐             │
│  │  Natural Language Processing Pipeline  │             │
│  │                                        │             │
│  │  1. Rule-based Intent Classification  │             │
│  │  2. Entity Extraction (PIN, name, ...) │             │
│  │  3. Heuristic Pattern Matching        │             │
│  │  4. LLM Fallback (optional)           │             │
│  └────────────────────────────────────────┘             │
│                                                         │
│  ┌────────────────────────────────────────┐             │
│  │  Security API Endpoints                │             │
│  │                                        │             │
│  │  POST /nl/execute                     │             │
│  │  POST /api/arm-system                 │             │
│  │  POST /api/disarm-system              │             │
│  │  POST /api/add-user                   │             │
│  │  POST /api/remove-user                │             │
│  │  GET  /api/list-users                 │             │
│  │  GET  /healthz                        │             │
│  └────────────────────────────────────────┘             │
│                                                         │
│  ┌────────────────────────────────────────┐             │
│  │  In-Memory State Store                 │             │
│  │  • System state (armed/disarmed)       │             │
│  │  • User registry (by name + PIN)       │             │
│  └────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

---

## How It Works

### NLP Pipeline

The system uses a **hybrid approach**: rule-based NLP with an optional LLM fallback.

```
User Input
    │
    ▼
[1] Creative Aliases Check
    (sesame, multilingual phrases)
    │ match → intent
    │ no match ▼
[2] Standard Rule Engine
    (regex patterns for common commands)
    │ match → intent + entity extraction
    │ no match ▼
[3] Heuristic Fallback
    (PIN + passcode keyword pattern)
    │ match → add_user intent
    │ no match ▼
[4] LLM Fallback (if configured)
  (Azure, GitHub)
    │
    ▼
Intent + Entities → Build API Call → Execute
```

**Key Design Choices:**
- `add_user` patterns checked before `arm` to prevent "arm and disarm" (permission language) from being misclassified
- All PINs masked in responses (`4321` → `**21`) for security
- System works **100% offline** by default—no LLM needed
- Correlation IDs tracked through entire request lifecycle

### Example Flow

**Input:** `"add a temporary user Sarah, pin 5678 from today 5pm to Sunday 10am"`

**Processing:**
1. Rule engine matches `add_user` pattern
2. Entity extraction:
   - Name: `"Sarah"`
   - PIN: `"5678"`
   - Time range: resolved via dateparser
3. API call built: `POST /api/add-user` with payload
4. User added to store
5. Response includes masked PIN: `"**78"`

---

## Documentation

- **[📖 Commands Reference](docs/commands.md)** — All supported commands in English and 8+ languages
- **[🔌 API Reference](docs/api.md)** — Complete endpoint documentation with request/response examples
- **[🤖 LLM Configuration](docs/llm.md)** — How to enable Azure or GitHub Models

---

## Running Tests

```bash
# Run all tests
docker compose run --rm backend python -m pytest -v
```

**Run specific test suites:**

```bash
# Unit tests (Logic and Rule Engine)
docker compose run --rm backend python -m pytest tests/unit/ -v

# Integration tests (API and Database)
docker compose run --rm backend python -m pytest tests/integration/ -v

# End-to-end tests
docker compose run --rm backend python -m pytest tests/e2e/ -v
```

**Coverage by test type:**
- **Unit tests** — Intent classification, entity extraction, store operations
- **Integration tests** — API endpoints, health checks, request validation
- **E2E tests** — Complete workflows from NL command to state change

---

## Local Development (without Docker)

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server starts on `:3005` and proxies `/nl` and `/api` requests to `http://localhost:8080`.

---

## Optional: LLM Mode

By default, the system uses **rule-based NLP only** (fast, offline, free). To enable LLM fallback for more complex commands:

```bash
cp .env.example .env
# Edit .env and add your LLM provider credentials
docker compose up --build
```

See **[LLM Configuration](docs/llm.md)** for detailed setup instructions for supported providers:
- Azure OpenAI
- GitHub Models

---

## Project Structure

```
nlp_security_control/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app setup
│   │   ├── config.py               # Environment configuration
│   │   ├── models.py               # Pydantic request models
│   │   ├── store.py                # In-memory state store
│   │   ├── middleware.py           # Correlation ID tracking
│   │   ├── logging_config.py       # Structured JSON logging
│   │   ├── routers/
│   │   │   ├── nl.py               # /nl/execute endpoint
│   │   │   ├── api.py              # Security API endpoints
│   │   │   └── health.py           # /healthz endpoint
│   │   └── nlp/
│   │       ├── rule_engine.py      # Intent classification
│   │       ├── entity_extractor.py # Entity extraction
│   │       ├── parser.py           # Main NLP coordinator
│   │       ├── llm_client.py       # Multi-LLM factory
│   │       └── llm_fallback.py     # LLM fallback logic
│   ├── tests/
│   │   ├── unit/                   # Unit test suite
│   │   ├── integration/            # Integration tests
│   │   ├── e2e/                    # End-to-end tests
│   │   └── conftest.py             # Pytest fixtures
│   ├── requirements.txt            # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.tsx                # React entry point
│   │   ├── App.tsx                 # Main component
│   │   ├── api.ts                  # API client
│   │   ├── types.ts                # TypeScript types
│   │   ├── hooks/
│   │   │   └── useCommandHistory.ts# Command history state
│   │   └── components/
│   │       ├── CommandInput.tsx    # Text input form
│   │       ├── CommandHistory.tsx  # Command list
│   │       ├── HistoryEntry.tsx    # Single command display
│   │       └── ExampleCommands.tsx # Quick-select buttons
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── nginx.conf                  # Production server config
│   └── Dockerfile
├── docs/
│   ├── commands.md                 # Supported commands reference
│   ├── api.md                      # API endpoint documentation
│   └── llm.md                      # LLM configuration guide
├── docker-compose.yml              # Multi-container setup
├── .env.example                    # Environment variable template
└── README.md (this file)
```

---

## Security Implementation

### PIN Masking

All PINs are masked in responses and logs:
- `4321` → `**21` (show only last 2 digits)
- Applied at the storage layer (`SecurityStore.mask_pin()`)
- Never exposed in API responses or logs

### Validation

- **PIN format** — 4-6 digits only (enforced by Pydantic validators)
- **User names** — non-empty strings
- **Modes** — `away`, `home`, `stay` only
- **Input sanitization** — whitespace trimmed, case-insensitive matching

### Logging

- All logs are JSON-formatted for automated parsing
- PINs never logged raw—always masked
- Correlation IDs track requests across the system
- Sensitive operations (add user, arm/disarm) logged with intent + masked PIN

---

## Common Commands

See **[Commands Reference](docs/commands.md)** for the complete list. Here are a few examples:

| Command | Intent |
|---------|--------|
| `arm the system` | ARM (away mode) |
| `please activate the alarm to stay mode` | ARM (stay mode) |
| `turn off the alarm now` | DISARM |
| `add user John with pin 4321` | ADD_USER |
| `add a temporary user Sarah, pin 5678 from today 5pm to Sunday 10am` | ADD_USER with time window |
| `remove user John` | REMOVE_USER |
| `show me all users` | LIST_USERS |
| `My mother-in-law is coming to stay for the weekend, make sure she can arm and disarm our system using passcode 1234` | ADD_USER (heuristic) |
| `open sesame` | DISARM (creative alias) |
| `armar el sistema` | ARM (Spanish) |

---

## API Quick Reference

See **[API Reference](docs/api.md)** for full details with examples.

### Main Endpoint: POST /nl/execute

Execute a natural language command in one call—NLP parsing and action execution happen server-side.

**Request:**
```json
{ "text": "arm the system" }
```

**Response:**
```json
{
  "ok": true,
  "parsed": {
    "text": "arm the system",
    "intent": "arm",
    "entities": { "mode": "away" },
    "api": { "method": "POST", "path": "/api/arm-system", "payload": { "mode": "away" } },
    "source": "rule"
  },
  "api_result": { "ok": true, "state": { "armed": true, "mode": "away" } },
  "error": null
}
```

### Direct API Endpoints

- `POST /api/arm-system` — Arm system (away/home/stay mode)
- `POST /api/disarm-system` — Disarm system
- `POST /api/add-user` — Add user with PIN
- `POST /api/remove-user` — Remove user by name or PIN
- `GET /api/list-users` — List all users (PINs masked)
- `GET /healthz` — Service health & uptime

---

## Troubleshooting

### Command not recognized?

1. Check **[Commands Reference](docs/commands.md)** for supported patterns
2. Try rephrasing using one of the example patterns
3. If you have LLM enabled, check logs for LLM fallback attempts (`"source": "llm"`)
4. Enable debug logging: `LOG_LEVEL=DEBUG`

### PIN not extracted?

- PIN must be 4-6 digits
- Keywords: `pin`, `passcode`, `password` help extraction
- Try: `"add user John with pin 4321"` instead of `"add user John 4321"`

### LLM fallback not working?

See **[LLM Configuration](docs/llm.md)** — verify:
- `LLM_PROVIDER` env var is set
- API key/credentials are valid
- `LLM_TIMEOUT` (default 10s) is sufficient
- Network connectivity to LLM endpoint

### Tests failing?

```bash
cd backend
pytest -v --tb=short
```

Check:
- Python version 3.12+ required
- All dependencies installed: `pip install -r requirements.txt`
- No instances running on ports 8080 or 3005
- `pytest` conftest fixtures are loading correctly

---

## Design Decisions

1. **Rule-based NLP first** — predictable, testable, fast, no API costs. LLM as optional fallback.

2. **Ordered intent patterns** — `add_user` checked before `arm` to prevent "arm and disarm" (permission-grant language) from triggering the arm intent.

3. **Heuristic for complex phrasing** — "My mother-in-law... passcode 1234" has no "add user" phrase, but PIN + passcode keyword is a strong signal → classified as `add_user`.

4. **Server-side parsing & execution** — `/nl/execute` does both in one round-trip. Frontend only needs one endpoint.

5. **In-memory store** — Per spec. State resets on container restart. Dual-indexed (by name + PIN) for $ O(1) lookup.

6. **PIN masking everywhere** — PINs never stored raw in logs or responses. `mask_pin("4321")` → `"**21"`.

7. **Correlation IDs** — Every request tracked via `X-Correlation-ID` header for debugging and audit trails.


## License

This is Just a demo Project.
