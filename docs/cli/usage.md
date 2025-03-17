# CLI Usage

Usage:

``` {.bash .select .copy}
tado --help
```

Output:

``` raw
Usage: tado [OPTIONS] COMMAND [ARGS]...

    This script provides a command line client for the Tado API.

    You can use the environment variables TADO_REFRESH_TOKEN and
    TADO_CREDENTIALS_FILE instead of the command line options.

    The first time you will have to login using a browser. The command
    will show an URL to perform the login.

    If using the credentials-file option or variable, the login will
    be stored so you don't have to do this next time.

    Call 'tado COMMAND --help' to see available options for subcommands.

Options:
    -f, --credentials-file TEXT   Full path to a file in which the Tado credentials will be stored and read from [optional]
    -t, --refresh-token TEXT      A Tado refresh token, retrieved from prior authentication with Tado [optional]
    -h, --help                    Show this message and exit.

Commands:
    capabilities        Display the capabilities of a zone.
    devices             Display all devices.
    early_start         Display or change the early start feature of a zone.
    end_manual_control  End manual control of a zone.
    home                Display information about your home.
    mobile              Display all mobile devices.
    set_temperature     Set the desired temperature of a zone.
    users               Display all users of your home.
    whoami              Tell me who the Tado API thinks I am.
    zone                Get the current state of a zone.
    zones               Get configuration information about all zones.
```
