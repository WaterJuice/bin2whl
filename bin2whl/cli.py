# ----------------------------------------------------------------------------------------
#   cli.py
#   ------
#
#   Command-line interface entry point for bin2whl. Supports building Python wheels
#   from pre-compiled binaries, either via a wheel.json config file or CLI arguments.
#
#   (c) 2026 WaterJuice — Unlicense; see LICENSE in the project root.
#
#   Version History
#   ---------------
#   Mar 2026 - Created
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------------------------

import sys
import traceback
from pathlib import Path
from bin2whl.config import DEFAULT_OUTPUT_DIR
from bin2whl.config import load_config
from bin2whl.version import VERSION_STR
from bin2whl.wheel_builder import build_wheel
from .argbuilder import ArgsParser
from .argbuilder import Namespace

# ----------------------------------------------------------------------------------------
#   Constants
# ----------------------------------------------------------------------------------------

LICENSE_TEXT = """\
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org>"""

EXAMPLE_CONFIG = """\
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
}"""

PLATFORMS_TEXT = """\
Supported platform tags:

  Linux x86_64      linux_x86_64
  Linux ARM64       linux_aarch64
  macOS x86_64      macosx_10_9_x86_64
  macOS ARM64       macosx_11_0_arm64
  Windows x86_64    win_amd64
  Windows ARM64     win_arm64

Any valid wheel platform tag is accepted — the above are the most common.
Use the exact tag string as the --platform value or as keys in wheel.json."""

# ----------------------------------------------------------------------------------------
#   Functions
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
def parse_args(argv: list[str]) -> Namespace:
    """Parse command-line arguments."""
    p = ArgsParser(
        prog="bin2whl",
        description=(
            f"bin2whl: {VERSION_STR}\n"
            "(c) 2026 WaterJuice. Unlicense.\n\n"
            "Build Python wheels from pre-compiled binaries."
        ),
        version=f"bin2whl: {VERSION_STR}\npython: {sys.version.split()[0]}",
    )

    p.add_argument(
        "--license",
        action="version",
        version=LICENSE_TEXT,
        help="show license and exit",
    )
    p.add_argument(
        "--example-config",
        action="version",
        version=EXAMPLE_CONFIG,
        help="print an example wheel.json and exit",
    )
    p.add_argument(
        "--platforms",
        action="version",
        version=PLATFORMS_TEXT,
        help="list supported platform tags and exit",
    )

    config_group = p.add_argument_group("config file mode")
    config_group.add_argument(
        "--config",
        "-c",
        default=None,
        help="path to config file (e.g. wheel.json)",
    )
    config_group.add_argument(
        "--version-str",
        "-v",
        default=None,
        dest="pkg_version",
        help="package version (overrides version in config file)",
    )

    single_group = p.add_argument_group("single binary mode")
    single_group.add_argument(
        "--name",
        "-n",
        default=None,
        help="package name",
    )
    single_group.add_argument(
        "--binary",
        "-b",
        default=None,
        help="path to binary file",
    )
    single_group.add_argument(
        "--platform",
        "-p",
        default=None,
        help="platform tag (see --platforms)",
    )
    single_group.add_argument(
        "--description",
        "-d",
        default="",
        help="package description",
    )
    single_group.add_argument(
        "--author",
        "-a",
        default="",
        help="author name",
    )
    single_group.add_argument(
        "--author-email",
        "-e",
        default="",
        help="author email",
    )

    output_group = p.add_argument_group("output")
    output_group.add_argument(
        "--output-dir",
        "-o",
        default=None,
        help="output directory for wheel files (default: wheels)",
    )

    return p.parse(argv)


# ----------------------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    """
    Main entry point for the bin2whl CLI.

    Parameters:
        argv: Command line arguments (without program name). If None, uses sys.argv[1:].

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    if argv is None:
        argv = sys.argv[1:]

    try:
        return _main_inner(argv)
    except KeyboardInterrupt:
        print()
        print("---- Manually Terminated ----")
        print()
        return 1
    except SystemExit:
        raise
    except BaseException as e:
        t = "-----------------------------------------------------------------------------\n"
        t += "UNHANDLED EXCEPTION OCCURRED!!\n"
        t += "\n"
        t += traceback.format_exc()
        t += "\n"
        t += f"EXCEPTION: {type(e)} {e}\n"
        t += "-----------------------------------------------------------------------------\n"
        t += "\n"
        print(t, file=sys.stderr)
        return 1


# ----------------------------------------------------------------------------------------
def _main_inner(argv: list[str]) -> int:
    """Inner main function that does the actual work."""
    args = parse_args(argv)

    # Determine mode: single binary or config file
    single_binary_args = [args.name, args.binary, args.platform]
    has_single_args = any(a is not None for a in single_binary_args)
    all_single_args = all(a is not None for a in single_binary_args) and args.pkg_version is not None

    if has_single_args and not all_single_args:
        print(
            "Error: --name, --version-str, --binary, and --platform are all required "
            "for single binary mode.",
            file=sys.stderr,
        )
        return 1

    if has_single_args:
        return _build_single(args)

    # Config file mode requires --config
    if args.config is not None:
        return _build_from_config(args)

    # No arguments given — show help
    parse_args(["--help"])
    return 0


# ----------------------------------------------------------------------------------------
def _build_single(args: Namespace) -> int:
    """
    Build a single wheel from CLI arguments.

    Parameters:
        args: Parsed command-line arguments.

    Returns:
        Exit code.
    """
    output_dir = Path(args.output_dir) if args.output_dir else Path(DEFAULT_OUTPUT_DIR)

    try:
        wheel_path = build_wheel(
            binary_path=Path(args.binary),
            name=args.name,
            version=args.pkg_version,
            platform=args.platform,
            output_dir=output_dir,
            description=args.description,
            author=args.author,
            author_email=args.author_email,
        )
    except (FileNotFoundError, IsADirectoryError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Built: {wheel_path}")
    return 0


# ----------------------------------------------------------------------------------------
def _build_from_config(args: Namespace) -> int:
    """
    Build wheels from a wheel.json configuration file.

    Parameters:
        args: Parsed command-line arguments.

    Returns:
        Exit code.
    """
    config_path = Path(args.config)

    try:
        config = load_config(config_path)
    except (FileNotFoundError, IsADirectoryError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    version = args.pkg_version if args.pkg_version else config.version
    if not version:
        print(
            "Error: version is required. Provide it in the config file or with --version-str.",
            file=sys.stderr,
        )
        return 1
    output_dir = Path(args.output_dir) if args.output_dir else Path(config.output_dir)
    built_count = 0

    for binary_mapping in config.binaries:
        wheel_path = build_wheel(
            binary_path=binary_mapping.binary_path,
            name=config.name,
            version=version,
            platform=binary_mapping.platform,
            output_dir=output_dir,
            description=config.description,
            author=config.author,
            author_email=config.author_email,
            license_name=config.license_name,
            homepage=config.homepage,
            python_requires=config.python_requires,
            classifiers=config.classifiers,
        )
        print(f"Built: {wheel_path}")
        built_count += 1

    print(f"\n{built_count} wheel(s) built in {output_dir}/")
    return 0
