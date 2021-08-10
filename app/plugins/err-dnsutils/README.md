# err-dnsutils

============

Run common DNS utils from Err: host, dig, nslookup

## Installation

You can install err-dnsutils directly from err using:

    !repos install err-dnsutils

Alternatively, you can also clone this repository into your BOT\_EXTRA\_PLUGIN\_DIR and restart your bot to load the new plugin.

## Configuration

This plugin requires no configuration at this time

## Dependencies

No extra python dependencies are required, however you do need to have host, dig and nslookup installed on your system.

Most Linux distributions have these packaged together as dnsutils. On Gentoo the package you need is called net-dns/bind-tools

## Safety information

Please note that this plugin calls dig/nslookup/host and passes arguments on to them directly without any form of checking.
Although this should be safe (commands are called directly, not via shell which could be tricked into redirecting output or executing arbitrary commands), this might still give users more direct access than desired. If you're really paranoid (like me!) you may want to avoid this plugin.
