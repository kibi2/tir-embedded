#!/usr/bin/env bash
set -eu
exec > out-actual.txt 2>&1

. $ROOT_DIR/tests/common.sh

CASE 7 stdin
    tir_parser parse < "$ROOT_DIR/tests/data/table.txt"

CASE 10 stdin
    tir_parser parse - --cursor-line=11 < "$ROOT_DIR/tests/data/table.txt"