# CLAUDE.md

This file provides guidance for AI agents working on this project.

## Project Overview

**bin2whl** is a CLI tool that takes pre-compiled binaries (Go, Zig, C, Rust, etc.) and packages them as proper Python wheels (.whl files) for distribution on PyPI. Each binary produces one platform-specific wheel. Supports macOS, Linux, and Windows on both x86_64 and ARM64 architectures. The binary lands directly in the venv's bin/ via .data/scripts/ — no Python wrapper.

## Language and Spelling

Use **Australian English** throughout:
- sanitise (not sanitize)
- initialise (not initialize)
- colour (not color)
- organisation (not organization)
- analyse (not analyze)
- licence (noun) / license (verb)

## Code Style

### Python Files

Every Python file should have:
1. A file header block with description, copyright, and version history
2. Section headers separating major sections (Imports, Constants, Functions, etc.)
3. Horizontal separators (96 chars) above each function definition

### General

- Python 3.12+
- Use type hints throughout
- Prefer pathlib.Path over os.path
- Single-line imports, no blank lines between import groups
- Run `make format` to auto-fix import ordering and formatting

## Common Commands

```bash
make help       # Show all available targets
make check      # Run ruff + pyright
make format     # Auto-fix and format code
make build      # Build wheel + docs into output/
make docs       # Build HTML documentation into html/
make clean      # Remove build artefacts
make dev        # Just create dev (.venv) setup
make publish    # Publish output/ to PyPI and docs
```

## Project Structure

```
bin2whl/
├── bin2whl/              # Main package
│   ├── __init__.py       # Package init with version
│   ├── __main__.py       # Entry point for python -m bin2whl
│   ├── cli.py            # CLI definition and dispatch
│   ├── argbuilder.py     # Argument parser wrapper
│   ├── config.py         # JSON config file parser
│   ├── wheel_builder.py  # Core wheel building logic (platform aliases, .data/scripts/)
│   └── metadata.py       # Wheel metadata generation (METADATA, WHEEL, RECORD)
├── docs/                 # Documentation source
│   ├── mkdocs.yml        # MkDocs config
│   ├── docinfo.json      # Project metadata for docs
│   └── mkdocs/           # Documentation content
│       ├── index.md      # Home page
│       ├── config.md     # Configuration reference
│       ├── cli.md        # CLI reference
│       ├── changelog.md  # Release notes (includes CHANGELOG.md)
│       └── license.md    # Licence page
├── Makefile              # Build automation
├── pyproject.toml        # Project metadata and tool config
├── README.md             # Project readme
├── CHANGELOG.md          # Version history
├── LICENSE               # Unlicense
└── CLAUDE.md             # This file
```

## Testing Changes

After making changes:
1. Run `make check` to verify linting and types pass
2. Run `make build` to verify the full build works
3. Test with `uv run bin2whl --help`

## Versioning

- Version is derived from git tags via Makefile
- Create a tag like `1.0.0` or `1.0.0b2` before running `make build` for a release (no `v` prefix)
- The Makefile generates `_version.py` at build time, which is not committed
- If no tags exist, version falls back to commit-based format like `0.0.0.dev0+e8b4100`

## Commits

When committing:
- Use clear, descriptive commit messages
- Include `Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>` in commits made with AI assistance
- **Never rewrite git history** (no `--amend`, `rebase`, `reset --hard`, `push --force`, etc.) unless explicitly asked to

## Licence

Unlicense — public domain. See LICENSE.
