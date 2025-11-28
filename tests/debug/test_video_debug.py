"""Temporary test to exercise video recording plumbing."""

import allure
import pytest


@allure.suite("Debug")
@allure.feature("Video Recording")
@pytest.mark.xfail(reason="Intentional failure to exercise video recording plumbing", raises=AssertionError)
def test_intentional_failure_for_video_debug(login_page):
    """This test intentionally fails to trigger video recording."""
    login_page.open()
    assert False, "\U0001f3a5 Intentional failure to test video recording and cleanup"
