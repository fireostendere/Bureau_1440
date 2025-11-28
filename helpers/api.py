"""API and network request helpers for testing."""


def capture_request_url(request_urls: list[str], request):
    """Capture request URL."""
    request_urls.append(request.url)
