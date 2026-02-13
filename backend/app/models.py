from typing import Literal, Optional

from pydantic import BaseModel, field_validator


class NLExecuteRequest(BaseModel):
    text: str


class ArmRequest(BaseModel):
    mode: Literal["away", "home", "stay"] = "away"


class AddUserRequest(BaseModel):
    name: str
    pin: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    permissions: Optional[list[Literal["arm", "disarm"]]] = None

    @field_validator("pin")
    @classmethod
    def pin_must_be_digits(cls, v: str) -> str:
        if not v.isdigit() or not (4 <= len(v) <= 6):
            raise ValueError("PIN must be 4-6 digits")
        return v

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be empty")
        return v


class RemoveUserRequest(BaseModel):
    name: Optional[str] = None
    pin: Optional[str] = None
