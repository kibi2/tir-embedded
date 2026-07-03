#!/usr/bin/env python3

import json
import sys
import re
from typing import Optional, Iterable, Any

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


def split_row(aline: str) -> list[str]:
    line = aline.rstrip(" \t")
    # 1. Temporarily escape \|
    placeholder = "\0PIPE\0"
    line = line.replace(r"\|", placeholder)
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
        cell = cell.replace(placeholder, "|")
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


def emit_first_grid_row(line: str) -> None:
    cells = split_row(line)
    print_json(
        {
            "kind": "grid",
            "prefix": get_prefix(line),
            "row": cells,
        },
    )

def emit_grid_row(line: str) -> None:
    cells = split_row(line)
    print_json(
        {
            "kind": "grid",
            "row": cells,
        },
    )

def get_prefix(aline: str) -> Optional[str]:
    line = aline.rstrip(" \t")
    if not line.endswith("|"):
        return None
    pipe_index = line.find("|")
    return line[:pipe_index] if 0 <= pipe_index < len(line) - 1 else None

def get_pre_mark(line: str) -> Optional[str]:
    prefix = get_prefix(line)
    return prefix.strip() if prefix is not None else None

def get_first_pre_mark(lines: list[str], cursor: int) -> Optional[str]:
    nline = len(lines)
    for index in range(nline):
        iline = (index + cursor) % nline
        mark = get_pre_mark(lines[iline])
        if mark is not None:
            return mark
    return None

def is_grid(pre_mark: Optional[str], mark: Optional[str]) -> bool:
    return pre_mark is not None and pre_mark == mark

def parse(cursor: int, input_file_path: Optional[str] = None ) -> None:
    lines = read_lines(input_file_path)
    master = get_first_pre_mark(lines, cursor - 1)
    print_attr_file()
    in_grid = False
    for line in lines:
        mark = get_pre_mark(line)
        if in_grid:
            in_grid = is_grid(master, mark)
            if in_grid:
                emit_grid_row(line)
            else:
                emit_plain(line)
        else:
            in_grid = is_grid(master, mark)
            if in_grid:
                emit_first_grid_row(line)
            else:
                emit_plain(line)


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


def unparse(output_file_path: Optional[str] = None) -> None:
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


from importlib.metadata import version


def get_version() -> str:
    return version("tir-embedded")


def usage() -> None:
    print(
        f"""tir-embedded {get_version()}

usage:
  tir-embedded parse    cursor [file|-]
  tir-embedded unparse         [file|-]
  tir-embedded --version

Options:

If file is omitted or '-', parse reads from stdin.
If file is omitted or '-', unparse writes to stdout.
""",
        file=sys.stderr,
    )


def parse_args(argv):
    return argv


# ------------------------------------------------------------
# pip entry point
# ------------------------------------------------------------


def run(argv) -> int:
    try:
        args = parse_args(argv)
    except Exception as error:
        print(str(error), file=sys.stderr)
        usage()
        return 1

    if not args:
        usage()
        return 1

    if args[0] == "--version":
        print(get_version())
        return 0

    if len(args) not in (1, 2, 3):
        usage()
        return 1

    command = args[0]

    try:
        if command == "parse":
            if len(args) not in (2, 3):
                usage()
                return 1
            cursor = int(args[1])
            file_argument = args[2] if len(args) == 3 else None
            parse(cursor, file_argument)
        elif command == "unparse":
            file_argument = args[1] if len(args) == 2 else None
            unparse(file_argument)
            return 0
        else:
            print(f"unknown sub command: {command}", file=sys.stderr)
            usage()
            return 1

    except Exception as error:
        print(str(error), file=sys.stderr)
        return 1

    return 0
