#!/usr/bin/env bash
set -eu
exec > out-actual.txt 2>&1

. $ROOT_DIR/tests/common.sh

CASE 7 cursor = line 1 plain
    tir_parser parse 1 "$ROOT_DIR/tests/data/table.txt"

CASE 10 cursor = line 11 bottom of gird
    tir_parser parse 11 "$ROOT_DIR/tests/data/table.txt"

CASE 13 cursor = line 12 plain
    tir_parser parse 12 "$ROOT_DIR/tests/data/table.txt"