"""Collection of utility functions"""
import functools
from typing import Callable, Any

from ir_api.core.exceptions import UnsafePathError


def forbid_path_characters(func: Callable[[str], Any]) -> Callable[[str], Any]:
    """Decorator that prevents path characters {/, ., \\} from a functions args by raising UnsafePathError"""

    @functools.wraps(func)
    def wrapper(arg: str):
        if any(char in arg for char in (".", "/", "\\")):
            raise UnsafePathError(f"Potentially unsafe path was requested: {arg}")
        return func(arg)

    return wrapper
