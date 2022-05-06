"""
Create kedro-dvc project or install in existing kedro project.
"""
from kedro_dvc.kd_context import KDContext


class KedroDVCContext:
    """
    Wrapper for kedro context with access to
    """


def install_kedro_dvc(
    kd_context: KDContext,
) -> None:
    """Install kedro-dvc in a kedro project.

    Args:
        project_dir: Path to the root of the kedro project.
    """
    # context = KDContext(project_dir, metadata, install_dvc=True)
    _setup_kd_conf_root(kd_context)
    _setup_kd_conf_catalog(kd_context)
    _setup_kd_conf_pipelines(kd_context)


def _setup_kd_conf_root(kd_context: KDContext) -> None:
    """
    Create kedro-dvc config root.
    """
    kd_root = kd_context.conf_path / "dvc"
    kd_root.mkdir(parents=True, exist_ok=True)
    readme = kd_root / "Readme.md"
    if not readme.exists():
        readme.write_text(
            _README_TEMPLATE.format(project_name=kd_context.project_name)
        )
    pipelines_dir = kd_root / "pipelines"
    pipelines_dir.mkdir(parents=True, exist_ok=True)


def _setup_kd_conf_catalog(context: KDContext) -> None:
    """
    Create kedro-dvc config catalog.
    """
    # conf_path /= "catalog.yml"
    # conf_path.touch()


def _setup_kd_conf_pipelines(context: KDContext) -> None:
    """
    Create kedro-dvc config pipelines.
    """
    # conf_path /= "pipelines.yml"
    # conf_path.touch()


_README_TEMPLATE = """
# Kedro-DVC Configuration for {project_name}

This is the kedro-dvc configuration for {project_name}.

The ".dvc" files corresponding to catalog entries are stored in "dvc/"
subdirectory of each kedro environment.

The piplines are stored in ./pipelines/. Under each pipeline, DVC lock files
are written in subdirectories corresponding to each sequence of kedro
environments used. For instance, when a pipeline "foo" is run in default
'base' and 'local' environments, the pipeline itself is in
"./pipelines/foo/foo-dvc.yaml" and the lock file is in
"./pipelines/foo/base/local/foo-dvc.lock" together with a symbolic link to the
pipeline itself.
"""
