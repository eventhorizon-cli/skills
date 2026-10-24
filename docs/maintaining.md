# Maintaining Skills

[简体中文](maintaining.zh-CN.md) · [Repository README](../README.md)

## Source of truth

The locally installed skill copies are authoritative for execution behavior. When repository skill files are synchronized from the local installation, preserve byte-identical contents unless the change intentionally updates the installed source as well. Keep user-facing English and Simplified Chinese documentation aligned with the same behavior.

The repository layout is:

```text
skills/  skill implementations
docs/    bilingual user and maintenance guides
scripts/ validation entry points
```

## Validation

From the repository root, create the development environment and run the repository validator:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate-skills.py
```

The validator checks skill metadata, local Markdown links and anchors, YAML and JSON syntax, and Python and Bash syntax. CI runs the same validation on pull requests and on pushes to `main`.
