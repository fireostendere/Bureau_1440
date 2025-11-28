import logging
from pathlib import Path
from typing import Generator, Optional

import pytest
import allure
from playwright.sync_api import Browser, BrowserContext, Error, Page, Playwright, sync_playwright

from config import AppConfig
from helpers.files import ensure_dir, get_artifact_path, safe_filename
from helpers.media import finalize_video_artifact
from helpers.qa import attach_html_to_allure, attach_screenshot_to_allure
from pages.login_page import LoginPage
from pages.book_demo_page import BookDemoPage

from .options import ArtifactPreferences

logger = logging.getLogger(__name__)


def _trace_path(nodeid: str) -> Path:
    return get_artifact_path("traces") / f"{safe_filename(nodeid)}.zip"


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, request) -> Generator[Browser, None, None]:
    """Launch browser for the test session."""
    headless = not request.config.getoption("--headed")
    browser_instance: Optional[Browser] = None
    try:
        browser_instance = playwright_instance.chromium.launch(
            headless=headless,
            args=["--no-sandbox"],
        )
    except (Error, Exception) as exc:
        allure.attach(str(exc), name="Browser launch error", attachment_type=allure.attachment_type.TEXT)
        pytest.skip("Unable to launch Playwright browser")

    try:
        yield browser_instance
    finally:
        if browser_instance is not None:
            browser_instance.close()


@pytest.fixture()
def context(
    browser: Browser,
    request,
    artifact_preferences: ArtifactPreferences,
) -> Generator[BrowserContext, None, None]:
    """Create browser context with optional video recording and tracing enabled."""

    video_prefs = artifact_preferences.video
    trace_prefs = artifact_preferences.trace

    context_options: dict[str, object] = {}
    ensure_dir(get_artifact_path("traces"))

    if video_prefs.record:
        video_dir = ensure_dir(get_artifact_path("videos"))
        context_options["record_video_dir"] = str(video_dir)
        context_options["record_video_size"] = {"width": 1280, "height": 720}

    context: Optional[BrowserContext] = None
    tracing_started = False
    try:
        context = browser.new_context(**context_options)
        setattr(context, "record_video_enabled", video_prefs.record)
        setattr(context, "keep_video_on_pass", video_prefs.keep_on_pass)
        setattr(context, "trace_enabled", trace_prefs.enabled)
        setattr(context, "trace_retain_on_failure", trace_prefs.retain_on_failure)
        setattr(context, "last_failed", False)

        context.set_default_timeout(5000)
        context.set_default_navigation_timeout(5000)

        if trace_prefs.enabled:
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
            tracing_started = True

        yield context
    finally:
        if context is None:
            return

        trace_enabled = getattr(context, "trace_enabled", False)
        retain_on_failure = getattr(context, "trace_retain_on_failure", False)
        failed_any = getattr(context, "last_failed", False)

        if trace_enabled and tracing_started:
            try:
                if retain_on_failure and not failed_any:
                    context.tracing.stop()
                else:
                    trace_path = _trace_path(request.node.nodeid)
                    context.tracing.stop(path=str(trace_path))
            except Exception as exc:
                logger.warning("Failed to stop tracing for %s: %s", request.node.nodeid, exc)

        try:
            context.close()
        except Exception as exc:
            logger.warning("Failed to close context for %s: %s", request.node.nodeid, exc)


@pytest.fixture()
def page(context: BrowserContext, request) -> Generator[Page, None, None]:
    """Create a page for each test."""
    page = context.new_page()
    yield page

    rep_setup = getattr(request.node, "rep_setup", None)
    rep_call = getattr(request.node, "rep_call", None)
    rep_teardown = getattr(request.node, "rep_teardown", None)

    def _is_failed(rep) -> bool:
        return getattr(rep, "failed", False)

    def _is_skipped(rep) -> bool:
        return getattr(rep, "skipped", False) or getattr(rep, "outcome", "") == "skipped"

    failed_any = any(_is_failed(rep) for rep in (rep_setup, rep_call, rep_teardown) if rep is not None)
    skipped_any = any(_is_skipped(rep) for rep in (rep_setup, rep_call, rep_teardown) if rep is not None)
    capture_needed = failed_any or skipped_any

    if capture_needed:
        try:
            screenshots_dir = ensure_dir(get_artifact_path("screenshots"))
            screenshot_path = screenshots_dir / f"{safe_filename(request.node.nodeid)}.png"
            screenshot = page.screenshot(path=str(screenshot_path), full_page=True)
            attach_screenshot_to_allure(screenshot, name=f"screenshot-{request.node.name}")
        except Exception as exc:
            logger.error("Failed to capture screenshot: %s", exc)

        try:
            html = page.content()
            attach_html_to_allure(html, name=f"dom-{request.node.name}.html")
        except Exception as exc:
            logger.error("Failed to capture HTML: %s", exc)

    try:
        video_obj = getattr(page, "video", None)
    except Exception:
        video_obj = None

    try:
        page.close()
    except Exception as exc:
        logger.warning("Error closing page: %s", exc)

    setattr(context, "last_failed", failed_any)

    record_video_enabled = getattr(context, "record_video_enabled", False)
    keep_on_pass = getattr(context, "keep_video_on_pass", False)

    if record_video_enabled:
        keep_video = failed_any or skipped_any or keep_on_pass
        attach_video = failed_any or skipped_any
        finalize_video_artifact(video_obj, request.node.nodeid, keep=keep_video, attach_on_keep=attach_video)
    elif video_obj:
        finalize_video_artifact(video_obj, request.node.nodeid, keep=False, attach_on_keep=False)


@pytest.fixture()
def login_page(page: Page, app_config: AppConfig) -> Generator[LoginPage, None, None]:
    """Create LoginPage instance."""
    yield LoginPage(page, app_config)


@pytest.fixture()
def opened_login_page(login_page: LoginPage) -> LoginPage:
    """Open login page and return the instance."""
    login_page.open()
    return login_page

@pytest.fixture()
def book_demo_page(page: Page, app_config: AppConfig) -> Generator[BookDemoPage, None, None]:
    """Create BookDemoPage instance."""
    yield BookDemoPage(page, app_config)


@pytest.fixture()
def opened_book_demo_page(book_demo_page: BookDemoPage) -> BookDemoPage:
    """Open book-a-demo page and return the instance."""
    book_demo_page.open()
    return book_demo_page


@pytest.fixture()
def authenticated_login_page(
    opened_login_page: LoginPage,
    admin_credentials: dict[str, str],
) -> Generator[LoginPage, None, None]:
    """Login with admin credentials and logout after test."""
    opened_login_page.attempt_login(admin_credentials["username"], admin_credentials["password"])
    yield opened_login_page


@pytest.fixture()
def authenticated_storage_state(
    browser: Browser,
    admin_credentials: dict[str, str],
    app_config: AppConfig,
) -> Generator[dict, None, None]:
    """Create and return storage state with authenticated session."""
    context = browser.new_context()
    page = context.new_page()
    login_page = LoginPage(page, app_config)

    login_page.open()
    login_page.attempt_login(admin_credentials["username"], admin_credentials["password"])

    storage = context.storage_state()
    context.close()

    yield storage
