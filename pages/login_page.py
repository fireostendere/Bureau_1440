import allure
from playwright.sync_api import Error, TimeoutError as PlaywrightTimeoutError

from config import AppConfig
from helpers.qa import is_form_centered_in_viewport
from helpers.ui_validator import LoginPageUIValidator
from .base_page import BasePage


class LoginPage(BasePage):
    """Page object for the admin login form.
    
    Responsibility: ONLY interaction with the login form elements.
    
    For additional functionality, use specialized helpers:
    - Network monitoring: helpers.network_monitor.LoginRequestMonitor
    - UI validation: helpers.ui_validator.LoginPageUIValidator
    - HTTP redirects: helpers.navigation.HTTPRedirectTester
    """

    LOGIN_PATH = "/admin/login/?next=/admin/login"
    SCREENSHOT_NAME = "login-page.png"
    _USERNAME_SELECTOR = "#id_username"
    _PASSWORD_SELECTOR = "#id_password"
    _SUBMIT_SELECTOR = "[type='submit']"
    _ERROR_SELECTOR = ".errornote"
    
    # Public selector for security tests
    PASSWORD_SELECTOR = _PASSWORD_SELECTOR

    def __init__(self, page, config: AppConfig) -> None:
        super().__init__(page)
        self.config = config

    @property
    def url(self) -> str:
        """Build full login URL with HTTPS."""
        login_url = self.config.build_admin_url(self.LOGIN_PATH)
        return login_url

    @property
    def http_url(self) -> str:
        """Build HTTP version of login URL (for redirect tests)."""
        http_url = f"http://{self.config.admin_host}{self.LOGIN_PATH}"
        return http_url

    def open(self) -> None:
        """Navigate to the login page and wait for the form to appear."""
        with allure.step("Open admin login page"):
            super().open()
            self.wait_for_visible(self._USERNAME_SELECTOR, timeout=None)

    def attempt_login(self, username: str, password: str) -> None:
        """Fill the login form and submit it."""
        with allure.step("Attempt to authenticate"):
            self.fill(self._USERNAME_SELECTOR, username, timeout=None)
            self.fill(self._PASSWORD_SELECTOR, password, timeout=None)
            self.click(self._SUBMIT_SELECTOR, timeout=None)

    def attempt_login_with_swapped_case_password(self, username: str, password: str) -> None:
        """Attempt login with password that has swapped case (for testing case sensitivity)."""
        swapped_password = password.swapcase()
        self.attempt_login(username, swapped_password)

    def fill_long_credentials(self, length: int = 300) -> None:
        """Fill form with excessively long credentials (for testing input validation)."""
        long_username = "a" * length
        long_password = "b" * length
        self.attempt_login(long_username, long_password)

    def navigate_via_register_link(self) -> None:
        """Click the registration/book-a-demo link."""
        register_link = self.page.get_by_role("link", name="register")
        register_link.click()

    def go_back(self) -> None:
        """Navigate back using browser history."""
        self.page.go_back()

    def is_password_field_empty(self) -> bool:
        """Check if password field is empty."""
        return self.get_password_field_value() == ""

    def submit_multiple(self, count: int, wait_ms: int = 500) -> None:
        """Click the submit button multiple times and wait briefly afterwards."""
        button = self.locator(self._SUBMIT_SELECTOR)
        for _ in range(count):
            button.click()
        self.page.wait_for_timeout(wait_ms)

    def wait_for_error(self, timeout_ms: int) -> bool:
        """Wait for an error banner to appear within the given timeout."""
        try:
            self.page.wait_for_selector(self._ERROR_SELECTOR, state="visible", timeout=timeout_ms)
            return True
        except PlaywrightTimeoutError:
            return False

    def is_error_visible(self) -> bool:
        """Check if an error message is visible on the page."""
        locator = self.locator(self._ERROR_SELECTOR)
        return locator.is_visible()

    def has_validation_error(self, field_selector: str) -> bool:
        """Check if a form field has HTML5 validation error."""
        locator = self.locator(field_selector)
        return bool(locator.evaluate("el => !el.validity.valid"))

    def has_username_validation_error(self) -> bool:
        """Check if username field has HTML5 validation error."""
        return self.has_validation_error(self._USERNAME_SELECTOR)

    def has_password_validation_error(self) -> bool:
        """Check if password field has HTML5 validation error."""
        return self.has_validation_error(self._PASSWORD_SELECTOR)

    def is_form_centered(self) -> tuple[bool, bool]:
        """Check if login form is centered on the page.
        
        Returns:
            Tuple of (is_horizontally_centered, is_vertically_centered)
        """
        return is_form_centered_in_viewport(self.page)

    def get_error_text(self) -> str:
        """Get error message text from error element."""
        error_locator = self.locator(self._ERROR_SELECTOR)
        return error_locator.inner_text()

    def get_page_content(self) -> str:
        """Get full page HTML content."""
        return self.page.content()

    def get_password_field_value(self) -> str:
        """Get current value of password field."""
        element = self.page.query_selector(self._PASSWORD_SELECTOR)
        if element is None:
            return ""
        try:
            return self.page.eval_on_selector(self._PASSWORD_SELECTOR, "el => el.value")
        except (Error, PlaywrightTimeoutError):
            return ""

    def get_username_field_value(self) -> str:
        """Get current value of username field."""
        element = self.page.query_selector(self._USERNAME_SELECTOR)
        if element is None:
            return ""
        try:
            return self.page.eval_on_selector(self._USERNAME_SELECTOR, "el => el.value")
        except (Error, PlaywrightTimeoutError):
            return ""

    def get_field_type(self, selector: str) -> str | None:
        """Get type attribute of an input field."""
        field_type = self.get_attribute(selector, "type", strict=False)
        return field_type

    def get_submit_button_hover_colors(self) -> tuple[str, str]:
        """Get submit button colors before and after hover via UI validator."""
        validator = LoginPageUIValidator(self.page)
        return validator.get_button_hover_colors()

    def is_on_login_page(self) -> bool:
        """Check if currently on login page."""
        return self.url in self.page.url

    def get_session_cookie(self) -> dict | None:
        """Get session cookie if present."""
        cookies = self.page.context.cookies()
        for cookie in cookies:
            if "sessionid" in cookie.get("name", "").lower():
                return cookie
        return None

    def fetch_headers(self, context) -> dict:
        """Fetch response headers for current page."""
        headers = {}
        
        def capture_headers(response):
            if self.config.admin_host in response.url:
                headers.update(response.headers)
        
        context.on("response", capture_headers)
        self.page.reload()
        return headers

    # UI validation methods
    
    def get_submit_button_color(self) -> str:
        """Get current background color of the submit button.
        
        Returns:
            CSS color value as string
        """
        button = self.locator(self._SUBMIT_SELECTOR)
        return button.evaluate("el => window.getComputedStyle(el).backgroundColor")
    
    def hover_submit_button(self) -> None:
        """Hover over the submit button and wait for stabilization."""
        button = self.locator(self._SUBMIT_SELECTOR)
        button.hover()
        self.page.wait_for_timeout(self.HOVER_STABILIZATION_DELAY)
    
    def get_submit_button_hover_colors(self) -> tuple[str, str]:
        """Get submit button colors before and after hover.
        
        Returns:
            Tuple of (initial_color, hovered_color)
        """
        initial_color = self.get_submit_button_color()
        self.hover_submit_button()
        hovered_color = self.get_submit_button_color()
        return (initial_color, hovered_color)

    # Network monitoring methods

    def start_login_request_monitoring(self) -> list[str]:
        """Start monitoring login POST requests.
        
        Returns:
            List that will be populated with request URLs as they occur.
        """
        captured_requests = []
        
        def handle_request(request):
            if request.method == "POST" and "/admin/login" in request.url:
                captured_requests.append(request.url)
        
        self.page.on("request", handle_request)
        return captured_requests

