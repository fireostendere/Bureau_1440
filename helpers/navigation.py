"""Navigation and HTTP redirect testing utilities."""

from playwright.sync_api import Browser


class HTTPRedirectTester:
    """Test HTTP to HTTPS redirects and navigation behavior.
    
    Provides utilities for testing security-related navigation patterns.
    """
    
    def __init__(self, browser: Browser):
        """Initialize tester with a Playwright browser.
        
        Args:
            browser: Playwright Browser instance
        """
        self.browser = browser
    
    def open_via_http_and_get_final_url(self, http_url: str) -> str:
        """Open a URL via HTTP in a fresh context and return the resulting URL.
        
        Useful for testing HTTP to HTTPS redirects.
        
        Args:
            http_url: HTTP URL to navigate to
            
        Returns:
            Final URL after navigation (may be HTTPS if redirected)
        """
        with self.browser.new_context() as context:
            page = context.new_page()
            page.goto(http_url, wait_until="domcontentloaded")
            final_url = page.url
        
        return final_url
