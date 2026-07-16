#!/usr/bin/env bash
set -eu
exec > out-actual.txt 2>&1

. $ROOT_DIR/tests/common.sh

CASE 7 unparse grid 1
    tir_parser unparse - < "$ROOT_DIR/tests/data/table-1.tir"

CASE 10 unparse grid 2
    tir_parser unparse < "$ROOT_DIR/tests/data/table-2.tir"
