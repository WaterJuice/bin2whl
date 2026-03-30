# ----------------------------------------------------------------------------------------
#   __main__.py
#   -----------
#
#   Entry point for python -m bin2whl.
#
#   (c) 2026 WaterJuice — Unlicense; see LICENSE in the project root.
#
#   Version History
#   ---------------
#   Mar 2026 - Created
# ----------------------------------------------------------------------------------------

import sys

MIN_PYTHON = (3, 12)
if sys.version_info < MIN_PYTHON:
    print(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required.", file=sys.stderr)
    sys.exit(1)

from bin2whl.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
