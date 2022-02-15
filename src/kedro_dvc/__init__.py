__version__ = "0.3.0"

import click
from kedro.framework.session import KedroSession


@click.group(name="JSON")
def commands():
    """Kedro plugin for printing the pipeline in JSON format"""
    pass


@commands.command()
@click.pass_obj
def to_json(metadata):
    """Display the pipeline in JSON format"""
    session = KedroSession.create(metadata.package_name)
    context = session.load_context()
    print(context.pipeline.to_json())
