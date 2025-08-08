# Tado python library

<img src="docs/logo.png" alt="Libtado Logo" width="200px" align="center"/>

---

![License: GPL-3.0](https://img.shields.io/github/license/germainlefebvre4/libtado?color=blue)
[![GitHub Repo stars](https://img.shields.io/github/stars/germainlefebvre4/libtado)](https://github.com/germainlefebvre4/libtado/stargazers)

![build](https://github.com/germainlefebvre4/libtado/workflows/Release%20Management/badge.svg?branch=master)
![Docs](https://readthedocs.org/projects/libtado/badge/?version=latest&style=default)

A library to control your Tado Smart Thermostat. This repository contains an actual library in `libtado/api.py` and a proof of concept command line client in `libtado/__main__.py`.

**The tested version of APIs is Tado v2.**

## ⚠️ Breaking change in v4 ⚠️

Starting the **21st of March 2025**, the Tado authentication workflow will definitely change to OAuth2 device code grant flow.

Here is the link to the official announcement: [Tado Support Article - How do I authenticate to access the REST API?](https://support.tado.com/en/articles/8565472-how-do-i-authenticate-to-access-the-rest-api)

Now, you have to use the `TADO_CREDENTIALS_FILE` or `TADO_REFRESH` variables to authenticate.
You can find more documentation on how to authenticate in the [**Libtado - CLI Configuration**](https://libtado.readthedocs.io/en/latest/cli/configuration/) documentation.

## Installation

You can download official library with `pip install libtado`.

But because I do not own a Tado anymore you may want to use a fork of libtado instead. For example you can install the fork that is currently (February 2019) maintained and improved by @germainlefebvre4. Please note that I do not monitor or verify changes of this repository. Please check the source yourself.

```sh
git clone https://github.com/germainlefebvre4/libtado.git
```

Please check out [https://libtado.readthedocs.io](https://libtado.readthedocs.io) for more documentation.

## Usage

Download the repository. You can work inside it. Beware that the examples assume that they can access the file `./libtado/api.py`.

Define a location and filename that will hold the credentials (refresh token) of your Tado login.

It is recommended to use a directory that only your application has access to, as the credentials file
holds sensitive information!

Now you can call it in your Python script!

```python
from libtado.api import Tado
import webbrowser   # only needed for direct web browser access

t = Tado(token_file_path='/tmp/.libtado-refresh-token')
# OR: t = Tado(saved_refresh_token='my-refresh-token')

status = t.get_device_activation_status()

if status == "PENDING":
    url = t.get_device_verification_url()

    # to auto-open the browser (on a desktop device), un-comment the following line:
    webbrowser.open_new_tab(url)

    t.device_activation()

    status = t.get_device_activation_status()

if status == "COMPLETED":
    print("Login successful")
else:
    print(f"Login status is {status}")

print(t.get_me())
print(t.get_home())
print(t.get_zones())
print(t.get_state(1))
```

The first time, the script will tell you to login to your Tado account.

It will show an output like:

```raw
Please visit the following URL in your Web browser to log in to your Tado account: https://login.tado.com/oauth2/device?user_code=1234567
Waiting for you to complete logging in. You have until yyyy-MM-dd hh:mm:ss
.
```

Complete your login before the time indicated.

Afterwards, the script should print the information from your Tado home.

If using the `token_file`, the next time you should not have to sign in.

## Examples

An example script is provided in the repository as `example.py`.
It shows you how to use the library and expose some structured responses. A more detailed example is available in `libtado/__main__.py`.

## Supported version and deprecations

### Python

| Python version | Supported versions   |
|----------------|----------------------|
| `3.7`          | `2.0.0` > `3.6.x`    |
| `3.8`          | `3.7.0` > `latest`   |
| `3.9`          | `3.7.0` > `latest`   |
| `3.10`         | `3.7.0` > `latest`   |
| `3.11`         | `3.7.0` > `latest`   |
| `3.12`         | `3.7.0` > `latest`   |

## Contributing

We thank everyone for their help and contributions to the library.

You want to report a bug? [Create an issue](https://github.com/germainlefebvre4/libtado/issues/new/choose)

You want to request a feature? [Create an issue](https://github.com/germainlefebvre4/libtado/issues/new/choose)

You want to contribute to the library? Read the [Contributing](https://libtado.readthedocs.io/en/latest/contributing/) page.
