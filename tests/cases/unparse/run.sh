#!/bin/sh
set -eu
exec > out-actual.txt 2>&1

source $ROOT_DIR/tests/common.sh

CASE $LINENO unparse grid 1
    tir_parser unparse - < "$ROOT_DIR/tests/data/table-1.tir"

CASE $LINENO unparse grid 2
    tir_parser unparse - < "$ROOT_DIR/tests/data/table-2.tir"
