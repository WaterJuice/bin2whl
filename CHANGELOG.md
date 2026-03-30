# bin2whl 1.0.0 Beta 1 — 30 Mar 2026

First stable release.

Build Python wheels from pre-compiled binaries.

## Features

- Build platform-specific wheels from any pre-compiled binary (Go, Zig, C, Rust, etc.)
- Binary placed directly into venv's bin/ via .data/scripts/ — no Python wrapper
- Config file mode (`--config wheel.json`) for multi-platform builds
- Single binary mode via CLI arguments
- Supports macOS, Linux, and Windows on x86_64 and ARM64
- Proper PEP 427 wheel metadata and SHA256 hashes
- Works with `pip install` and `uv tool install`

- Zero external dependencies — Python 3.12+ stdlib only
