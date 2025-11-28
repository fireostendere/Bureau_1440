import allure
import pytest
from playwright.sync_api import Browser

from helpers.data import SQL_INJECTION_PAYLOAD, XSS_HTML_PAYLOAD, XSS_SCRIPT_PAYLOAD
from helpers.navigation import HTTPRedirectTester
from helpers.qa import has_x_frame_options_protection
from pages.login_page import LoginPage
from tests.login.shared import random_credentials

pytestmark = allure.suite("Login Page")


class TestSecurity:
    pytestmark = [pytest.mark.security, allure.feature("Security")]

    def test_fun_sql_injection_is_blocked(self, opened_login_page: LoginPage) -> None:
        opened_login_page.attempt_login(SQL_INJECTION_PAYLOAD, SQL_INJECTION_PAYLOAD)
        assert opened_login_page.is_on_login_page(), "SQL injection payload must not bypass login"

    def test_fun_xss_payload_is_escaped(self, opened_login_page: LoginPage) -> None:
        opened_login_page.attempt_login(XSS_SCRIPT_PAYLOAD, XSS_SCRIPT_PAYLOAD)
        error_html = opened_login_page.get_error_text()
        assert "<script>" not in error_html, "Error message should escape script tags"

    def test_sec_https_redirect_enforced(self, browser: Browser, opened_login_page: LoginPage) -> None:
        redirect_tester = HTTPRedirectTester(browser)
        final_url = redirect_tester.open_via_http_and_get_final_url(opened_login_page.http_url)
        assert final_url.startswith("https://"), "HTTP login should redirect to HTTPS"

    def test_sec_cookie_flags_set(self, authenticated_login_page: LoginPage) -> None:
        session_cookie = authenticated_login_page.get_session_cookie()
        assert session_cookie.get("httpOnly"), "Session cookie should include HttpOnly flag"

    def test_sec_password_not_exposed_in_dom(self, opened_login_page: LoginPage) -> None:
        username, password = random_credentials()
        opened_login_page.attempt_login(username, password)
        opened_login_page.is_error_visible()
        page_source = opened_login_page.get_page_content()
        assert password not in page_source, "Password must not be exposed in DOM source"

    def test_sec_x_frame_options_header_present(self, context, opened_login_page: LoginPage) -> None:
        headers = opened_login_page.fetch_headers(context)
        assert has_x_frame_options_protection(headers), "X-Frame-Options header should protect against clickjacking"

    def test_neg_xss_payload_not_in_dom(self, opened_login_page: LoginPage) -> None:
        opened_login_page.attempt_login(XSS_HTML_PAYLOAD, XSS_HTML_PAYLOAD)
        opened_login_page.is_error_visible()
        page_html = opened_login_page.get_page_content()
        assert XSS_HTML_PAYLOAD not in page_html, "HTML payload should be sanitized out of DOM"

    def test_sec_password_field_type(self, opened_login_page: LoginPage) -> None:
        field_type = opened_login_page.get_field_type(opened_login_page.PASSWORD_SELECTOR)
        assert field_type == "password", "Password field must keep type='password'"
