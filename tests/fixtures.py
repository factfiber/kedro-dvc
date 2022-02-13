import os
import shutil

from dvc.repo import Repo as DvcRepo
from pytest_cases import fixture


@fixture(name="dvc_repo_session", scope="session")
def fix_dvc_repo_session() -> DvcRepo:
    os.mkdir("./temp_test")
    dvc = DvcRepo.init("./temp_test", subdir=True)
    yield dvc
    dvc.close()
    shutil.rmtree("./temp_test")


@fixture(name="dvc_repo")
def fix_dvc_repo() -> DvcRepo:
    return fix_dvc_repo_session()
