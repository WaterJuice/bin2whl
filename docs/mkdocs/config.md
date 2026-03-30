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
        "linux_aarch64": "dist/your-tool-linux-aarch64",
        "macosx_10_9_x86_64": "dist/your-tool-macos-x86_64",
        "macosx_11_0_arm64": "dist/your-tool-macos-arm64",
        "win_amd64": "dist/your-tool-win-x86_64.exe",
        "win_arm64": "dist/your-tool-win-arm64.exe"
    },
    "output-dir": "wheels",
    "python-requires": ">=3.7"
}
```

## Package fields

| Field          | Required | Description              |
|----------------|----------|--------------------------|
| `name`         | Yes      | Package name             |
| `version`      | Yes      | PEP 440 version string   |
| `description`  | No       | Short description         |
| `author`       | No       | Author name              |
| `author-email` | No       | Author email             |
| `license`      | No       | Licence identifier       |
| `homepage`     | No       | Project URL              |

## binaries

Map of platform tags to binary file paths (relative to wheel.json location).

```json
{
    "binaries": {
        "linux_x86_64": "dist/tool-linux-x86_64",
        "macosx_11_0_arm64": "dist/tool-macos-arm64"
    }
}
```

## Options

| Field            | Default    | Description                        |
|------------------|------------|------------------------------------|
| `output-dir`     | `wheels`   | Output directory for .whl files    |
| `python-requires`| `>=3.7`    | Minimum Python version             |

## Supported Platforms

Run `bin2whl --platforms` to see this list.

| Platform            | Tag                    |
|---------------------|------------------------|
| Linux x86_64        | `linux_x86_64`         |
| Linux ARM64         | `linux_aarch64`        |
| macOS x86_64        | `macosx_10_9_x86_64`  |
| macOS ARM64         | `macosx_11_0_arm64`   |
| Windows x86_64      | `win_amd64`            |
| Windows ARM64       | `win_arm64`            |

Any valid wheel platform tag is accepted — the above are the most common.
