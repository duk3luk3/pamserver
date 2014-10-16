pamserver
=========

A minimalist pam password auth server

This server is intended to build a secure bridge between a linux server's PAM
user authentication system and any application that needs to authenticate users.

Pamserver creates a unix socket where it listens for username/password pairs
encoded as JSON, like so:

    {
      "username": "jdoe",
      "password": "topsecret"
    }

The reference client is available as pamclient.

For full access to PAM, the server must be run as root.

To create a pam server that is reachable over the network, use the unix socket
as a backend to an appropriately secured ssl server using e.g. stunnel.

Dependencies
============

* simplepam

Usage
=====

    $ ./pamserver.py -h
    usage: pamserver.py [-h] [--config CONFIGFILE] [--sock SOCKFILE]
                        [--pid PIDFILE] [--syslog] [--no-syslog] [--no-pid]
    
    optional arguments:
      -h, --help           show this help message and exit
      --config CONFIGFILE  The config file
      --sock SOCKFILE      Pass to customize the sockfile location
      --pid PIDFILE        Pass to customize the pidfile location
      --syslog             Pass to turn on logger to syslog
      --no-syslog          Pass to turn off logger to syslog
      --no-pid             Pass to turn off pidfile

    $ ./pamclient.py -h
    usage: pamclient.py [-h] sock
    
    positional arguments:
      sock        the socket file
    
    optional arguments:
      -h, --help  show this help message and exit

Todo
====

* chroot implementation
* stunnel sample config
* Systemd service and init files

License
=======

BSD 3-clause.
