import os
import subprocess

import pytest

from src.kedro_dvc.create_sample_project import create_sample_project


def test_create_sample_project_success():
    prev_dir: str = os.getcwd()
    name: str = "test"
    from_branch: str = "sample-project-basic"

    create_sample_project(name, from_branch)

    current_dir: str = os.getcwd()
    dirs = [d for d in os.listdir() if not os.path.isfile(d)]
    # pip.utils.get_installed_distributions() no longer exists
    freeze = subprocess.check_output(["pip", "freeze"])
    pip_modules = [
        i[i.find("\\n") + 2 :] for i in ("\\n" + str(freeze)[2:]).split("==")
    ][:-1]

    assert prev_dir != current_dir
    assert current_dir.endswith(f"tmp/{name}")
    assert "env" in dirs
    assert "src" in dirs
    print(pip_modules)
    assert "wcwidth" in pip_modules


def test_create_sample_project_no_name():
    prev_dir: str = os.getcwd()
    name: str = ""
    from_branch: str = "sample-project-basic"

    create_sample_project(name, from_branch)

    current_dir: str = os.getcwd()

    assert prev_dir == current_dir


def test_create_sample_project_nonexistant_branch():
    name: str = "test"
    from_branch: str = "nonexistant-branch"
    with pytest.raises(Exception):
        create_sample_project(name, from_branch)
