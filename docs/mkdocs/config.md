# Configuration Reference

bin2whl reads a JSON config file (typically `wheel.json`) when invoked with `--config`.

You can also generate this from the CLI with `bin2whl --example-config`.

## Example

```json
{
    "name": "your-tool",
    "version": "0.1.0",
    "description": "A CLI tool packaged for PyPI",
    "author": "Your Name",
    "author-email": "you@example.com",
    "license": "MIT",
    "homepage": "https://github.com/yourname/your-tool",
    "binaries": {
        "linux_x86_64": "dist/your-tool-linux-x86_64",
        "linux_arm64": "dist/your-tool-linux-arm64",
        "macos_x86_64": "dist/your-tool-macos-x86_64",
        "macos_arm64": "dist/your-tool-macos-arm64",
        "windows_amd64": "dist/your-tool-win-x86_64.exe",
        "windows_arm64": "dist/your-tool-win-arm64.exe"
    },
    "readme": "README.md",
    "classifiers": [
        "Environment :: Console",
        "License :: OSI Approved :: MIT License"
    ],
    "output-dir": "wheels",
    "python-requires": ">=3.7"
}
```

## Package fields

| Field          | Required | Description              |
|----------------|----------|--------------------------|
| `name`         | Yes      | Package name             |
| `version`      | No       | PEP 440 version string (can be provided via `--version-str` instead) |
| `description`  | No       | Short description         |
| `author`       | No       | Author name              |
| `author-email` | No       | Author email             |
| `license`      | No       | Licence identifier       |
| `homepage`     | No       | Project URL              |
| `classifiers`  | No       | List of PyPI [classifier strings](https://pypi.org/classifiers/) |
| `readme`       | No       | Path to a markdown file for PyPI long description |

## binaries

Map of platform tags (or aliases) to binaries. Each value can be either:

- A **string** — path to a single binary (command name matches the package name)
- A **list of objects** — multiple binaries with explicit command names

### Single binary per platform

```json
{
    "binaries": {
        "linux_x86_64": "dist/tool-linux-x86_64",
        "macos_arm64": "dist/tool-macos-arm64"
    }
}
```

### Multiple binaries per platform

Each entry needs a `name` (the command name when installed) and a `path` (relative to the config file):

```json
{
    "binaries": {
        "linux_x86_64": [
            {"name": "my-server", "path": "dist/server-linux-x86_64"},
            {"name": "my-client", "path": "dist/client-linux-x86_64"}
        ],
        "macos_arm64": [
            {"name": "my-server", "path": "dist/server-darwin-arm64"},
            {"name": "my-client", "path": "dist/client-darwin-arm64"}
        ]
    }
}
```

All binaries for a platform are included in a single wheel. When installed, each binary becomes a separate command in the venv's bin/ directory.

## Options

| Field            | Default    | Description                        |
|------------------|------------|------------------------------------|
| `output-dir`     | `wheels`   | Output directory for .whl files    |
| `python-requires`| `>=3.7`    | Minimum Python version             |

## Platform Aliases

Run `bin2whl --platforms` to see this list.

Short aliases are expanded to standard wheel platform tags automatically:

| Alias             | Expands to                  |
|-------------------|-----------------------------|
| `linux_x86_64`    | `manylinux_2_17_x86_64`    |
| `linux_amd64`     | `manylinux_2_17_x86_64`    |
| `linux_aarch64`   | `manylinux_2_17_aarch64`   |
| `linux_arm64`     | `manylinux_2_17_aarch64`   |
| `macos_x86_64`    | `macosx_10_9_x86_64`       |
| `macos_amd64`     | `macosx_10_9_x86_64`       |
| `macos_arm64`     | `macosx_11_0_arm64`        |
| `macos_aarch64`   | `macosx_11_0_arm64`        |
| `windows_amd64`   | `win_amd64`                |
| `windows_x86_64`  | `win_amd64`                |
| `windows_arm64`   | `win_arm64`                |

Any valid wheel platform tag is also accepted directly (e.g. `macosx_14_0_arm64`).
