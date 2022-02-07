# Ketro-DVC

Kedro-DVC integration to track and distribute experiments.

We are just starting out. See [the design document](./doc/design.md) for plans.

## Contributing

**NOTE**: install hack for the moment until kedro version 0.18 which
supports python 3.9.

```shell
git clone git@github.com:FactFiber/kedro-dvc.git
cd kedro-dvc
poetry run pre-commit install && poetry run pre-commit install ----hook-type commit-msg
poetry env use python3.9
poetry install
poetry shell
pip install kedro
...
poetry run pytest
```

This repository uses [semantic-release](https://semantic-release.gitbook.io/semantic-release/) via [python-semantic-release](https://github.com/relekang/python-semantic-release/blob/master/docs/automatic-releases/github-actions.rst). A high major version number **is not** a sign of maturity. This documentation will be updated when the repo does anything useful.

Commit messages use the [commitizen angular style](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-format), which is enforced in the pre-commit hook and the repo CI.
