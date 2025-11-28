"""QA-oriented helper utilities."""

import allure


def attach_screenshot_to_allure(screenshot_bytes: bytes, name: str) -> None:
    """Attach screenshot bytes to Allure report."""
    allure.attach(screenshot_bytes, name=name, attachment_type=allure.attachment_type.PNG)


def attach_html_to_allure(html: str, name: str) -> None:
    """Attach HTML content to Allure report."""
    allure.attach(html, name=name, attachment_type=allure.attachment_type.HTML)


def has_x_frame_options_protection(headers: dict) -> bool:
    """Check if X-Frame-Options header protects against clickjacking."""
    frame_options = headers.get("x-frame-options", "").upper()
    is_protected = frame_options in {"DENY", "SAMEORIGIN"}
    return is_protected


def is_element_centered(position: float, size: float, viewport_size: float, tolerance: float) -> bool:
    """Check if element center aligns with viewport center within tolerance for a single dimension."""
    element_center = position + size / 2
    viewport_center = viewport_size / 2
    center_delta = abs(element_center - viewport_center)
    is_centered = center_delta < viewport_size * tolerance
    return is_centered


def is_form_centered_in_viewport(page, form_selector: str = "form") -> tuple[bool, bool]:
    """Check if a form is centered horizontally and vertically on the page.
    
    Args:
        page: Playwright Page object
        form_selector: CSS selector for the form element
        
    Returns:
        Tuple of (is_horizontally_centered, is_vertically_centered)
    """
    # Centering tolerance constants
    HORIZONTAL_CENTERING_TOLERANCE = 0.15
    VERTICAL_CENTERING_TOLERANCE = 0.25
    
    form_locator = page.locator(form_selector)
    bbox = form_locator.bounding_box()
    viewport = page.viewport_size
    
    horizontal_centered = is_element_centered(
        bbox["x"],
        bbox["width"],
        viewport["width"],
        HORIZONTAL_CENTERING_TOLERANCE
    )
    
    vertical_centered = is_element_centered(
        bbox["y"],
        bbox["height"],
        viewport["height"],
        VERTICAL_CENTERING_TOLERANCE
    )
    
    return (horizontal_centered, vertical_centered)

