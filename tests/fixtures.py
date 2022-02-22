import os
import shutil
import subprocess
import tempfile
from typing import Iterator

from dvc.repo import Repo as DvcRepo
from pytest_cases import fixture


@fixture(name="dvc_repo_session", scope="session")  # type: ignore
def fix_dvc_repo_session() -> Iterator[DvcRepo]:
    with tempfile.TemporaryDirectory() as dir:
        subprocess.check_call(["git", "init"], cwd=dir)
        dvc = DvcRepo.init(dir, subdir=True)
        prev_dir = os.getcwd()
        os.chdir(dir)

        yield dvc

        dvc.close()
        os.chdir(prev_dir)


@fixture(name="dvc_repo")  # type: ignore
def fix_dvc_repo(dvc_repo_session: DvcRepo) -> Iterator[DvcRepo]:
    with tempfile.TemporaryDirectory() as dir:
        dvc_repo = DvcRepo(root_dir=dir)
        dvc_repo.root_dir = dir
        shutil.copytree(dvc_repo_session.root_dir, dvc_repo.root_dir)
        prev_dir = os.getcwd()
        os.chdir(dvc_repo.root_dir)

        yield dvc_repo

        dvc_repo.close()
        os.chdir(prev_dir)


@fixture(name="empty_kedro_repo_session", scope="session")  # type: ignore
def fix_empty_kedro_repo_session() -> Iterator[str]:
    with tempfile.TemporaryDirectory() as dir:
        # Might be able to do this from python, not sure
        args = "test-project sample-project-basic"
        subprocess.check_call(
            f"poetry exec create-sample-project {args}",
            shell=True,
        )
        subprocess.check_call(f"mv tmp/name {dir}/tmp/name", shell=True)
        subprocess.check_call(["git", "init"], cwd=dir)
        prev_dir = os.getcwd()
        os.chdir(dir)

        yield dir

        os.chdir(prev_dir)


@fixture(name="empty_repo_session", scope="session")  # type: ignore
def fix_empty_repo_session(
    empty_kedro_repo_session: str, dvc_repo_session: DvcRepo
) -> Iterator[DvcRepo]:
    with tempfile.TemporaryDirectory() as dir:
        empty_repo = DvcRepo(root_dir=dir)
        shutil.copytree(dvc_repo_session.root_dir, dir)
        shutil.copytree(empty_kedro_repo_session, dir)
        empty_repo.git.add_commit(".", "feat: first commit of empty repo")
        prev_dir = os.getcwd()
        os.chdir(dir)

        yield empty_repo

        empty_repo.close()
        os.chdir(prev_dir)


@fixture(name="empty_repo", scope="session")  # type: ignore
def fix_empty_repo(empty_repo_session: DvcRepo) -> Iterator[DvcRepo]:
    with tempfile.TemporaryDirectory() as dir:
        empty_repo = DvcRepo(root_dir=dir)
        shutil.copytree(empty_repo_session.root_dir, dir)
        prev_dir = os.getcwd()
        os.chdir(dir)

        yield empty_repo

        empty_repo.close()
        os.chdir(prev_dir)
