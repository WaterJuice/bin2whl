# ----------------------------------------------------------------------------------------
#   wheel_builder.py
#   ----------------
#
#   Core wheel building logic. Creates PEP 427 compliant .whl files (ZIP archives)
#   containing a pre-compiled binary placed directly into the scripts directory
#   via the .data/scripts/ mechanism. No Python wrapper — the binary lands straight
#   in the venv's bin/ directory.
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
from bin2whl.metadata import generate_metadata
from bin2whl.metadata import generate_record
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
    python_requires: str = ">=3.7",
) -> Path:
    """
    Build a single wheel file from a pre-compiled binary.

    The binary is placed into the .data/scripts/ directory so that pip installs
    it directly into the venv's bin/ (or Scripts/ on Windows) with no Python
    wrapper script.

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
    data_dir = f"{pkg_name}-{version}.data"

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
        # Add the binary into .data/scripts/ — pip copies this to bin/
        binary_data = binary_path.read_bytes()
        binary_arcname = f"{data_dir}/scripts/{binary_filename}"
        _write_to_zip(whl, binary_arcname, binary_data, executable=True)
        records.append(
            FileRecord(
                path=binary_arcname,
                sha256_digest=compute_file_hash(binary_data),
                size=len(binary_data),
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
