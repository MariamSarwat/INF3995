PACKAGE=bixi-server
VERSION=1.0.0

# Do not touch the order of these files!
include mk/config.mk

include mk/std.mk
include mk/util.mk

include mk/cc.mk

ifndef VERBOSE
.SILENT:
endif

# Target
TARGET-NAME = $(PACKAGE)
TARGET-DIR  = $(CONFIG_BUILD_DIR)/bin
TARGET      = $(TARGET-DIR)/$(TARGET-NAME)

# This need to be include after target!
include mk/modules.mk

# Copy source tree to build
MKDIR=$(TARGET-DIR) $(patsubst %,$(CONFIG_BUILD_DIR)/%,$(shell find -name '*.c' | xargs dirname | sort | uniq))

# Add to this list stuff to clean up
CLEAN=$(CONFIG_BUILD_DIR) $(shell find -iname "*.o")

# Build
all: mk/config.mk include/config.h $(MKDIR) $(TARGET)

# Directory tree
$(MKDIR):
	$(foreach d,$@,$(call DO_MKDIR,$d))


# Compilation

## Final linkage of target
$(TARGET): $(BUILTIN) | $(OBJ) $(LOADABLE)
	$(QUIET_LINK) $(CC) $(CPPFLAGS) $(CFLAGS) $(LDFLAGS) -o $@ $^ $(LIBS)

## Shared objects (loadable)
.SECONDEXPANSION:
$(TARGET-DIR)/$(TARGET-NAME)-%.so: CFLAGS:=$(CFLAGS) -fPIC -shared -Wl,-Bsymbolic
$(TARGET-DIR)/$(TARGET-NAME)-%.so: $$(%-objects)
	$(QUIET_LINK) $(CC) $(CPPFLAGS) $(CFLAGS) -o $@ $^ $($*-libs)


## Object files
$(CONFIG_BUILD_DIR)/%.o: %.c
	$(QUIET_CC) $(CC) $(CPPFLAGS) -MMD $(CFLAGS) -c $< -o $@

-include $(OBJ:%.o=%.d)

## Bison
%.c: %.y
	$(QUIET_YACC)bison -d -o $@ $^

## Flex
%.c: %.l
	$(QUIET_YACC)flex -d -o $@ $^

# Configurer
mk/config.mk include/config.h: config.lua
	$(QUIET_CONF) tools/configurer config.lua

# Distribute
define DISTRIBUTE
./core
./etc
./include
./mk
./routes
./tests
./tools
./utils
./Makefile
./README.txt
./config.lua
endef

dist: $(PACKAGE).tar.gz

distclean: clean
	$(call DO_RM, $(PACKAGE))
	$(call DO_RM, $(PACKAGE).tar.gz)

$(PACKAGE):
	$(call DO_MKDIR, $@)
	$(foreach e,$(call strip-newline, $(DISTRIBUTE)), $(call DO_CP, $e, $(PACKAGE)))

$(PACKAGE).tar.bz2: $(PACKAGE)
	$(call DO_TAR_BZ2, $@,$<)
	rm -rf $(PACKAGE)

install:
	cp $(CONFIG_BUILD_DIR)/bin/bixi-server $(bindir)
	mkdir -p /etc/bixi-server

# Util
clean:
	$(foreach i,$(CLEAN),$(call DO_RM, $i))

print-%:
	@echo $* = $($*)

help:
	@echo "PHONIES: "
	$(foreach p,$(PHONIES), echo -e "\t$p";)

grun: $(TARGET)
	gdb $(TARGET)

test: $(TARGET)
	./tests/run

.PHONY: all clean config dist distclean grun help img install print run run-daemon test uninstall
