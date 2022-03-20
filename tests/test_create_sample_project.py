import os
import pathlib
import random
import shutil
import string
import subprocess
from typing import Callable, Iterator

import click
import pytest
from click.testing import CliRunner
from pytest_cases import fixture, parametrize_with_cases

from kedro_dvc import create_sample_project as create_sample_project_mod
from kedro_dvc.create_sample_project import (
    AlreadyExists,
    CantCheckout,
    InvalidName,
    _exec_file,
    create_sample_project,
    create_sample_project_cmd,
)

from .fixtures import fix_tmp_dir  # noqa

PROJ_DIR = str(pathlib.Path(__file__).parent.parent)

CreateFct = Callable[[str, str, str], None]


class CommandError(RuntimeError):
    pass


class CreateVia:
    """
    Cases: how to call `create_sample_project`:

    Either call `create_sample_project` directly or using via cli.
    """

    def case_api(self) -> CreateFct:
        return create_sample_project  # type: ignore

    def case_command(self) -> CreateFct:
        def create(name: str, branch: str, proj_path: str) -> None:
            runner = CliRunner()
            result = runner.invoke(
                create_sample_project_cmd, [name, branch, proj_path]
            )
            if result.exit_code != 0:
                if "Path exists" in result.output:
                    raise AlreadyExists()
                if "Can't check out branch" in result.output:
                    raise CantCheckout()

        return create


@fixture(name="sample_dir")  # type: ignore
def fix_sample_dir() -> Iterator[str]:
    """
    Choose sample dir name
    """
    suffix = random.choices(string.ascii_uppercase + string.digits, k=6)
    name = f"test_{''.join(suffix)}"
    try:
        yield name
    finally:
        q_name = "tmp/{name}"
        if os.path.exists(q_name):  # pragma: no cover
            shutil.rmtree(q_name)


def add_dummy_command(
    dir_path: pathlib.Path, name: str, command: str = ""
) -> None:  # pragma: no cover
    """
    Create a dummy executable in `dir_path`.

    Note: ignore in coverage because we don't run "--fast"
    when doing coverage.
    """
    command_path = dir_path / name
    command_path.write_text(command)
    # TODO: chmod not portable to windows
    os.chmod(str(command_path), 0o744)


@fixture(name="_mock_pip")  # type: ignore
def fix_mock_pip(
    tmp_dir: pathlib.Path,
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[str]:  # pragma: no cover
    """
    Add mock "pip" command to path if "--mock-pip" option is set.

    Also adds "virtualenv" to path

    To speed up tests that use pip install but don't depend
    on correct functioning.

    Note: ignore in coverage because we don't run "--fast"
    when doing coverage.
    """
    if request.config.getoption("--fast"):
        add_dummy_command(tmp_dir, "pip")
        add_dummy_command(tmp_dir, "virtualenv", "mkdir -p env")
        old_path = os.environ["PATH"]
        monkeypatch.setattr(
            create_sample_project_mod, "_exec_file", lambda *args: None
        )
        try:
            # TODO: path format not portable to windows
            os.environ["PATH"] = f"{str(tmp_dir)}:{old_path}"
            yield str(tmp_dir)
        finally:
            os.environ["PATH"] = old_path
    else:
        yield str(tmp_dir)


@pytest.mark.slow
@parametrize_with_cases("create", cases=CreateVia)
def test_create_sample_project_success(
    tmp_dir: pathlib.Path,
    sample_dir: str,
    create: CreateFct,
    _mock_pip: str,
    request: pytest.FixtureRequest,
) -> None:
    from_branch: str = "sample-project-basic"

    create(sample_dir, from_branch, PROJ_DIR)

    q_name = pathlib.Path(f"tmp/{sample_dir}")
    assert q_name.exists()
    assert q_name.is_dir()
    os.chdir(q_name)
    dirs = [d for d in os.listdir() if not os.path.isfile(d)]
    # pip.utils.get_installed_distributions() no longer exists
    activate_this_file = f"env/{sample_dir}/bin/activate_this.py"
    _exec_file(activate_this_file)
    freeze = subprocess.check_output(["pip", "freeze"])
    pip_modules = [
        i[i.find("\\n") + 2 :] for i in ("\\n" + str(freeze)[2:]).split("==")
    ][:-1]
    assert "env" in dirs
    assert "src" in dirs
    if not request.config.getoption("--fast"):
        assert "wcwidth" in pip_modules


def test_create_sample_project_no_name(tmp_dir: pathlib.Path) -> None:
    prev_dir: str = os.getcwd()
    name: str = ""
    from_branch: str = "sample-project-basic"

    with pytest.raises((InvalidName, click.BadParameter)):
        create_sample_project(name, from_branch)

    current_dir: str = os.getcwd()

    assert prev_dir == current_dir


@parametrize_with_cases("create", cases=CreateVia)
def test_create_sample_project_nonexistent_branch(
    create: CreateFct, sample_dir: str
) -> None:
    name = sample_dir
    from_branch: str = "nonexistent-branch"
    with pytest.raises((CantCheckout, click.BadParameter)):
        create(name, from_branch, PROJ_DIR)


@parametrize_with_cases("create", cases=CreateVia)
def test_create_sample_project_already_exists(
    sample_dir: str, create: CreateFct
) -> None:
    name = sample_dir
    from_branch: str = "sample-project-basic"
    q_dir = pathlib.Path(f"tmp/{name}")
    q_dir.mkdir(parents=True)
    with pytest.raises((AlreadyExists, click.UsageError)):
        create(name, from_branch, PROJ_DIR)
