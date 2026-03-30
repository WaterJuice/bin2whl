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
- Entry point generation (command lands in PATH)
- Works with `pip install` and `uv tool install`

## Installation

```bash
pip install bin2whl
```

## Quick Start

### Config file mode (recommended)

Create a `wheel.json` in your project:

```json
{
    "name": "your-go-tool",
    "version": "0.1.0",
    "description": "A Go CLI tool packaged for PyPI",
    "author": "Your Name",
    "author-email": "you@example.com",
    "license": "MIT",
    "homepage": "https://github.com/yourname/your-go-tool",
    "binaries": {
        "linux_x86_64": "dist/your-go-tool-linux-x86_64",
        "linux_aarch64": "dist/your-go-tool-linux-aarch64",
        "macosx_10_9_x86_64": "dist/your-go-tool-macos-x86_64",
        "macosx_11_0_arm64": "dist/your-go-tool-macos-arm64",
        "win_amd64": "dist/your-go-tool-win-x86_64.exe",
        "win_arm64": "dist/your-go-tool-win-arm64.exe"
    }
}
```

Then build all wheels:

```bash
bin2whl
```

### Single binary mode

```bash
bin2whl \
  --name your-go-tool \
  --version-str 0.1.0 \
  --binary dist/your-go-tool-linux-x86_64 \
  --platform linux_x86_64
```

## Supported Platforms

| Platform            | Tag                    |
|---------------------|------------------------|
| Linux x86_64        | `linux_x86_64`         |
| Linux ARM64         | `linux_aarch64`        |
| macOS x86_64        | `macosx_10_9_x86_64`  |
| macOS ARM64         | `macosx_11_0_arm64`   |
| Windows x86_64      | `win_amd64`            |
| Windows ARM64       | `win_arm64`            |

## Configuration Reference

### Package fields

| Field          | Required | Description              |
|----------------|----------|--------------------------|
| `name`         | Yes      | Package name             |
| `version`      | Yes      | PEP 440 version string   |
| `description`  | No       | Short description         |
| `author`       | No       | Author name              |
| `author-email` | No       | Author email             |
| `license`      | No       | Licence identifier       |
| `homepage`     | No       | Project URL              |

### binaries

Map of platform tags to binary file paths (relative to wheel.json location).

### Options

| Field            | Default    | Description                        |
|------------------|------------|------------------------------------|
| `output-dir`     | `wheels`   | Output directory for .whl files    |
| `python-requires`| `>=3.7`    | Minimum Python version             |

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
bin2whl

# 3. Upload to PyPI
twine upload wheels/*

# Users install with:
pip install your-go-tool
your-go-tool --help
```

## CLI Reference

```
--8<-- "_generated_command_line_help.txt"
```
