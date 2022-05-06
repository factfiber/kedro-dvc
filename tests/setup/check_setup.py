from kedro_dvc import kd_context, setup


def check_repo_setup(context: kd_context.KDContext) -> None:
    """
    Check that setup was successful.
    """
    assert context.conf_path.exists()
    kd_conf_path = context.conf_path / "dvc"
    assert kd_conf_path.exists()
    readme_path = kd_conf_path / "Readme.md"
    assert readme_path.exists()
    assert readme_path.read_text() == setup._README_TEMPLATE.format(
        project_name=context.project_name
    )
    pipelines_path = kd_conf_path / "pipelines"
    assert pipelines_path.exists()
    assert pipelines_path.is_dir()
