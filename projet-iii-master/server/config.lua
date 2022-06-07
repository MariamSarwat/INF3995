-- SPDX-License-Identifier: GPL-2.0-only
--
-- Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
--
-- config.lua - configuration file.
--
-- All values are set for release


-- Build system configuration

--- Where to build the sources
BUILD_DIR = env("BUILD_DIR") or "/tmp/bixi-server"

--- Build for release?
RELEASE = true

-- Build from CI?
CI = env("CI") ~= nil


-- Compiler configuration

--- Deactivate all optimization

BLAME_GCC = false
--- Make warnings act like errors; Doesn't work with clang
MANIAC = false


----------------------------------------------------------------
--                     DEVELOPER ONLY BELOW                   --
----------------------------------------------------------------

-- Runtime configuration

--- Enable runtime address sanitizer
ASAN = true and not RELEASE

--- Enable runtime assertion
ASSERT = true and not RELEASE

--- Set HTTP transfert-encoding chunk
TRANSFERT_ENCODING_CHUNKED = true


------------------------------------------------------------
--                     DO NO EDIT BELOW                   --
------------------------------------------------------------

-- System specific configuration
PAGE_SIZE         = shell("getconf PAGE_SIZE")
D1CACHE_LINE_SIZE = shell("getconf LEVEL1_DCACHE_LINESIZE")
SMP               = shell("if [ $(getconf _NPROCESSORS_ONLN) -gt 1 ]; then echo -n true; else echo -n false; fi")
