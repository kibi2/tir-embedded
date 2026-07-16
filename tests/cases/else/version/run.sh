#!/usr/bin/env bash
set -u
exec > out-actual.txt 2>&1

. $ROOT_DIR/tests/common.sh

CASE 7 version
    tir_parser version