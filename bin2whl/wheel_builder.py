# ----------------------------------------------------------------------------------------
#   wheel_builder.py
#   ----------------
#
#   Core wheel building logic. Creates PEP 427 compliant .whl files (ZIP archives)
#   containing a pre-compiled binary and proper metadata.
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

import re
import stat
import zipfile
from pathlib import Path
from bin2whl.metadata import FileRecord
from bin2whl.metadata import compute_file_hash
from bin2whl.metadata import generate_entry_points
from bin2whl.metadata import generate_metadata
from bin2whl.metadata import generate_record
from bin2whl.metadata import generate_top_level
from bin2whl.metadata import generate_wheel_metadata

# ----------------------------------------------------------------------------------------
#   Constants
# ----------------------------------------------------------------------------------------

# Permissions for files inside the wheel ZIP
_EXECUTABLE_PERMS = 0o755
_REGULAR_PERMS = 0o644

# ----------------------------------------------------------------------------------------
#   Functions
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
def normalise_name(name: str) -> str:
    """
    Normalise a package name for use in wheel filenames and directory names.
    Replaces hyphens and dots with underscores.

    Parameters:
        name: The raw package name.

    Returns:
        The normalised name.
    """
    return re.sub(r"[-.]", "_", name)


# ----------------------------------------------------------------------------------------
def build_wheel(
    binary_path: Path,
    name: str,
    version: str,
    platform: str,
    output_dir: Path,
    description: str = "",
    author: str = "",
    author_email: str = "",
    license_name: str = "",
    homepage: str = "",
    console_script: bool = True,
    python_requires: str = ">=3.7",
) -> Path:
    """
    Build a single wheel file from a pre-compiled binary.

    Parameters:
        binary_path:     Path to the pre-compiled binary.
        name:            Package name (e.g. your-go-tool).
        version:         Package version (e.g. 1.0.0).
        platform:        Platform tag (e.g. linux_x86_64).
        output_dir:      Directory to write the .whl file to.
        description:     Short description for metadata.
        author:          Author name.
        author_email:    Author email address.
        license_name:    Licence identifier.
        homepage:        Project homepage URL.
        console_script:  Whether to create a console_scripts entry point.
        python_requires: Minimum Python version specifier.

    Returns:
        Path to the created .whl file.

    Raises:
        FileNotFoundError: If the binary does not exist.
        ValueError: If the binary path is not a file.
    """
    if not binary_path.exists():
        raise FileNotFoundError(f"Binary not found: {binary_path}")
    if not binary_path.is_file():
        raise ValueError(f"Not a file: {binary_path}")

    pkg_name = normalise_name(name)
    dist_info = f"{pkg_name}-{version}.dist-info"

    # Determine the binary filename inside the wheel
    binary_filename = name
    if platform.startswith("win"):
        binary_filename = name + ".exe"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Wheel filename per PEP 427
    wheel_filename = f"{pkg_name}-{version}-py3-none-{platform}.whl"
    wheel_path = output_dir / wheel_filename

    # Collect all files and their records
    records: list[FileRecord] = []

    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as whl:
        # Add the binary
        binary_data = binary_path.read_bytes()
        binary_arcname = f"{pkg_name}/bin/{binary_filename}"
        _write_to_zip(whl, binary_arcname, binary_data, executable=True)
        records.append(
            FileRecord(
                path=binary_arcname,
                sha256_digest=compute_file_hash(binary_data),
                size=len(binary_data),
            )
        )

        # Add __init__.py with a main() function that launches the binary
        init_content = _generate_init_py(pkg_name, binary_filename)
        init_data = init_content.encode("utf-8")
        init_arcname = f"{pkg_name}/__init__.py"
        _write_to_zip(whl, init_arcname, init_data)
        records.append(
            FileRecord(
                path=init_arcname,
                sha256_digest=compute_file_hash(init_data),
                size=len(init_data),
            )
        )

        # Add METADATA
        metadata_content = generate_metadata(
            name=name,
            version=version,
            description=description,
            author=author,
            author_email=author_email,
            license_name=license_name,
            homepage=homepage,
            python_requires=python_requires,
        )
        metadata_data = metadata_content.encode("utf-8")
        metadata_arcname = f"{dist_info}/METADATA"
        _write_to_zip(whl, metadata_arcname, metadata_data)
        records.append(
            FileRecord(
                path=metadata_arcname,
                sha256_digest=compute_file_hash(metadata_data),
                size=len(metadata_data),
            )
        )

        # Add WHEEL
        wheel_meta_content = generate_wheel_metadata(platform)
        wheel_meta_data = wheel_meta_content.encode("utf-8")
        wheel_meta_arcname = f"{dist_info}/WHEEL"
        _write_to_zip(whl, wheel_meta_arcname, wheel_meta_data)
        records.append(
            FileRecord(
                path=wheel_meta_arcname,
                sha256_digest=compute_file_hash(wheel_meta_data),
                size=len(wheel_meta_data),
            )
        )

        # Add top_level.txt
        top_level_content = generate_top_level(pkg_name)
        top_level_data = top_level_content.encode("utf-8")
        top_level_arcname = f"{dist_info}/top_level.txt"
        _write_to_zip(whl, top_level_arcname, top_level_data)
        records.append(
            FileRecord(
                path=top_level_arcname,
                sha256_digest=compute_file_hash(top_level_data),
                size=len(top_level_data),
            )
        )

        # Add entry_points.txt (if console_script is enabled)
        if console_script:
            entry_points_content = generate_entry_points(name, pkg_name)
            entry_points_data = entry_points_content.encode("utf-8")
            entry_points_arcname = f"{dist_info}/entry_points.txt"
            _write_to_zip(whl, entry_points_arcname, entry_points_data)
            records.append(
                FileRecord(
                    path=entry_points_arcname,
                    sha256_digest=compute_file_hash(entry_points_data),
                    size=len(entry_points_data),
                )
            )

        # Add RECORD (must be last)
        record_content = generate_record(records, dist_info)
        record_data = record_content.encode("utf-8")
        record_arcname = f"{dist_info}/RECORD"
        _write_to_zip(whl, record_arcname, record_data)

    return wheel_path


# ----------------------------------------------------------------------------------------
def _write_to_zip(
    zf: zipfile.ZipFile,
    arcname: str,
    data: bytes,
    executable: bool = False,
) -> None:
    """
    Write data to a ZIP file with proper permissions.

    Parameters:
        zf:         The open ZipFile.
        arcname:    Archive member name.
        data:       File content as bytes.
        executable: Whether to set executable permissions.
    """
    info = zipfile.ZipInfo(arcname)
    info.compress_type = zipfile.ZIP_DEFLATED

    # Set external attributes for Unix permissions
    perms = _EXECUTABLE_PERMS if executable else _REGULAR_PERMS
    info.external_attr = (stat.S_IFREG | perms) << 16

    zf.writestr(info, data)


# ----------------------------------------------------------------------------------------
def _generate_init_py(pkg_name: str, binary_filename: str) -> str:
    """
    Generate an __init__.py that provides a main() function to launch the binary.
    The main() function is used as the console_scripts entry point.

    Parameters:
        pkg_name:        The normalised package name.
        binary_filename: The binary filename inside the bin/ directory.

    Returns:
        The __init__.py content as a string.
    """
    return f'''"""Wrapper to launch the {binary_filename} binary."""

import os
import subprocess
import sys


def main() -> None:
    """Launch the bundled binary, passing through all arguments and exit code."""
    binary = os.path.join(os.path.dirname(__file__), "bin", "{binary_filename}")
    result = subprocess.run([binary, *sys.argv[1:]])
    raise SystemExit(result.returncode)
'''
