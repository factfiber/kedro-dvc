# import os
# import shutil
import subprocess
import tempfile

from dvc.repo import Repo as DvcRepo
from pytest_cases import fixture


@fixture(name="dvc_repo_session", scope="session")
def fix_dvc_repo_session() -> DvcRepo:
    with tempfile.TemporaryDirectory() as dir:
        # os.mkdir("./temp_test")
        subprocess.check_call(["git", "init"], cwd=dir)
        dvc = DvcRepo.init(dir, subdir=True)
        yield dvc
        dvc.close()


@fixture(name="dvc_repo")
def fix_dvc_repo() -> DvcRepo:
    return fix_dvc_repo_session()
