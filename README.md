# tir-embedded

ANY <-> TIR converter backend for tirenvi.

## Install

```bash
pip install tir-embedded
```

## Usage

```bash
tir-embedded parse start file.md > file.tir
tir-embedded unparse file.md < file.tir
```

## Behavior

- Table cells do not support multiline content in GFM
- Newlines inside a cell are encoded as `\n` on unparse

## Note

This is a simplified (lite) GFM parser.

- Tables end when a line does not contain a pipe (`|`)
- Not fully compliant with the GFM specification
