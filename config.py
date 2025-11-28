"""Application-wide configuration helpers for test runs."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(os.getenv("TEST_PROJECT_ROOT", Path(__file__).resolve().parent))
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class AppConfig:
    """Normalized configuration values shared across fixtures and page objects."""

    admin_host: str
    marketing_host: str
    scheme: str
    artifacts_dir: Path

    @property
    def admin_base_url(self) -> str:
        return f"{self.scheme}://{self.admin_host}"

    @property
    def marketing_base_url(self) -> str:
        return f"{self.scheme}://{self.marketing_host}"

    def build_admin_url(self, path: str) -> str:
        normalized = path if path.startswith("/") else f"/{path}"
        return f"{self.admin_base_url}{normalized}"

    def build_marketing_url(self, path: str) -> str:
        normalized = path if path.startswith("/") else f"/{path}"
        return f"{self.marketing_base_url}{normalized}"


@lru_cache(maxsize=1)
def get_app_config(base_host: str | None = None) -> AppConfig:
    """Return cached application configuration."""
    env_file = Path(os.getenv("TEST_ENV_FILE", DEFAULT_ENV_FILE))
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=False, encoding="utf-8")

    scheme = os.getenv("APP_SCHEME", "https")
    admin_host_env = os.getenv("APP_BASE_HOST")
    marketing_host_env = os.getenv("MARKETING_BASE_HOST")

    admin_host = base_host or admin_host_env
    if not admin_host:
        raise ValueError("APP_BASE_HOST must be set (no default admin host)")

    marketing_host = marketing_host_env or admin_host

    artifacts_dir = Path(os.getenv("ARTIFACTS_ROOT", "artifacts")).resolve()

    return AppConfig(
        admin_host=admin_host,
        marketing_host=marketing_host,
        scheme=scheme,
        artifacts_dir=artifacts_dir,
    )
