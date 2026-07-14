#!/usr/bin/env bash
set -u
exec > out-actual.txt 2>&1

source $ROOT_DIR/tests/common.sh

CASE $LINENO help
    tir_parser help