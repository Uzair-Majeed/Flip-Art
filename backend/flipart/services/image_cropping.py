"""Face detection, face crops, and center-square sketch crops."""

import cv2
import numpy as np
from PIL import Image

_FACE_CASCADE = None


def get_face_cascade():
    global _FACE_CASCADE
    if _FACE_CASCADE is None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _FACE_CASCADE = cv2.CascadeClassifier(cascade_path)
    return _FACE_CASCADE


def crop_face_or_center(pil_img, enable_face_crop=True):
    """
    Detect the largest face using OpenCV Haar cascade.
    Expand the bounding box to ~1.8x the face size, pad if outside image bounds,
    and crop to a square.
    If no face is found, performs a center square crop. If disabled, keeps the whole image.

    Returns:
        cropped_pil: square cropped PIL Image
        face_found: bool (True if face detected, False if center crop fallback, None if disabled)
    """
    w, h = pil_img.size

    if not enable_face_crop:
        return pil_img, None

    # OpenCV detection expects BGR numpy array
    img_np = np.array(pil_img)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    cascade = get_face_cascade()
    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )

    if len(faces) == 0:
        # Fall back to center crop
        crop_size = min(w, h)
        left = (w - crop_size) // 2
        top = (h - crop_size) // 2
        cropped = pil_img.crop((left, top, left + crop_size, top + crop_size))
        return cropped, False

    # Choose largest face by area
    largest_face = max(faces, key=lambda f: f[2] * f[3])
    fx, fy, fw, fh = largest_face

    # Expand box to square ~1.8x face size centered on face center
    center_x = fx + fw / 2.0
    center_y = fy + fh / 2.0
    box_size = int(max(fw, fh) * 1.8)

    # Calculate crop coordinates
    x1 = int(round(center_x - box_size / 2.0))
    y1 = int(round(center_y - box_size / 2.0))
    x2 = x1 + box_size
    y2 = y1 + box_size

    # Handle padding if box extends beyond image bounds
    pad_left = max(0, -x1)
    pad_top = max(0, -y1)
    pad_right = max(0, x2 - w)
    pad_bottom = max(0, y2 - h)

    if pad_left > 0 or pad_top > 0 or pad_right > 0 or pad_bottom > 0:
        # Replicate border edge pixels to preserve natural lighting at boundary
        padded_np = cv2.copyMakeBorder(
            img_np, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_REFLECT_101
        )
        # Shift coordinates into padded image space
        x1 += pad_left
        y1 += pad_top
        x2 += pad_left
        y2 += pad_top
        face_crop_np = padded_np[y1:y2, x1:x2]
        face_crop_pil = Image.fromarray(face_crop_np)
    else:
        face_crop_pil = pil_img.crop((x1, y1, x2, y2))

    return face_crop_pil, True


def crop_sketch_square(pil_img):
    """
    For sketches: skip face detection. Center-crop to square.
    If nearly square, pad with white border if needed, else center crop.
    """
    w, h = pil_img.size
    crop_size = min(w, h)
    left = (w - crop_size) // 2
    top = (h - crop_size) // 2
    return pil_img.crop((left, top, left + crop_size, top + crop_size))
