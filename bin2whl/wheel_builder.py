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

_EXECUTABLE_PERMS = 0o755
_REGULAR_PERMS = 0o644

# Short aliases for common platform tags
PLATFORM_ALIASES: dict[str, str] = {
    "linux_x86_64": "manylinux_2_17_x86_64",
    "linux_amd64": "manylinux_2_17_x86_64",
    "linux_aarch64": "manylinux_2_17_aarch64",
    "linux_arm64": "manylinux_2_17_aarch64",
    "macos_x86_64": "macosx_10_9_x86_64",
    "macos_amd64": "macosx_10_9_x86_64",
    "macos_arm64": "macosx_11_0_arm64",
    "macos_aarch64": "macosx_11_0_arm64",
    "windows_amd64": "win_amd64",
    "windows_x86_64": "win_amd64",
    "windows_arm64": "win_arm64",
}

# ----------------------------------------------------------------------------------------
#   Functions
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
def resolve_platform(tag: str) -> str:
    """
    Resolve a platform tag, expanding aliases to their canonical form.
    Unknown tags are passed through as-is (any valid wheel tag is accepted).

    Parameters:
        tag: Platform tag or alias.

    Returns:
        The canonical platform tag.
    """
    return PLATFORM_ALIASES.get(tag, tag)


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
    classifiers: list[str] | None = None,
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
        IsADirectoryError: If the binary path is a directory.
    """
    platform = resolve_platform(platform)
    pkg_name = normalise_name(name)
    dist_info = f"{pkg_name}-{version}.dist-info"
    data_dir = f"{pkg_name}-{version}.data"

    binary_filename = name
    if platform.startswith("win"):
        binary_filename = name + ".exe"

    output_dir.mkdir(parents=True, exist_ok=True)

    wheel_filename = f"{pkg_name}-{version}-py3-none-{platform}.whl"
    wheel_path = output_dir / wheel_filename

    records: list[FileRecord] = []

    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as whl:
        # Binary into .data/scripts/ — pip copies this directly to bin/
        binary_data = binary_path.read_bytes()
        _add_file(
            whl,
            f"{data_dir}/scripts/{binary_filename}",
            binary_data,
            records,
            executable=True,
        )

        metadata_content = generate_metadata(
            name=name,
            version=version,
            description=description,
            author=author,
            author_email=author_email,
            license_name=license_name,
            homepage=homepage,
            python_requires=python_requires,
            classifiers=classifiers,
        )
        _add_file(
            whl, f"{dist_info}/METADATA", metadata_content.encode("utf-8"), records
        )
        _add_file(
            whl,
            f"{dist_info}/WHEEL",
            generate_wheel_metadata(platform).encode("utf-8"),
            records,
        )

        # RECORD must be last — lists all other files, then itself without a hash
        record_content = generate_record(records, dist_info)
        _write_to_zip(whl, f"{dist_info}/RECORD", record_content.encode("utf-8"))

    return wheel_path


# ----------------------------------------------------------------------------------------
def _add_file(
    whl: zipfile.ZipFile,
    arcname: str,
    data: bytes,
    records: list[FileRecord],
    executable: bool = False,
) -> None:
    """
    Write a file to the wheel and append its hash record.

    Parameters:
        whl:        The open ZipFile.
        arcname:    Archive member name.
        data:       File content as bytes.
        records:    Record list to append to.
        executable: Whether to set executable permissions.
    """
    _write_to_zip(whl, arcname, data, executable=executable)
    records.append(
        FileRecord(
            path=arcname,
            sha256_digest=compute_file_hash(data),
            size=len(data),
        )
    )


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
    perms = _EXECUTABLE_PERMS if executable else _REGULAR_PERMS
    info.external_attr = (stat.S_IFREG | perms) << 16
    zf.writestr(info, data)
