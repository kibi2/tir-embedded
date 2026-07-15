#!/usr/bin/env bash
set -eu
exec > out-actual.txt 2>&1

. $ROOT_DIR/tests/common.sh

CASE 7 cursor = line 1 plain
    tir_parser parse 1 "$ROOT_DIR/tests/data/table0.txt"

CASE 10 empty
    tir_parser parse 1 "$ROOT_DIR/tests/data/empty.txt"