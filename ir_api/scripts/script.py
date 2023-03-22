"""
Module containing the Script and ScriptResponse classes
"""


from pydantic import BaseModel


class ScriptResponse(BaseModel):
    """
    ScriptResponse is the model returned by the script api resource
    """

    value: str
    is_latest: bool


class Script:
    """
    Script is the domain model representing a reduction script, tracking both the original value and if the script is
    the latest version.
    """

    def __init__(self, value: str, is_latest: bool = False):
        self.value = value
        self._original_value = value
        self.is_latest = is_latest

    @property
    def original_value(self) -> str:
        """
        Read only original_value is the value before any transforms are applied.
        :return: str - original value  pre transforms
        """
        return self._original_value

    def to_response(self) -> ScriptResponse:
        """
        Return a ScriptResponse model to be returned by the api
        :return: ScriptResponse - the ScriptResponse
        """
        return ScriptResponse(value=self.value, is_latest=self.is_latest)
