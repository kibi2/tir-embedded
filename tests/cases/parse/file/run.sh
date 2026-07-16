#!/usr/bin/env bash
set -eu
exec > out-actual.txt 2>&1

. $ROOT_DIR/tests/common.sh

CASE 7 cursor = line 1 plain
    tir_parser parse "$ROOT_DIR/tests/data/table.txt"

CASE 10 cursor = line 11 bottom of gird
    tir_parser parse "$ROOT_DIR/tests/data/table.txt" --cursor-line=11 

CASE 13 cursor = line 12 plain
    tir_parser parse --cursor-line=12 "$ROOT_DIR/tests/data/table.txt"

CASE 16 cursor = line one plain
    tir_parser parse --cursor-line=one "$ROOT_DIR/tests/data/table.txt"