import os
import pathlib
from typing import Optional, Union

import anyconfig

from kedro_dvc.kd_context import KDContext


def add_catalog_entry(
    context: KDContext,
    env: str,
    entry_name: str,
    data_path: Optional[Union[str, os.PathLike[str]]],
    catalog_name: str = "catalog",
) -> None:
    """
    Add catalog entry & data file to kedro environment.
    """
    if data_path is not None:
        data_path = pathlib.Path(data_path)
    env_path = context.conf_path / env
    env_path.mkdir(exist_ok=True)
    if catalog_name == "catalog":
        catalog_path = env_path / (catalog_name + ".yml")
    else:
        # case: catalog name must terminate with catalog/<somename>.yaml
        # we chose <name>/catalog/<name>.yaml
        catalog_path = (
            env_path / catalog_name / "catalog" / (catalog_name + ".yml")
        )
    catalog_path.parent.mkdir(exist_ok=True, parents=True)
    if catalog_path.exists():
        conf = anyconfig.load(catalog_path)
    else:
        conf = {}
    if data_path is not None:
        conf[entry_name] = dict(
            type="text.TextDataSet",
            filepath=str(data_path),
        )
    else:
        conf[entry_name] = dict(type="text.TextDataSet")
    anyconfig.dump(conf, catalog_path)
    if data_path is not None:
        data_path.parent.mkdir(exist_ok=True, parents=True)
        data_path.write_text("Example data: {}".format(entry_name))
