import subprocess
import tempfile

from dvc.repo import Repo as DvcRepo
from pytest_cases import fixture


@fixture(name="dvc_repo_session", scope="session")
def fix_dvc_repo_session() -> DvcRepo:
    with tempfile.TemporaryDirectory() as dir:
        subprocess.check_call(["git", "init"], cwd=dir)
        print(dir)
        dvc = DvcRepo.init(dir, subdir=True)
        yield dvc
        dvc.close()


@fixture(name="dvc_repo")
def fix_dvc_repo(dvc_repo_session) -> DvcRepo:
    return  # take the repo from^ this and make a copy
