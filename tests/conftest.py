import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Register extra option to skip pip and virtualenv for speed.
    """
    parser.addoption("--fast", action="store_true")
    parser.addoption("--fixture-cache-clear", action="store_true")
    parser.addoption("--fixture-cache-ignore", action="store_true")


def pytest_runtest_setup(item: pytest.Item) -> None:  # pragma: no cover
    """
    Optionally exclude tests based on passed in options.

    * exclude tests marked "slow" if "--fast" is passed.
    """
    if "slow" in item.keywords and item.config.getoption("--fast"):
        pytest.skip("Test marked slow and --fast is in effect.")
    if item.config.getoption("--fixture-cache-clear"):
        from .fixtures import clear_fixture_cache

        clear_fixture_cache()
