import logging
import pathlib

import anyconfig
import pytest
from dvc.exceptions import PathMissingError
from dvc.repo import Repo as DvcRepo

from kedro_dvc import data, kd_context
from kedro_dvc.data.catalog import iter_catalog_entries

from ..datautil import add_catalog_entry
from ..fixtures import (  # noqa
    fix_dvc_repo_session,
    fix_empty_kedro_repo_session,
    fix_empty_repo,
    fix_empty_repo_session,
    fix_tmp_dir_session,
)


def test_data_update_single(empty_repo: DvcRepo) -> None:
    """
    Test data update with single file.
    """
    context = kd_context.KDContext(project_dir=empty_repo.root_dir)
    add_catalog_entry(
        context,
        "base",
        "test",
        "data/test_data_update_single.txt",
    )
    data.update(context, env=["base"])
    check_dvc_status(context, 1)


def test_data_update_single_no_commit(empty_repo: DvcRepo) -> None:
    """
    Test data update with single file.
    """
    commit = False
    context = kd_context.KDContext(project_dir=empty_repo.root_dir)
    add_catalog_entry(
        context,
        "base",
        "test",
        "data/test_data_update_single.txt",
    )
    data.update(context, env=["base"], commit=commit)
    check_dvc_status(context, 1, commit=commit)


def test_data_update_single_no_data(empty_repo: DvcRepo) -> None:
    """
    Test data update with single file.
    """
    context = kd_context.KDContext(project_dir=empty_repo.root_dir)
    add_catalog_entry(
        context,
        "base",
        "test",
        None,
    )
    data.update(context, env=["base"])
    check_dvc_status(context, 0)


def test_data_update_remove_obsolete(
    empty_repo: DvcRepo, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Test data update with single file.
    """
    context = kd_context.KDContext(project_dir=empty_repo.root_dir)
    datafile = "data/test_data_update_single.txt"
    add_catalog_entry(
        context,
        "base",
        "test",
        datafile,
    )
    data.update(context, env=["base"])
    entry = iter_catalog_entries(context).__next__()
    entry.path.unlink()
    entry.path.write_text("")
    with caplog.at_level(logging.DEBUG, "kedro-dvc"):
        data.update(context, env=["base"], remove_obsolete=True)
        assert pathlib.Path(entry.item["filepath"]).exists()
        assert not (entry.path.parent / "dvc" / (entry.name + ".dvc")).exists()
    # assert "Removing obsolete file foo" in caplog.text

    with pytest.raises(PathMissingError):
        context.dvc_repo.ls(
            str(context.project_path),
            path="data",
            dvc_only=True,
        )

    assert datafile not in (context.project_path / ".gitignore").read_text()


def test_data_update_remove_obsolete_no_commit(
    empty_repo: DvcRepo, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Test data update with single file.
    """
    context = kd_context.KDContext(project_dir=empty_repo.root_dir)
    datafile = "data/test_data_update_single.txt"
    add_catalog_entry(
        context,
        "base",
        "test",
        datafile,
    )
    data.update(context, env=["base"])
    entry = iter_catalog_entries(context).__next__()
    entry.path.unlink()
    entry.path.write_text("")
    with caplog.at_level(logging.DEBUG, "kedro-dvc"):
        data.update(context, env=["base"], remove_obsolete=True, commit=False)
        assert pathlib.Path(entry.item["filepath"]).exists()
        assert not (entry.path.parent / "dvc" / (entry.name + ".dvc")).exists()
    # assert "Removing obsolete file foo" in caplog.text

    with pytest.raises(PathMissingError):
        context.dvc_repo.ls(
            str(context.project_path),
            path="data",
            dvc_only=True,
        )
    status = context.dvc_repo.status()
    assert len(status) == 0

    assert datafile not in (context.project_path / ".gitignore").read_text()


def test_data_update_single_move(empty_repo: DvcRepo) -> None:
    """
    Test data update with single file, then update again to move.
    """
    context = kd_context.KDContext(project_dir=empty_repo.root_dir)
    add_catalog_entry(
        context,
        "base",
        "test",
        "data/test_data_update_single.txt",
    )
    data.update(context, env=["base"])
    add_catalog_entry(
        context,
        "base",
        "test",
        "data/test_data_update_single_2.txt",
    )
    data.update(context, env=["base"], update_existing=True)
    check_dvc_status(context, 1)


def test_data_update_single_move_skip(empty_repo: DvcRepo) -> None:
    """
    Test data update with single file, then update again to move.
    """
    context = kd_context.KDContext(project_dir=empty_repo.root_dir)
    add_catalog_entry(
        context,
        "base",
        "test",
        "data/test_data_update_single.txt",
    )
    data.update(context, env=["base"])
    add_catalog_entry(
        context,
        "base",
        "test",
        "data/test_data_update_single_2.txt",
    )
    entry = iter_catalog_entries(context).__next__()
    assert entry.item["filepath"] == "data/test_data_update_single_2.txt"
    data.update(context, env=["base"], update_existing=False)
    dvc_path = entry.path.parent / "dvc" / (entry.name + ".dvc")
    dvc = anyconfig.load(dvc_path, ac_parser="yaml")
    assert dvc["outs"][0]["path"] == "data/test_data_update_single.txt"


def test_data_update_skip_obsolete(
    empty_repo: DvcRepo, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Test data update with single file.
    """
    context = kd_context.KDContext(project_dir=empty_repo.root_dir)
    datafile = "data/test_data_update_single.txt"
    add_catalog_entry(
        context,
        "base",
        "test",
        datafile,
    )
    data.update(context, env=["base"])
    entry = iter_catalog_entries(context).__next__()
    entry.path.unlink()
    entry.path.write_text("")
    with caplog.at_level(logging.DEBUG, "kedro-dvc"):
        data.update(context, env=["base"], remove_obsolete=False)
        assert pathlib.Path(entry.item["filepath"]).exists()
        assert (entry.path.parent / "dvc" / (entry.name + ".dvc")).exists()
    # assert "Removing obsolete file foo" in caplog.text

    assert (
        len(
            context.dvc_repo.ls(
                str(context.project_path),
                path="data",
                dvc_only=True,
            )
        )
        == 1
    )


def check_dvc_status(
    context: kd_context.KDContext, n_entries: int, commit: bool = True
) -> None:
    """
    Check that dvc repo state reflects data in kedro catalog.
    """
    catalog = list(iter_catalog_entries(context))
    if n_entries == 0:
        with pytest.raises(PathMissingError):
            context.dvc_repo.ls(
                str(context.project_path),
                path="data",
                dvc_only=True,
            )
        for entry in catalog:
            assert not (
                entry.path.parent / "dvc" / (entry.name + ".dvc")
            ).exists()

        return
    info = context.dvc_repo.ls(
        str(context.project_path),
        path="data",
        dvc_only=True,
        # rev="HEAD",
    )
    data_files = [item["path"] for item in info]
    assert len(data_files) == n_entries
    assert len(data_files) == len(catalog)
    status = context.dvc_repo.status()
    if not commit:
        assert len(status) == len(catalog)
    else:
        assert len(status) == 0

    gitignore = pathlib.Path(".gitignore").read_text()
    for entry in catalog:
        dvc_file = entry.path.parent / "dvc" / (entry.name + ".dvc")

        dvc = anyconfig.load(dvc_file, ac_parser="yaml")
        assert len(dvc["outs"]) == 1
        out = dvc["outs"][0]
        assert out["path"] == str(entry.item["filepath"])
        assert out["path"] in gitignore
        if entry.path.name == "catalog.yml":
            assert dvc["wdir"] == "../../.."
        else:
            # case: catalog at env/<name>/catalog/<name>.yaml
            assert dvc["wdir"] == "../../../.."
        assert dvc["meta"] == dict(
            type=entry.item["type"], catalogName=entry.name
        )
        assert pathlib.Path(out["path"]).name in data_files
        if not commit:
            # dvc file should be in status as modified
            dvc_file_rel = str(dvc_file.relative_to(context.project_path))
            assert dvc_file_rel in status
            status_item = status[dvc_file_rel]
            assert len(status_item) == 1
            changed = status_item[0]["changed outs"]
            assert len(changed) == 1
            key, key_status = changed.popitem()
            assert key == entry.item["filepath"]
            assert key_status == "modified"
        else:
            assert "md5" in out
            assert "size" in out
