from abc import ABC, abstractmethod

from playwright.sync_api import Error, Locator, Page, TimeoutError as PlaywrightTimeoutError


class BasePage(ABC):
    """Base class for page objects.
    
    Provides common methods and timeout constants for all page objects.
    All page objects must implement the `url` property.
    """
    
    # Timeout constants (in milliseconds)
    DEFAULT_TIMEOUT = 5000
    LONG_TIMEOUT = 30000
    SHORT_TIMEOUT = 1000
    HOVER_STABILIZATION_DELAY = 150

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    @abstractmethod
    def url(self) -> str:
        """Return the full URL for this page. Must be implemented by subclasses."""
        pass

    def open(self, wait_until: str = "domcontentloaded") -> None:
        """Navigate to this page's URL.
        
        Args:
            wait_until: When to consider navigation succeeded. 
                       Options: 'load', 'domcontentloaded', 'networkidle'
        """
        self.page.goto(self.url, wait_until=wait_until)

    def locator(self, selector: str) -> Locator:
        """Create a locator for the given selector."""
        return self.page.locator(selector)

    def wait_for_visible(self, selector: str, *, timeout: int | None = None) -> Locator:
        """Wait for a selector to become visible and return the locator."""
        locator = self.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        return locator

    def click(self, selector: str, *, timeout: int | None = None) -> None:
        """Click an element."""
        self.locator(selector).click(timeout=timeout)

    def fill(self, selector: str, value: str, *, timeout: int | None = None) -> None:
        """Fill an input element."""
        self.locator(selector).fill(value, timeout=timeout)

    def get_attribute(self, selector: str, name: str, *, strict: bool = True) -> str | None:
        """Get attribute value of an element, returning None on error if not strict."""
        if strict:
            return self.locator(selector).get_attribute(name)
        try:
            return self.locator(selector).get_attribute(name)
        except (Error, PlaywrightTimeoutError):
            return None

    def take_screenshot(self, path: str, *, full_page: bool = False) -> None:
        """Take a screenshot of the current page.
        
        Args:
            path: Path where the screenshot will be saved
            full_page: If True, captures the entire scrollable page. 
                      If False, captures only the visible viewport.
        """
        self.page.screenshot(path=path, full_page=full_page)
