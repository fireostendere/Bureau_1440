"""Network monitoring utilities for Page Objects."""

from typing import Callable

from playwright.sync_api import Page


class LoginRequestMonitor:
    """Monitor network requests for login page.
    
    Provides utilities for tracking and intercepting login POST requests.
    Separates network monitoring concerns from Page Object responsibilities.
    """
    
    def __init__(self, page: Page):
        """Initialize monitor with a Playwright page.
        
        Args:
            page: Playwright Page instance to monitor
        """
        self.page = page
        self._handler: Callable | None = None
        self._listener_registered = False
    
    def on_login_request(self, handler: Callable) -> None:
        """Register a callback that fires for login POST requests.
        
        Args:
            handler: Callback function to handle login requests
        """
        if not self._listener_registered:
            self.page.on("request", self._handle_request)
            self._listener_registered = True
        
        self._handler = handler
    
    def collect_requests(self, storage: list[str]) -> None:
        """Collect login POST request URLs into the provided storage list.
        
        Args:
            storage: List to store request URLs
        """
        def store_url(request):
            storage.append(request.url)
        
        self.on_login_request(store_url)
    
    def _handle_request(self, request) -> None:
        """Internal dispatcher for login request listeners.
        
        Args:
            request: Playwright Request object
        """
        is_login_post = request.method == "POST" and "/admin/login" in request.url
        
        if is_login_post and self._handler:
            self._handler(request)
