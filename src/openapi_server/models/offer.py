# coding: utf-8


from __future__ import annotations
import pprint
import json
from pydantic import BaseModel, Field, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self


# ============================================================================
# OFFER RESPONSE MODEL (as generated — KEEP THIS)
# ============================================================================

class Offer(BaseModel):
    """
    Offer
    Represents an allocation offer generated from a match.
    Tracks its delivery and acceptance lifecycle.
    """

    id: Optional[StrictStr] = None
    match_id: StrictStr = Field(alias="matchId")
    recipient_id: Optional[StrictStr] = Field(None, alias="recipientId")
    status: Optional[StrictStr] = None
    created_at: Optional[StrictStr] = Field(None, alias="createdAt")
    updated_at: Optional[StrictStr] = Field(None, alias="updatedAt")

    __properties: ClassVar[List[str]] = [
        "id",
        "matchId",
        "recipientId",
        "status",
        "createdAt",
        "updatedAt",
    ]

    @field_validator("status")
    def status_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value
        allowed = ("pending", "accepted", "declined", "expired")
        if value not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return value

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "protected_namespaces": (),
    }

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of Offer from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return dict using alias; excludes None"""
        return self.model_dump(
            by_alias=True,
            exclude_none=True,
        )

    @classmethod
    def from_dict(cls, obj: Dict) -> Self:
        """Create an instance from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        return cls.model_validate(
            {
                "id": obj.get("id"),
                "matchId": obj.get("matchId"),
                "recipientId": obj.get("recipientId"),
                "status": obj.get("status"),
                "createdAt": obj.get("createdAt"),
                "updatedAt": obj.get("updatedAt"),
            }
        )


# ============================================================================
# OFFER CREATE MODEL (POST /offers)
# ============================================================================

class OfferCreate(BaseModel):
    """
    OfferCreate
    Payload for creating a new offer.
    """

    match_id: StrictStr = Field(alias="matchId")
    recipient_id: StrictStr = Field(alias="recipientId")
    status: Optional[StrictStr] = "pending"

    @field_validator("status")
    def validate_status(cls, value):
        allowed = ("pending", "accepted", "declined", "expired")
        if value and value not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return value

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
    }


# ============================================================================
# OFFER UPDATE MODEL (PUT / PATCH /offers/{id})
# ============================================================================

class OfferUpdate(BaseModel):
    """
    OfferUpdate
    Partial update model for modifying an offer.
    """

    match_id: Optional[StrictStr] = Field(None, alias="matchId")
    recipient_id: Optional[StrictStr] = Field(None, alias="recipientId")
    status: Optional[StrictStr] = None

    @field_validator("status")
    def validate_status(cls, value):
        allowed = ("pending", "accepted", "declined", "expired")
        if value and value not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return value

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
    }
