import allure
import pytest

from pages.login_page import LoginPage

pytestmark = allure.suite("Login Page")


class TestStability:
    pytestmark = [pytest.mark.stability, allure.feature("Stability")]

    def test_neg_multiple_clicks_trigger_single_request(self, opened_login_page: LoginPage) -> None:
        request_urls = opened_login_page.start_login_request_monitoring()
        opened_login_page.attempt_login("invalid-user", "invalid-pass")
        opened_login_page.submit_multiple(count=2, wait_ms=1500)
        assert len(request_urls) <= 1, "Multiple rapid clicks should not trigger duplicate POST requests"
