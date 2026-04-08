# bin2whl

Build Python wheels from pre-compiled binaries. Takes any pre-compiled binary
(Go, Zig, C, Rust, etc.) and packages it as a platform-specific Python wheel
for distribution on PyPI. One wheel per binary, per platform.

## Features

- Zero dependencies (pure Python, standard library only)
- **Multi-binary support** — include multiple binaries per wheel (e.g. server + client)
- Config file support (`--config wheel.json`) for repeatable builds
- Single binary mode for one-off builds
- Platform aliases for cleaner config (e.g. `linux_arm64` instead of `manylinux_2_17_aarch64`)
- Binaries land directly in venv's bin/ — no Python wrapper
- Supports macOS, Linux, and Windows on x86_64 and ARM64
- Proper wheel metadata and SHA256 hashes (PEP 427)
- Optional PyPI classifiers
- Works with `pip install` and `uv tool install`

## Installation

```bash
# Using uv
uv pip install bin2whl

# Using pip
pip install bin2whl
```

## Usage

### Config file mode

Create a `wheel.json`. For a single binary per platform:

```json
{
    "name": "your-go-tool",
    "version": "0.1.0",
    "description": "A Go CLI tool packaged for PyPI",
    "author": "Your Name",
    "binaries": {
        "linux_x86_64": "dist/tool-linux-x86_64",
        "linux_arm64": "dist/tool-linux-arm64",
        "macos_arm64": "dist/tool-macos-arm64",
        "windows_amd64": "dist/tool-win-x86_64.exe"
    }
}
```

For multiple binaries per platform (e.g. server + client):

```json
{
    "name": "your-suite",
    "version": "0.1.0",
    "binaries": {
        "linux_x86_64": [
            {"name": "your-server", "path": "dist/server-linux-x86_64"},
            {"name": "your-client", "path": "dist/client-linux-x86_64"}
        ],
        "macos_arm64": [
            {"name": "your-server", "path": "dist/server-darwin-arm64"},
            {"name": "your-client", "path": "dist/client-darwin-arm64"}
        ]
    }
}
```

Then build:

```bash
bin2whl --config wheel.json
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
├── your_go_tool-0.1.0-py3-none-manylinux_2_17_x86_64.whl
├── your_go_tool-0.1.0-py3-none-manylinux_2_17_aarch64.whl
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
