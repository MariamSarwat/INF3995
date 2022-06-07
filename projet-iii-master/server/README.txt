===========
bixi-server
===========


DESCRIPTION
-----------
Small RESTful server for the Bixi project.  For full documentation, see files
under _server/docs/_.

All relative path references in this document project refer to path inside
_server/_, excepted when explicitly told otherwise.


CONFIGURATION
-------------
The project is configure by the file _config.lua_.  The default values should be
fine for production.  To build the server, do `make`, then run `make test` to
run tests (see developement dependencies).


NOTES
-----
This project follows the Linux Kernel coding style.  See
<https://www.kernel.org/doc/html/v4.10/process/coding-style.html>.  Please set
your text editor to only use TABs with 1 tab = 8 spaces.


AUTHORS
-------
Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>


LICENSE
-------
SPDX-License-Identifier: GPL-2.0-only


DEPENDENCIES
------------
These are named after Debian's packages.

* production
** bash
** bison
** flex
** lua
** gcc/clang
** make
** libssl-dev
** pkg-config

* Developpement
** curl
** gdb
** libasan
** yajl-tools
** netcat-openbsd
** yajl

* runtime
** libssl-dev
