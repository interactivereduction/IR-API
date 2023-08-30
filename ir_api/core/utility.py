"""Collection of utility functions"""
import functools
from typing import Callable, Any, TypeVar, cast

from ir_api.core.exceptions import UnsafePathError

FuncT = TypeVar("FuncT", bound=Callable[[str], Any])


def forbid_path_characters(func: FuncT) -> FuncT:
    """Decorator that prevents path characters {/, ., \\} from a functions args by raising UnsafePathError"""

    @functools.wraps(func)
    def wrapper(arg: str) -> Any:
        if any(char in arg for char in (".", "/", "\\")):
            raise UnsafePathError(f"Potentially unsafe path was requested: {arg}")
        return func(arg)

    return cast(FuncT, wrapper)
