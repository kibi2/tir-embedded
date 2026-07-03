#!/bin/sh
set -eu
exec > out-actual.txt 2>&1

source $ROOT_DIR/tests/common.sh

CASE $LINENO cursor = line 1 plain
    tir_parser parse 1 "$ROOT_DIR/tests/data/table.txt" | tir_parser unparse

CASE $LINENO cursor = line 11 bottom of gird
    tir_parser parse 11 "$ROOT_DIR/tests/data/table.txt" | tir_parser unparse
