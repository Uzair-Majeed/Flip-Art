"""Shared paths and image limits, independent of the working directory."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEIGHTS_DIR = PROJECT_ROOT / "backend" / "weights"
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
IMAGE_SIZE = 128
DISPLAY_SIZE = 512
MAX_FILE_BYTES = 10 * 1024 * 1024
# A 10 MB camera image expands to roughly 13.4 MB in base64.
MAX_REQUEST_BYTES = 15 * 1024 * 1024
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
