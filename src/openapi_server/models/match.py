# src/openapi_server/models/match_model.py

# coding: utf-8
"""
Match model — represents relationship between donor, organ, and recipient.
"""

from __future__ import annotations
import pprint
import json
from pydantic import BaseModel, Field, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self


# ===============================================================
# Main Match Response Model
# ===============================================================
class Match(BaseModel):
    id: Optional[StrictStr] = None
    donor_id: StrictStr = Field(alias="donorId")
    organ_id: StrictStr = Field(alias="organId")
    recipient_id: Optional[StrictStr] = Field(None, alias="recipientId")

    donor_blood_type: Optional[StrictStr] = Field(None, alias="donorBloodType")
    recipient_blood_type: Optional[StrictStr] = Field(None, alias="recipientBloodType")
    organ_type: Optional[StrictStr] = Field(None, alias="organType")
    score: Optional[float] = None
    status: Optional[StrictStr] = None

    __properties: ClassVar[List[str]] = [
        "id",
        "donorId",
        "organId",
        "recipientId",
        "donorBloodType",
        "recipientBloodType",
        "organType",
        "score",
        "status",
    ]

    @field_validator("status")
    def validate_status(cls, value):
        allowed = ("pending", "matched", "accepted", "declined", "expired")
        if value is None:
            return value
        if value not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return value

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "protected_namespaces": (),
    }

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_none=True)

    @classmethod
    def from_dict(cls, obj: Dict) -> Self:
        if obj is None:
            return None

        return cls.model_validate(
            {
                "id": obj.get("id"),
                "donorId": obj.get("donorId"),
                "organId": obj.get("organId"),
                "recipientId": obj.get("recipientId"),
                "donorBloodType": obj.get("donorBloodType"),
                "recipientBloodType": obj.get("recipientBloodType"),
                "organType": obj.get("organType"),
                "score": obj.get("score"),
                "status": obj.get("status"),
            }
        )


# ===============================================================
# MatchCreate — POST /matches
# ===============================================================
class MatchCreate(BaseModel):
    donor_id: StrictStr = Field(alias="donorId")
    organ_id: StrictStr = Field(alias="organId")
    recipient_id: Optional[StrictStr] = Field(None, alias="recipientId")

    donor_blood_type: Optional[StrictStr] = Field(None, alias="donorBloodType")
    recipient_blood_type: Optional[StrictStr] = Field(None, alias="recipientBloodType")
    organ_type: Optional[StrictStr] = Field(None, alias="organType")

    score: Optional[float] = None
    status: Optional[StrictStr] = None

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "protected_namespaces": (),
    }


# ===============================================================
# MatchUpdate — PATCH/PUT /matches/{id}
# ===============================================================
class MatchUpdate(BaseModel):
    donor_id: Optional[StrictStr] = Field(None, alias="donorId")
    organ_id: Optional[StrictStr] = Field(None, alias="organId")
    recipient_id: Optional[StrictStr] = Field(None, alias="recipientId")

    donor_blood_type: Optional[StrictStr] = Field(None, alias="donorBloodType")
    recipient_blood_type: Optional[StrictStr] = Field(None, alias="recipientBloodType")
    organ_type: Optional[StrictStr] = Field(None, alias="organType")

    score: Optional[float] = None
    status: Optional[StrictStr] = None

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "protected_namespaces": (),
    }
