import allure
import pytest

from pages.book_demo_page import BookDemoPage
from tests.book_demo.shared import CALENDLY_DOMAIN, BookingCopy

pytestmark = allure.suite("Book Demo")


class TestBookDemoUI:
    pytestmark = [pytest.mark.ui, allure.feature("UI/UX")]

    @pytest.mark.flaky(reruns=2, reruns_delay=2)
    def test_ui_calendar_heading_visible(self, opened_book_demo_page: BookDemoPage) -> None:
        page = opened_book_demo_page
        page.accept_cookies()
        assert page.wait_for_embed_ready(), "Calendly embed did not render within timeout"
        assert page.is_calendar_visible(), "Calendly embed should render calendar heading"

    @pytest.mark.flaky(reruns=2, reruns_delay=2)
    def test_ui_event_title_matches_copy(self, opened_book_demo_page: BookDemoPage) -> None:
        copy = BookingCopy()
        page = opened_book_demo_page
        page.accept_cookies()
        assert page.wait_for_embed_ready(), "Calendly embed did not render within timeout"
        assert page.get_event_title() == copy.event_title, "Event heading should match expected copy"

    @pytest.mark.flaky(reruns=2, reruns_delay=2)
    def test_ui_powered_by_calendly_link_present(self, opened_book_demo_page: BookDemoPage) -> None:
        page = opened_book_demo_page
        page.accept_cookies()
        assert page.wait_for_embed_ready(), "Calendly embed did not render within timeout"
        href = page.get_powered_by_href()
        assert href, "Powered by Calendly link should be present"

    @pytest.mark.flaky(reruns=2, reruns_delay=2)
    def test_ui_powered_by_calendly_link_is_secure(self, opened_book_demo_page: BookDemoPage) -> None:
        page = opened_book_demo_page
        page.accept_cookies()
        assert page.wait_for_embed_ready(), "Calendly embed did not render within timeout"
        href = page.get_powered_by_href()
        assert href and href.startswith("https://"), "Powered by link should use HTTPS"

    @pytest.mark.flaky(reruns=2, reruns_delay=2)
    def test_ui_powered_by_calendly_link_points_to_calendly(self, opened_book_demo_page: BookDemoPage) -> None:
        page = opened_book_demo_page
        page.accept_cookies()
        assert page.wait_for_embed_ready(), "Calendly embed did not render within timeout"
        href = page.get_powered_by_href()
        assert href and CALENDLY_DOMAIN in href, "Powered by link should navigate to Calendly domain"

    @pytest.mark.flaky(reruns=2, reruns_delay=2)
    def test_ui_iframe_src_present(self, opened_book_demo_page: BookDemoPage) -> None:
        page = opened_book_demo_page
        page.accept_cookies()
        assert page.wait_for_embed_ready(), "Calendly embed did not render within timeout"
        src = page.get_iframe_src()
        assert src, "Calendly iframe src should be defined"

    @pytest.mark.flaky(reruns=2, reruns_delay=2)
    def test_ui_iframe_src_is_secure(self, opened_book_demo_page: BookDemoPage) -> None:
        page = opened_book_demo_page
        page.accept_cookies()
        assert page.wait_for_embed_ready(), "Calendly embed did not render within timeout"
        src = page.get_iframe_src()
        assert src and src.startswith("https://"), "Calendly embed must load over HTTPS"
