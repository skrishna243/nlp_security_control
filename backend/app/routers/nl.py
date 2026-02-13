import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from app.models import (
    AddUserRequest,
    ArmRequest,
    NLExecuteRequest,
    RemoveUserRequest,
)
from app.nlp.parser import parse_command
from app.routers.api import (
    add_user,
    arm_system,
    disarm_system,
    list_users,
    remove_user,
)

router = APIRouter(tags=["NL"])
logger = logging.getLogger(__name__)


def _execute_api_call(api_call: dict[str, Any]) -> Any:
    path = api_call["path"]
    payload = api_call.get("payload") or {}

    if path == "/api/arm-system":
        return arm_system(ArmRequest(**payload))
    if path == "/api/disarm-system":
        return disarm_system()
    if path == "/api/add-user":
        return add_user(AddUserRequest(**payload))
    if path == "/api/remove-user":
        return remove_user(RemoveUserRequest(**payload))
    if path == "/api/list-users":
        return list_users()
    return None


@router.post(
    "/nl/execute",
    summary="Execute a natural language command",
    description=(
        "Parse and execute a free-text security command in one step. "
        "The NLP engine classifies the intent, extracts entities, and dispatches "
        "to the appropriate `/api/*` endpoint. "
        "Supports English plus creative aliases (e.g. 'open sesame', Spanish, French, "
        "German, Arabic, Hindi). "
        "Returns the parsed interpretation, the API call made, and the result."
    ),
)
def nl_execute(req: NLExecuteRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text must not be empty")

    parsed = parse_command(req.text)
    api_result = None
    error = None

    api_call = parsed.get("api")
    if api_call:
        try:
            api_result = _execute_api_call(api_call)
        except HTTPException as exc:
            error = exc.detail
            logger.warning("API execution HTTP error: %s", exc.detail)
        except Exception as exc:
            error = str(exc)
            logger.warning("API execution error: %s", exc)
    elif parsed.get("intent") is None:
        error = "Could not understand command. Try rephrasing."

    return {
        "ok": error is None,
        "parsed": parsed,
        "api_result": api_result,
        "error": error,
    }
