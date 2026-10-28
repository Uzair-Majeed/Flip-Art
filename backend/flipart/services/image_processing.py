"""Sketch cleanup, exact training normalization, and output rendering."""

import cv2
import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps

from ..config import DISPLAY_SIZE, IMAGE_SIZE


def apply_sketch_cleanup(pil_img):
    """
    Optional sketch cleanup.
    Gentle noise reduction and conservative contrast correction for scanned/rough sketches.
    Preserves pencil shading and facial contours; avoids harsh binarization or thickening.
    """
    arr = np.array(pil_img)
    # Convert to grayscale for subtle noise filtering
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

    # 1. Gentle bilateral filter preserves crisp sketch edges while smoothing paper grain
    denoised_gray = cv2.bilateralFilter(gray, d=5, sigmaColor=25, sigmaSpace=25)

    # 2. Conservative background whitening: gently push near-white pixels (e.g. >235) to 255
    # without blowing out light pencil shading
    # Linear stretch between p5 and p98
    p_low = np.percentile(denoised_gray, 2)
    p_high = np.percentile(denoised_gray, 98)
    if p_high > p_low + 10:
        stretched = np.clip((denoised_gray - p_low) / (p_high - p_low) * 255.0, 0, 255).astype(np.uint8)
    else:
        stretched = denoised_gray

    # Subtle blend with original to keep natural hand-drawn feel (70% cleaned, 30% original)
    blended = cv2.addWeighted(stretched, 0.75, gray, 0.25, 0)

    # Replicate back to 3-channel RGB
    cleaned_rgb = cv2.cvtColor(blended, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(cleaned_rgb)


def prepare_model_input(pil_img):
    """
    Resize image to 128x128 with bilinear antialiasing and normalize to [-1, 1].
    Ensures input is strictly 3-channel RGB.
    Returns:
        tensor: TensorFlow tensor of shape (1, 128, 128, 3), float32 in [-1.0, 1.0]
        preview_pil: 128x128 PIL image
    """
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")

    # Preserve floating point resize values, exactly as in the training notebook.
    resized = tf.image.resize(
        np.asarray(pil_img, dtype=np.float32),
        [IMAGE_SIZE, IMAGE_SIZE], method="bilinear", antialias=True,
    )
    tensor = ((resized / 127.5) - 1.0)[None, ...]
    preview = Image.fromarray(np.round(np.clip(resized.numpy(), 0, 255)).astype(np.uint8))
    return tensor, preview


def postprocess_output(output_tensor, target_type="sketch", grayscale_sketch=True, enhance_contrast=False):
    """
    Convert model output tensor in [-1, 1] to a uint8 PIL Image and apply postprocessing.

    Parameters:
        output_tensor: shape (1, 128, 128, 3) or (128, 128, 3) with values in [-1, 1]
        target_type: "sketch" (output of G) or "photo" (output of F)
        grayscale_sketch: bool, convert sketch to pure grayscale replicated to 3 channels
        enhance_contrast: bool, apply autocontrast to sketch output

    Returns:
        upscaled_pil: 512x512 PIL Image for crisp UI display
    """
    arr = np.squeeze(output_tensor)  # (128, 128, 3)
    # Exact postprocessing formula: uint8 = round(clip((y + 1) * 127.5, 0, 255))
    arr_clipped = np.clip((arr + 1.0) * 127.5, 0, 255)
    uint8_arr = np.round(arr_clipped).astype(np.uint8)

    img = Image.fromarray(uint8_arr, mode="RGB")

    # Only postprocess generated sketches
    if target_type == "sketch":
        if grayscale_sketch or enhance_contrast:
            # Convert to luminance grayscale and replicate to 3 channels to eliminate tint
            gray = img.convert("L")
            if enhance_contrast:
                gray = ImageOps.autocontrast(gray, cutoff=1)
            img = Image.merge("RGB", (gray, gray, gray))

    # Upscale with Lanczos for display
    upscaled = img.resize((DISPLAY_SIZE, DISPLAY_SIZE), Image.Resampling.LANCZOS)
    return upscaled
