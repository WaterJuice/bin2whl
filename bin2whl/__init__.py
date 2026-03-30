# ----------------------------------------------------------------------------------------
#   __init__.py
#   -----------
#
#   bin2whl package initialisation.
#
#   (c) 2026 WaterJuice — Unlicense; see LICENSE in the project root.
#
#   Version History
#   ---------------
#   Mar 2026 - Created
# ----------------------------------------------------------------------------------------

"""bin2whl: Build Python wheels from pre-compiled binaries."""

from bin2whl.version import VERSION_STR

__all__ = ["__version__"]

__version__ = VERSION_STR
