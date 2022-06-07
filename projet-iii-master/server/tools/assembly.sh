#!/bin/sh

gcc $CFLAGS -I include -include include/def.h -fverbose-asm -S $1 -o $2
