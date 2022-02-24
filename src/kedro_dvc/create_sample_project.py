import os
import subprocess
import sys


def create_sample_project(
    name: str, from_branch: str = "sample-project-basic"
):  # type: ignore
    if name == "":
        print("usage: python3.8 setup_sample_project.py <name> [from_branch]")
        return

    print("creating sample project $name from branch $from_branch")

    os.makedirs(f"tmp/{name}")
    os.chdir(f"tmp/{name}")
    subprocess.check_call(
        [
            "git",
            "clone",
            "https://github.com/FactFiber/kedro-dvc.git",
            "-b",
            from_branch,
            ".",
        ]
    )
    # using virtualenv.create_environment no longer works
    subprocess.check_call(["virtualenv", f"env/{name}"])
    activate_this_file = "env/test/bin/activate_this.py"
    exec(
        compile(
            open(activate_this_file, "rb").read(), activate_this_file, "exec"
        ),
        dict(__file__=activate_this_file),
    )
    subprocess.check_call(["pip", "install", "--upgrade", "pip"])
    subprocess.check_call(["pip", "install", "-r", "src/requirements.txt"])
    # we should see kedro-dvc commands listed
    print(subprocess.check_output(["pip", "freeze"]))
    print('to use the sample project run "source env/$name/bin/activate"')


if __name__ == "__main__":
    create_sample_project(name=sys.argv[1], from_branch=sys.argv[2])
