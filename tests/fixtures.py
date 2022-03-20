import contextlib
import os
import pathlib
import shutil
import subprocess
import tempfile
from typing import Callable, Iterator, Optional, Tuple, cast

import pytest
from dvc.repo import Repo as DvcRepo
from pytest_cases import fixture

from kedro_dvc.create_sample_project import create_sample_project

CACHE_DIR = pathlib.Path(__file__).parent / ".fixture-cache"
APP_DIR = pathlib.Path(__file__).parent.parent

root = os.getcwd()


@contextlib.contextmanager
def to_tmp_dir() -> Iterator[pathlib.Path]:
    """
    Create temp directory, yield context within it.
    """
    with tempfile.TemporaryDirectory() as dir:
        prev_dir = os.getcwd()
        os.chdir(dir)
        try:
            yield pathlib.Path(dir)
        finally:
            try:
                os.chdir(prev_dir)
            except Exception:  # pragma: no cover
                print(
                    "WARNING: Couldn't change back to previous"
                    + f" directory after test: {str(prev_dir)}"
                )
                os.chdir(root)


@fixture(name="tmp_dir")  # type: ignore
def fix_tmp_dir() -> Iterator[pathlib.Path]:
    """
    Test in temp directory
    """
    with to_tmp_dir() as dir:
        yield dir


@fixture(name="tmp_dir_session", scope="session")  # type: ignore
def fix_tmp_dir_session() -> Iterator[pathlib.Path]:
    """
    Test in temp directory.

    Session scoped.
    """
    with to_tmp_dir() as dir:
        yield dir


@contextlib.contextmanager
def to_memoized_dir(
    cache_dir: pathlib.Path, ignore_cache: bool = False
) -> Iterator[Tuple[pathlib.Path, Optional[Callable[[], None]]]]:
    """
    Create temp dir; fill from cache if exists; yield context within it.

    If the cache dir is empty, `save_cache` will be a function that
    will save the cache. Otherwise, it will be None.

    Returns: tuple of (`dir`, `save_cache`):
        dir: pathlib.Path to the created directory
        save_cache: optional callable to save the cache to the `cache_dir`
    """
    with to_tmp_dir() as tmp_dir:
        save_cache: Optional[Callable[[], None]] = None
        if (
            cache_dir.exists()
            and len(os.listdir(cache_dir)) != 0
            and not ignore_cache
        ):
            shutil.copytree(str(cache_dir), str(tmp_dir), dirs_exist_ok=True)
        else:
            if cache_dir.exists() and len(os.listdir(cache_dir)) != 0:
                shutil.rmtree(cache_dir)
                # for f in cache_dir.iterdir():
                #     if f.is_file():
                #         f.unlink()
                #     else:
                #         shutil.rmtree(f)
            save_cache = cast(
                Callable[[], None],
                lambda: shutil.copytree(
                    str(tmp_dir), str(cache_dir), dirs_exist_ok=True
                ),
            )
        yield tmp_dir, save_cache


@fixture(name="dvc_repo_session", scope="session")  # type: ignore
def fix_dvc_repo_session(
    request: pytest.FixtureRequest, tmp_dir_session: pathlib.Path
) -> Iterator[DvcRepo]:
    """
    Create dvc repo; test cwd will be within repo dir.
    """
    cache_dir = CACHE_DIR / "dvc_repo_session"
    ignore_cache = request.config.getoption("--fixture-cache-ignore")
    with to_memoized_dir(cache_dir, ignore_cache=ignore_cache) as (
        dir,
        save_cache,
    ):
        if save_cache:
            subprocess.check_call(["git", "init"])
            dvc = DvcRepo.init(".", subdir=True)
            save_cache()
        else:  # pragma: no cover
            # note: we run with --fixture-cache-ignore for coverage so
            # don't hit this branch
            dvc = DvcRepo(root_dir=dir)
        try:
            yield dvc
        finally:
            dvc.close()


@fixture(name="dvc_repo")  # type: ignore
def fix_dvc_repo(dvc_repo_session: DvcRepo) -> Iterator[DvcRepo]:
    """
    Create dvc repo (copying session repo); cwd within repo.
    """
    with to_tmp_dir() as dir:
        shutil.copytree(dvc_repo_session.root_dir, dir, dirs_exist_ok=True)
        dvc_repo = DvcRepo(root_dir=dir)
        try:
            yield dvc_repo
        finally:
            dvc_repo.close()


@fixture(name="empty_kedro_repo_session", scope="session")  # type: ignore
def fix_empty_kedro_repo_session(
    request: pytest.FixtureRequest,
) -> Iterator[pathlib.Path]:
    """
    Create sample kedro project.

    Session scoped.
    """
    cache_dir = CACHE_DIR / "empty_kedro_repo_session"
    ignore_cache = request.config.getoption("--fixture-cache-ignore")
    with to_memoized_dir(cache_dir, ignore_cache=ignore_cache) as (
        dir,
        save_cache,
    ):
        if save_cache:
            create_sample_project("test", kd_repo_path=str(APP_DIR))
            for path in pathlib.Path("tmp/test").iterdir():
                shutil.move(str(path), ".")
            shutil.rmtree("tmp")
            save_cache()
        yield dir


@fixture(name="empty_repo_session", scope="session")  # type: ignore
def fix_empty_repo_session(
    request: pytest.FixtureRequest,
    empty_kedro_repo_session: pathlib.Path,
    dvc_repo_session: DvcRepo,
) -> Iterator[DvcRepo]:
    """
    Create kedro sample project with dvc repo; cwd inside.

    Session scoped.
    """
    cache_dir = CACHE_DIR / "empty_repo_session"
    ignore_cache = request.config.getoption("--fixture-cache-ignore")
    with to_memoized_dir(cache_dir, ignore_cache=ignore_cache) as (
        dir,
        save_cache,
    ):
        if save_cache:
            shutil.copytree(dvc_repo_session.root_dir, dir, dirs_exist_ok=True)
            shutil.copytree(empty_kedro_repo_session, dir, dirs_exist_ok=True)
            empty_repo = DvcRepo(root_dir=dir)
            empty_repo.scm.add(".")
            empty_repo.scm.commit("feat: first commit of empty repo")
            save_cache()
        else:  # pragma: no cover
            # note: we run with --fixture-cache-ignore for coverage so
            # don't hit this branch
            empty_repo = DvcRepo(root_dir=dir)
        try:
            yield empty_repo
        finally:
            empty_repo.close()


@fixture(name="empty_repo")  # type: ignore
def fix_empty_repo(empty_repo_session: DvcRepo) -> Iterator[DvcRepo]:
    """
    Create kedro sample with dvc repo (copying session repo); cwd inside.
    """
    with to_tmp_dir() as dir:
        shutil.copytree(empty_repo_session.root_dir, dir, dirs_exist_ok=True)
        dvc_repo = DvcRepo(root_dir=dir)
        try:
            yield dvc_repo
        finally:
            dvc_repo.close()


def clear_fixture_cache() -> None:  # pragma: no cover
    """
    Removes the cached fixtures.
    """
    if CACHE_DIR.exists():
        shutil.rmtree(CACHE_DIR)
