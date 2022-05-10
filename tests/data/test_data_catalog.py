"""
Test utilities for reading kedro catalog.
"""
import logging
import pathlib

import pytest

from kedro_dvc.data.catalog import iter_catalog_entries
from kedro_dvc.kd_context import KDContext

from ..datautil import add_catalog_entry
from ..fixtures import (  # noqa
    fix_dvc_repo_session,
    fix_empty_kedro_repo_session,
    fix_empty_repo,
    fix_empty_repo_session,
    fix_kd_context,
    fix_tmp_dir_session,
)


def test_iter_catalog_empty(kd_context: KDContext) -> None:
    """
    Test iter_catalog with empty catalog.
    """
    assert list(iter_catalog_entries(kd_context)) == []


def test_iter_catalog_single(kd_context: KDContext) -> None:
    """
    Test iter_catalog with single entry.
    """
    datapath = pathlib.Path("data/test_data_catalog.txt")
    add_catalog_entry(
        kd_context,
        "base",
        "test",
        datapath,
    )
    entries = list(iter_catalog_entries(kd_context))
    assert len(entries) == 1
    assert entries[0].name == "test"
    assert str(entries[0].path).endswith("conf/base/catalog.yml")
    assert str(entries[0].item["filepath"]) == str(datapath)


def test_iter_catalog_single_nested(kd_context: KDContext) -> None:
    """
    Test iter_catalog with single entry.
    """
    datapath = pathlib.Path("data/test_data_catalog.txt")
    add_catalog_entry(kd_context, "base", "test", datapath, catalog_name="foo")
    entries = list(iter_catalog_entries(kd_context))
    assert len(entries) == 1
    assert entries[0].name == "test"
    assert str(entries[0].path).endswith("conf/base/foo/catalog/foo.yml")
    assert str(entries[0].item["filepath"]) == str(datapath)


def test_iter_catalog_env_not_exists(
    kd_context: KDContext, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Test iter_catalog with non-existent environment.
    """
    datapath = pathlib.Path("data/test_data_catalog.txt")
    add_catalog_entry(
        kd_context,
        "base",
        "test",
        datapath,
    )
    with caplog.at_level(logging.INFO, logger="kedro_dvc"):
        entries = list(
            iter_catalog_entries(kd_context, env=["non-existent"], silent=False)
        )
        assert len(entries) == 0
        assert "Environment non-existent does not exist" in caplog.text
