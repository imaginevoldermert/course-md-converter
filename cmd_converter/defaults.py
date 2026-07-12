import os
from pathlib import Path


def get_default_output_dir() -> Path:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    configured = os.getenv("CMD_OUTPUT_DIR")
    return Path(configured).expanduser() if configured else (Path.cwd() / "outputs").resolve()


DEFAULT_OUTPUT_DIR = get_default_output_dir()
