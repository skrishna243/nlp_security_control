import logging

from fastapi import APIRouter, HTTPException

from app.models import AddUserRequest, ArmRequest, RemoveUserRequest
from app.store import store

router = APIRouter(tags=["Security API"])
logger = logging.getLogger(__name__)


@router.post(
    "/arm-system",
    summary="Arm the security system",
    description="Arms the security system in the specified mode. Default mode is 'away'.",
)
def arm_system(req: ArmRequest):
    """
    Arm the security system.

    - **mode**: `away` (default) — full perimeter armed; `home` — interior zones off;
      `stay` — same as home, typically used for overnight stays
    """
    state = store.arm(req.mode)
    return {"ok": True, "state": state}


@router.post(
    "/disarm-system",
    summary="Disarm the security system",
    description="Disarms the security system. No payload required.",
)
def disarm_system():
    """Disarm the security system."""
    state = store.disarm()
    return {"ok": True, "state": state}


@router.post(
    "/add-user",
    summary="Add a user with a PIN",
    description=(
        "Adds a new user to the system with a 4-6 digit PIN. "
        "Optionally set a time window (start/end) and specific permissions. "
        "PINs are stored masked in all responses."
    ),
)
def add_user(req: AddUserRequest):
    """
    Add a user.

    - **name**: User display name
    - **pin**: 4-6 digit numeric PIN (returned masked as `**XX`)
    - **start_time**: Optional ISO 8601 UTC datetime — user active from
    - **end_time**: Optional ISO 8601 UTC datetime — user active until
    - **permissions**: `["arm", "disarm"]` (default — full access), or a subset
    """
    if req.pin is None:
        raise HTTPException(status_code=400, detail="pin is required")
    user = store.add_user(
        name=req.name,
        pin=req.pin,
        start_time=req.start_time,
        end_time=req.end_time,
        permissions=req.permissions,
    )
    return {"ok": True, "user": user}


@router.post(
    "/remove-user",
    summary="Remove a user",
    description="Remove a user by name or PIN. At least one identifier is required.",
)
def remove_user(req: RemoveUserRequest):
    """
    Remove a user.

    - **name**: Look up by name (case-insensitive)
    - **pin**: Look up by PIN (exact match against stored PIN)

    Provide at least one of `name` or `pin`.
    """
    if not req.name and not req.pin:
        raise HTTPException(
            status_code=400, detail="Either name or pin is required"
        )
    user = store.remove_user(name=req.name, pin=req.pin)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True, "removed": user}


@router.get(
    "/list-users",
    summary="List all users",
    description="Returns all users with masked PINs (last 2 digits shown, e.g. `**21`).",
)
def list_users():
    """List all registered users. PINs are masked in the response."""
    users = store.list_users()
    return {"ok": True, "users": users, "count": len(users)}
