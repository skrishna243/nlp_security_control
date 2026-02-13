from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SecurityStore:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._system_state: dict[str, Any] = {"armed": False, "mode": "away"}
        self._users_by_name: dict[str, dict[str, Any]] = {}
        self._users_by_pin: dict[str, dict[str, Any]] = {}

    # ---- System state ----

    def arm(self, mode: str = "away") -> dict[str, Any]:
        self._system_state = {"armed": True, "mode": mode}
        logger.info("System armed", extra={"endpoint": "arm-system"})
        return dict(self._system_state)

    def disarm(self) -> dict[str, Any]:
        self._system_state = {"armed": False, "mode": self._system_state["mode"]}
        logger.info("System disarmed", extra={"endpoint": "disarm-system"})
        return dict(self._system_state)

    def get_state(self) -> dict[str, Any]:
        return dict(self._system_state)

    # ---- Users ----

    def add_user(
        self,
        name: str,
        pin: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        permissions: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        if permissions is None:
            permissions = ["arm", "disarm"]
        user: dict[str, Any] = {
            "name": name,
            "pin": pin,
            "start_time": start_time,
            "end_time": end_time,
            "permissions": permissions,
        }
        self._users_by_name[name.lower()] = user
        self._users_by_pin[pin] = user
        logger.info(
            "User added",
            extra={"endpoint": "add-user", "masked_pin": self.mask_pin(pin)},
        )
        return self._public_user(user)

    def remove_user(
        self, name: Optional[str] = None, pin: Optional[str] = None
    ) -> Optional[dict[str, Any]]:
        user: Optional[dict[str, Any]] = None
        if name:
            user = self._users_by_name.get(name.lower())
        elif pin:
            user = self._users_by_pin.get(pin)

        if user is None:
            return None

        self._users_by_name.pop(user["name"].lower(), None)
        self._users_by_pin.pop(user["pin"], None)
        logger.info("User removed", extra={"endpoint": "remove-user"})
        return self._public_user(user)

    def list_users(self) -> list[dict[str, Any]]:
        seen: set[str] = set()
        result: list[dict[str, Any]] = []
        for user in self._users_by_name.values():
            if user["name"] not in seen:
                seen.add(user["name"])
                result.append(self._public_user(user))
        return result

    def get_user_by_name(self, name: str) -> Optional[dict[str, Any]]:
        user = self._users_by_name.get(name.lower())
        return self._public_user(user) if user else None

    # ---- Helpers ----

    @staticmethod
    def mask_pin(pin: str) -> str:
        """Mask all but last 2 digits: '4321' -> '**21'. Short PINs shown as-is."""
        if len(pin) <= 2:
            return pin
        return "*" * (len(pin) - 2) + pin[-2:]

    def _public_user(self, user: dict[str, Any]) -> dict[str, Any]:
        """Return user dict with PIN masked."""
        return {**user, "pin": self.mask_pin(user["pin"])}


# Singleton store instance
store = SecurityStore()
