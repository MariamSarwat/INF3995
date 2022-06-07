# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
#
# mk/modules.mk - Modules definitions

define to-object
$(patsubst %.c,$(CONFIG_BUILD_DIR)/%.o,$1)
endef

define get-objects
$(value $(basename $m)-objects)
endef

define get-libs
$(value $(basename $m)-libs)
endef


# Define modules here
utils-objects := $(call to-object, utils/base64.c utils/btree.c utils/opt.c utils/json.c utils/json-parser.c utils/http.c utils/http-scanner.c)
MODULES       += utils.a

core-objects := $(call to-object, $(wildcard core/*.c))
core-libs    := $(shell pkg-config --libs openssl)
MODULES      += core.a

routes-objects := $(call to-object, $(wildcard routes/*.c))
MODULES        += routes.a

tests-objects := $(call to-object, $(wildcard tests/routes/*.c))
MODULES       += tests.so

# DO NOT EDIT

## All objects; required for generating *.d files
OBJ  := $(foreach m,$(MODULES),$(call get-objects, $m))
LIBS += $(foreach m,$(filter %.a, $(MODULES)), $(call get-libs, $m))

## All builtins
BUILTIN += $(foreach m,$(filter %.a, $(MODULES)),$(call get-objects, $m))

## All loadable and their objects; for -fPIC flag
LOADABLE := $(patsubst %,$(TARGET-DIR)/$(TARGET-NAME)-%,$(filter %.so, $(MODULES)))
