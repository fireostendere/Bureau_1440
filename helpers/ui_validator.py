"""UI validation utilities for testing visual aspects of pages."""

from playwright.sync_api import Page


class LoginPageUIValidator:
    """Validate UI aspects of the login page.
    
    Provides methods for testing visual elements, hover states, and colors.
    Separates UI testing concerns from Page Object responsibilities.
    """
    
    _SUBMIT_SELECTOR = "[type='submit']"
    HOVER_STABILIZATION_DELAY = 150
    
    def __init__(self, page: Page):
        """Initialize validator with a Playwright page.
        
        Args:
            page: Playwright Page instance to validate
        """
        self.page = page
    
    def hover_submit_button(self) -> None:
        """Hover over the submit button and wait for stabilization."""
        button = self.page.locator(self._SUBMIT_SELECTOR)
        button.hover()
        self.page.wait_for_timeout(self.HOVER_STABILIZATION_DELAY)
    
    def get_submit_button_color(self) -> str:
        """Get current background color of the submit button.
        
        Returns:
            CSS color value as string
        """
        button = self.page.locator(self._SUBMIT_SELECTOR)
        return button.evaluate("el => window.getComputedStyle(el).backgroundColor")
    
    def get_button_hover_colors(self) -> tuple[str, str]:
        """Get submit button colors before and after hover.
        
        Returns:
            Tuple of (initial_color, hovered_color)
        """
        initial_color = self.get_submit_button_color()
        self.hover_submit_button()
        hovered_color = self.get_submit_button_color()
        return (initial_color, hovered_color)
