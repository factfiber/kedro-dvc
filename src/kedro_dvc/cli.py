import pathlib
from typing import Any

import click
from kedro.framework.startup import ProjectMetadata

from kedro_dvc import kd_context, setup


@click.group(name="kedro-dvc")  # type: ignore
def kedro_dvc_cli() -> None:  # pragma: no cover
    """Kedro-DVC integration."""
    pass


@kedro_dvc_cli.group(name="dvc")  # type: ignore
@click.pass_context  # type: ignore
def dvc(ctx: click.Context) -> None:
    """
    Kedro DVC commands.
    """
    # convert kedro-passed metadata to kedro-dvc context
    metadata: ProjectMetadata = ctx.obj
    options: Any
    if metadata is None:
        options = dict(project_dir=pathlib.Path.cwd())
    # NB: using via kedro cli currently not supported by test suite
    else:  # pragma: no cover
        options = dict(metadata=metadata)
    install_dvc = ctx.invoked_subcommand == "install"
    ctx.obj = kd_context.KDContext(install_dvc=install_dvc, **options)


@dvc.command(name="install")  # type: ignore
@click.pass_obj  # type: ignore
def install(context: kd_context.KDContext) -> None:
    """
    Install kedro-dvc in kedro project
    """
    setup.install_kedro_dvc(context)
    print(
        "Kedro-DVC installed successfully. "
        + f"Configuration under {context.conf_path}"
    )
