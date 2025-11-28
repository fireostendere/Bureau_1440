"""Reusable credential factories for negative authentication scenarios."""

from dataclasses import dataclass
from functools import lru_cache
from typing import Callable, Iterable, List, Sequence, Tuple

from faker import Faker

from helpers.data import DEFAULT_FAKER_LOCALE, DEFAULT_PASSWORD_LENGTH

CredentialFactory = Callable[[Faker], str]


@dataclass(frozen=True)
class CredentialScenario:
    username_factory: CredentialFactory
    password_factory: CredentialFactory
    description: str


def constant(value: str) -> CredentialFactory:
    """Return a factory that always yields the provided value."""

    def provider(_: Faker) -> str:
        constant_value = value
        return constant_value

    return provider


def username_email(fake: Faker) -> str:
    email_value = fake.email()
    return email_value


def username_random(fake: Faker) -> str:
    random_username = fake.user_name() + fake.pystr(min_chars=5, max_chars=5)
    return random_username


def username_long(fake: Faker) -> str:
    long_username = fake.user_name() + "x" * 200
    return long_username


def username_cyrillic(fake: Faker) -> str:
    cyrillic_username = fake.name()
    return cyrillic_username


def password_random(fake: Faker) -> str:
    random_password = fake.password(length=DEFAULT_PASSWORD_LENGTH)
    return random_password


DEFAULT_SCENARIOS: Sequence[CredentialScenario] = (
    CredentialScenario(username_email, password_random, "Valid email with random password"),
    CredentialScenario(username_random, constant("123456"), "Weak password"),
    CredentialScenario(username_long, password_random, "Very long username"),
    CredentialScenario(constant("!@#$%^&*()_+-=[]{}|;':\"<>?,./"), constant("!@#$%^&*()"), "Special characters"),
    CredentialScenario(username_cyrillic, constant("Пароль123"), "Cyrillic characters"),
)


def build_invalid_credential_scenarios(
    scenarios: Iterable[CredentialScenario] | None,
) -> List[CredentialScenario]:
    """Return a list of invalid credential scenarios with optional overrides."""
    combined = list(DEFAULT_SCENARIOS)
    if scenarios:
        combined.extend(scenarios)
    scenario_list = combined
    return scenario_list


@lru_cache(maxsize=64)
def materialize_credentials(description: str, scenario: CredentialScenario) -> Tuple[str, str]:
    """Generate concrete username/password pair for a scenario (cached by description)."""
    faker = Faker(DEFAULT_FAKER_LOCALE)
    username = scenario.username_factory(faker)
    password = scenario.password_factory(faker)
    credentials = (username, password)
    return credentials


def scenario_id(scenario: CredentialScenario) -> str:
    """Provide readable identifier for parametrized scenarios."""
    identifier = scenario.description
    return identifier
