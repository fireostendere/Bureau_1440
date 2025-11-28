import allure
import pytest

from pages.book_demo_page import BookDemoPage
from pages.login_page import LoginPage

pytestmark = allure.suite("Login Page")


class TestNavigation:
    pytestmark = [pytest.mark.ui, allure.feature("Navigation")]

    def test_fun_registration_link_navigation(self, opened_login_page: LoginPage) -> None:
        opened_login_page.navigate_via_register_link()
        book_demo_page = BookDemoPage(opened_login_page.page, opened_login_page.config)
        assert book_demo_page.is_on_book_demo_page(), "Registration link should route to book-a-demo page"

    def test_neg_browser_back_does_not_expose_password(self, authenticated_login_page: LoginPage) -> None:
        authenticated_login_page.go_back()
        assert authenticated_login_page.is_password_field_empty(), "Password field should be cleared after navigating back"
