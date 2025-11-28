import allure
import pytest

from pages.book_demo_page import BookDemoPage
from tests.book_demo.shared import DEFAULT_SLOT_WAIT_MS

pytestmark = allure.suite("Book Demo")


class TestBookDemoNavigation:
    pytestmark = [pytest.mark.ui, allure.feature("Navigation")]

    def test_nav_select_available_day_reveals_time_slots(self, opened_book_demo_page: BookDemoPage) -> None:
        page = opened_book_demo_page
        page.accept_cookies()
        assert page.wait_for_embed_ready(), "Calendly embed did not render within timeout"
        assert page.choose_day(strategy="first"), "No available days with open slots"
        assert page.wait_for_time_slots(timeout_ms=DEFAULT_SLOT_WAIT_MS), "Selecting available day should reveal time slots"

    def test_nav_timezone_control_visible(self, opened_book_demo_page: BookDemoPage) -> None:
        page = opened_book_demo_page
        page.accept_cookies()
        assert page.wait_for_embed_ready(), "Calendly embed did not render within timeout"
        assert page.is_timezone_control_visible(), "Time zone control should be visible when embed renders"

    def test_nav_select_random_day_and_time_opens_form(self, opened_book_demo_page: BookDemoPage) -> None:
        page = opened_book_demo_page
        page.accept_cookies()
        assert page.wait_for_embed_ready(), "Calendly embed did not render within timeout"
        assert page.choose_day(strategy="random"), "No available days with open slots"
        assert page.wait_for_time_slots(timeout_ms=DEFAULT_SLOT_WAIT_MS), "Time slots not visible after selecting day"
        
        # Check if slots are available before attempting selection
        slot_count = page.get_available_time_slot_count()
        if slot_count == 0:
            pytest.skip("No available time slots on selected day - skipping test to avoid flakiness")
        
        # Use atomic methods for better error diagnostics
        slot_label = page.select_time_slot()
        assert slot_label is not None, f"Failed to select time slot from {slot_count} available slots"
        
        # Click Next button if present (some Calendly flows require it)
        page.click_next_button()
        # Confirm selection and wait for invitee form
        assert page.confirm_slot(), "Invitee form should appear after choosing a time slot"
