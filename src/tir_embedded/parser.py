#!/usr/bin/env python3

import json
import sys
import re
from typing import Optional, Any

FORMAT_VERSION = "tir/0.1"

# ------------------------------------------------------------
# parse : GFM lite -> TIR (NDJSON)
# ------------------------------------------------------------


def read_lines(path: Optional[str]) -> list[str]:
    if path is None or path == "-":
        return sys.stdin.read().splitlines()
    with open(path, encoding="utf-8") as file:
        return file.read().splitlines()


def print_json(obj: dict[str, Any]) -> None:
    print(json.dumps(obj, ensure_ascii=False))

PLACEHOLDER_PIPE = "\0PIPE\0"

def split_row(aline: str) -> list[str]:
    line = aline.rstrip(" \t")
    # 1. Temporarily escape \|
    line = line.replace(r"\|", PLACEHOLDER_PIPE)
    # 2. Remove leading/trailing pipes
    pipe_index = line.find("|") + 1
    line = line[pipe_index:]
    line = line[:-1]
    # 3. split
    parts = line.split("|")
    # 4. trim + restore
    cells = []
    for cell in parts:
        cell = cell.strip()
        cell = cell.replace(PLACEHOLDER_PIPE, "|")
        cell = re.sub(r"<br\s*/?>", "\n", cell, flags=re.IGNORECASE)
        cells.append(cell)
    return cells


def print_attr_file() -> None:
    print_json(
        {
            "kind": "attr_file",
            "version": FORMAT_VERSION,
        }
    )


def emit_plain(line: str) -> None:
    print_json(
        {
            "kind": "plain",
            "line": line,
        },
    )


def emit_grid_row(line: str, is_first: bool) -> None:
    obj = {
            "kind": "grid",
            "row": split_row(line),
        }
    if is_first:
        obj["prefix"] = get_prefix(line)
    print_json(obj)

def get_prefix(aline: str) -> Optional[str]:
    line = aline.rstrip(" \t")
    if not line.endswith("|"):
        return None
    pipe_index = line.find("|")
    return line[:pipe_index] if 0 <= pipe_index < len(line) - 1 else None

def get_key(line: str) -> Optional[str]:
    prefix = get_prefix(line)
    return prefix.strip() if prefix is not None else None

def get_first_key(lines: list[str], cursor_line: int) -> Optional[str]:
    nline = len(lines)
    for index in range(nline):
        iline = (index + cursor_line) % nline
        key = get_key(lines[iline])
        if key is not None:
            return key
    return None

def is_grid(pre_mark: Optional[str], mark: Optional[str]) -> bool:
    return pre_mark is not None and pre_mark == mark

def parse(args)-> None:
    params = args["params"]
    options = args["options"]
    input_file_path = params[0] if params else None
    lines = read_lines(input_file_path)
    cursor = int(options.get("cursor-line", 1))
    master_key = get_first_key(lines, cursor -1)
    print_attr_file()
    prev_in_grid = False
    for line in lines:
        key = get_key(line)
        in_grid = is_grid(master_key, key)
        if in_grid:
            emit_grid_row(line, not prev_in_grid)
        else:
            emit_plain(line)
        prev_in_grid = in_grid


# ------------------------------------------------------------
# unparse : TIR (NDJSON) -> GFM
# ------------------------------------------------------------


def encode_newline(cell: str) -> str:
    return cell.replace("\n", r"<br>")


def escape_gfm(cell: str) -> str:
    return cell.replace("|", r"\|")


def escape_cell(cell: str) -> str:
    cell = encode_newline(cell)
    cell = escape_gfm(cell)
    return cell


def format_row(row: list[str]) -> str:
    escaped = [escape_cell(c) for c in row]
    return "| " + " | ".join(escaped) + " |"


def read_ndjson_records(lines: list[str]) -> list[dict[str, Any]]:
    records = []
    for iline, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exception:
            raise ValueError(
                f"JSON error at line {iline+1}: {exception}"
            ) from exception
        records.append(record)
    return records


def unparse(args) -> None:
    params = args["params"]
    output_file_path = params[0] if params else None
    out = (
        sys.stdout
        if output_file_path in (None, "-")
        else open(output_file_path, "w", encoding="utf-8")
    )
    try:
        first = True
        last_line = ""

        def emit(line: str):
            nonlocal first
            nonlocal last_line
            if not first:
                out.write("\n")
            out.write(line)
            first = False
            last_line = line

        lines = read_lines(None)
        records = read_ndjson_records(lines)
        prev_kind = None
        prefix  = ""
        for record in records:
            kind = record.get("kind")
            if kind == "plain":
                emit(record.get("line", ""))
            elif kind == "grid":
                if prev_kind != "grid":
                    prefix= record.get("prefix" , "")
                row = record.get("row", [])
                emit(prefix + format_row(row))
            elif kind == "attr_file":
                pass
            else:
                raise ValueError(f"unknown kind: {kind}")
            prev_kind = kind
        if last_line != "":
            out.write("\n")
    finally:
        if out is not sys.stdout:
            out.close()

# ------------------------------------------------------------
# utilities
# ------------------------------------------------------------

def parse_args(argv):
    args = {
        "command": None,
        "params": [],
        "options": {},
    }
    if not argv:
        return args
    args["command"] = argv[0]
    for arg in argv[1:]:
        if arg.startswith("--"):
            key, sep, value = arg[2:].partition("=")
            if not sep:
                value = None
            args["options"][key] = value
        else:
            args["params"].append(arg)
    return args

# ------------------------------------------------------------
# pip entry point
# ------------------------------------------------------------

from importlib.metadata import version as package_version

COMMANDS = {
    "parse": parse,
    "unparse": unparse,
    "version": lambda args: print(package_version("tir-embedded")),
}

def run(argv) -> int:
    try:
        args = parse_args(argv)
        command = args["command"]
        COMMANDS[command](args)
        return 0
    except KeyError:
        print(f"unknown sub command: {command}", file=sys.stderr)
        return 1
    except Exception as error:
        print(error, file=sys.stderr)
        return 1