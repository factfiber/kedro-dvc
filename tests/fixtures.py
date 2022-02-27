import contextlib
import os
import pathlib
import shutil
import subprocess
import tempfile
from typing import Iterator

from dvc.repo import Repo as DvcRepo
from pytest_cases import fixture

from kedro_dvc.create_sample_project import create_sample_project


@contextlib.contextmanager
def to_tmp_dir() -> Iterator[pathlib.Path]:
    """
    Create temp directory, yield context within it.
    """
    with tempfile.TemporaryDirectory() as dir:
        prev_dir = os.getcwd()
        os.chdir(dir)
        try:
            yield pathlib.Path(dir)
        finally:
            os.chdir(prev_dir)


@fixture(name="tmp_dir")  # type: ignore
def fix_tmp_dir() -> Iterator[pathlib.Path]:
    """
    Test in temp directory
    """
    with to_tmp_dir() as dir:
        yield dir


@fixture(name="tmp_dir_session")  # type: ignore
def fix_tmp_dir_session() -> Iterator[pathlib.Path]:
    """
    Test in temp directory.

    Session scoped.
    """
    with to_tmp_dir() as dir:
        yield dir


@fixture(name="dvc_repo_session", scope="session")  # type: ignore
def fix_dvc_repo_session(tmp_dir_session: pathlib.Path) -> Iterator[DvcRepo]:
    """
    Create dvc repo; test cwd will be within repo dir.
    """
    subprocess.check_call(["git", "init"])
    dvc = DvcRepo.init(".", subdir=True)
    try:
        yield dvc
    finally:
        dvc.close()


@fixture(name="dvc_repo")  # type: ignore
def fix_dvc_repo(dvc_repo_session: DvcRepo) -> Iterator[DvcRepo]:
    """
    Create dvc repo (copying session repo); cwd within repo.
    """
    with to_tmp_dir() as dir:
        dvc_repo = DvcRepo(root_dir=dir)
        shutil.copytree(dvc_repo_session.root_dir, dvc_repo.root_dir)
        try:
            yield dvc_repo
        finally:
            dvc_repo.close()


@fixture(name="empty_kedro_repo_session", scope="session")  # type: ignore
def fix_empty_kedro_repo_session() -> Iterator[pathlib.Path]:
    """
    Create sample kedro project.

    Session scoped.
    """
    with to_tmp_dir() as dir:
        create_sample_project("test")
        shutil.move("tmp/test", ".")
        shutil.rmtree("tmp")
        yield dir


@fixture(name="empty_repo_session", scope="session")  # type: ignore
def fix_empty_repo_session(
    empty_kedro_repo_session: pathlib.Path, dvc_repo_session: DvcRepo
) -> Iterator[DvcRepo]:
    """
    Create kedro sample project with dvc repo; cwd inside.

    Session scoped.
    """
    with to_tmp_dir() as dir:
        shutil.copytree(dvc_repo_session.root_dir, dir)
        shutil.copytree(empty_kedro_repo_session, dir)
        empty_repo = DvcRepo(root_dir=dir)
        empty_repo.git.add_commit(".", "feat: first commit of empty repo")
        try:
            yield dir
        finally:
            empty_repo.close()


@fixture(name="empty_repo", scope="session")  # type: ignore
def fix_empty_repo(empty_repo_session: DvcRepo) -> Iterator[DvcRepo]:
    """
    Create kedro sample with dvc repo (copying session repo); cwd inside.
    """
    with to_tmp_dir() as dir:
        shutil.copytree(empty_repo_session.root_dir, dir)
        dvc_repo = DvcRepo(root_dir=dir)
        try:
            yield dvc_repo
        finally:
            dvc_repo.close()
