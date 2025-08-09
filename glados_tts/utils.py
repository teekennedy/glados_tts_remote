from functools import lru_cache
import os
from pathlib import Path

import glados_tts


@lru_cache(maxsize=1)
def get_models_dir() -> Path:
    """Get the absolute path to the model directory (cached)."""
    # Check for environment variable first
    models_dir = os.environ.get("GLADOS_TTS_MODELS_DIR")
    if models_dir:
        return Path(models_dir)

    # Default to the directory where the glados_tts module is located
    return Path(os.path.dirname(os.path.abspath(glados_tts.__file__)))


def resource_path(relative_path: str) -> Path:
    """Return absolute path to a model file."""
    return get_models_dir() / relative_path
