#!/usr/bin/env bash
set -u
exec > out-actual.txt 2>&1

. $ROOT_DIR/tests/common.sh

CASE 7 version
        if tir_parser version | grep -Eq '^[0-9]+\.[0-9]+([.-].*)?$'; then
            echo OK
        else
            echo NG
            tir_parser version
        fi