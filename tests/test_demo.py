# import os
import subprocess

# import dvc.api
from pytest_cases import fixture

import kedro_dvc


@fixture(scope="session")  # put in different file fixtures.py
def dvc_repo(tmpdir):
    # os.mkdir("./temp_test")
    # subprocess.Popen('dvc init --subdir', cwd="./temp_test")
    subprocess.Popen("ls", cwd=tmpdir)


def test_demo(dvc_repo):
    kedro_dvc is not None
