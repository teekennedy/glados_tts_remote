from functools import lru_cache
import os
from pathlib import Path

import glados_tts


@lru_cache(maxsize=1)
def get_package_root() -> Path:
    """Get the absolute path to the package root directory (cached)."""
    # Get the directory where the glados_tts module is located
    package_dir = Path(os.path.dirname(os.path.abspath(glados_tts.__file__)))
    # Go up to the tts directory
    return package_dir.parent


def resource_path(relative_path: str) -> Path:
    """Return absolute path to a model file."""
    return get_package_root() / relative_path