CASE() {
    local lineno="$1"
    shift
    printf "\n--- CASE %d: %s ---\n" "$lineno" "$*"
}

tir_parser() {
    PYTHONPATH="$ROOT_DIR/src" \
        python3 -m tir_embedded.cli "$@"
}