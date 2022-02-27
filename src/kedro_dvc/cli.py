import click

# from kedro.framework.session import KedroSession


@click.group(name="dvc")  # type: ignore
def dvc() -> None:  # pragma: no cover
    """Kedro-DVC integration."""
    pass


# @dvc.command()
# @click.pass_obj
# def hello(metadata):
#     """Display the pipeline in JSON format"""
#     # session = KedroSession.create(metadata.package_name)
#     # context = session.load_context()
#     # print(context.pipeline.to_json())
#     print("HELLO", metadata)
