# check info function of returned structs of each fixture
# test correct working directory
import os
import pathlib
import tempfile
from functools import wraps
from typing import Any, Callable

from dvc.repo import Repo as DvcRepo

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


def ensure_root_at_end(test_fct: Callable[..., None]) -> Callable[..., None]:
    """
    Ensure that the root directory is at the end of the stack.
    """

    @wraps(test_fct)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            test_fct(*args, **kwargs)
        finally:
            os.chdir(root)

    return wrapper


def test_to_tmp_dir() -> None:
    cwd = os.getcwd()
    with to_tmp_dir() as tmp_dir:
        print(tmp_dir, cwd, os.getcwd())

        assert tmp_dir.resolve() == pathlib.Path(os.getcwd()).resolve()
        assert cwd != os.getcwd()
        assert len(os.listdir(tmp_dir)) == 0

    assert cwd == os.getcwd()
    assert not os.path.isdir(str(tmp_dir))


def test_fix_tmp_dir(tmp_dir: pathlib.Path) -> None:
    assert len(os.listdir(tmp_dir)) == 0


@ensure_root_at_end
def test_fix_tmp_dir_session(
    tmp_dir_session: pathlib.Path, tmp_dir: pathlib.Path
) -> None:
    assert fix_tmp_dir_session._pytestfixturefunction.scope == "session"
    assert tmp_dir_session != tmp_dir
    assert os.listdir(tmp_dir_session) == os.listdir(tmp_dir)


def test_to_memoized_dir() -> None:
    with tempfile.TemporaryDirectory() as cache_dir_:
        cache_dir = pathlib.Path(cache_dir_)
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
            # if cache didn't exist, save_cache should be a function
            assert save_cache is not None
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


@ensure_root_at_end
def test_fix_dvc_repo(dvc_repo_session: DvcRepo, dvc_repo: DvcRepo) -> None:
    assert fix_dvc_repo_session._pytestfixturefunction.scope == "session"
    assert dvc_repo_session != dvc_repo
    assert os.listdir(dvc_repo_session.root_dir) == os.listdir(
        dvc_repo.root_dir
    )

    assert ".dvc" in os.listdir(dvc_repo.root_dir)


@ensure_root_at_end
def test_fix_empty_kedro_repo(empty_kedro_repo_session: pathlib.Path) -> None:
    print("kedro repo", os.getcwd(), empty_kedro_repo_session)
    assert (
        fix_empty_kedro_repo_session._pytestfixturefunction.scope == "session"
    )

    assert "conf" in os.listdir(empty_kedro_repo_session)
    # os.chdir(root)


@ensure_root_at_end
def test_fix_empty_repo(
    empty_repo_session: DvcRepo, empty_repo: DvcRepo
) -> None:
    print("empty repo", os.getcwd(), empty_repo)
    assert fix_empty_repo_session._pytestfixturefunction.scope == "session"
    assert fix_empty_repo._pytestfixturefunction.scope == "function"
    assert empty_repo_session != empty_repo
    assert os.listdir(empty_repo_session.root_dir) == os.listdir(
        empty_repo.root_dir
    )

    assert ".dvc" in os.listdir(empty_repo.root_dir)
    assert "conf" in os.listdir(empty_repo.root_dir)
