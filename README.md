# bin2whl

Build Python wheels from pre-compiled binaries. Takes any pre-compiled binary
(Go, Zig, C, Rust, etc.) and packages it as a platform-specific Python wheel
for distribution on PyPI. One wheel per binary, per platform.

## Features

- Zero dependencies (pure Python, standard library only)
- Config file support (wheel.json) for repeatable builds
- Single binary mode for one-off builds
- Supports macOS, Linux, and Windows on x86_64 and ARM64
- Proper wheel metadata and SHA256 hashes (PEP 427)
- Entry point generation (command lands in PATH)
- Works with `pip install` and `uv tool install`

## Installation

```bash
# Using uv
uv pip install bin2whl

# Using pip
pip install bin2whl
```

## Usage

### Config file mode (recommended)

Create a `wheel.json`:

```json
{
    "name": "your-go-tool",
    "version": "0.1.0",
    "description": "A Go CLI tool packaged for PyPI",
    "author": "Your Name",
    "author-email": "you@example.com",
    "binaries": {
        "linux_x86_64": "dist/tool-linux-x86_64",
        "linux_aarch64": "dist/tool-linux-aarch64",
        "macosx_10_9_x86_64": "dist/tool-macos-x86_64",
        "macosx_11_0_arm64": "dist/tool-macos-arm64",
        "win_amd64": "dist/tool-win-x86_64.exe",
        "win_arm64": "dist/tool-win-arm64.exe"
    }
}
```

Then build:

```bash
bin2whl
```

### Single binary mode

```bash
bin2whl \
  --name your-go-tool \
  --version-str 0.1.0 \
  --binary dist/tool-linux-x86_64 \
  --platform linux_x86_64
```

### Output

Each binary produces one wheel:
```
wheels/
├── your_go_tool-0.1.0-py3-none-linux_x86_64.whl
├── your_go_tool-0.1.0-py3-none-linux_aarch64.whl
├── your_go_tool-0.1.0-py3-none-macosx_10_9_x86_64.whl
├── your_go_tool-0.1.0-py3-none-macosx_11_0_arm64.whl
├── your_go_tool-0.1.0-py3-none-win_amd64.whl
└── your_go_tool-0.1.0-py3-none-win_arm64.whl
```

Upload to PyPI, then users just run:
```bash
pip install your-go-tool
your-go-tool --help
```

## Development

```bash
# Set up development environment
make dev

# Run linting and type checks
make check

# Format code
make format

# Build wheel and docs
make build
```

## Publishing

Publishing requires `cal-publish-python` configuration.

```bash
# Build first
make build

# Publish wheel to PyPI and docs to GitLab Pages
make publish
```

## Licence

Unlicense — public domain. See [LICENSE](LICENSE).
