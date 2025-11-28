"""Media processing helpers: screenshots, diffs, video artifacts."""

from pathlib import Path
from typing import Any, Optional

import allure
from PIL import Image, ImageChops, ImageStat

from .files import ensure_dir, get_artifact_path, safe_filename


def finalize_video_artifact(
    video: Any,
    nodeid: str,
    *,
    keep: bool,
    attach_on_keep: bool,
) -> Optional[Path]:
    """Persist or delete a Playwright video artifact in a consistent way."""
    if video is None:
        return None

    if keep:
        video_path = get_artifact_path("videos") / f"{safe_filename(nodeid)}.webm"
        ensure_dir(video_path.parent)
        video.save_as(str(video_path))

        if attach_on_keep:
            allure.attach.file(
                str(video_path),
                name="video",
                attachment_type=allure.attachment_type.WEBM,
            )

        video.delete()
        return video_path

    video.delete()
    return None


def calculate_screenshot_difference(current_path: Path, baseline_path: Path) -> float:
    """Calculate RMS difference score between two screenshots."""
    baseline_img = Image.open(baseline_path).convert("RGB")
    current_img = Image.open(current_path).convert("RGB")

    if baseline_img.size != current_img.size:
        baseline_img.close()
        current_img.close()
        raise ValueError(f"Image dimensions mismatch: {baseline_img.size} vs {current_img.size}")

    diff = ImageChops.difference(baseline_img, current_img)
    diff_score = max(ImageStat.Stat(diff).rms)

    baseline_img.close()
    current_img.close()

    return diff_score


def are_screenshots_matching(current_path: Path, baseline_path: Path, tolerance: float) -> bool:
    """Check if two screenshots match within tolerance."""
    diff_score = calculate_screenshot_difference(current_path, baseline_path)
    matches = diff_score <= tolerance
    return matches


def save_screenshot_diff(current_path: Path, baseline_path: Path) -> Path:
    """Generate and save difference image between screenshots."""
    baseline_img = Image.open(baseline_path).convert("RGB")
    current_img = Image.open(current_path).convert("RGB")

    diff = ImageChops.difference(baseline_img, current_img)
    diff_path = current_path.parent / f"{current_path.stem}-diff{current_path.suffix}"
    diff.save(diff_path)

    baseline_img.close()
    current_img.close()

    return diff_path


def attach_screenshot_diff_if_needed(
    current_path: Path,
    baseline_path: Path,
    diff_score: float,
    tolerance: float,
) -> None:
    """Generate and attach screenshot diff to Allure if score exceeds tolerance."""
    if diff_score <= tolerance:
        return

    diff_path = save_screenshot_diff(current_path, baseline_path)
    allure.attach.file(str(diff_path), name="diff", attachment_type=allure.attachment_type.PNG)


def take_screenshot_with_allure(page, screenshot_dir: Path, filename: str) -> Path:
    """Take full page screenshot and attach to Allure report."""
    screenshot_path = screenshot_dir / filename
    page.screenshot(path=str(screenshot_path), full_page=True)
    allure.attach.file(str(screenshot_path), name="current", attachment_type=allure.attachment_type.PNG)
    return screenshot_path
