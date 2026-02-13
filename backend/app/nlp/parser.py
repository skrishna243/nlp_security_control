import logging
from typing import Any, Optional

from app.nlp.entity_extractor import (
    extract_mode,
    extract_name,
    extract_permissions,
    extract_pin,
    extract_time_range,
)
from app.nlp.llm_fallback import llm_parse
from app.nlp.rule_engine import classify_intent
from app.store import store

logger = logging.getLogger(__name__)


def _build_api_call(intent: str, entities: dict[str, Any]) -> Optional[dict[str, Any]]:
    if intent == "arm":
        return {
            "method": "POST",
            "path": "/api/arm-system",
            "payload": {"mode": entities.get("mode", "away")},
        }
    if intent == "disarm":
        return {"method": "POST", "path": "/api/disarm-system", "payload": {}}
    if intent == "add_user":
        return {
            "method": "POST",
            "path": "/api/add-user",
            "payload": {
                "name": entities.get("name") or "unknown",
                "pin": entities.get("pin"),
                "start_time": entities.get("start_time"),
                "end_time": entities.get("end_time"),
                "permissions": entities.get("permissions", ["arm", "disarm"]),
            },
        }
    if intent == "remove_user":
        payload: dict[str, Any] = {}
        if entities.get("name"):
            payload["name"] = entities["name"]
        if entities.get("pin"):
            payload["pin"] = entities["pin"]
        return {"method": "POST", "path": "/api/remove-user", "payload": payload}
    if intent == "list_users":
        return {"method": "GET", "path": "/api/list-users", "payload": None}
    return None


def parse_command(text: str) -> dict[str, Any]:
    source = "rule"
    intent = classify_intent(text)
    entities: dict[str, Any] = {}

    if intent is None:
        # Attempt LLM fallback
        llm_result = llm_parse(text)
        if llm_result and llm_result.get("intent"):
            intent = llm_result["intent"]
            raw_entities = llm_result.get("entities") or {}
            # Flatten LLM entities, filter None values
            entities = {k: v for k, v in raw_entities.items() if v is not None}
            source = "llm"
            logger.info("LLM fallback used", extra={"intent": intent, "source": source})
    else:
        # Rule-based entity extraction
        entities["name"] = extract_name(text)
        entities["pin"] = extract_pin(text)
        if intent == "arm":
            entities["mode"] = extract_mode(text)
        start, end = extract_time_range(text)
        if start:
            entities["start_time"] = start
        if end:
            entities["end_time"] = end
        if intent in ("add_user", "remove_user"):
            entities["permissions"] = extract_permissions(text)
        # Remove None values
        entities = {k: v for k, v in entities.items() if v is not None}

    # Log with masked PIN
    log_extra: dict[str, Any] = {"intent": intent, "source": source}
    if "pin" in entities:
        log_extra["masked_pin"] = store.mask_pin(entities["pin"])
    logger.info("Command parsed", extra=log_extra)

    api_call = _build_api_call(intent, entities) if intent else None

    return {
        "text": text,
        "intent": intent,
        "entities": entities,
        "api": api_call,
        "source": source,
    }
