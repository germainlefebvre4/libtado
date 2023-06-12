# Contributing

You can download the library sources at
<https://github.com/germainlefebvre4/libtado>:

```bash
git clone https://github.com/germainlefebvre4/libtado.git
```

## Requirements

The library development requires at least python `3.7`.

This library is tested with following python versions:

- `3.7`
- `3.8`

## Setup

Update your system and install a python version (at least the minimum required) and install the python virtualenv tool
`pipenv` (or `poetry`).

```bash
sudo apt update
sudo apt install python3.7 python3.7-pip
sudo pip install pipenv
# sudo pip install poetry
```

Initialize your `pipenv` (or `poetry`) setup and install all the development libraries.

```bash
pipenv update --dev
# poetry install
```

## Improve the library

The library is served through 2 sections:

- API in `./libtado/api.py`
- CLI in `./libtado/cli.py`

## Write and run some tests

Unit tests are important for the developement team because it adds strenghtness and confidence to the code.

The tests are written in the following files:

- Global Tado in `./tests/global/test_tado.py`
- Library API in `./tests/api/test_api.py`
- Library CLI in `./tests/cli/test_cli.py`

Run the tests inside `pipenv` or `poetry`.

```bash
pipenv run pytest -sv tests/
# poetry run pytest -sv tests/
```
