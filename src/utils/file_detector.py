"""
RAG Preprocessor - File Type Detection Utilities
Detects and routes files to appropriate drivers.
"""

from pathlib import Path
from typing import Optional, Callable, Dict, Any


# Supported file extensions and their types
FILE_TYPE_MAP = {
    # PDF files
    '.pdf': 'pdf',

    # Excel files
    '.xlsx': 'excel',
    '.xls': 'excel',
    '.xlsm': 'excel',

    # Markdown files
    '.md': 'markdown',
    '.markdown': 'markdown',
    '.mdown': 'markdown',

    # Manus files (treated as markdown)
    '.manus': 'markdown',
}


def detect_file_type(file_path: str) -> Optional[str]:
    """
    Detect the file type based on extension.

    Args:
        file_path: Path to the file

    Returns:
        File type string ('pdf', 'excel', 'markdown') or None if unsupported
    """
    path = Path(file_path)
    extension = path.suffix.lower()

    return FILE_TYPE_MAP.get(extension)


def is_supported_file(file_path: str) -> bool:
    """
    Check if a file type is supported.

    Args:
        file_path: Path to the file

    Returns:
        True if the file type is supported
    """
    return detect_file_type(file_path) is not None


def get_supported_extensions() -> list:
    """
    Get list of supported file extensions.

    Returns:
        List of supported extensions
    """
    return list(FILE_TYPE_MAP.keys())


def get_files_from_directory(directory: str, recursive: bool = True) -> list:
    """
    Get all supported files from a directory.

    Args:
        directory: Path to directory
        recursive: Whether to search subdirectories

    Returns:
        List of file paths
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        return []

    files = []

    if recursive:
        for ext in FILE_TYPE_MAP.keys():
            files.extend(dir_path.rglob(f"*{ext}"))
    else:
        for ext in FILE_TYPE_MAP.keys():
            files.extend(dir_path.glob(f"*{ext}"))

    return [str(f) for f in files if f.is_file()]
