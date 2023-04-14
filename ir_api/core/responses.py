"""
responses module contains api response definitions
"""
from __future__ import annotations

from pydantic import BaseModel


class ScriptResponse(BaseModel):
    """
    ScriptResponse is the model returned by the script api resource
    """

    value: str
    is_latest: bool
