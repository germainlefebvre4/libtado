# Tado python library

A library to control your Tado Smart Thermostat. This repository contains an actual library in `libtado/api.py` and a proof of concept command line client in `libtado/__main__.py`.

**The tested version of APIs is Tado v2.**

## Installation

You can download official library with `pip install libtado`.

But because I do not own a Tado anymore you may want to use a fork of libtado instead. For example you can install the fork that is currently (February 2019) maintained and improved by @germainlefebvre4. Please note that I do not monitor or verify changes of this repository. Please check the source yourself.

```sh
git clone https://github.com/germainlefebvre4/libtado.git
```

Please check out https://libtado.readthedocs.io for more documentation.

## Preparation

Retrieve the `CLIENT_SECRET` before running the script otherwise you will get a `401 Unauthorized Access`.

The latest `CLIENT_SECRET` can be found at [https://my.tado.com/webapp/env.js](https://my.tado.com/webapp/env.js).  It will look something like this:

```
var TD = {
	config: {
		version: 'v588',
		oauth: {
			clientSecret: 'wZaRN7rpjn3FoNyF5IFuxg9uMzYJcvOoQ8QWiIqS3hfk6gLhVlG57j5YNoZL2Rtc'
		}
	}
};
```

An alternative way to get your `CLIENT_SECRET` is to enable the Developper Mode when logging in and catch the Headers. You will find the form data like this :
```
client_id: tado-web-app
client_secret: fndskjnjzkefjNFRNkfKJRNFKRENkjnrek
grant_type: password
password: MyBeautifulPassword
scope: home.user
username: email@example.com
```

Then you just have to get the value in the attribute `client_secret`. You will need it to connect to your account through Tado APIs. The `client_secret` never dies so you can base your script on it.

## Usage

Download the repository. You can work inside it. Beware that the examples assume that they can access the file `./libtado/api.py`.

Now you can call it in your Pyhton script!

```python
import libtado.api

t = api.Tado('my@email.com', 'myPassword', 'client_secret')

print(t.get_me())
print(t.get_home())
print(t.get_zones())
print(t.get_state(1))
```

## Examples

An example script is provided in the repository as `example.py`.
It shows you how to use the library and expose some structured responses. A more detailed example is available in `libtado/__main__.py`.

## Development

### Setup
```bash
sudo apt update
sudo apt install python3.7 python3.7-pip
sudo pip install pipenv
pipenv update --dev
```

### Run application
Follow the indications in sectio [Usage](#usage).

### Run tests
```bash
pipenv run pytest tests/
```