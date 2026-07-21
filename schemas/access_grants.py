from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


AccessGrantPurpose = Literal[
    "platform_beta",
    "summit_general",
    "summit_investor",
    "partner",
]


class AccessGrantValidateIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=4, max_length=128)
    purpose: AccessGrantPurpose = "platform_beta"


class AccessGrantOut(BaseModel):
    granted: bool = True
    purpose: AccessGrantPurpose
    expires_at: int
    scope: list[str] = Field(default_factory=list)
    # R1.7 compatibility bridge. Returned only when the explicit header
    # transport flag is enabled; clients must keep it in memory only.
    grant_token: Optional[str] = None


class AccessGrantStatusOut(BaseModel):
    granted: bool
    purpose: Optional[str] = None
    expires_at: Optional[int] = None
    scope: list[str] = Field(default_factory=list)
