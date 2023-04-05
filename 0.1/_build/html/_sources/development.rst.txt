.. _development:

==================
Step-by-Step Guide
==================

You can download the library sources at https://github.com/germainlefebvre4/libtado:

.. code-block:: bash
    git clone https://github.com/germainlefebvre4/libtado.git

************
Requirements
************

The library development requires at least python ``3.7``.

This library is tested with following python versions:

* ``3.7``
* ``3.8``

*****
Setup
*****

Update your system and install a python version (at least the minimum required) and install the python virtualenv tol `pipenv`.

.. code-block:: bash

    sudo apt update
    sudo apt install python3.7 python3.7-pip
    sudo pip install pipenv

Initialize your `pipenv` setup and install all the development libraries 

.. code-block:: bash

    pipenv update --dev

*******************
Improve the library
*******************

The library is served through 2 sections:

* API in ``./libtado/api.py``
* CLI in ``./libtado/cli.py``

************************
Write and run some tests
************************

Unit tests are important for the developer team because it add strenghtness and confidence to the code.

The tests are written in the following files:

* Global Tado in ``./tests/global/test_tado.py``
* Library API in ``./tests/api/test_api.py``
* Library CLI in ``./tests/cli/test_cli.py``

Run the tests inside pipenv.

.. code-block:: bash

    pipenv run pytest tests/
