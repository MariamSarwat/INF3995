CC?=gcc
AR?=ar

CPPFLAGS=-Iinclude -include include/def.h

define DIALECT
-std=gnu11
endef

ifeq ($(CC),cc)
include mk/gcc.mk
else ifeq ($(CC),gcc)
include mk/gcc.mk
else ifeq ($(CC),clang)
include mk/clang.mk
endif


ifeq ($(CONFIG_RELEASE),1)

define CFLAGS
-ggdb3 -Wall -Wextra -Werror -O2
$(WARNINGS)
endef
CFLAGS:=$(call strip-newline, $(CFLAGS))

else ifeq ($(CONFIG_BLAME_GCC), 1)
CFLAGS = -O0 -g -Wall -Wextra

else

define CFLAGS :=
$(DIALECT)
$(WFORMAT)
$(WARNINGS)
$(DEBUG)
$(OPTIMIZATION)
$(CODE)
$(PROF)
$(SANITIZER)
$(CFLAGS)
endef
CFLAGS:=$(call strip-newline, $(CFLAGS))
endif

LDFLAGS += -rdynamic -Wl,-rpath=$(TARGET-DIR)
LIBS += -ldl

ifeq ($(CONFIG_MANIAC), 1)
CFLAGS += -Werror
endif

ifeq ($(CONFIG_CI), 1)
define CFLAGS :=
$(CFLAGS)
$(PROF)
endef
CFLAGS:=$(call strip-newline, $(CFLAGS))
endif
