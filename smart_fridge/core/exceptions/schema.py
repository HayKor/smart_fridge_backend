from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ErrorSchema(BaseModel):
    detail: str | None = Field(
        description="Optional exception detail. Public and can be showed to the user.",
        examples=["Record 1 not found."],
    )
    error_code: str = Field(description="Exception name.", examples=["RecordNotFoundException"])
    event_id: str | UUID = Field(
        description="Exception event UUID. Can be used to track exceptions. "
        "Can be provided to support team to request for more details. "
        "If it equals zero, then exception is not tracked.",
    )
    additional_info: dict[str, Any] = Field(
        description="Additional computer-readable information.", examples=[{"record_id": 1}]
    )
