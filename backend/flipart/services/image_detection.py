"""
Sketch-vs-Photo Auto-Detection Module.

Real dataset sketches are grayscale with mostly white background and dark lines.
Real photos are colored faces with rich saturation and varied pixel distributions.
"""

import numpy as np

# Tunable detector thresholds
SATURATION_THRESHOLD = 0.05
WHITE_FRACTION_THRESHOLD = 0.50
WHITE_PIXEL_INTENSITY = 0.85

# Optional weights for linear boundary confidence calculation
W_SAT = 10.0
W_WHITE = 4.0


def extract_detector_features(image_rgb):
    """
    Compute features from an RGB image.
    image_rgb can be a float array in [0, 1] or uint8 in [0, 255].
    """
    arr = np.asarray(image_rgb, dtype=np.float32)
    if arr.max() > 1.0:
        arr = arr / 255.0

    # Ensure 3-channel RGB
    if arr.ndim == 2:
        arr = np.stack([arr, arr, arr], axis=-1)
    elif arr.ndim == 3 and arr.shape[-1] == 1:
        arr = np.concatenate([arr, arr, arr], axis=-1)
    elif arr.ndim == 3 and arr.shape[-1] == 4:
        arr = arr[:, :, :3]

    # Saturation heuristic: max(channel) - min(channel)
    channel_max = arr.max(axis=-1)
    channel_min = arr.min(axis=-1)
    saturation = float((channel_max - channel_min).mean())

    # White fraction: fraction of pixels whose average intensity exceeds threshold
    pixel_means = arr.mean(axis=-1)
    white_fraction = float((pixel_means > WHITE_PIXEL_INTENSITY).mean())

    return {
        "saturation": saturation,
        "white_fraction": white_fraction,
        "array_float": arr,
    }


def compute_confidence(saturation, white_fraction, is_sketch):
    """
    Compute an uncalibrated heuristic score in [0.5, 0.99] based on the margin
    from the decision boundary.
    """
    # Distance metric from boundary:
    # Sketch condition: saturation < SATURATION_THRESHOLD and white_fraction > WHITE_FRACTION_THRESHOLD
    sat_margin = (SATURATION_THRESHOLD - saturation) / max(SATURATION_THRESHOLD, 1e-4)
    white_margin = (white_fraction - WHITE_FRACTION_THRESHOLD) / max(1.0 - WHITE_FRACTION_THRESHOLD, 1e-4)

    if is_sketch:
        # Both margins are positive for a clear sketch
        combined = 0.5 * (sat_margin + white_margin)
        # Map combined margin to confidence in [0.5, 0.99]
        conf = 0.5 + 0.49 / (1.0 + np.exp(-3.0 * combined))
    else:
        # Distance into photo territory
        photo_sat_margin = (saturation - SATURATION_THRESHOLD) / 0.20
        photo_white_margin = (WHITE_FRACTION_THRESHOLD - white_fraction) / max(WHITE_FRACTION_THRESHOLD, 1e-4)
        combined = max(photo_sat_margin, photo_white_margin)
        conf = 0.5 + 0.49 / (1.0 + np.exp(-3.0 * combined))

    return round(float(np.clip(conf, 0.50, 0.99)), 4)


def detect_image_type(image_input):
    """
    Detect whether an input image is a sketch or a real face photo.

    Parameters:
        image_input: PIL Image or numpy array (RGB)

    Returns:
        dict with:
            "detected_type": "sketch" or "photo"
            "confidence": float in [0.5, 0.99]
            "saturation": float
            "white_fraction": float
    """
    features = extract_detector_features(image_input)
    sat = features["saturation"]
    white_frac = features["white_fraction"]

    is_sketch = (sat < SATURATION_THRESHOLD) and (white_frac > WHITE_FRACTION_THRESHOLD)
    detected_type = "sketch" if is_sketch else "photo"
    confidence = compute_confidence(sat, white_frac, is_sketch)

    return {
        "detected_type": detected_type,
        "confidence": confidence,
        "saturation": round(sat, 5),
        "white_fraction": round(white_frac, 5),
    }
