import os
import pathlib
import shutil
import subprocess
from typing import Sequence

import click
import virtualenv
from pygit2 import clone_repository, init_repository


class InvalidName(ValueError):
    """
    Name of sample project invalid.
    """


class AlreadyExists(KeyError):
    """
    Sample project already exists.
    """


class CantCheckout(KeyError):
    """
    Couldn't check out sample branch.
    """


DEFAULT_SAMPLE_BRANCH = "sample-project-basic"


def create_sample_project(
    name: str,
    from_branch: str = DEFAULT_SAMPLE_BRANCH,
    kd_repo_path: str = "../..",
    preserve_git: bool = False,
) -> None:
    """
    Create a kedro sample project from repo branch with skeleton.

    Args:
        name: name of sample project
        from_branch: name of branch for kedro starter
        kd_repo_path: path to kedro repo
        preserve_git: if True, don't replace git repo with newly initialized
    """
    if name == "":
        raise InvalidName("pass valid directory name")
    q_dir = pathlib.Path(f"tmp/{name}")
    if q_dir.exists():
        raise AlreadyExists(f"Path exists: {q_dir}")

    q_dir.mkdir(parents=True)
    try:
        os.chdir(q_dir)
        try:
            clone_repository(
                "https://github.com/FactFiber/kedro-dvc.git",
                ".",
                checkout_branch=from_branch,
            )
        except Exception as exc:
            raise CantCheckout(f"result: {exc}")
        if not preserve_git:
            shutil.rmtree(".git")
            init_repository(".")
        virtualenv.cli_run([f"env/{name}"])
        # # using virtualenv.create_environment no longer works
        activate_this_file = f"env/{name}/bin/activate_this.py"
        _exec_file(activate_this_file)
        subprocess.check_call(["pip", "install", "--upgrade", "pip"])
        if str(kd_repo_path) != "../..":
            # for local dev, we install in tmp/{name} under project
            # if we are installing elsewhere, fix requirements for path
            new_req = subprocess.check_output(
                ["tail", "-n", "+2", "src/requirements.txt"]
            ).decode()
            new_req = f"-e {kd_repo_path}\n{new_req}"
            pathlib.Path("src/requirements.txt").write_text(new_req)
        subprocess.check_call(["pip", "install", "-r", "src/requirements.txt"])
        subprocess.check_call(["git", "add", "."])
        subprocess.check_call(["git", "commit", "-m", "chore: initial commit"])
    finally:
        # make sure we leave shell, return to original directory after finished
        try:
            subprocess.call(["deactivate"])
        except FileNotFoundError:  # pragma: no cover
            pass
        os.chdir("../..")


def _exec_file(activate_this_file: str) -> None:
    exec(
        compile(
            open(activate_this_file, "rb").read(),
            activate_this_file,
            "exec",
        ),
        dict(__file__=activate_this_file),
    )


@click.command(name="create-sample-project")  # type: ignore
@click.argument("name")  # type: ignore
@click.argument(
    "branch", required=False, default=DEFAULT_SAMPLE_BRANCH  # type: ignore
)
@click.argument("kd_path", required=False, default="../..")  # type: ignore
@click.option(
    "--preserve-git",
    is_flag=True,
    default=False,
    help="preserve git repo w/ link to origin",
)  # type: ignore
@click.pass_context  # type: ignore
def create_sample_project_cmd(
    ctx: click.Context, name: str, branch: str, kd_path: str, preserve_git: bool
) -> None:
    """
    Create sample project in tmp/<name>.

    NAME: name of sample project subdirectory
    BRANCH: name of repo branch with sample content
    """
    print(f"creating sample project {name} from branch {branch}")
    try:
        create_sample_project(
            name,
            from_branch=branch,
            kd_repo_path=kd_path,
            preserve_git=preserve_git,
        )
    except CantCheckout:
        param = _get_param(ctx.command.params, "branch")
        raise click.BadParameter("Can't check out branch", param=param)
    except AlreadyExists as exc:
        raise click.UsageError(message=str(exc))
    print(f'To use the sample project run "source env/{name}/bin/activate"')


def _get_param(
    param_list: Sequence[click.Parameter], name: str
) -> click.Parameter:
    return list(filter(lambda p: p.name == "branch", param_list))[0]


if __name__ == "__main__":  # pragma: no cover
    create_sample_project_cmd()
