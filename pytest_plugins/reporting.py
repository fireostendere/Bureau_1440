import time
from typing import Any, Dict, List

import pytest


def _safe_print(text: str, fallback: str | None = None) -> None:
    """Print text, falling back to ASCII-only output if required."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(fallback if fallback is not None else text.encode("ascii", "ignore").decode("ascii"))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    start = time.perf_counter()
    outcome = yield
    total = time.perf_counter() - start

    durations: List[Dict[str, Any]] | None = getattr(item.config, "_test_runtimes", None)
    if durations is None:
        durations = []
        item.config._test_runtimes = durations

    rep_call = getattr(item, "rep_call", None)
    rep_setup = getattr(item, "rep_setup", None)
    rep_teardown = getattr(item, "rep_teardown", None)

    if rep_call is not None:
        outcome_label = rep_call.outcome
    elif rep_setup is not None and rep_setup.failed:
        outcome_label = "failed"
    else:
        outcome_label = "skipped"

    durations.append(
        {
            "name": item.name,
            "nodeid": item.nodeid,
            "duration": total,
            "outcome": outcome_label,
        }
    )


def pytest_sessionfinish(session, exitstatus):
    """Print test execution statistics after all tests complete."""
    durations: List[Dict[str, Any]] | None = getattr(session.config, "_test_runtimes", None)
    if not durations:
        return

    _safe_print("\n" + "=" * 80)
    _safe_print("📊 Test Execution Summary", "Test Execution Summary")
    _safe_print("=" * 80)

    sorted_tests = sorted(durations, key=lambda x: x["duration"], reverse=True)

    for test in sorted_tests:
        if test["outcome"] == "passed":
            status_icon, fallback_icon = "✅", "[PASS]"
        elif test["outcome"] == "failed":
            status_icon, fallback_icon = "❌", "[FAIL]"
        else:
            status_icon, fallback_icon = "⏭️", "[SKIP]"
        line = f"{status_icon} {test['name']:<60} {test['duration']:.2f}s"
        fallback_line = f"{fallback_icon} {test['name']:<60} {test['duration']:.2f}s"
        _safe_print(line, fallback_line)

    total_duration = sum(t["duration"] for t in durations)
    passed = sum(1 for t in durations if t["outcome"] == "passed")
    failed = sum(1 for t in durations if t["outcome"] == "failed")

    _safe_print("=" * 80)
    summary = f"Total tests: {len(durations)} | Passed: {passed} | Failed: {failed} | Total time: {total_duration:.2f}s"
    _safe_print(summary)
    _safe_print("=" * 80 + "\n")
