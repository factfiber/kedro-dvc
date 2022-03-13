import os

from .fixtures import *  # noqa

dir = None


def test_1(tmp_dir_session):
    global dir
    dir = tmp_dir_session
    with open(str(tmp_dir_session) + "/uhh", "w+") as file:
        file.write("blah")


def test_2(tmp_dir_session):
    assert dir == tmp_dir_session
    assert "uhh" in os.listdir(tmp_dir_session)


def test_3(dvc_repo_session):
    global dir
    dir = dvc_repo_session.root_dir

    assert ".dvc" in os.listdir(dvc_repo_session.root_dir)
    with open(dvc_repo_session.root_dir + "/uhh", "w+") as file:
        file.write("blah")


def test_4(dvc_repo_session):
    assert dir == dvc_repo_session.root_dir
    assert "uhh" in os.listdir(dvc_repo_session.root_dir)


def test_5(empty_kedro_repo_session):
    global dir
    dir = str(empty_kedro_repo_session)

    assert "conf" in os.listdir(str(empty_kedro_repo_session))
    with open(str(empty_kedro_repo_session) + "/uhh", "w+") as file:
        file.write("blah")


def test_6(empty_kedro_repo_session):
    assert dir == str(empty_kedro_repo_session)
    assert "uhh" in os.listdir(str(empty_kedro_repo_session))


def test_7(empty_repo_session):
    global dir
    dir = empty_repo_session.root_dir

    assert ".dvc" in os.listdir(empty_repo_session.root_dir)
    assert "conf" in os.listdir(empty_repo_session.root_dir)
    with open(empty_repo_session.root_dir + "/uhh", "w+") as file:
        file.write("blah")


def test_8(empty_repo_session):
    assert dir == empty_repo_session.root_dir
    assert "uhh" in os.listdir(empty_repo_session.root_dir)
