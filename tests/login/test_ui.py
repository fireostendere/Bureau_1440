import allure
import pytest

from helpers.files import ensure_dir, get_artifact_path, get_baseline_path
from helpers.media import calculate_screenshot_difference
from pages.login_page import LoginPage

pytestmark = allure.suite("Login Page")


class TestUI:
    pytestmark = [pytest.mark.ui, allure.feature("UI/UX")]

    def test_ui_form_is_centered(self, opened_login_page: LoginPage) -> None:
        is_h_centered, is_v_centered = opened_login_page.is_form_centered()
        assert is_h_centered and is_v_centered, "Login form should remain centered both horizontally and vertically"

    def test_ui_login_page_visual_baseline(self, opened_login_page: LoginPage) -> None:
        screenshot_dir = ensure_dir(get_artifact_path("screenshots"))
        screenshot_path = screenshot_dir / LoginPage.SCREENSHOT_NAME
        opened_login_page.take_screenshot(path=str(screenshot_path), full_page=True)
        baseline_path = get_baseline_path(LoginPage.SCREENSHOT_NAME)
        diff_score = calculate_screenshot_difference(screenshot_path, baseline_path)
        assert diff_score <= 2.0, f"Visual diff score {diff_score:.2f} exceeds tolerated threshold"

    def test_ui_login_button_hover_feedback(self, opened_login_page: LoginPage) -> None:
        initial_color, hovered_color = opened_login_page.get_submit_button_hover_colors()
        assert initial_color != hovered_color, "Submit button should change color on hover"

