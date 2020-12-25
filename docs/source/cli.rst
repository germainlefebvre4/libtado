.. _cli:

=======================
Command Line Client
=======================

::

  Usage: tado [OPTIONS] COMMAND [ARGS]...

    This script provides a command line client for the Tado API.

    You can use the environment variables TADO_USERNAME and TADO_PASSWORD
    instead of the command line options.

    Call 'tado COMMAND --help' to see available options for subcommands.

  Options:
    -u, --username TEXT       Tado username  [required]
    -p, --password TEXT       Tado password  [required]
    -c, --client-secret TEXT  Tado password  [optional]
    -h, --help                Show this message and exit.

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
