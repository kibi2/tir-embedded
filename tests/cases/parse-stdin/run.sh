#!/usr/bin/env bash
set -eu
exec > out-actual.txt 2>&1

. $ROOT_DIR/tests/common.sh

CASE 7 stdin
    tir_parser parse 1 < "$ROOT_DIR/tests/data/table.txt"