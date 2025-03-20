# CLI Configuration

!!! warning

    The variables `TADO_USERNAME` and `TADO_PASSWORD` and `TADO_CLIENT_SECRET` are deprecated. Use `TADO_CREDENTIALS_FILE` or `TADO_REFRESH_TOKEN` instead.

## Configuration File

There is no configuration file. No need.

## Environment Variables

The following environment variables are supported:

* `TADO_CREDENTIALS_FILE` - Path to a file which holds your Tado credentials. Be careful: do not share this file with others.
* `TADO_REFRESH_TOKEN` - Tado refresh token, from previous login. Valid for one-time use only.

!!! note

    The variables `TADO_CREDENTIALS_FILE` and `TADO_REFRESH_TOKEN` are mutually exclusive. If both are set, an error will be raised.

Environment variables can be set up in multiples ways:

* System environment variables
* File `.env` in the current directory
