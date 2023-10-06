import pytest

from test.utils import setup_database


@pytest.fixture(scope="session", autouse=True)
def setup():
    """
    Setup database pre-testing
    :return:
    """
    setup_database()
