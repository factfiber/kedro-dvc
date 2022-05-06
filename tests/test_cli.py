"""
Test basic subcommand capability.
"""
from click.testing import CliRunner

from kedro_dvc import cli


def test_cli() -> None:
    """
    Test the CLI.
    """
    runner = CliRunner()
    result = runner.invoke(cli.kedro_dvc_cli, "--help")
    assert result.exit_code == 0
    assert cli.kedro_dvc_cli.__doc__ in result.stdout
