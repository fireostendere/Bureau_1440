"""Test data generation helpers."""

from faker import Faker

SQL_INJECTION_PAYLOAD = "admin' OR '1'='1"
XSS_SCRIPT_PAYLOAD = "<script>alert('XSS')</script>"
XSS_HTML_PAYLOAD = "<b>user</b>"
DEFAULT_FAKER_LOCALE = "ru_RU"
DEFAULT_PASSWORD_LENGTH = 12


def generate_username(locale: str) -> str:
    """Generate random username using Faker."""
    username = Faker(locale).user_name()
    return username


def generate_password(length: int, locale: str) -> str:
    """Generate random password using Faker."""
    password = Faker(locale).password(length=length)
    return password
