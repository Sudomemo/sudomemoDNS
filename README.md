# sudomemoDNS

This server will allow you to connect to Sudomemo when
your Internet Service Provider does not work with custom DNS.

## Setup

The setup process does not differ from what is shown at
https://support.sudomemo.net/setup except for the values
to enter in your custom DNS settings.

First, make sure that your Nintendo DSi is connected to the
same network as this computer.

# Running on Windows

Right click on sudomemoDNS_##.exe (the ## will instead show the version number) and click on "Run as administrator".

# Building on Windows

Install dnslib and requests via npm (as well as pyinstaller) and then build with pyinstaller:

C:\Users\Administrator\sudomemo-dns>C:\Users\Administrator\AppData\Local\Programs\Python\Python36\Scripts\pyinstaller.exe sud
omemoDNS_v1.0.spec
