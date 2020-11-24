![sudomemoDNS Logo](/sudomemoDNS_banner.png)
### This server will allow you to connect to Sudomemo when your Internet Service Provider does not work with custom DNS.

## Setup

The setup process does not differ from what is shown at https://flipnot.es/setup except for the values to enter in your custom DNS settings.

First, make sure that your console is connected to the same network as this computer.

Please submit any issues to Sudomemo Support.

## Running on Windows:

Run the .exe provided in this release. You may have to click past a warning from Windows SmartScreen (as it sometimes turns its nose up at applications bundled by PyInstaller) or your firewall (as it needs to listen for DNS requests).

## Running on anything else:

Required packages (installable with pip): `requests`, `dnslib`

Required Python version: 3+, tested with 3.6

    sudo <name of your python binary> sudomemoDNS.py

## What you'll see when it starts up

The following will display when you start it up:

    +===============================+
    |      Sudomemo DNS Server      |
    |          Version 1.2          |
    +===============================+

    == Welcome to sudomemoDNS! ==
    This server will allow you to connect to Sudomemo when your Internet Service Provider does
    not work with custom DNS.

    == How To Use ==
    First, make sure that your console is connected to the same network as this computer.

    Then, put these settings in for DNS on your console:
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Primary DNS:   XXX.XXX.XXX.XXX (NOTE: This value will be unique when you run the program)
    Secondary DNS: 8.8.8.8
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    == Getting Help ==
    Need help? Visit our Discord server or check out https://support.sudomemo.net

When entering your DNS settings, if the Primary DNS is displayed like this (this is an example):

192.168.1.7 

then you can enter it as follows:

192.168.001.007

## Building on Windows

Install dnslib, requests, and pyinstaller via pip, then modify the paths in the spec file to where sudomemoDNS and the sudomemoDNS icon is stored.

Then, run the following as an administrator:

    pyinstaller.exe sudomemoDNS_v1.2.spec
