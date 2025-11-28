from tests.data_factory.credentials import (
    CredentialScenario,
    build_invalid_credential_scenarios,
    materialize_credentials,
    scenario_id,
)
from helpers.data import (
    DEFAULT_FAKER_LOCALE,
    DEFAULT_PASSWORD_LENGTH,
    generate_password,
    generate_username,
)

AUTH_CHECK_TIMEOUT = 500
SCENARIOS = build_invalid_credential_scenarios(None)


def random_credentials() -> tuple[str, str]:
    username = generate_username(DEFAULT_FAKER_LOCALE)
    password = generate_password(DEFAULT_PASSWORD_LENGTH, DEFAULT_FAKER_LOCALE)
    return username, password


__all__ = [
    "AUTH_CHECK_TIMEOUT",
    "SCENARIOS",
    "random_credentials",
    "CredentialScenario",
    "materialize_credentials",
    "scenario_id",
]
