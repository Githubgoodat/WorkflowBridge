"""Portable paths; never inspect another application's profile."""
from pathlib import Path
import os
import sys

PROJECT_ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[2]


def get_data_dir():
    value = os.environ.get("WORKFLOW_BRIDGE_HOME")
    path = Path(value) if value else PROJECT_ROOT / "data"
    if not path.is_absolute() or ".." in path.parts or str(path).startswith(("\\\\", "//")):
        raise ValueError("data_directory_must_be_absolute_and_local")
    for parent in (path, *path.parents):
        if parent.exists():
            info = parent.lstat()
            if parent.is_symlink() or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ValueError("linked_data_directory_not_allowed")
    return path


def get_cache_dir():
    return get_data_dir() / "cache"


def get_user_data_dir():
    return get_data_dir() / "profile"
