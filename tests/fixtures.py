"""
Fixtures for kedro-dvc tests.

Several fixtures create or depend on a temporary sample project.

Creating a sample project is time consuming, as it involves installing
dependencies. For this reason, the fixtures are cached.

In particular, session-scoped fixtures are cached, and per-function-scoped
fixtures then copy from the session-scoped fixtures.

Unfortunately, this mechanism is still slow, as the "env" directory is very
large, so takes much time to copy. For this reason, we link to "env" rather
than copy it.

In fact, this doesn't produce a fully working project. In particular,
env/test/bin/ python files have absolute paths which refer to the original
temp directory where the project was created.

TODO: This could be fixed: these links could be made to point to the cached
versions -- then copies of repo would always link to cached version, which
would point to self. Also, kedro-dvc itself can be installed in "dev" mode,
using a relative link to the development repo.

Currently this is only a problem for full end-to-end test of cli via kedro cli
(which is supposed to read the kedro-dvc cli entrypoint at startup).
"""

import pathlib
import shutil
import subprocess
from typing import Iterator

import pytest
from dvc.repo import Repo as DvcRepo
from pytest_cases import fixture

from kedro_dvc.create_sample_project import create_sample_project
from kedro_dvc.kd_context import KDContext

from .util import add_python_path, copy_link_tree, to_memoized_dir, to_tmp_dir

CACHE_DIR = pathlib.Path(__file__).parent / ".fixture-cache"
APP_DIR = pathlib.Path(__file__).parent.parent


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
    with to_memoized_dir(
        cache_dir, ignore_cache=ignore_cache, link=("env",)
    ) as (
        dir,
        save_cache,
    ):
        if save_cache:
            create_sample_project(
                "test",
                kd_repo_path=str(APP_DIR),
                initial_commit_hook=_initial_commit_with_dummy_user,
            )
            for path in pathlib.Path("tmp/test").iterdir():
                shutil.move(str(path), ".")
            shutil.rmtree("tmp")
            save_cache()
        yield dir


@fixture(name="empty_kedro_repo")  # type: ignore
def fix_empty_kedro_repo(
    empty_kedro_repo_session: DvcRepo,
) -> Iterator[pathlib.Path]:
    """
    Create kedro repo (copying session repo); cwd within repo.
    """
    with to_tmp_dir() as dir, add_python_path(pathlib.Path(dir) / "src"):
        copy_link_tree(empty_kedro_repo_session, dir, "env")
        # shutil.copytree(empty_kedro_repo_session, dir, dirs_exist_ok=True)
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
    with to_memoized_dir(
        cache_dir, ignore_cache=ignore_cache, link=("env",)
    ) as (
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
    with to_tmp_dir() as dir, add_python_path(pathlib.Path(dir) / "src"):
        copy_link_tree(empty_repo_session.root_dir, dir, "env")
        # shutil.copytree(empty_repo_session.root_dir, dir, dirs_exist_ok=True)
        dvc_repo = DvcRepo(root_dir=dir)
        try:
            yield dvc_repo
        finally:
            dvc_repo.close()


@fixture(name="kd_context")  # type: ignore
def fix_kd_context(empty_repo: DvcRepo) -> KDContext:
    """
    Return kedro-dvc context for repo.
    """
    return KDContext(empty_repo.root_dir)


def _initial_commit_with_dummy_user() -> None:
    """
    Initial commit of test sample project with dummy user.
    """
    subprocess.check_call(["git", "config", "user.name", "dummy_user"])
    subprocess.check_call(
        ["git", "config", "user.email", "dummy@factfiber.com"]
    )
    subprocess.check_call(["git", "add", "."])
    subprocess.check_call(["git", "commit", "-m", "chore: initial commit"])


def clear_fixture_cache() -> None:  # pragma: no cover
    """
    Removes the cached fixtures.
    """
    if CACHE_DIR.exists():
        shutil.rmtree(CACHE_DIR)
