import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Register extra option to skip pip and virtualenv for speed.
    """
    parser.addoption("--fast", action="store_true")


def pytest_runtest_setup(item: pytest.Item) -> None:
    """
    Optionally exclude tests based on passed in options.

    * exclude tests marked "slow" if "--fast" is passed.
    """
    if "slow" in item.keywords and item.config.getoption("--fast"):
        pytest.skip("Test marked slow and --fast is in effect.")
