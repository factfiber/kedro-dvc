import functools
import pathlib
from typing import Callable, Sequence

from click.testing import CliRunner
from pytest_cases import fixture

from kedro_dvc import kd_context
from kedro_dvc.cli import kedro_dvc_cli

from ..fixtures import fix_empty_kedro_repo as fix_empty_kedro_repo  # noqa
from ..fixtures import (  # noqa
    fix_empty_kedro_repo_session as fix_empty_kedro_repo_session,
)
from ..fixtures import fix_tmp_dir_session as fix_tmp_dir_session  # noqa
from .check_setup import check_repo_setup


@fixture  # type: ignore
def kedro_runner() -> Callable[[Sequence[str]], None]:
    """
    Fixture to run kedro-dvc cli commands.

    Setup kedro cli including plugin init; then return click runner
    """
    # cli._init_plugins()  # type: ignore
    # cli_collection = cli.KedroCLI(project_path=pathlib.Path.cwd())
    runner = CliRunner()
    return functools.partial(runner.invoke, kedro_dvc_cli)


def test_cli_install_kedro_dvc_in_kedro_repo(
    empty_kedro_repo: pathlib.Path, kedro_runner: CliRunner
) -> None:
    """
    Test cli setup with existing kedro, but no dvc or kedro-dvc.
    """
    result = kedro_runner(["dvc", "install"])
    assert result.exit_code == 0
    assert "Kedro-DVC installed successfully" in result.stdout
    context = kd_context.KDContext(project_dir=empty_kedro_repo)
    check_repo_setup(context)
