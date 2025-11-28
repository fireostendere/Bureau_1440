import os
from dataclasses import dataclass
from typing import Optional

import pytest

TRUTHY_VALUES = {"1", "true", "yes", "on", "enabled"}
FALSY_VALUES = {"0", "false", "no", "off", "disabled"}
VIDEO_KEEP_VALUES = {"all", "always", "keep"}
TRACE_MODES = {"off", "on", "retain-on-failure"}


@dataclass(frozen=True)
class VideoPreferences:
    record: bool
    keep_on_pass: bool


@dataclass(frozen=True)
class TracePreferences:
    enabled: bool
    retain_on_failure: bool


@dataclass(frozen=True)
class ArtifactPreferences:
    video: VideoPreferences
    trace: TracePreferences


def _parse_bool(value: str | None) -> Optional[bool]:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in TRUTHY_VALUES:
        return True
    if normalized in FALSY_VALUES:
        return False
    return None


def _resolve_video_preferences(pytestconfig) -> VideoPreferences:
    record = bool(pytestconfig.getoption("--video"))
    keep_on_pass = bool(pytestconfig.getoption("--keep-video-on-pass"))

    env_video = os.getenv("PLAYWRIGHT_VIDEO")
    if env_video:
        normalized = env_video.strip().lower()
        parsed = _parse_bool(normalized)
        if parsed is not None:
            record = parsed
        elif normalized in VIDEO_KEEP_VALUES:
            record = True
            keep_on_pass = True
        else:
            record = True

    env_keep = os.getenv("PLAYWRIGHT_KEEP_VIDEO_ON_PASS")
    keep_override = _parse_bool(env_keep)
    if keep_override is not None:
        keep_on_pass = keep_override

    return VideoPreferences(record=record, keep_on_pass=keep_on_pass)


def _resolve_trace_preferences(pytestconfig) -> TracePreferences:
    mode = pytestconfig.getoption("--pw-trace")
    env_trace = os.getenv("PLAYWRIGHT_TRACE")
    if env_trace:
        normalized = env_trace.strip().lower()
        if normalized in TRACE_MODES:
            mode = normalized
        else:
            parsed = _parse_bool(normalized)
            if parsed:
                mode = "retain-on-failure" if normalized in VIDEO_KEEP_VALUES else "on"

    enabled = mode != "off"
    retain_on_failure = mode == "retain-on-failure"
    return TracePreferences(enabled=enabled, retain_on_failure=retain_on_failure)


def pytest_addoption(parser):
    """Register CLI options for Playwright test runs."""
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run browser in headed mode (with GUI)",
    )
    parser.addoption(
        "--base-url",
        action="store",
        default="app.mera.fit",
        help="Base URL for the application under test",
    )
    parser.addoption(
        "--video",
        action="store_true",
        default=False,
        help="Enable video recording for tests",
    )
    parser.addoption(
        "--keep-video-on-pass",
        action="store_true",
        default=False,
        help="Keep recorded videos even when tests pass",
    )
    parser.addoption(
        "--pw-trace",
        action="store",
        choices=sorted(TRACE_MODES),
        default="off",
        help="Control Playwright tracing (off | on | retain-on-failure)",
    )


@pytest.fixture(scope="session")
def artifact_preferences(pytestconfig) -> ArtifactPreferences:
    """Session-wide media/tracing preferences derived from CLI/ENV."""
    video = _resolve_video_preferences(pytestconfig)
    trace = _resolve_trace_preferences(pytestconfig)
    return ArtifactPreferences(video=video, trace=trace)
