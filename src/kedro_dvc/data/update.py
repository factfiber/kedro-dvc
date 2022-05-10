"""
Maintain correspondence between catalog and '.dvc' files.

Docs on kedro catalog:
1. Location: https://kedro.readthedocs.io/en/stable/kedro_project_setup/configuration.html?highlight=catalog%20subdirectory#local-and-base-configuration-environments

2. Contents:
"""  # noqa
import os
import pathlib
from typing import Dict, Iterable, List, Optional, Set

import anyconfig

from kedro_dvc.kd_context import KDContext
from kedro_dvc.logger import log

from .catalog import CatalogEntry, iter_catalog_entries, iter_kd_dvc_files
from .constants import DEFAULT_ENV


def update(
    context: KDContext,
    env: Iterable[str] = DEFAULT_ENV,
    remove_obsolete: bool = False,
    update_existing: bool = True,
    commit: bool = True,
) -> None:
    """
    Update '.dvc' files to correspond to kedro catalog.

    Args:
        context: kedro-dvc context
        env: environments to update
        remove_obsolete: remove obsolete dvc files not corresponding to kedro catalog
        update_existing: update existing dvc files, overwriting existing metadata
        commit: commit changes to dvc repo
    """
    dvc_path_entries: Dict[pathlib.Path, Set[str]] = {}

    gitignore_lines: List[str] = []
    gitignore = context.project_path / ".gitignore"
    if gitignore.exists():
        gitignore_lines = gitignore.read_text().split("\n")

    for entry in iter_catalog_entries(context, env):
        dvc_path_entries.setdefault(entry.path, set()).add(entry.name)
        w_dir = pathlib.Path(
            os.path.relpath(context.project_path, entry.path.parent / "dvc")
        )
        update_config_item(
            context,
            entry,
            w_dir,
            gitignore_lines=gitignore_lines,
            update_existing=update_existing,
            commit=commit,
        )

    # remove dvc files not corresponding to kedro catalog
    for dvc_path in iter_kd_dvc_files(context, env):
        cat_path = dvc_path.parent.parent / "catalog.yml"
        if cat_path in dvc_path_entries:
            entries = dvc_path_entries[cat_path]
            if dvc_path.stem in entries:
                continue
        if remove_obsolete:
            log.debug("Removing obsolete file %s", dvc_path)
            dvc_entry = anyconfig.load(dvc_path, ac_parser="yaml")
            if commit:
                # remove ".dvc" from dvc, .gitignore
                context.dvc_repo.remove(str(dvc_path))
            else:
                dvc_path.unlink()

            for out in dvc_entry["outs"]:
                filepath = out["path"]
                if filepath in gitignore_lines:
                    gitignore_lines.remove(filepath)
        else:
            log.debug("Skipping obsolete file %s", dvc_path)

    if len(gitignore_lines) > 0:
        (context.project_path / ".gitignore").write_text(
            "\n".join(gitignore_lines)
        )


def update_config_item(
    context: KDContext,
    entry: CatalogEntry,
    w_dir: pathlib.Path,
    gitignore_lines: List[str],
    update_existing: bool = False,
    commit: bool = True,
) -> Optional[str]:
    """
    Update '.dvc' file to correspond to kedro catalog item.

    Returns dvc path that was updated. If no update was performed, returns None.

    Note: kedro stores paths as relative to the project root; dvc stores paths
    as relative to the location of the '.dvc' file. However, it allows
    optional 'wdir' parameter to be specified, which is relative path from
    .dvc file to the working directory to use with filepath. We set wdir to
    path to project root, and leave filepath as is from kedro.

    Args:
        context: kedro-dvc context
        entry: catalog entry
        w_dir: working directory entry: path from dvc to repo root.
        update_existing: update existing dvc files, overwriting existing
        metadata
        commit: commit changes to dvc repo
    """
    filepath = entry.item.get("filepath")
    if not filepath:
        log.debug("No filepath found in %s", str(entry.path))
        return None
    # TODO: support via import-url?
    # protocol = filepath.split(":", 1)[0]
    # if protocol != 'file:' and protocol in fsspec.known_protocols:

    dataset_type = entry.item["type"]
    dvc_entry = dict(
        outs=[dict(path=filepath)],
        wdir=str(w_dir),
        meta=dict(
            type=dataset_type,
            catalogName=entry.name,
        ),
    )
    dvc_path = entry.path.parent / "dvc" / f"{entry.name}.dvc"
    if dvc_path.exists():
        if not update_existing:
            log.debug("Skipping existing file %s", dvc_path)
            return None
        old_dvc = anyconfig.load(dvc_path, ac_parser="yaml")
        out_paths = set((out["path"] for out in old_dvc["outs"]))
        if filepath not in out_paths:
            for path in out_paths:
                if path in gitignore_lines:
                    gitignore_lines.remove(path)
        anyconfig.merge(old_dvc, dvc_entry, ac_merge=anyconfig.MS_DICTS)
    anyconfig.dump(dvc_entry, dvc_path, ac_parser="yaml")

    # git should ignore data file
    if filepath not in gitignore_lines:
        gitignore_lines.append(filepath)

    if commit:
        log.debug("Writing file %s", dvc_path)
        context.dvc_repo.commit(str(dvc_path), force=True)
    return str(dvc_path)
