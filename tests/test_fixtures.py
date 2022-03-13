# check info function of returned structs of each fixture
# test correct working directory
import os
import pathlib
import tempfile

import pytest

from .fixtures import to_memoized_dir, to_tmp_dir  # noqa


def test_to_tmp_dir():
    cwd = os.getcwd()
    with to_tmp_dir() as tmp_dir:
        print(tmp_dir, cwd, os.getcwd())

        assert str(tmp_dir) == os.getcwd()
        assert cwd != os.getcwd()
        assert len(os.listdir(tmp_dir)) == 0

    assert cwd == os.getcwd()
    assert not os.path.isdir(str(tmp_dir))


def test_fix_tmp_dir(tmp_dir):
    assert len(os.listdir(tmp_dir)) == 0


def test_fix_tmp_dir_session():
    dirs = os.listdir("./tmp")
    res = pytest.main(
        ["tests/fix_tmp_dir_session_test_util.py", "-k", "test_1 or test_2"]
    )
    assert dirs == os.listdir("./tmp")
    assert "TESTS_FAILED" not in str(res)


def test_to_memoized_dir():
    with tempfile.TemporaryDirectory() as cache_dir:
        cache_dir = pathlib.Path(cache_dir)
        assert len(os.listdir(cache_dir)) == 0
        with to_memoized_dir(cache_dir) as (
            tmp_dir,
            save_cache,
        ):  # test cache isn't saved
            tmp = tmp_dir
            with open(str(tmp_dir) + "/uhh", "w+") as file:
                file.write("blah")
        assert len(os.listdir(cache_dir)) == 0
        assert not os.path.isdir(tmp)

        with to_memoized_dir(cache_dir) as (
            tmp_dir,
            save_cache,
        ):  # test cache is created
            tmp2 = tmp_dir
            assert tmp != tmp2
            with open(str(tmp_dir) + "/uhh", "w+") as file:
                file.write("blah")
            assert len(os.listdir(cache_dir)) == 0
            save_cache()
            assert len(os.listdir(cache_dir)) != 0
        assert not os.path.isdir(tmp2)
        assert "uhh" in os.listdir(cache_dir)

        with to_memoized_dir(cache_dir) as (
            tmp_dir,
            save_cache,
        ):  # test cache exists
            tmp3 = tmp_dir
            assert tmp2 != tmp3
            assert tmp != tmp3
            assert "uhh" in os.listdir(tmp_dir)
        assert not os.path.isdir(tmp3)
        assert "uhh" in os.listdir(cache_dir)


def test_fix_dvc_repo_session():
    dirs = os.listdir("./tmp")
    res = pytest.main(
        ["tests/fix_tmp_dir_session_test_util.py", "-k", "test_3 or test_4"]
    )
    assert dirs == os.listdir("./tmp")
    assert "TESTS_FAILED" not in str(res)


dir = None


def test_fix_dvc_repo_helper(dvc_repo_session):
    global dir
    dir = dvc_repo_session.root_dir
    assert dir is not None
    os.chdir("../..")


def test_fix_dvc_repo(dvc_repo):
    print(os.getcwd())
    assert dir != dvc_repo.root_dir
    assert os.listdir(dir) == os.listdir(dvc_repo.root_dir)


def test_fix_empty_kedro_repo_session():
    dirs = os.listdir("./tmp")
    res = pytest.main(
        ["tests/fix_tmp_dir_session_test_util.py", "-k", "test_5 or test_6"]
    )
    assert dirs == os.listdir("./tmp")
    assert "TESTS_FAILED" not in str(res)


def test_fix_empty_repo_session():
    dirs = os.listdir("./tmp")
    res = pytest.main(
        ["tests/fix_tmp_dir_session_test_util.py", "-k", "test_7 or test_8"]
    )
    assert dirs == os.listdir("./tmp")
    assert "TESTS_FAILED" not in str(res)


def test_fix_empty_repo_helper(empty_repo_session):
    global dir
    dir = empty_repo_session.root_dir
    assert dir is not None
    os.chdir("../..")


def test_fix_empty_repo(empty_repo):
    print(os.getcwd())
    assert dir != empty_repo.root_dir
    assert os.listdir(dir) == os.listdir(empty_repo.root_dir)
