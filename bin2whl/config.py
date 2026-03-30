# ----------------------------------------------------------------------------------------
#   config.py
#   ---------
#
#   JSON configuration file parser for bin2whl. Reads wheel.json files that
#   define package metadata and binary-to-platform mappings.
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

import json
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import cast

# ----------------------------------------------------------------------------------------
#   Constants
# ----------------------------------------------------------------------------------------

DEFAULT_OUTPUT_DIR = "wheels"
DEFAULT_PYTHON_REQUIRES = ">=3.7"

# ----------------------------------------------------------------------------------------
#   Data Classes
# ----------------------------------------------------------------------------------------


@dataclass
class BinaryMapping:
    """A mapping from a platform tag to a binary file path."""

    platform: str
    binary_path: Path


@dataclass
class WheelConfig:
    """Complete configuration for building wheels."""

    name: str
    version: str
    description: str
    author: str
    author_email: str
    license_name: str
    homepage: str
    binaries: list[BinaryMapping]
    output_dir: str
    python_requires: str


@dataclass
class ConfigErrors:
    """Collection of validation errors from config parsing."""

    errors: list[str] = field(default_factory=list[str])

    def add(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)

    @property
    def has_errors(self) -> bool:
        """Whether any errors were recorded."""
        return len(self.errors) > 0


# ----------------------------------------------------------------------------------------
#   Functions
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
def load_config(config_path: Path) -> WheelConfig:
    """
    Load and validate a wheel.json configuration file.

    Parameters:
        config_path: Path to the wheel.json file.

    Returns:
        Parsed and validated configuration.

    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config file is invalid or missing required fields.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        raw_value = json.load(f)

    if not isinstance(raw_value, dict):
        raise ValueError("Configuration file must contain a JSON object")
    raw = cast("dict[str, object]", raw_value)

    errors = ConfigErrors()
    base_dir = config_path.parent

    # Parse package fields (top-level in JSON)
    name = _require_str(raw, "name", errors)
    version = _require_str(raw, "version", errors)
    description = _optional_str(raw, "description", "")
    author = _optional_str(raw, "author", "")
    author_email = _optional_str(raw, "author-email", "")
    license_name = _optional_str(raw, "license", "")
    homepage = _optional_str(raw, "homepage", "")

    # Validate package name
    if name and not _is_valid_package_name(name):
        errors.add(
            f"Invalid package name: '{name}' (use alphanumeric, hyphens, or underscores)"
        )

    # Validate version (basic PEP 440 check)
    if version and not _is_valid_version(version):
        errors.add(f"Invalid version: '{version}' (must follow PEP 440)")

    # Parse binaries object
    binaries_raw = raw.get("binaries", {})
    if not isinstance(binaries_raw, dict):
        raise ValueError('"binaries" must be a JSON object')
    binaries_table = cast("dict[str, object]", binaries_raw)

    binaries: list[BinaryMapping] = []
    for platform_tag, binary_path_value in binaries_table.items():
        if not isinstance(binary_path_value, str):
            errors.add(f"Binary path for '{platform_tag}' must be a string")
            continue

        binary_path = base_dir / binary_path_value
        if not binary_path.exists():
            errors.add(f"Binary not found: {binary_path} (platform: {platform_tag})")
            continue

        binaries.append(BinaryMapping(platform=platform_tag, binary_path=binary_path))

    if not binaries and not errors.has_errors:
        errors.add('No binaries specified in "binaries"')

    # Parse options
    output_dir = _optional_str(raw, "output-dir", DEFAULT_OUTPUT_DIR)
    python_requires = _optional_str(raw, "python-requires", DEFAULT_PYTHON_REQUIRES)

    if errors.has_errors:
        raise ValueError(
            "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors.errors)
        )

    return WheelConfig(
        name=name,
        version=version,
        description=description,
        author=author,
        author_email=author_email,
        license_name=license_name,
        homepage=homepage,
        binaries=binaries,
        output_dir=output_dir,
        python_requires=python_requires,
    )


# ----------------------------------------------------------------------------------------
def _require_str(table: dict[str, object], key: str, errors: ConfigErrors) -> str:
    """
    Extract a required string field from a JSON object.

    Parameters:
        table:  The parsed JSON object.
        key:    The key to look up.
        errors: Error collector.

    Returns:
        The string value, or empty string if missing.
    """
    value = table.get(key)
    if value is None:
        errors.add(f'Missing required field: "{key}"')
        return ""
    if not isinstance(value, str):
        errors.add(f'"{key}" must be a string')
        return ""
    return value


# ----------------------------------------------------------------------------------------
def _optional_str(table: dict[str, object], key: str, default: str) -> str:
    """
    Extract an optional string field from a JSON object.

    Parameters:
        table:   The parsed JSON object.
        key:     The key to look up.
        default: Default value if key is missing.

    Returns:
        The string value, or default if missing.
    """
    value = table.get(key)
    if value is None:
        return default
    if not isinstance(value, str):
        return default
    return value


# ----------------------------------------------------------------------------------------
def _is_valid_package_name(name: str) -> bool:
    """
    Check whether a package name is valid (alphanumeric, hyphens, underscores).

    Parameters:
        name: The package name to validate.

    Returns:
        True if valid.
    """
    import re

    return bool(re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$", name))


# ----------------------------------------------------------------------------------------
def _is_valid_version(version: str) -> bool:
    """
    Check whether a version string is valid per PEP 440 (basic check).

    Parameters:
        version: The version string to validate.

    Returns:
        True if valid.
    """
    import re

    # Basic PEP 440 pattern: N.N.N with optional pre/post/dev suffixes
    pattern = r"^\d+(\.\d+)*((a|b|rc)\d+)?(\.post\d+)?(\.dev\d+)?$"
    return bool(re.match(pattern, version))
