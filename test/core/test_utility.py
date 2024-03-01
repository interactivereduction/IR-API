"""
Tests for utility functions
"""

import pytest

from ir_api.core.exceptions import UnsafePathError
from ir_api.core.utility import forbid_path_characters


def dummy_string_arg_function(arg: str) -> str:
    """Dummy function for testing"""
    return arg


def test_forbid_path_characters_with_dot_raises():
    """
    Test raises when string contains dot
    :return: None
    """
    with pytest.raises(UnsafePathError):
        forbid_path_characters(dummy_string_arg_function)("foo.")


def test_forbid_path_characters_with_fslash_raises():
    """
    Test raises when string contains forward slash
    :return: None
    """
    with pytest.raises(UnsafePathError):
        forbid_path_characters(dummy_string_arg_function)("foo/bar")


def test_forbid_path_characters_with_bslash_raises():
    """
    Test raises when string contains back slash
    :return:
    """
    with pytest.raises(UnsafePathError):
        forbid_path_characters(dummy_string_arg_function)("foo/\\bar\\baz")


def test_no_raise_when_no_bad_characters():
    """
    Test no raise when no bad characters
    :return:
    """
    assert forbid_path_characters(dummy_string_arg_function)("hello") == "hello"
