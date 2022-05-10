import pathlib
from typing import Any, Iterable, Iterator, Mapping, NamedTuple

import anyconfig

from ..kd_context import KDContext
from ..logger import log
from .constants import DEFAULT_ENV


class CatalogEntry(NamedTuple):
    """
    Kedro catalog entry.
    """

    path: pathlib.Path
    name: str
    item: Mapping[str, Any]


def iter_catalog_files(
    context: KDContext, env: Iterable[str] = DEFAULT_ENV, silent: bool = True
) -> Iterator[pathlib.Path]:
    """
    Iterate over kedro catalog files.
    """
    for k_env in env:
        env_path = context.conf_path / k_env
        if not env_path.exists():
            if not silent:
                log.info("Environment %s does not exist", k_env)
            continue
        for path in env_path.glob("catalog.*"):
            yield path
        for path in env_path.rglob("catalog/*"):
            yield path


def iter_catalog_entries(
    context: KDContext, env: Iterable[str] = DEFAULT_ENV, silent: bool = True
) -> Iterator[CatalogEntry]:
    """
    Iterate over kedro catalog entries.
    """
    for path in iter_catalog_files(context, env, silent):
        conf = anyconfig.load(path)
        for name, item in conf.items():
            yield CatalogEntry(path, name, item)


def iter_kd_dvc_files(
    context: KDContext, env: Iterable[str] = DEFAULT_ENV, silent: bool = True
) -> Iterator[pathlib.Path]:
    """
    Iterate over kedro dvc files in kedro conf environments.
    """
    for path in iter_catalog_files(context, env, silent):
        for file in path.parent.glob("dvc/*.dvc"):
            yield file
