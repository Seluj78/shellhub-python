# [Shellhub Python SDK]

[![codecov](https://codecov.io/gh/Seluj78/shellhub-python/graph/badge.svg?token=FPWuNDtwdz)](https://codecov.io/gh/Seluj78/shellhub-python)

* [What is it](#what-is-it)
* [Installation](#installation)
   * [Locally](#locally)
      * [Create a virtual environment](#create-a-virtual-environment)
      * [Activate it](#activate-it)
      * [Install the requirements](#install-the-requirements)
      * [Edit the env file with the correct parametters](#edit-the-env-file-with-the-correct-parametters)
      * [Install the module locally](#install-the-module-locally)
* [Deployment](#deployment)
* [Repository rules](#repository-rules)
* [Code owner](#code-owner)


## What is it

This repository contains the source code to a Shellhub (https://shellhub.io) Python SDK. It is used to interact with the Shellhub API.

Tested with shellhub `v0.14.1`

Open to all contributions, wether it is a bug fix, a new feature or a documentation improvement, or even a better way to do things.

## Installation

From pip: `pip install shellhub`

### Locally

#### Create a virtual environment
```shell
python3.11 -m venv venv
```
You can use any version starting python `3.8`

#### Activate it
```shell
source venv/bin/activate
```

#### Install the requirements
```shell
pip install -r requirements-dev.txt
```

#### Activate the pre-commit

```shell
pip install pre-commit
pre-commit install
pre-commit install --hook commit-msg
```

#### Edit the env file with the correct parameters
```shell
vim .env
```

#### Install the module locally
```shell
python setup.py develop
```

## Deployment

In your Pull Request, make sure you have modified the version in `__init__.py` according to semver.org
Once done, and the PR is merged, you need to push on the `main` branch a tag with a `v` prefix

For example: If the `__version__` in `__init__.py` is `1.0.0`, you need to tag the last commit on main with your changes with `v1.0.0`

Procedure:

- Merge the PR
- `git checkout main`
- `git pull`
- `git tag vx.x.x`
- `git push --tags`

Once done, go to the repository, find the tag and create a release from the tag. In the description, explain what has changed so we can easily see what has been done
A few seconds after, the package should be up in the pypi server.

## Repository rules

When contributing:

- Create a branch based on `main`
- Code on it and commit
- Create PR
- Wait for it to be approved and make sure all checks pass
- Merge it

## Code owner

jules.lasne@gmail.com

## TODO:

- [ ] Migrate tests to pytest-recording
- [ ] Add a readthedocs documentation
- [ ] Switch to an OpenAPI generated client ? see https://github.com/shellhub-io/shellhub/issues/3497#issuecomment-1917478654
- [ ] Add deployment to pypi on merge to main
- [ ] Add a changelog
- [ ] Setup coverage reporting
- [ ] Update tests to tests on multiple python versions