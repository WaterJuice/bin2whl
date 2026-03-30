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
import re
from dataclasses import dataclass
from pathlib import Path
from typing import cast

# ----------------------------------------------------------------------------------------
#   Constants
# ----------------------------------------------------------------------------------------

DEFAULT_OUTPUT_DIR = "wheels"
DEFAULT_PYTHON_REQUIRES = ">=3.7"

_PACKAGE_NAME_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$")
_PEP440_VERSION_RE = re.compile(r"^\d+(\.\d+)*((a|b|rc)\d+)?(\.post\d+)?(\.dev\d+)?$")

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
    classifiers: list[str]
    readme_content: str


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
    with config_path.open("r", encoding="utf-8") as f:
        raw_value = json.load(f)

    if not isinstance(raw_value, dict):
        raise ValueError("Configuration file must contain a JSON object")
    raw = cast("dict[str, object]", raw_value)

    errors: list[str] = []
    base_dir = config_path.parent

    # Parse package fields (top-level in JSON)
    name = _require_str(raw, "name", errors)
    version = _optional_str(raw, "version", "")
    description = _optional_str(raw, "description", "")
    author = _optional_str(raw, "author", "")
    author_email = _optional_str(raw, "author-email", "")
    license_name = _optional_str(raw, "license", "")
    homepage = _optional_str(raw, "homepage", "")

    if name and not _PACKAGE_NAME_RE.match(name):
        errors.append(
            f"Invalid package name: '{name}' (use alphanumeric, hyphens, or underscores)"
        )

    if version and not _PEP440_VERSION_RE.match(version):
        errors.append(f"Invalid version: '{version}' (must follow PEP 440)")

    # Parse binaries object
    binaries_raw = raw.get("binaries", {})
    if not isinstance(binaries_raw, dict):
        raise ValueError('"binaries" must be a JSON object')
    binaries_table = cast("dict[str, object]", binaries_raw)

    binaries: list[BinaryMapping] = []
    for platform_tag, binary_path_value in binaries_table.items():
        if not isinstance(binary_path_value, str):
            errors.append(f"Binary path for '{platform_tag}' must be a string")
            continue

        binary_path = base_dir / binary_path_value
        if not binary_path.exists():
            errors.append(f"Binary not found: {binary_path} (platform: {platform_tag})")
            continue

        binaries.append(BinaryMapping(platform=platform_tag, binary_path=binary_path))

    if not binaries and not errors:
        errors.append('No binaries specified in "binaries"')

    # Parse readme file
    readme_path_str = _optional_str(raw, "readme", "")
    readme_content = ""
    if readme_path_str:
        readme_path = base_dir / readme_path_str
        if not readme_path.exists():
            errors.append(f"Readme file not found: {readme_path}")
        else:
            readme_content = readme_path.read_text(encoding="utf-8")

    # Parse options
    output_dir = _optional_str(raw, "output-dir", DEFAULT_OUTPUT_DIR)
    python_requires = _optional_str(raw, "python-requires", DEFAULT_PYTHON_REQUIRES)

    classifiers_raw = raw.get("classifiers")
    classifiers: list[str] = []
    if classifiers_raw is not None:
        if not isinstance(classifiers_raw, list):
            errors.append('"classifiers" must be an array')
        else:
            for i, c in enumerate(cast("list[object]", classifiers_raw)):
                if isinstance(c, str):
                    classifiers.append(c)
                else:
                    errors.append(f"classifiers[{i}] must be a string")

    if errors:
        raise ValueError(
            "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
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
        classifiers=classifiers,
        readme_content=readme_content,
    )


# ----------------------------------------------------------------------------------------
def _require_str(table: dict[str, object], key: str, errors: list[str]) -> str:
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
        errors.append(f'Missing required field: "{key}"')
        return ""
    if not isinstance(value, str):
        errors.append(f'"{key}" must be a string')
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
