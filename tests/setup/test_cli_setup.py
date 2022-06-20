import functools
import pathlib
from typing import Callable, Sequence

from click.testing import CliRunner, Result
from pytest_cases import fixture

from kedro_dvc import kd_context
from kedro_dvc.cli import kedro_dvc_cli

from ..fixtures import fix_empty_kedro_repo as fix_empty_kedro_repo  # noqa
from ..fixtures import (  # noqa
    fix_empty_kedro_repo_session as fix_empty_kedro_repo_session,
)
from ..fixtures import fix_tmp_dir_session as fix_tmp_dir_session  # noqa
from .check_setup import check_repo_setup

KDRunner = Callable[[Sequence[str]], Result]


@fixture  # type: ignore
def kedro_runner() -> KDRunner:
    """
    Fixture to run kedro-dvc cli commands.

    Setup kedro cli including plugin init; then return click runner
    """
    # cli._init_plugins()  # type: ignore
    # cli_collection = cli.KedroCLI(project_path=pathlib.Path.cwd())
    runner = CliRunner()
    return functools.partial(runner.invoke, kedro_dvc_cli)  # type: ignore


def test_cli_install_kedro_dvc_in_kedro_repo(
    empty_kedro_repo: pathlib.Path, kedro_runner: KDRunner
) -> None:
    """
    Test cli install with existing kedro, but no dvc or kedro-dvc.
    """
    result = kedro_runner(["dvc", "install"])
    assert result.exit_code == 0
    assert "Kedro-DVC installed successfully" in result.stdout
    context = kd_context.KDContext(project_dir=empty_kedro_repo)
    check_repo_setup(context)


def test_cli_install_dvc_exists(
    empty_kedro_repo: pathlib.Path, kedro_runner: KDRunner
) -> None:
    """
    Test cli install with existing dvc, but no kedro-dvc.
    """
    kd_context.KDContext(project_dir=empty_kedro_repo, install_dvc=True)
    result = kedro_runner(["dvc", "install"])
    assert result.exit_code == 1
    assert "Kedro-DVC is already installed" in result.stdout


def test_cli_update_dvc_exists(
    empty_kedro_repo: pathlib.Path, kedro_runner: KDRunner
) -> None:
    """
    Test cli update with existing dvc.
    """
    kd_context.KDContext(project_dir=empty_kedro_repo, install_dvc=True)
    result = kedro_runner(["dvc", "update"])
    assert result.exit_code == 0
    assert "Kedro-DVC updated successfully" in result.stdout
    context = kd_context.KDContext(project_dir=empty_kedro_repo)
    check_repo_setup(context)


def test_cli_update_no_dvc_exists(
    empty_kedro_repo: pathlib.Path, kedro_runner: KDRunner
) -> None:
    """
    Test cli update with existing dvc.
    """
    result = kedro_runner(["dvc", "update"])
    assert result.exit_code == 1
    assert (
        "DVC is not installed. Use `kedro dvc install` to install."
        in result.stdout
    )
