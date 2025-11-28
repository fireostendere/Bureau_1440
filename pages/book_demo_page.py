import logging
import random
import re
from typing import Optional

import allure
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config import AppConfig
from .base_page import BasePage

logger = logging.getLogger(__name__)


class BookDemoPage(BasePage):
    """Page object for the book-a-demo registration page."""

    BOOK_DEMO_PATH = "/book-a-demo"
    CALENDLY_IFRAME_SELECTOR = "iframe[src*='calendly.com']"
    EVENT_HEADING = "30 Minute Meeting"
    CALENDAR_HEADING_PATTERN = re.compile(r"Select a (Day|Date)", flags=re.IGNORECASE)
    TIME_HEADING_PATTERN = re.compile(r"Select a Time", flags=re.IGNORECASE)
    TIME_SLOT_PATTERN = re.compile(r"\b\d{1,2}:\d{2}\s*(am|pm)?\b", flags=re.IGNORECASE)
    COOKIE_ACCEPT_TEXT = "I understand"
    DEFAULT_EMBED_TIMEOUT_MS = 15000
    INVITEE_FORM_TIMEOUT_MS = 30000
    EMAIL_INPUT_SELECTOR = "input[type='email'], input[name*='email' i]"

    def __init__(self, page, config: AppConfig) -> None:
        super().__init__(page)
        self.config = config

    @property
    def url(self) -> str:
        """Build full book-a-demo URL."""
        return self.config.build_marketing_url(self.BOOK_DEMO_PATH)

    def open(self) -> None:
        """Navigate to the book-a-demo page and wait for embed to appear."""
        with allure.step("Open book-a-demo page"):
            self.page.goto(self.url, wait_until="domcontentloaded")
            self.wait_for_visible(self.CALENDLY_IFRAME_SELECTOR, timeout=10000)

    def is_on_book_demo_page(self) -> bool:
        """Check if current URL is on book-a-demo page."""
        expected_prefix = self.url
        on_demo_page = self.page.url.startswith(expected_prefix)
        return on_demo_page

    def calendly_frame(self):
        """Return frame locator targeting Calendly embed."""
        return self.page.frame_locator(self.CALENDLY_IFRAME_SELECTOR)

    def _calendly_frame_object(self):
        """Return underlying Playwright Frame for the Calendly embed (internal use only)."""
        return self.page.frame(url=re.compile("calendly.com"))

    def accept_cookies(self) -> bool:
        """Dismiss Calendly cookie banner if present."""
        button = self.calendly_frame().get_by_role("button", name=self.COOKIE_ACCEPT_TEXT)
        try:
            if button.count() == 0:
                return False
            button.first.click()
            return True
        except PlaywrightTimeoutError:
            return False

    def wait_for_embed_ready(self, timeout_ms: int | None = None) -> bool:
        """Wait for Calendly embed to render the calendar heading."""
        self.wait_for_loading_to_finish(timeout_ms)
        heading = self.calendly_frame().get_by_role("heading", name=self.CALENDAR_HEADING_PATTERN)
        try:
            heading.wait_for(state="visible", timeout=timeout_ms or self.DEFAULT_EMBED_TIMEOUT_MS)
            return True
        except PlaywrightTimeoutError:
            return False

    def choose_day(self, strategy: str = "random", timeout_ms: int | None = None) -> bool:
        """Select a day with available slots (random or first)."""
        if strategy == "first":
            return self.select_first_available_day(timeout_ms)
        return self.select_random_available_day(timeout_ms)

    def wait_for_loading_to_finish(self, timeout_ms: int | None = None) -> None:
        """Wait for embed loading indicators/progress bars to disappear."""
        progress_locator = self.calendly_frame().locator("[role='progressbar'], .progress, .loading-indicator")
        try:
            progress_locator.wait_for(state="hidden", timeout=timeout_ms or self.DEFAULT_EMBED_TIMEOUT_MS)
        except PlaywrightTimeoutError:
            # If progress remains, continue anyway to avoid hard failure
            pass

    def get_iframe_src(self) -> Optional[str]:
        """Return Calendly iframe src value."""
        return self.get_attribute(self.CALENDLY_IFRAME_SELECTOR, "src", strict=False)

    def get_event_title(self) -> str:
        """Return the heading text for the Calendly event."""
        heading = self.calendly_frame().get_by_role("heading", name=self.EVENT_HEADING)
        try:
            return heading.inner_text()
        except PlaywrightTimeoutError:
            return ""

    def is_calendar_visible(self, timeout: int = 5000) -> bool:
        """Check if calendar heading is visible inside the embed."""
        return self.wait_for_embed_ready(timeout)

    def get_powered_by_href(self) -> Optional[str]:
        """Get href of powered-by Calendly link."""
        link = self.calendly_frame().get_by_role("link", name="powered by Calendly")
        try:
            return link.get_attribute("href")
        except PlaywrightTimeoutError:
            return None

    def select_first_available_day(self, timeout_ms: int | None = None) -> bool:
        """Click the first day that has available times, if any."""
        frame = self._calendly_frame_object()
        if frame is None:
            return False

        if not self._wait_for_available_day(frame, timeout_ms):
            return False

        available_buttons = self._get_available_day_buttons(frame)
        if not available_buttons:
            return False

        available_buttons[0][0].click()
        return True

    def select_random_available_day(self, timeout_ms: int | None = None) -> bool:
        """Click a random available day to avoid always hitting the same slot."""
        frame = self._calendly_frame_object()
        if frame is None:
            return False

        if not self._wait_for_available_day(frame, timeout_ms):
            return False

        available_buttons = self._get_available_day_buttons(frame)
        if not available_buttons:
            return False

        button, _ = random.choice(available_buttons)
        button.click()
        return True

    def wait_for_time_slots(self, timeout_ms: int = 20000) -> bool:
        """Wait until time slots section becomes visible (heading or slot buttons)."""
        self.wait_for_loading_to_finish(timeout_ms)
        frame = self._calendly_frame_object()
        if frame is None:
            return False
        try:
            frame.wait_for_function(
                """(pattern) => {
                    const re = new RegExp(pattern, "i");
                    const headings = Array.from(document.querySelectorAll("h1, h2, [role='heading']"));
                    const hasHeading = headings.some(h => re.test((h.textContent || "").toString()));
                    const slotButtons = Array.from(document.querySelectorAll("button[role='button'], button"));
                    const hasSlot = slotButtons.some(btn => /\\d{1,2}:\\d{2}/.test(btn.textContent || btn.getAttribute("aria-label") || ""));
                    return hasHeading || hasSlot;
                }""",
                arg=self.TIME_HEADING_PATTERN.pattern,
                timeout=timeout_ms,
            )
            return True
        except PlaywrightTimeoutError:
            return False

    def get_available_time_slot_count(self) -> int:
        """Return count of available time slots on the current day.
        
        Returns:
            Number of available time slots, or 0 if frame not accessible.
        """
        frame = self._calendly_frame_object()
        if frame is None:
            logger.warning("Cannot count time slots: Calendly frame not found")
            return 0
        
        slots = self._get_available_time_slots(frame)
        return len(slots)

    def select_time_slot(self, index: int | None = None) -> Optional[str]:
        """Select a time slot by index (or random if index is None).
        
        Args:
            index: Specific slot index to select, or None for random selection.
        
        Returns:
            Label of the selected time slot, or None if selection failed.
        """
        frame = self._calendly_frame_object()
        if frame is None:
            logger.error("Cannot select time slot: Calendly frame not found")
            return None

        if not self.wait_for_time_slots(timeout_ms=self.DEFAULT_EMBED_TIMEOUT_MS):
            logger.error("Cannot select time slot: time slots did not appear")
            return None

        slots = self._get_available_time_slots(frame)
        if not slots:
            logger.warning("No available time slots found on selected day")
            return None

        # Select by index or randomly
        if index is not None:
            if index < 0 or index >= len(slots):
                logger.error(f"Invalid slot index {index}, available slots: 0-{len(slots)-1}")
                return None
            button, label = slots[index]
        else:
            button, label = random.choice(slots)
        
        with allure.step(f"Select time slot: {label}"):
            button.click()
            logger.info(f"Selected time slot: {label}")
        
        return label

    def click_next_button(self, timeout_ms: int | None = None) -> bool:
        """Click the 'Next' button if present after time slot selection.
        
        Returns:
            True if Next button was found and clicked, False otherwise.
        """
        frame = self._calendly_frame_object()
        if frame is None:
            return False
        
        try:
            next_btn = frame.get_by_role("button", name=re.compile(r"^Next", flags=re.IGNORECASE))
            if next_btn.count() > 0:
                with allure.step("Click Next button"):
                    next_btn.first.click(timeout=timeout_ms or self.DEFAULT_EMBED_TIMEOUT_MS)
                    self.wait_for_loading_to_finish(timeout_ms)
                    logger.info("Clicked Next button after time slot selection")
                return True
        except PlaywrightTimeoutError:
            logger.debug("Next button not found or not clickable")
        
        return False

    def confirm_time_selection(self, timeout_ms: int | None = None, raise_on_failure: bool = False) -> bool:
        """Confirm time selection and wait for invitee form to appear.
        
        Args:
            timeout_ms: Maximum wait time in milliseconds.
            raise_on_failure: If True, raises exception with diagnostics on failure.
        
        Returns:
            True if invitee form appeared, False otherwise.
        
        Raises:
            TimeoutError: If raise_on_failure=True and form doesn't appear.
        """
        result = self.wait_for_invitee_form(timeout_ms=timeout_ms, raise_on_failure=raise_on_failure)
        if result:
            logger.info("Time selection confirmed, invitee form visible")
        elif raise_on_failure:
            raise PlaywrightTimeoutError("Invitee form did not appear after time selection")
        else:
            logger.warning("Invitee form did not appear within timeout")
        return result

    def confirm_slot(self, timeout_ms: int | None = None, raise_on_failure: bool = False) -> bool:
        """Click Next (if present) and wait for invitee form."""
        self.click_next_button(timeout_ms=timeout_ms)
        return self.wait_for_invitee_form(timeout_ms=timeout_ms, raise_on_failure=raise_on_failure)

    def is_timezone_control_visible(self, timeout_ms: int | None = None) -> bool:
        """Check visibility of time zone button inside the embed."""
        if not self.wait_for_embed_ready(timeout_ms):
            return False
        tz_button = self.calendly_frame().get_by_role(
            "button",
            name=re.compile("Time zone", flags=re.IGNORECASE),
        )
        try:
            tz_button.wait_for(state="visible", timeout=timeout_ms or self.DEFAULT_EMBED_TIMEOUT_MS)
            return tz_button.is_visible()
        except PlaywrightTimeoutError:
            return False

    def wait_for_invitee_form(self, timeout_ms: int | None = None, raise_on_failure: bool = False) -> bool:
        """Wait for invitee details form (email/name fields) after picking a time slot.
        
        Args:
            timeout_ms: Maximum wait time in milliseconds.
            raise_on_failure: If True, logs diagnostics and can be used for debugging.
        
        Returns:
            True if form appeared, False otherwise.
        """
        frame = self._calendly_frame_object()
        if frame is None:
            logger.error("Cannot wait for invitee form: Calendly frame not found")
            if raise_on_failure:
                raise PlaywrightTimeoutError("Calendly frame not accessible")
            return False
        
        timeout = timeout_ms or self.INVITEE_FORM_TIMEOUT_MS

        # Some embeds require an extra click on a secondary "Next"/"Confirm" button.
        try:
            confirm_btn = frame.get_by_role("button", name=re.compile(r"^(Next|Confirm|Continue)", flags=re.IGNORECASE))
            if confirm_btn.count() > 0:
                confirm_btn.first.click(timeout=timeout)
                logger.debug("Clicked confirmation button before waiting for form")
        except PlaywrightTimeoutError:
            logger.debug("No confirmation button found")

        self.wait_for_loading_to_finish(timeout)

        try:
            frame.wait_for_function(
                """(emailSel) => {
                    if (document.querySelector(emailSel)) return true;
                    const headings = Array.from(document.querySelectorAll("h1, h2, [role='heading']"));
                    return headings.some(h => /enter details|invitee|your info/i.test(h.textContent || ""));
                }""",
                arg=self.EMAIL_INPUT_SELECTOR,
                timeout=timeout,
            )
            logger.info("Invitee form appeared successfully")
            return True
        except PlaywrightTimeoutError as e:
            logger.warning(f"Invitee form did not appear within {timeout}ms")
            if raise_on_failure:
                # Log current page state for diagnostics
                try:
                    current_html = frame.content()
                    logger.error(f"Current frame HTML (first 500 chars): {current_html[:500]}")
                except Exception:
                    pass
                raise PlaywrightTimeoutError(f"Invitee form did not appear after {timeout}ms") from e
            return False

    def _wait_for_available_day(self, frame, timeout_ms: int | None = None) -> bool:
        """Wait until Calendly marks at least one day as available."""
        self.wait_for_loading_to_finish(timeout_ms)
        try:
            frame.wait_for_function(
                """() => Array.from(document.querySelectorAll("button[aria-label]"))
                    .some(btn => {
                        const label = (btn.getAttribute("aria-label") || "").toLowerCase();
                        return !btn.disabled && label.includes("available") && !label.includes("no times");
                    })""",
                timeout=timeout_ms or self.DEFAULT_EMBED_TIMEOUT_MS,
            )
            return True
        except PlaywrightTimeoutError:
            return False

    def _get_available_day_buttons(self, frame):
        """Return list of (button, label) for selectable days with open slots."""
        buttons = frame.query_selector_all("button[aria-label]")
        available = []
        for button in buttons:
            label = (button.get_attribute("aria-label") or "").lower()
            if button.is_disabled():
                continue
            if "available" in label and "no times" not in label:
                available.append((button, label))
        return available

    def _get_available_time_slots(self, frame):
        """Return list of (button, label) for selectable time slots on chosen day.
        
        Uses multiple selector strategies for robustness:
        1. Buttons with data-testid attributes (if present)
        2. Buttons with role='button' and time-like aria-label
        3. Generic buttons with time pattern in text content
        """
        available = []
        
        # Strategy 1: Try data-testid first (most specific)
        testid_buttons = frame.query_selector_all("button[data-testid*='time'], button[data-testid*='slot']")
        for button in testid_buttons:
            if button.is_disabled():
                continue
            text = (button.text_content() or button.get_attribute("aria-label") or "").strip()
            if text and self.TIME_SLOT_PATTERN.search(text):
                available.append((button, text))
        
        # If we found slots via testid, return them
        if available:
            logger.debug(f"Found {len(available)} time slots via data-testid")
            return available
        
        # Strategy 2: Buttons with known Calendly classes
        class_buttons = frame.query_selector_all("button.booking-kit_button_59b1e549, button[class*='booking-kit_button']")
        for button in class_buttons:
            if button.is_disabled():
                continue
            text = (button.text_content() or button.get_attribute("aria-label") or "").strip()
            if text and self.TIME_SLOT_PATTERN.search(text):
                available.append((button, text))

        if available:
            logger.debug(f"Found {len(available)} time slots via booking-kit classes")
            return available
        
        # Strategy 3: role=button with aria-label
        role_buttons = frame.query_selector_all("button[role='button'][aria-label]")
        for button in role_buttons:
            if button.is_disabled():
                continue
            aria_label = button.get_attribute("aria-label") or ""
            text_content = button.text_content() or ""
            text = (aria_label or text_content).strip()
            
            if text and self.TIME_SLOT_PATTERN.search(text):
                available.append((button, text))
        
        if available:
            logger.debug(f"Found {len(available)} time slots via role=button")
            return available
        
        # Strategy 4: Fallback to generic button selector
        buttons = frame.query_selector_all("button")
        for button in buttons:
            text = (button.text_content() or button.get_attribute("aria-label") or "").strip()
            if not text or button.is_disabled():
                continue
            if not self.TIME_SLOT_PATTERN.search(text):
                continue
            available.append((button, text))
        
        if available:
            logger.debug(f"Found {len(available)} time slots via generic button selector")
        else:
            logger.warning("No time slots found with any selector strategy")
        
        return available
