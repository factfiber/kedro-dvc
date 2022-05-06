import pathlib

import pytest
from dvc.repo import NotDvcRepoError
from dvc.repo import Repo as DvcRepo
from kedro.framework.startup import _get_project_metadata

from kedro_dvc import kd_context

from .fixtures import fix_dvc_repo_session as fix_dvc_repo_session  # noqa
from .fixtures import fix_empty_kedro_repo as fix_empty_kedro_repo  # noqa
from .fixtures import (  # noqa
    fix_empty_kedro_repo_session as fix_empty_kedro_repo_session,
)
from .fixtures import fix_empty_repo as fix_empty_repo  # noqa
from .fixtures import fix_empty_repo_session as fix_empty_repo_session  # noqa
from .fixtures import fix_tmp_dir_session as fix_tmp_dir_session  # noqa


def test_kd_context(empty_repo: DvcRepo) -> None:
    """
    Test kedro dvc context init.
    """
    context = kd_context.KDContext(empty_repo.root_dir)
    check_context(context, empty_repo.root_dir)


def test_kd_context_defaults_to_cwd(empty_repo: DvcRepo) -> None:
    """
    Test kedro dvc context init with no project dir.
    """
    context = kd_context.KDContext()
    check_context(context, empty_repo.root_dir)


def test_kd_context_provide_metadata(empty_repo: DvcRepo) -> None:
    """
    Test kedro dvc context init with metadata.
    """
    metadata = _get_project_metadata(empty_repo.root_dir)
    context = kd_context.KDContext(metadata=metadata)
    check_context(context, empty_repo.root_dir)


def test_kd_context_no_dvc(empty_kedro_repo: str) -> None:
    """
    Test kedro dvc context init: fails if no dvc by default.
    """
    with pytest.raises(NotDvcRepoError):
        kd_context.KDContext(empty_kedro_repo, install_dvc=False)  # type: ignore


def test_kd_context_install_dvc(empty_kedro_repo: str) -> None:
    """
    Test kedro dvc context init: no dvc can install.
    """
    context = kd_context.KDContext(empty_kedro_repo, install_dvc=True)  # type: ignore
    check_context(context, str(empty_kedro_repo))


def check_context(context: kd_context.KDContext, repo_dir: str) -> None:
    """
    Check kedro dvc context after init.
    """
    repo_path = pathlib.Path(repo_dir)
    assert context.project_path == repo_path
    assert context.project_name == "basic-project"
    assert context.dvc_repo is not None
    assert (
        pathlib.Path(context.dvc_repo.root_dir).resolve() == repo_path.resolve()
    )
    assert context.conf_path == pathlib.Path(repo_dir) / "conf"
