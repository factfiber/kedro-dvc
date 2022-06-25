import shutil
from pathlib import Path

import pytest
from dvc.repo import Repo as DvcRepo
from kedro.framework.project import settings
from pytest_mock import MockerFixture

from kedro_dvc import kd_context, setup

from ..fixtures import fix_dvc_repo_session as fix_dvc_repo_session  # noqa
from ..fixtures import fix_empty_kedro_repo as fix_empty_kedro_repo  # noqa
from ..fixtures import (  # noqa
    fix_empty_kedro_repo_session as fix_empty_kedro_repo_session,
)
from ..fixtures import fix_empty_repo as fix_empty_repo  # noqa
from ..fixtures import fix_empty_repo_session as fix_empty_repo_session  # noqa
from ..fixtures import fix_tmp_dir as fix_tmp_dir  # noqa
from ..fixtures import fix_tmp_dir_session as fix_tmp_dir_session  # noqa
from .check_setup import check_repo_setup


def test_install_kedro_dvc_in_kedro_repo(empty_kedro_repo: Path) -> None:
    """
    Test setup with existing kedro, but no dvc or kedro-dvc.
    """
    context = kd_context.KDContext(
        project_dir=empty_kedro_repo, install_dvc=True
    )
    setup.install_kedro_dvc(context)
    check_repo_setup(context)


def test_install_kedro_dvc_in_kedro_nonstandard_conf(
    empty_kedro_repo: Path, mocker: MockerFixture
) -> None:
    """
    Test setup with existing kedro, but no dvc or kedro-dvc; conf/ not standard.
    """
    alt = "conf_alt"
    conf_dir = empty_kedro_repo / "conf"
    alt_conf = empty_kedro_repo / alt
    shutil.move(str(conf_dir), alt_conf)

    mocker.patch.object(settings._CONF_SOURCE, "default", alt)
    context = kd_context.KDContext(
        project_dir=empty_kedro_repo, install_dvc=True
    )
    assert context.conf_path == alt_conf
    setup.install_kedro_dvc(context)
    check_repo_setup(context)


def test_install_kedro_dvc_idempotent(empty_repo: DvcRepo) -> None:
    """
    Test that setup is idempotent.
    """
    # first: try w/ dvc already existing, but no conf
    context = kd_context.KDContext(project_dir=empty_repo.root_dir)
    setup.install_kedro_dvc(context)
    check_repo_setup(context)

    # then: try w/ dvc already existing and conf
    setup.install_kedro_dvc(context)
    check_repo_setup(context)


def test_install_kedro_dvc_not_in_kedro_repo(tmp_dir: Path) -> None:
    """
    Test setup with no kedro.
    """
    with pytest.raises(RuntimeError):
        context = kd_context.KDContext(project_dir=tmp_dir)
        setup.install_kedro_dvc(context)


def test_install_kedro_dvc_kedro_conf_missing(empty_kedro_repo: Path) -> None:
    """
    Test setup with no kedro conf.
    """
    conf_dir = empty_kedro_repo / "conf"
    shutil.rmtree(conf_dir)
    with pytest.raises(RuntimeError):
        context = kd_context.KDContext(
            project_dir=empty_kedro_repo, install_dvc=True
        )
        setup.install_kedro_dvc(context)
