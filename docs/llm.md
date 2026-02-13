# LLM Configuration Guide

The system includes an optional LLM fallback for handling complex or unusual natural language commands. It is **completely optional**—the rule-based NLP works 100% offline by default.

---

## When LLM Is Used

The LLM fallback is only invoked when:

1. The **rule-based engine cannot classify the intent** (returns `null`)
2. **LLM is configured and enabled** (see below)

Once the LLM successfully parses a command, it returns structured intent + entities. If the LLM is not configured or fails, the system returns an error to the user.

---

## Supported LLM Providers

This project supports only the following LLM providers via `LLM_PROVIDER` in your `.env` file:

- **azure** — Azure OpenAI (recommended for enterprise/data residency)
- **github** — GitHub Models (inference via GitHub infrastructure)

Leave `LLM_PROVIDER` empty to run rule-based NLP only (no external LLM).

---

## Provider Setup

### Azure OpenAI (recommended)

For enterprise or private deployments use Azure's OpenAI service.

#### Environment Variables

```bash
LLM_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_API_KEY=<your-key>    # optional when using DefaultAzureCredential
LLM_TIMEOUT=10
```

#### Setup Steps

1. Create an Azure OpenAI resource and deploy a model (deployment name required).
2. Provide credentials either via `AZURE_OPENAI_API_KEY` or configure `azure-identity`/managed identity so `DefaultAzureCredential` works in the container.
3. Set `LLM_PROVIDER=azure` and the AZURE_* variables in `.env` or your environment.
4. Restart the service:
```bash
docker compose up --build
```

See the code path in `backend/app/nlp/llm_client.py`: `_build_azure_client` prefers `DefaultAzureCredential` and falls back to API key auth if `azure-identity` is not installed.

---


### GitHub Models

A cost-friendly option using GitHub's inference endpoints.

#### Environment Variables

```bash
LLM_PROVIDER=github
GITHUB_TOKEN=ghp_...                # Your GitHub personal access token
GITHUB_MODEL=openai/gpt-4o          # Model identifier
LLM_TIMEOUT=10
```

#### Setup Steps

1. Create a GitHub personal access token (no special scopes required for inference).
2. Set `LLM_PROVIDER=github` and provide `GITHUB_TOKEN` and (optionally) `GITHUB_MODEL` in `.env`.
3. Restart the service.

---

## Checking If LLM Is Enabled

The backend will log which LLM client is used on startup. Example log lines:

```bash
# If Azure configured
INFO: LLM client: Azure OpenAI, deployment=<your-deployment>

# If GitHub configured
INFO: LLM client: GitHub Models, model=<your-model>

# If disabled
INFO: LLM is disabled; rule-based NLP only
```

You can also check at runtime:

```bash
curl http://localhost:8080/healthz | jq .
```

The health response won't explicitly show LLM status, but logs will.

## LLM Fallback Behavior

### Flow

```
User sends command → Rule engine tries to classify
                      ├─ Match found → Use rule-based result
                      └─ No match → Try LLM fallback
                                    ├─ LLM enabled & success → Use LLM result
                                    └─ LLM disabled or fails → Return error
```

### Example: Complex Add User

**Command:** `"My mother-in-law is coming to stay for the weekend, make sure she can arm and disarm our system using passcode 1234"`

**Without LLM:**
1. Rule engine does **not** find an explicit `add_user` pattern
2. But heuristic detects PIN + passcode keyword
3. Classifies as `add_user` ✅ (heuristic catches it)

**If heuristic failed (hypothetically):**
1. Rule engine returns `null`
2. LLM fallback tries to parse
3. LLM understands context + "make sure she can..." = add_user intent
4. Extracts PIN, infers name, sets permissions
5. Returns structured result ✅

docker compose up --build

### Response Format

When **LLM is used**, the response includes structured parse result and source metadata. Example:

```json
{
  "ok": true,
  "parsed": {
    "intent": "add_user",
    "source": "llm",     
    "entities": { ... },
    "api": { ... }
  },
  "api_result": { ... },
  "error": null
}
```

---

## Tuning & Optimization

### Request Timeout

Adjust `LLM_TIMEOUT` if you experience timeouts:

```bash
# For low-latency cloud providers
LLM_TIMEOUT=10

# For slower networks or heavier models
LLM_TIMEOUT=30

# For unreliable networks or very large models
LLM_TIMEOUT=60
```

### Model Selection

Prefer the smallest model that reliably parses your commands. For Azure use your deployed model name (e.g. `gpt-4o-mini`); for GitHub choose an appropriate hosted model. Smaller models are cheaper and faster; larger models increase accuracy but add latency and cost.

### Disable LLM Temporarily

To test rule-based only, unset `LLM_PROVIDER` or leave it empty in `.env` and restart:

```bash
# remove or unset LLM_PROVIDER in .env
docker compose up --build
```

System will work 100% offline (only rule-based).

---

## Troubleshooting

### "LLM fallback failed"

**Symptoms:**
```
WARNING: LLM fallback failed: ...
```

**Causes & solutions:**

| Issue | Check |
|-------|-------|
| Invalid API key | Verify your provider-specific key (Azure: `AZURE_OPENAI_API_KEY`, GitHub: `GITHUB_TOKEN`) |
| Network unreachable | Test connectivity to your provider endpoint (Azure endpoint or GitHub models endpoint) |
| Rate limited | Provider returned 429 — check quota/usage limits |
| Timeout | Increase `LLM_TIMEOUT` (e.g., `LLM_TIMEOUT=30`) |
| Azure endpoint wrong | Verify format: `https://<resource>.openai.azure.com` (no trailing slash) |
| GitHub token invalid | Check token at https://github.com/settings/tokens |

### "LLM enabled but not being used"

**Symptoms:**
- Commands fail with `error: "Could not understand command"`
- Logs show `source: "rule"` but you expected `source: "llm"`

**Causes:**
1. Rule engine is succeeding → LLM is never invoked
   - This is expected! LLM only used when rule fails
2. LLM is disabled
   - Check logs: `LLM is disabled; rule-based NLP only`
   - Verify `LLM_PROVIDER` and credentials are set

**To test LLM:**
- Use a command the rule engine doesn't handle
- Check logs for `source: "rule"` vs `source: "llm"`

### Low quality LLM results

**Symptoms:**
- LLM returns wrong intent or missing entities

**Solutions:**
1. Use a better model (gpt-4 > gpt-4o-mini)
2. Rephrase command to be more explicit
3. Check system prompt in `backend/app/nlp/llm_fallback.py`
4. File an issue with the problematic command
