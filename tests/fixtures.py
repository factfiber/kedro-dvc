import contextlib
import os
import pathlib
import shutil
import subprocess
import tempfile
from typing import Callable, Iterator, Optional, Tuple, cast

from dvc.repo import Repo as DvcRepo
from pytest_cases import fixture

from kedro_dvc.create_sample_project import create_sample_project

CACHE_DIR = pathlib.Path(__file__).parent / ".fixture-cache"
APP_DIR = pathlib.Path(__file__).parent.parent


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
            os.chdir(prev_dir)


@fixture(name="tmp_dir")  # type: ignore
def fix_tmp_dir() -> Iterator[pathlib.Path]:
    """
    Test in temp directory
    """
    with to_tmp_dir() as dir:
        yield dir


@fixture(name="tmp_dir_session")  # type: ignore
def fix_tmp_dir_session() -> Iterator[pathlib.Path]:
    """
    Test in temp directory.

    Session scoped.
    """
    with to_tmp_dir() as dir:
        yield dir


@contextlib.contextmanager
def to_memoized_dir(
    cache_dir: pathlib.Path,
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
        breakpoint()
        if cache_dir.exists():
            shutil.copytree(str(cache_dir), str(tmp_dir))
        else:
            save_cache = cast(
                Callable[[], None],
                lambda: shutil.copytree(
                    str(tmp_dir), str(cache_dir), dirs_exist_ok=True
                ),
            )
        yield tmp_dir, save_cache


@fixture(name="dvc_repo_session", scope="session")  # type: ignore
def fix_dvc_repo_session(tmp_dir_session: pathlib.Path) -> Iterator[DvcRepo]:
    """
    Create dvc repo; test cwd will be within repo dir.
    """
    cache_dir = CACHE_DIR / "dvc_repo_session"
    with to_memoized_dir(cache_dir) as (dir, save_cache):
        if save_cache:
            subprocess.check_call(["git", "init"])
            dvc = DvcRepo.init(".", subdir=True)
            save_cache()
        else:
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
        shutil.copytree(dvc_repo_session.root_dir, dir)
        dvc_repo = DvcRepo(root_dir=dir)
        try:
            yield dvc_repo
        finally:
            dvc_repo.close()


@fixture(name="empty_kedro_repo_session", scope="session")  # type: ignore
def fix_empty_kedro_repo_session() -> Iterator[pathlib.Path]:
    """
    Create sample kedro project.

    Session scoped.
    """
    cache_dir = CACHE_DIR / "empty_kedro_repo_session"
    with to_memoized_dir(cache_dir) as (dir, save_cache):
        if save_cache:
            create_sample_project("test", kedro_dvc_path=APP_DIR)
            shutil.move("tmp/test", ".")
            shutil.rmtree("tmp")
            save_cache()
        yield dir


@fixture(name="empty_repo_session", scope="session")  # type: ignore
def fix_empty_repo_session(
    empty_kedro_repo_session: pathlib.Path, dvc_repo_session: DvcRepo
) -> Iterator[DvcRepo]:
    """
    Create kedro sample project with dvc repo; cwd inside.

    Session scoped.
    """
    cache_dir = CACHE_DIR / "empty_repo_session"
    with to_memoized_dir(cache_dir) as (dir, save_cache):
        if save_cache:
            shutil.copytree(dvc_repo_session.root_dir, dir)
            shutil.copytree(empty_kedro_repo_session, dir)
            empty_repo = DvcRepo(root_dir=dir)
            empty_repo.git.add_commit(".", "feat: first commit of empty repo")
            save_cache()
        else:
            empty_repo = DvcRepo(root_dir=dir)
        try:
            yield empty_repo
        finally:
            empty_repo.close()


@fixture(name="empty_repo", scope="session")  # type: ignore
def fix_empty_repo(empty_repo_session: DvcRepo) -> Iterator[DvcRepo]:
    """
    Create kedro sample with dvc repo (copying session repo); cwd inside.
    """
    with to_tmp_dir() as dir:
        shutil.copytree(empty_repo_session.root_dir, dir)
        dvc_repo = DvcRepo(root_dir=dir)
        try:
            yield dvc_repo
        finally:
            dvc_repo.close()


def clear_fixture_cache() -> None:
    """
    Removes the cached fixtures.
    """
    if CACHE_DIR.exists():
        shutil.rmtree(CACHE_DIR)
