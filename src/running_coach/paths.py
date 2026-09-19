import os
from pathlib import Path

from platformdirs import user_data_dir

DATA_DIR_ENV_VAR = "RUNNING_COACH_DATA_DIR"


def get_data_dir() -> Path:
    override = os.getenv(DATA_DIR_ENV_VAR)
    data_dir = Path(override).expanduser() if override else Path(user_data_dir("running-coach"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir
