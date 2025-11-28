import allure
import pytest
from playwright.sync_api import Browser

from config import AppConfig
from pages.admin_page import AdminPage
from pages.login_page import LoginPage
from tests.login.shared import (
    AUTH_CHECK_TIMEOUT,
    SCENARIOS,
    CredentialScenario,
    materialize_credentials,
    random_credentials,
    scenario_id,
)

pytestmark = allure.suite("Login Page")


class TestAuthentication:
    pytestmark = [pytest.mark.auth, allure.feature("Authentication")]

    @allure.story("Negative path")
    def test_login_with_invalid_credentials_shows_error(self, opened_login_page: LoginPage) -> None:
        username, password = random_credentials()
        opened_login_page.attempt_login(username, password)
        assert opened_login_page.wait_for_error(AUTH_CHECK_TIMEOUT), "Error banner should appear for invalid credentials"

    @allure.story("Positive path")
    def test_login_with_valid_credentials_navigates_to_admin(self, authenticated_login_page: LoginPage, app_config: AppConfig) -> None:
        admin_page = AdminPage(authenticated_login_page.page, app_config)
        assert admin_page.is_authenticated(timeout=AUTH_CHECK_TIMEOUT), "Valid credentials should navigate to admin dashboard"

    @allure.story("Negative path")
    def test_login_with_empty_credentials_shows_error(self, opened_login_page: LoginPage) -> None:
        opened_login_page.attempt_login("", "")
        assert opened_login_page.has_username_validation_error(), "Username field should block empty submission"

    @allure.story("Negative path")
    def test_login_with_empty_username_shows_error(self, opened_login_page: LoginPage) -> None:
        _, password = random_credentials()
        opened_login_page.attempt_login("", password)
        assert opened_login_page.has_username_validation_error(), "Username HTML5 validation should trigger for empty value"

    @allure.story("Negative path")
    def test_login_with_empty_password_shows_error(self, opened_login_page: LoginPage, admin_credentials: dict[str, str]) -> None:
        opened_login_page.attempt_login(admin_credentials["username"], "")
        assert opened_login_page.has_password_validation_error(), "Password HTML5 validation should trigger for empty value"

    @allure.story("Negative path")
    @pytest.mark.parametrize("scenario", SCENARIOS, ids=scenario_id)
    def test_login_with_various_invalid_inputs(self, opened_login_page: LoginPage, scenario: CredentialScenario) -> None:
        username, password = materialize_credentials(scenario.description, scenario)
        opened_login_page.attempt_login(username, password)
        if opened_login_page.wait_for_error(AUTH_CHECK_TIMEOUT):
            return
        admin_page = AdminPage(opened_login_page.page, opened_login_page.config)
        assert not admin_page.is_authenticated(timeout=AUTH_CHECK_TIMEOUT), f"Authentication should fail for scenario: {scenario.description}"

    @allure.story("Positive path")
    def test_fun_password_case_sensitive(self, opened_login_page: LoginPage, admin_credentials: dict[str, str]) -> None:
        opened_login_page.attempt_login_with_swapped_case_password(
            admin_credentials["username"],
            admin_credentials["password"],
        )
        if opened_login_page.wait_for_error(AUTH_CHECK_TIMEOUT):
            return
        admin_page = AdminPage(opened_login_page.page, opened_login_page.config)
        assert not admin_page.is_authenticated(timeout=AUTH_CHECK_TIMEOUT), "Swapped-case password must not authenticate"

    @allure.story("Positive path")
    def test_fun_session_persists_after_restart(
        self,
        browser: Browser,
        authenticated_storage_state: dict,
        app_config: AppConfig,
    ) -> None:
        context = browser.new_context(storage_state=authenticated_storage_state)
        page = context.new_page()
        admin_page = AdminPage(page, app_config)
        admin_page.open()
        session_persisted = admin_page.is_authenticated(timeout=AUTH_CHECK_TIMEOUT)
        context.close()
        assert session_persisted, "Session should survive context recreation with stored state"

    @allure.story("Negative path")
    def test_neg_excessive_input_length_rejected(self, opened_login_page: LoginPage) -> None:
        opened_login_page.fill_long_credentials(length=300)
        assert opened_login_page.wait_for_error(AUTH_CHECK_TIMEOUT), "Overly long credentials must be rejected"

    @allure.story("Negative path")
    def test_neg_password_cleared_after_failed_login(self, opened_login_page: LoginPage) -> None:
        username, password = random_credentials()
        opened_login_page.attempt_login(username, password)
        assert opened_login_page.wait_for_error(AUTH_CHECK_TIMEOUT), "Error banner should appear for invalid credentials"
        assert opened_login_page.get_password_field_value() == "", "Password field should clear after failed login"
        assert opened_login_page.get_username_field_value() == username, "Username field should preserve entered value after failed login"
