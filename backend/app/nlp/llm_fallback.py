"""
LLM fallback NLP parser.

Invoked by parser.py when the rule engine cannot classify the intent.
Uses the multi-LLM client factory (llm_client.py) to support Azure OpenAI and
GitHub Models (via the OpenAI-compatible client API).
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """\
You are a security system NLP parser. Given a natural language command, extract
structured intent and entities as JSON. Do not add commentary.

Respond with exactly this JSON schema:
{{
  "intent": "arm" | "disarm" | "add_user" | "remove_user" | "list_users" | null,
  "entities": {{
    "name": "<string or null>",
    "pin": "<4-6 digit string or null>",
    "mode": "away" | "home" | "stay" | null,
    "start_time": "<ISO 8601 UTC datetime or null>",
    "end_time": "<ISO 8601 UTC datetime or null>",
    "permissions": ["arm", "disarm"] | ["arm"] | ["disarm"] | null
  }}
}}

Rules:
- For arm commands, default mode is "away" unless stay/home/away is mentioned.
- PINs are numeric strings of 4-6 digits. Never include spaces.
- Resolve relative time expressions like "today 5pm" or "Sunday 10am" to ISO 8601 UTC.
  Today's date in UTC is: {today_iso}.
- For add_user with no explicit permissions stated, default to ["arm", "disarm"].
- If someone says "she can arm and disarm using passcode 1234", that is add_user intent
  with permissions ["arm", "disarm"] and pin "1234".
"""


def llm_parse(text: str) -> Optional[dict[str, Any]]:
    """
    Parse text using the configured LLM provider.
    Returns parsed intent+entities dict, or None if LLM is unavailable/fails.
    """
    from app.config import settings

    if not settings.llm_enabled():
        return None

    try:
        from app.nlp.llm_client import get_llm_client

        client, model = get_llm_client()
        today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(today_iso=today_iso)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        raw = response.choices[0].message.content
        if not raw:
            return None
        result = json.loads(raw)
        logger.info(
            "LLM parse succeeded",
            extra={"intent": result.get("intent"), "source": settings.LLM_PROVIDER},
        )
        return result

    except Exception as exc:
        logger.warning("LLM fallback failed (%s): %s", settings.LLM_PROVIDER, exc)
        return None
