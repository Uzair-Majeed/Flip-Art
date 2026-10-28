"""Validate multipart and JSON conversion requests."""

from flask import request
from werkzeug.exceptions import RequestEntityTooLarge

from ..config import MAX_FILE_BYTES
from ..services.image_io import decode_image_bytes, decode_base64_data_url


def read_image_request():
    """Decode one upload/capture and validate shared preview/conversion options."""
    options = request.get_json(silent=True) if request.is_json else request.form
    if options is None:
        options = {}
    if not hasattr(options, "get"):
        raise ValueError("JSON body must be an object.")
    if "image" in request.files:
        upload = request.files["image"]
        if not upload.filename:
            raise ValueError("Choose an image file.")
        raw = upload.read(MAX_FILE_BYTES + 1)
    elif options.get("image"):
        raw = decode_base64_data_url(options["image"])
    else:
        raise ValueError("No image provided. Upload an image or capture a camera frame.")
    if len(raw) > MAX_FILE_BYTES:
        raise RequestEntityTooLarge()
    if not raw:
        raise ValueError("The image is empty.")
    image = decode_image_bytes(raw)
    mode = options.get("mode", "auto")
    if mode not in ("auto", "photo", "sketch"):
        raise ValueError("Mode must be auto, photo, or sketch.")
    parsed = {"mode": mode}
    for name, default in (("face_crop", True), ("grayscale_sketch", True),
                          ("enhance_contrast", False), ("clean_sketch", False)):
        value = options.get(name, default)
        if isinstance(value, bool):
            parsed[name] = value
        elif str(value).lower() in ("true", "1", "yes", "on", "false", "0", "no", "off"):
            parsed[name] = str(value).lower() in ("true", "1", "yes", "on")
        else:
            raise ValueError(f"{name} must be a boolean.")
    return image, parsed
