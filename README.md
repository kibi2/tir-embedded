# tir-embedded

Embedded table <-> TIR converter backend for tirenvi.

## Install

```bash
pip install tir-embedded
```

## Usage

```bash
tir-embedded parse <cursor-line> file > file.tir
tir-embedded unparse file < file.tir
```

`<cursor-line>` specifies the current cursor line (1-based).

The parser uses this line to determine which embedded table to parse and which table prefix (`key`) to use.

## Embedded table format

An embedded table consists of consecutive lines that:

* contain at least two `|` characters
* end with `|` (ignoring trailing whitespace)
* share the same prefix (`key`)

Example:

```text
// |Name|Age|
// |Alice|20|
// |Bob|30|
```

or

```python
# |Name|Age|
# |Alice|20|
# |Bob|30|
```

The `key` is the text before the first `|` (excluding leading/trailing whitespace).

The parser determines the `key` from the first table found at or below the cursor line.

Only tables with that `key` are considered.

## Behavior

* Embedded tables may appear in any text file.
* Tables are separated by blank lines or lines with a different key.
* Rows may have different numbers of cells. The maximum column count is used.
* A literal `|` inside a cell is written as `\|`.
* A newline inside a cell is represented as `<br>`.

## Note

This parser is intentionally simple.

* It is not tied to any particular programming language.
* It does not parse language syntax.
* It only recognizes embedded tables based on the table format described above.
