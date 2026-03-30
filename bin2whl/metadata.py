# ----------------------------------------------------------------------------------------
#   metadata.py
#   -----------
#
#   Wheel metadata generation. Creates METADATA, WHEEL, entry_points.txt, RECORD,
#   and top_level.txt files compliant with PEP 427.
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

import base64
import hashlib
from dataclasses import dataclass

# ----------------------------------------------------------------------------------------
#   Data Classes
# ----------------------------------------------------------------------------------------


@dataclass
class FileRecord:
    """A file entry for the RECORD file."""

    path: str
    sha256_digest: str
    size: int


# ----------------------------------------------------------------------------------------
#   Functions
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
def generate_metadata(
    name: str,
    version: str,
    description: str,
    author: str,
    author_email: str,
    license_name: str,
    homepage: str,
    python_requires: str,
    classifiers: list[str] | None = None,
    readme_content: str = "",
) -> str:
    """
    Generate the METADATA file content for a wheel.

    Parameters:
        name:            Package name.
        version:         Package version.
        description:     Short description.
        author:          Author name.
        author_email:    Author email.
        license_name:    Licence identifier.
        homepage:        Project homepage URL.
        python_requires: Minimum Python version specifier.

    Returns:
        The METADATA file content as a string.
    """
    lines = [
        "Metadata-Version: 2.1",
        f"Name: {name}",
        f"Version: {version}",
        f"Summary: {description}",
    ]

    if homepage:
        lines.append(f"Home-page: {homepage}")
    if author:
        lines.append(f"Author: {author}")
    if author_email:
        lines.append(f"Author-email: {author_email}")
    if license_name:
        lines.append(f"License: {license_name}")
    if python_requires:
        lines.append(f"Requires-Python: {python_requires}")
    if classifiers:
        for classifier in classifiers:
            lines.append(f"Classifier: {classifier}")
    if readme_content:
        lines.append("Description-Content-Type: text/markdown")

    lines.append("")

    if readme_content:
        return "\n".join(lines) + readme_content + "\n"
    return "\n".join(lines)


# ----------------------------------------------------------------------------------------
def generate_wheel_metadata(platform: str) -> str:
    """
    Generate the WHEEL file content.

    Parameters:
        platform: The platform tag (e.g. linux_x86_64, macosx_11_0_arm64).

    Returns:
        The WHEEL file content as a string.
    """
    lines = [
        "Wheel-Version: 1.0",
        "Generator: bin2whl",
        "Root-Is-Purelib: false",
        f"Tag: py3-none-{platform}",
        "",
    ]
    return "\n".join(lines)


# ----------------------------------------------------------------------------------------
def compute_file_hash(data: bytes) -> str:
    """
    Compute the SHA256 hash of file data in the format used by RECORD files.

    Parameters:
        data: The file content as bytes.

    Returns:
        The hash in 'sha256=<urlsafe-base64>' format.
    """
    digest = hashlib.sha256(data).digest()
    b64 = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return f"sha256={b64}"


# ----------------------------------------------------------------------------------------
def generate_record(files: list[FileRecord], dist_info_prefix: str) -> str:
    """
    Generate the RECORD file content listing all files in the wheel.

    Parameters:
        files:            List of file records with paths, hashes, and sizes.
        dist_info_prefix: The dist-info directory name (e.g. pkg-1.0.0.dist-info).

    Returns:
        The RECORD file content as a string.
    """
    lines: list[str] = []
    for f in files:
        lines.append(f"{f.path},{f.sha256_digest},{f.size}")

    # RECORD itself is listed without hash or size
    lines.append(f"{dist_info_prefix}/RECORD,,")
    lines.append("")
    return "\n".join(lines)
