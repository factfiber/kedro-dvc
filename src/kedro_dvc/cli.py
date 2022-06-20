import pathlib
from typing import Any

import click
from dvc.exceptions import NotDvcRepoError
from kedro.framework.startup import ProjectMetadata

from kedro_dvc import exceptions, kd_context, setup


@click.group(name="kedro-dvc")  # type: ignore
def kedro_dvc_cli() -> None:  # pragma: no cover
    """Kedro-DVC integration."""
    pass


@kedro_dvc_cli.group()  # type: ignore
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
    try:
        ctx.obj = kd_context.KDContext(install_dvc=install_dvc, **options)
    except exceptions.AlreadyInstalled:
        raise click.ClickException(
            "Kedro-DVC is already installed. Use `kedro dvc update` to update."
        )
    except NotDvcRepoError:
        raise click.ClickException(
            "DVC is not installed. Use `kedro dvc install` to install."
        )


@dvc.command(name="install")  # type: ignore
@click.pass_obj  # type: ignore
def install(context: kd_context.KDContext) -> None:
    """
    Install kedro-dvc in kedro project

    Note: just like update command, but expects DVC repo to be absent.
    """
    setup.install_kedro_dvc(context)
    print(
        "Kedro-DVC installed successfully. "
        + f"Configuration under {context.conf_path}"
    )


@dvc.command(name="update")  # type: ignore
@click.pass_obj  # type: ignore
def update(context: kd_context.KDContext) -> None:
    """
    Update kedro-dvc in kedro project.

    Note: just like install command, but expects DVC repo to be present.
    """
    setup.install_kedro_dvc(context)
    print(
        "Kedro-DVC updated successfully. "
        + f"Configuration under {context.conf_path}"
    )
