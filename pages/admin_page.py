import allure

from config import AppConfig
from playwright.sync_api import Error, TimeoutError as PlaywrightTimeoutError
from .base_page import BasePage


class AdminPage(BasePage):
    """Page object for the Django admin panel."""

    ADMIN_PATH = "/admin/"

    USER_MENU_SELECTOR = "#user-tools"
    LOGOUT_SELECTORS = ("text='LOG OUT'", "text='Log out'")

    PASSWORD_CHANGE_LINK = "a[href='/admin/password_change/']"
    AUTH_HOME_LINK = "a[href='/admin/auth/']"

    GROUP_LIST_LINK = "a[href='/admin/auth/group/']"
    GROUP_CREATE_LINK = "a[href='/admin/auth/group/add/']"

    USER_LIST_LINK = "a[href='/admin/auth/user/']"
    USER_CREATE_LINK = "a[href='/admin/auth/user/add/']"

    ATHLETE_LIST_LINK = "a[href='/admin/cms/athlete/']"
    ATHLETE_CREATE_LINK = "a[href='/admin/cms/athlete/add/']"

    FILE_LIST_LINK = "a[href='/admin/cms/merafile/']"
    FILE_CREATE_LINK = "a[href='/admin/cms/merafile/add/']"

    TEST_LIST_LINK = "a[href='/admin/cms/test/']"
    TEST_CREATE_LINK = "a[href='/admin/cms/test/add/']"

    TASK_RESULT_LIST_LINK = "a[href='/admin/django_tasks_database/dbtaskresult/']"
    TASK_RESULT_CREATE_LINK = "a[href='/admin/django_tasks_database/dbtaskresult/add/']"

    WELCOME_HEADING_SELECTOR = "h1, h2"
    WEEK_BUTTON_SELECTOR = 'text="Week"'
    MONTH_BUTTON_SELECTOR = 'text="Month"'

    def __init__(self, page, config: AppConfig) -> None:
        super().__init__(page)
        self.config = config

    @property
    def url(self) -> str:
        """Build full admin URL with HTTPS."""
        admin_url = self.config.build_admin_url(self.ADMIN_PATH)
        return admin_url

    def is_authenticated(self, timeout: int) -> bool:
        """Detect whether the user menu is visible, implying a successful login."""
        try:
            self.page.wait_for_selector(
                self.USER_MENU_SELECTOR,
                state="visible",
                timeout=timeout,
            )
            return True
        except (Error, PlaywrightTimeoutError):
            return False

    def open(self) -> None:
        """Navigate directly to the admin root URL."""
        self.page.goto(self.url, wait_until="domcontentloaded")

    def logout(self) -> bool:
        """Log out of the admin if the option is available."""
        with allure.step("Log out from admin panel"):
            for selector in self.LOGOUT_SELECTORS:
                try:
                    self.click(selector, timeout=None)
                    return True
                except (Error, PlaywrightTimeoutError):
                    continue
            return False

    def open_password_change(self) -> None:
        """Navigate to the password change screen."""
        with allure.step("Open password change page"):
            self.click(self.PASSWORD_CHANGE_LINK)

    def open_auth_dashboard(self) -> None:
        """Navigate to the authentication/authorization section."""
        with allure.step("Open auth dashboard"):
            self.click(self.AUTH_HOME_LINK)

    def open_group_list(self) -> None:
        """Open the groups list."""
        with allure.step("Open group list"):
            self.locator(self.GROUP_LIST_LINK).first.click()

    def open_group_create(self) -> None:
        """Navigate to the group creation form."""
        with allure.step("Open group creation form"):
            self.click(self.GROUP_CREATE_LINK)

    def open_group_edit(self, index: int = 1) -> None:
        """Open a group edit page by index (defaults to the first entry)."""
        with allure.step(f"Open group edit form at index {index}"):
            self.locator(self.GROUP_LIST_LINK).nth(index).click()

    def open_user_list(self) -> None:
        """Open the users list."""
        with allure.step("Open user list"):
            self.locator(self.USER_LIST_LINK).first.click()

    def open_user_create(self) -> None:
        """Navigate to the user creation form."""
        with allure.step("Open user creation form"):
            self.click(self.USER_CREATE_LINK)

    def open_user_edit(self, index: int = 1) -> None:
        """Open a user edit page by index (defaults to the first entry)."""
        with allure.step(f"Open user edit form at index {index}"):
            self.locator(self.USER_LIST_LINK).nth(index).click()

    def open_athlete_list(self) -> None:
        """Open the athlete CMS list."""
        with allure.step("Open athlete list"):
            self.locator(self.ATHLETE_LIST_LINK).first.click()

    def open_athlete_create(self) -> None:
        """Navigate to the athlete creation form."""
        with allure.step("Open athlete creation form"):
            self.click(self.ATHLETE_CREATE_LINK)

    def open_athlete_edit(self, index: int = 1) -> None:
        """Open an athlete edit page by index (defaults to the first entry)."""
        with allure.step(f"Open athlete edit form at index {index}"):
            self.locator(self.ATHLETE_LIST_LINK).nth(index).click()

    def open_file_list(self) -> None:
        """Open the file CMS list."""
        with allure.step("Open file list"):
            self.locator(self.FILE_LIST_LINK).first.click()

    def open_file_create(self) -> None:
        """Navigate to the file creation form."""
        with allure.step("Open file creation form"):
            self.click(self.FILE_CREATE_LINK)

    def open_file_edit(self, index: int = 1) -> None:
        """Open a file edit page by index (defaults to the first entry)."""
        with allure.step(f"Open file edit form at index {index}"):
            self.locator(self.FILE_LIST_LINK).nth(index).click()

    def open_test_list(self) -> None:
        """Open the test CMS list."""
        with allure.step("Open test list"):
            self.locator(self.TEST_LIST_LINK).first.click()

    def open_test_create(self) -> None:
        """Navigate to the test creation form."""
        with allure.step("Open test creation form"):
            self.click(self.TEST_CREATE_LINK)

    def open_test_edit(self, index: int = 1) -> None:
        """Open a test edit page by index (defaults to the first entry)."""
        with allure.step(f"Open test edit form at index {index}"):
            self.locator(self.TEST_LIST_LINK).nth(index).click()

    def open_task_result_list(self) -> None:
        """Open the task result list."""
        with allure.step("Open task result list"):
            self.locator(self.TASK_RESULT_LIST_LINK).first.click()

    def open_task_result_create(self) -> None:
        """Navigate to the task result creation form."""
        with allure.step("Open task result creation form"):
            self.click(self.TASK_RESULT_CREATE_LINK)

    def open_task_result_edit(self, index: int = 1) -> None:
        """Open a task result edit page by index (defaults to the first entry)."""
        with allure.step(f"Open task result edit form at index {index}"):
            self.locator(self.TASK_RESULT_LIST_LINK).nth(index).click()

    def get_welcome_heading(self) -> str | None:
        """Return the text of the welcome heading if present."""
        with allure.step("Read welcome heading"):
            return self.locator(self.WELCOME_HEADING_SELECTOR).first.text_content()

    def select_week_view(self) -> None:
        """Activate the 'Week' view."""
        with allure.step("Select week view"):
            self.click(self.WEEK_BUTTON_SELECTOR)

    def select_month_view(self) -> None:
        """Activate the 'Month' view."""
        with allure.step("Select month view"):
            self.click(self.MONTH_BUTTON_SELECTOR)
