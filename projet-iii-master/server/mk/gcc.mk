define WFORMAT
-fdiagnostics-color=auto
endef

define WARNINGS
-Waggregate-return
-Wall
-Warray-bounds=2
-Wno-override-init
-Wattribute-alias
-Wcast-align
-Wchar-subscripts
-Wdouble-promotion
-Wduplicated-branches
-Wduplicated-cond
-Wunreachable-code
-Wendif-labels
-Wextra
-Wfloat-equal
-Winit-self
-Winline
-Wcast-align
-Wmissing-include-dirs
-Wno-unused-parameter
-Wnonnull
-Wnonnull-compare
-Wnull-dereference
-Wshadow
-Wsign-compare
-Wswitch-enum
-Wstrict-overflow=5
-Wstringop-overflow=4
-Wno-stringop-truncation
-Wsuggest-attribute=cold
-Wsuggest-attribute=const
-Wsuggest-attribute=format
-Wsuggest-attribute=malloc
-Wsuggest-attribute=noreturn
-Wsuggest-attribute=pure
-Wuninitialized
-Wwrite-strings
endef

define DEBUG
-ggdb3
endef

define OPTIMIZATION
-fstrict-overflow
-O0
endef

define PROF
--coverage
-fprofile-abs-path
endef


ifeq ($(CONFIG_ASAN), 1)
define SANITIZER
-ftrapv
-fsanitize-address-use-after-scope
-fsanitize=address
-fsanitize=alignment
-fsanitize=bounds
-fsanitize=bounds-strict
-fsanitize=integer-divide-by-zero
-fsanitize=leak
-fsanitize=nonnull-attribute
-fsanitize=null
-fsanitize=object-size
-fsanitize=pointer-compare
-fsanitize=pointer-overflow
-fsanitize=pointer-subtract
-fsanitize=returns-nonnull-attribute
-fsanitize=shift-base
-fsanitize=shift-exponent
-fsanitize=signed-integer-overflow
-fsanitize=undefined
-fsanitize=vla-bound
endef
else ifeq ($(CONFIG_TSAN), 1)
SANITIZER=-fsanitize=thread
endif

