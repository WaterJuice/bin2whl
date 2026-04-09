# bin2whl 1.0.0 - 9 Apr 2026

Initial release.

Build Python wheels from pre-compiled binaries.

## Features

- Build platform-specific wheels from any pre-compiled binary (Go, Zig, C, Rust, etc.)
- **Multi-binary support** — include multiple binaries per wheel (e.g. server + client)
- Binary placed directly into venv's bin/ via .data/scripts/ — no Python wrapper
- Config file mode (`--config wheel.json`) for multi-platform builds
- Single binary mode via CLI arguments
- Platform aliases for cleaner config (e.g. `linux_arm64` instead of `manylinux_2_17_aarch64`)
- `--version-str` works with both modes (overrides config version)
- Optional PyPI classifiers support
- Optional `readme` field for PyPI long description
- `--example-config` and `--platforms` for discoverability
- Short flags for all options (`-n`, `-v`, `-b`, `-p`, `-c`, `-o`, `-d`, `-a`, `-e`)
- Supports macOS, Linux, and Windows on x86_64 and ARM64
- Proper PEP 427 wheel metadata and SHA256 hashes
- Works with `pip install` and `uv tool install`

- Zero external dependencies — Python 3.12+ stdlib only
