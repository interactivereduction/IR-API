"""
responses module contains api response definitions
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ScriptResponse(BaseModel):
    """
    ScriptResponse returns from the API a script value
    """

    value: str


class PreScriptResponse(BaseModel):
    """
    PreScript response returns from the API a PreScript
    """

    value: str
    is_latest: bool
    sha: Optional[str] = None
