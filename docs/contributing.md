# Contributing

You can download the library sources at
<https://github.com/germainlefebvre4/libtado>:

```bash
git clone https://github.com/germainlefebvre4/libtado.git
```

## Requirements

The library development requires at least python `3.11`.

This library is tested with following python versions:

- `3.11`
- `3.12`
- `3.13`

The default/recommended dev environment uses python `3.13`.

## Setup

Update your system and install a python version (at least the minimum required) and install [`uv`](https://docs.astral.sh/uv/).

```bash
sudo apt update
sudo apt install python3.13 python3.13-pip
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Initialize your `uv` setup and install all the development and test libraries.

```bash
uv sync --group test
```

## Improve the library

The library is served through 2 sections:

- API in `./libtado/api.py`
- CLI in `./libtado/cli.py`

## Test your changes

### Write and run some tests

Unit tests are important for the development team because it adds strength and confidence to the code.

The tests are written in the following files:

- Global Tado in `./tests/global/test_tado.py`
- Library API in `./tests/api/test_api.py`
- Library CLI in `./tests/cli/test_cli.py`

Run the tests with `uv`.

```bash
uv run pytest -sv tests/
```

### Generate the JSON Scheams

The JSON schemas are generated from the Tado API. You can generate them with the following command:

```bash
uv run python generate_json_schemas.py
```

## Improve the documentation

The documentation is written in markdown and can be found in the `docs/` folder. It is built with `mkdocs` and `mkdocs-material`.

```bash
uv run mkdocs serve
```

## Validation gate

Before validating your pull request, please run the following commands:

```bash
uv run ruff check .
uv run pytest -sv tests/
uv run python generate_json_schemas.py
```

The pull request checking pipeline will run the same commands on several python versions to ensure the compatibility of the library.

## Clean the releases on PyPi

Every commit on feature branches will generate a new release on PyPi Test to ensure everything is working fine on release management.

Only admins can do this part.

Delete the release on PyPi Test:

```bash
export PYPI_CLEANUP_USERNAME=""
export PYPI_CLEANUP_PASSWORD=""
pypi-cleanup --host https://test.pypi.org --username $PYPI_CLEANUP_USERNAME --package libtado
```
