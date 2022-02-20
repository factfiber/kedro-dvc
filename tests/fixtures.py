import subprocess
import tempfile
import shutil
import copy
import os

from dvc.repo import Repo as DvcRepo
from pytest_cases import fixture


@fixture(name="dvc_repo_session", scope="session")
def fix_dvc_repo_session() -> DvcRepo:
    with tempfile.TemporaryDirectory() as dir:
        subprocess.check_call(["git", "init"], cwd=dir)
        dvc = DvcRepo.init(dir, subdir=True)
        prev_dir = os.getcwd()
        os.chdir(dir)

        yield dvc

        dvc.close()
        os.chdir(prev_dir)

@fixture(name="dvc_repo")
def fix_dvc_repo(dvc_repo_session) -> DvcRepo:
    with tempfile.TemporaryDirectory() as dir:
        dvc_repo = copy.deepcopy(dvc_repo_session)
        dvc_repo.root_dir = dir
        shutil.copytree(dvc_repo_session.root_dir, dvc_repo.root_dir)
        prev_dir = os.getcwd()
        os.chdir(dvc_repo.root_dir)

        yield dvc_repo
        
        os.chdir(prev_dir)

@fixture(name="empty_repo_session", scope="session")
def fix_empty_repo_session() -> str:
    with tempfile.TemporaryDirectory() as dir:
        # Might be able to do this from python, not sure
        subprocess.check_call(
            f"poetry exec create-sample-project test-project sample-project-basic", 
            shell=True
        )
        subprocess.check_call(
            f"mv tmp/name {dir}/tmp/name",
            shell=True
        )
        subprocess.check_call(["git", "init"], cwd=dir)
        prev_dir = os.getcwd()
        os.chdir(dir)

        yield dir

        os.chdir(prev_dir)

@fixture(name="empty_repo_session")
def fix_empty_repo(empty_repo_session) -> str:
    with tempfile.TemporaryDirectory() as dir:
        empty_repo = dir
        shutil.copytree(empty_repo_session, empty_repo)
        prev_dir = os.getcwd()
        os.chdir(empty_repo)

        yield empty_repo

        os.chdir(prev_dir)


