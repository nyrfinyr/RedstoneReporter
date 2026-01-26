"""Service layer for screenshot storage (FR-B5, NFR-03)."""

from fastapi import UploadFile
from pathlib import Path
import aiofiles
import time
import re
from typing import Optional

from app.config import settings


def slugify(text: str) -> str:
    """Convert text to a safe filename.

    Args:
        text: Input text to convert.

    Returns:
        str: Safe filename without special characters.
    """
    # Remove special characters and replace spaces with underscores
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s]+', '_', text)
    return text.lower()


async def save_screenshot(
    run_id: int,
    case_name: str,
    file: UploadFile
) -> str:
    """Save uploaded screenshot asynchronously (NFR-03).

    Screenshots are saved to filesystem (not database) in a structured
    directory: data/screenshots/{run_id}/{case_name}_{timestamp}.{ext}

    Args:
        run_id: ID of the test run.
        case_name: Name of the test case (used for filename).
        file: Uploaded file from FastAPI.

    Returns:
        str: Relative path to screenshot (for storage in database).

    Example:
        path = await save_screenshot(1, "Login Test", screenshot_file)
        # Returns: "1/login_test_1706280123.png"
    """
    # Create run-specific directory
    run_dir = settings.SCREENSHOT_DIR / str(run_id)
    run_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    timestamp = int(time.time())
    ext = Path(file.filename).suffix if file.filename else ".png"
    safe_name = slugify(case_name)
    filename = f"{safe_name}_{timestamp}{ext}"

    # Full path for saving
    file_path = run_dir / filename

    # Save file asynchronously (NFR-03: don't block main thread)
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    # Return relative path for database storage
    return f"{run_id}/{filename}"


def get_screenshot_full_path(relative_path: str) -> Optional[Path]:
    """Convert relative screenshot path to full filesystem path.

    Args:
        relative_path: Relative path stored in database (e.g., "1/screenshot.png").

    Returns:
        Optional[Path]: Full path to screenshot file, or None if not exists.
    """
    if not relative_path:
        return None

    full_path = settings.SCREENSHOT_DIR / relative_path

    if full_path.exists():
        return full_path

    return None


def delete_screenshot(relative_path: str) -> bool:
    """Delete a screenshot file.

    Args:
        relative_path: Relative path to screenshot.

    Returns:
        bool: True if deleted successfully, False otherwise.
    """
    full_path = get_screenshot_full_path(relative_path)

    if full_path and full_path.exists():
        try:
            full_path.unlink()
            return True
        except Exception:
            return False

    return False
