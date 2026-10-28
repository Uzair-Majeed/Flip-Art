"""Decode uploads safely and encode PNG data URLs."""

import base64
import io
from PIL import Image, ImageOps

from ..config import ALLOWED_EXTENSIONS, MAX_FILE_BYTES


def decode_image_bytes(image_bytes):
    """
    Safely load an image from bytes into a PIL RGB Image.
    Applies EXIF transpose and converts RGBA/palette/grayscale to 3-channel RGB.
    """
    if len(image_bytes) > MAX_FILE_BYTES:
        raise ValueError(f"File size exceeds 10 MB limit ({len(image_bytes)} bytes).")

    try:
        pil_img = Image.open(io.BytesIO(image_bytes))
        # Force decoding here so truncated files receive the same 400 response.
        pil_img.load()
    except Exception as e:
        raise ValueError("Invalid or corrupted image file.") from e

    # Check format if available
    img_format = (pil_img.format or "").lower()
    if img_format and f".{img_format}" not in ALLOWED_EXTENSIONS and img_format not in {"jpeg", "png", "bmp", "webp"}:
        raise ValueError(f"Unsupported image format: {img_format}. Allowed: PNG, JPG, JPEG, BMP, WEBP.")

    # Normalize EXIF orientation
    pil_img = ImageOps.exif_transpose(pil_img)

    # Convert to RGB mode (replicates grayscale to 3 channels, strips alpha properly)
    if pil_img.mode != "RGB":
        if pil_img.mode in ("RGBA", "LA") or "transparency" in pil_img.info:
            pil_img = pil_img.convert("RGBA")
            # Blend onto white background for transparent images
            bg = Image.new("RGB", pil_img.size, (255, 255, 255))
            alpha = pil_img.split()[-1]
            bg.paste(pil_img, mask=alpha)
            pil_img = bg
        else:
            pil_img = pil_img.convert("RGB")

    # Downscale very large images to prevent excessive latency (e.g. max dimension 1600)
    w, h = pil_img.size
    max_dim = max(w, h)
    if max_dim > 1600:
        scale = 1600 / max_dim
        new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
        pil_img = pil_img.resize((new_w, new_h), Image.Resampling.BILINEAR)

    return pil_img


def decode_base64_data_url(data_url):
    """Decode a data URL (e.g. data:image/png;base64,...) or raw base64 string to bytes."""
    if not isinstance(data_url, str):
        raise ValueError("Image data must be a string.")
    if "," in data_url:
        _, encoded = data_url.split(",", 1)
    else:
        encoded = data_url
    try:
        return base64.b64decode(encoded, validate=True)
    except Exception as e:
        raise ValueError("Invalid base64 encoding.") from e


def pil_to_base64(pil_img, format="PNG"):
    """Convert a PIL Image to a base64 data URL string."""
    buf = io.BytesIO()
    pil_img.save(buf, format=format)
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    mime = "image/png" if format.upper() == "PNG" else "image/jpeg"
    return f"data:{mime};base64,{encoded}"
