"""Orchestrate detection, image preparation, and generator inference."""

import time
from PIL import Image

from ..config import DISPLAY_SIZE
from ..models.inference import generate_photo, generate_sketch
from .image_detection import detect_image_type
from .image_cropping import crop_face_or_center, crop_sketch_square
from .image_processing import apply_sketch_cleanup, prepare_model_input, postprocess_output
from .image_io import pil_to_base64


def prepare_image(image, options):
    # Detection always precedes cropping and cleanup, including manual overrides.
    detection = detect_image_type(image)
    effective = detection["detected_type"] if options["mode"] == "auto" else options["mode"]
    face_found = None
    cleaned = effective == "sketch" and options["clean_sketch"]
    if effective == "photo":
        processed, face_found = crop_face_or_center(image, options["face_crop"])
    else:
        processed = crop_sketch_square(image)
        if cleaned:
            processed = apply_sketch_cleanup(processed)
    tensor, preview = prepare_model_input(processed)
    return tensor, {
        "detected_type": detection["detected_type"],
        "effective_input_type": effective,
        "direction": "photo->sketch" if effective == "photo" else "sketch->photo",
        "detection_confidence": detection["confidence"],
        "manual_override": options["mode"] != "auto",
        "face_found": face_found,
        "cleanup_applied": cleaned,
        "input_preview": pil_to_base64(preview.resize((DISPLAY_SIZE, DISPLAY_SIZE), Image.Resampling.LANCZOS)),
    }


def convert_image(image, options):
    tensor, metadata = prepare_image(image, options)
    started = time.perf_counter()
    if metadata["effective_input_type"] == "photo":
        output = generate_sketch(tensor)
        target = "sketch"
    else:
        output = generate_photo(tensor)
        target = "photo"
    elapsed = round((time.perf_counter() - started) * 1000)
    result = postprocess_output(output, target, options["grayscale_sketch"], options["enhance_contrast"])
    return dict(**metadata, output_image=pil_to_base64(result), inference_ms=elapsed)
