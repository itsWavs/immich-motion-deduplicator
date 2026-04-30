import os
from pathlib import Path


ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def load_dotenv():
    if not ENV_PATH.exists():
        return

    for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def require_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def require_directory_env(name):
    value = Path(require_env(name)).expanduser()

    if not value.exists():
        raise FileNotFoundError(f"Configured path for {name} does not exist: {value}")

    if not value.is_dir():
        raise NotADirectoryError(f"Configured path for {name} is not a directory: {value}")

    return str(value)


def get_immich_api_url():
    api_url = require_env("IMMICH_API_URL").rstrip("/")
    if not api_url.endswith("/api"):
        api_url = f"{api_url}/api"
    return api_url
