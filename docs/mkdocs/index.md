# bin2whl

Build Python wheels from pre-compiled binaries. Takes Go, Zig, C, Rust, or any other
pre-compiled binary and packages it as a proper platform-specific Python wheel (.whl file)
for distribution on PyPI.

## Features

- Zero dependencies (pure Python, standard library only)
- Builds one wheel per binary, per platform
- Config file support (wheel.json) for repeatable builds
- Supports macOS, Linux, and Windows on x86_64 and ARM64
- Proper wheel metadata and SHA256 hashes (PEP 427)
- Binary lands directly in venv's bin/ — no Python wrapper
- Works with `pip install` and `uv tool install`

## Installation

```bash
pip install bin2whl
```

## Quick Start

### Config file mode

Create a `wheel.json` (see [Configuration Reference](config.md) for the full format), then:

```bash
bin2whl --config wheel.json
```

### Single binary mode

```bash
bin2whl \
  -n your-go-tool \
  -v 0.1.0 \
  -b dist/your-go-tool-linux-x86_64 \
  -p linux_x86_64
```

## Workflow Example

```bash
# 1. Compile binaries for all platforms
GOOS=linux GOARCH=amd64 go build -o dist/tool-linux-x86_64 ./src
GOOS=linux GOARCH=arm64 go build -o dist/tool-linux-aarch64 ./src
GOOS=darwin GOARCH=amd64 go build -o dist/tool-macos-x86_64 ./src
GOOS=darwin GOARCH=arm64 go build -o dist/tool-macos-arm64 ./src
GOOS=windows GOARCH=amd64 go build -o dist/tool-win-x86_64.exe ./src
GOOS=windows GOARCH=arm64 go build -o dist/tool-win-arm64.exe ./src

# 2. Build all wheels
bin2whl --config wheel.json

# 3. Upload to PyPI
twine upload wheels/*

# Users install with:
pip install your-go-tool
your-go-tool --help
```
