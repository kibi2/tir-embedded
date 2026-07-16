#!/usr/bin/env bash
set -eu

rg -n -g '*.py' -g '*.sh' '[^\x00-\x7F]' $ROOT_DIR > out-actual.txt