#!/bin/sh

set -eu
exec > out-actual.txt 2>&1

source $ROOT_DIR/tests/common.sh

CASE $LINENO stdin
    tir_parser parse 1 < "$ROOT_DIR/tests/data/table.txt"