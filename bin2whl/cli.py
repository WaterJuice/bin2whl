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

    # Config file path
    p.add_argument(
        "--config",
        "-c",
        default=None,
        help="path to config file (e.g. wheel.json)",
    )

    # Output directory override
    p.add_argument(
        "--output-dir",
        "-o",
        default=None,
        help="output directory for wheel files (overrides config)",
    )

    # Single binary mode arguments
    p.add_argument(
        "--name",
        default=None,
        help="package name (single binary mode)",
    )
    p.add_argument(
        "--version-str",
        default=None,
        dest="pkg_version",
        help="package version (single binary mode)",
    )
    p.add_argument(
        "--binary",
        default=None,
        help="path to binary file (single binary mode)",
    )
    p.add_argument(
        "--platform",
        default=None,
        help="platform tag, e.g. linux_x86_64 (single binary mode)",
    )
    p.add_argument(
        "--description",
        default="",
        help="package description",
    )
    p.add_argument(
        "--author",
        default="",
        help="author name",
    )
    p.add_argument(
        "--author-email",
        default="",
        help="author email",
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
    single_binary_args = [args.name, args.pkg_version, args.binary, args.platform]
    has_single_args = any(a is not None for a in single_binary_args)
    all_single_args = all(a is not None for a in single_binary_args)

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
    name: str = args.name
    version: str = args.pkg_version
    binary_path = Path(args.binary)
    platform: str = args.platform
    output_dir = Path(args.output_dir) if args.output_dir else Path("wheels")

    if not binary_path.exists():
        print(f"Error: Binary not found: {binary_path}", file=sys.stderr)
        return 1

    if not binary_path.is_file():
        print(f"Error: Not a file: {binary_path}", file=sys.stderr)
        return 1

    wheel_path = build_wheel(
        binary_path=binary_path,
        name=name,
        version=version,
        platform=platform,
        output_dir=output_dir,
        description=args.description,
        author=args.author,
        author_email=args.author_email,
    )

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
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir) if args.output_dir else Path(config.output_dir)
    built_count = 0

    for binary_mapping in config.binaries:
        wheel_path = build_wheel(
            binary_path=binary_mapping.binary_path,
            name=config.name,
            version=config.version,
            platform=binary_mapping.platform,
            output_dir=output_dir,
            description=config.description,
            author=config.author,
            author_email=config.author_email,
            license_name=config.license_name,
            homepage=config.homepage,
            python_requires=config.python_requires,
        )
        print(f"Built: {wheel_path}")
        built_count += 1

    print(f"\n{built_count} wheel(s) built in {output_dir}/")
    return 0
