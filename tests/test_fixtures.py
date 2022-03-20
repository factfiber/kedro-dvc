# check info function of returned structs of each fixture
# test correct working directory
import os
import pathlib
import tempfile

from .fixtures import (  # noqa
    fix_dvc_repo,
    fix_dvc_repo_session,
    fix_empty_kedro_repo_session,
    fix_empty_repo,
    fix_empty_repo_session,
    fix_tmp_dir,
    fix_tmp_dir_session,
    to_memoized_dir,
    to_tmp_dir,
)

root = os.getcwd()


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


def test_fix_tmp_dir_session(tmp_dir_session, tmp_dir):
    assert fix_tmp_dir_session._pytestfixturefunction.scope == "session"
    assert tmp_dir_session != tmp_dir
    assert os.listdir(tmp_dir_session) == os.listdir(tmp_dir)
    os.chdir(root)


def test_to_memoized_dir():
    with tempfile.TemporaryDirectory() as cache_dir:
        cache_dir = pathlib.Path(cache_dir)
        assert len(os.listdir(cache_dir)) == 0
        with to_memoized_dir(cache_dir) as (
            tmp_dir,
            save_cache,
        ):  # test cache isn't saved
            tmp = tmp_dir
            with open(str(tmp_dir) + "/test_file", "w+") as file:
                file.write("contents")
        assert len(os.listdir(cache_dir)) == 0
        assert not os.path.isdir(tmp)

        with to_memoized_dir(cache_dir) as (
            tmp_dir,
            save_cache,
        ):  # test cache is created
            tmp2 = tmp_dir
            assert tmp != tmp2
            with open(str(tmp_dir) + "/test_file", "w+") as file:
                file.write("contents")
            assert len(os.listdir(cache_dir)) == 0
            save_cache()
            assert len(os.listdir(cache_dir)) != 0
        assert not os.path.isdir(tmp2)
        assert "test_file" in os.listdir(cache_dir)

        with to_memoized_dir(cache_dir) as (
            tmp_dir,
            save_cache,
        ):  # test cache exists
            tmp3 = tmp_dir
            assert tmp2 != tmp3
            assert tmp != tmp3
            assert "test_file" in os.listdir(tmp_dir)
        assert not os.path.isdir(tmp3)
        assert "test_file" in os.listdir(cache_dir)


def test_fix_dvc_repo(dvc_repo_session, dvc_repo):
    assert fix_dvc_repo_session._pytestfixturefunction.scope == "session"
    assert dvc_repo_session != dvc_repo
    assert os.listdir(dvc_repo_session.root_dir) == os.listdir(
        dvc_repo.root_dir
    )

    assert ".dvc" in os.listdir(dvc_repo.root_dir)
    os.chdir(root)


def test_fix_empty_kedro_repo(empty_kedro_repo_session):
    print("kedro repo", os.getcwd(), empty_kedro_repo_session)
    assert (
        fix_empty_kedro_repo_session._pytestfixturefunction.scope == "session"
    )

    assert "conf" in os.listdir(empty_kedro_repo_session)
    os.chdir(root)


def test_fix_empty_repo(empty_repo_session, empty_repo):
    print("empty repo", os.getcwd(), empty_repo)
    assert fix_empty_repo_session._pytestfixturefunction.scope == "session"
    assert empty_repo_session != empty_repo
    assert os.listdir(empty_repo_session.root_dir) == os.listdir(
        empty_repo.root_dir
    )

    assert ".dvc" in os.listdir(empty_repo.root_dir)
    assert "conf" in os.listdir(empty_repo.root_dir)
