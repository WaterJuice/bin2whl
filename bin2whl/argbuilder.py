# ----------------------------------------------------------------------------------------
#   argbuilder.py
#   -------------
#
#   Argument parser wrapper with deferred execution. Provides a thin layer over
#   argparse for consistent CLI argument handling.
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

import argparse
import sys
from typing import Any

# ----------------------------------------------------------------------------------------
#   Types
# ----------------------------------------------------------------------------------------

Namespace = argparse.Namespace

# ----------------------------------------------------------------------------------------
#   Classes
# ----------------------------------------------------------------------------------------


class ArgsParser:
    """
    Thin wrapper over argparse.ArgumentParser with a simplified interface.
    """

    # ------------------------------------------------------------------------------------
    def __init__(
        self,
        prog: str,
        description: str,
        version: str,
    ) -> None:
        """
        Initialise the argument parser.

        Parameters:
            prog:        Program name.
            description: Program description shown in help.
            version:     Version string shown with --version.
        """
        self._parser = argparse.ArgumentParser(
            prog=prog,
            description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self._parser.add_argument(
            "--version",
            action="version",
            version=version,
        )

    # ------------------------------------------------------------------------------------
    def add_argument(self, *args: Any, **kwargs: Any) -> argparse.Action:
        """
        Add an argument to the parser. Passes through to argparse.

        Parameters:
            args:   Positional arguments for argparse.
            kwargs: Keyword arguments for argparse.

        Returns:
            The created Action.
        """
        return self._parser.add_argument(*args, **kwargs)

    # ------------------------------------------------------------------------------------
    def add_mutex_group(self) -> "MutexGroup":
        """
        Add a mutually exclusive argument group.

        Returns:
            A MutexGroup wrapper.
        """
        group = self._parser.add_mutually_exclusive_group()
        return MutexGroup(group)

    # ------------------------------------------------------------------------------------
    def parse(self, argv: list[str]) -> Namespace:
        """
        Parse arguments and return the namespace.

        Parameters:
            argv: List of argument strings (without program name).

        Returns:
            Parsed argument namespace.
        """
        return self._parser.parse_args(argv)

    # ------------------------------------------------------------------------------------
    def error(self, message: str) -> None:
        """
        Print an error message and exit.

        Parameters:
            message: The error message to display.
        """
        self._parser.error(message)
        sys.exit(2)


class MutexGroup:
    """Wrapper for a mutually exclusive argument group."""

    # ------------------------------------------------------------------------------------
    def __init__(self, group: argparse._MutuallyExclusiveGroup) -> None:  # pyright: ignore[reportPrivateUsage]
        self._group = group

    # ------------------------------------------------------------------------------------
    def add_argument(self, *args: Any, **kwargs: Any) -> argparse.Action:
        """
        Add an argument to the mutex group. Passes through to argparse.

        Parameters:
            args:   Positional arguments for argparse.
            kwargs: Keyword arguments for argparse.

        Returns:
            The created Action.
        """
        return self._group.add_argument(*args, **kwargs)
