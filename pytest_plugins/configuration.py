import pytest

from config import AppConfig, get_app_config
from helpers.files import get_env


@pytest.fixture(scope="session")
def app_config(pytestconfig) -> AppConfig:
    """Provide normalized configuration derived from CLI/env values."""
    base_host = pytestconfig.getoption("--base-url")
    try:
        return get_app_config(base_host)
    except ValueError as exc:
        pytest.skip(f"Missing required host configuration: {exc}")


@pytest.fixture
def admin_credentials() -> dict[str, str]:
    """Fetch admin credentials or skip tests if they are unavailable."""
    username = get_env("ADMIN_USERNAME", None)
    password = get_env("ADMIN_PASSWORD", None)
    if not username or not password:
        pytest.skip("ADMIN_USERNAME/ADMIN_PASSWORD are required for auth fixtures")
    return {"username": username, "password": password}
