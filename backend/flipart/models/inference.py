"""Cached generator loading, startup validation, and locked inference."""

import os
import threading
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import numpy as np
import tensorflow as tf

from ..config import IMAGE_SIZE, WEIGHTS_DIR
from .generator import build_generator, NUM_RESIDUAL_BLOCKS
from .layers import InstanceNormalization, ReflectionPadding2D

inference_lock = threading.Lock()
_G_photo2sketch = None
_F_sketch2photo = None


def run_self_check(generator, name="generator"):
    """Verify generator output shape and value range on dummy input."""
    dummy_input = tf.random.uniform((1, IMAGE_SIZE, IMAGE_SIZE, 3), minval=-1.0, maxval=1.0, dtype=tf.float32)
    output = generator(dummy_input, training=False)
    if output.shape != (1, IMAGE_SIZE, IMAGE_SIZE, 3):
        raise RuntimeError(
            f"Self-check failed for {name}: expected shape (1, 128, 128, 3), got {output.shape}"
        )
    min_val = float(tf.reduce_min(output).numpy())
    max_val = float(tf.reduce_max(output).numpy())
    if not np.isfinite(output.numpy()).all() or min_val < -1.0 or max_val > 1.0:
        raise RuntimeError(
            f"Self-check failed for {name}: outputs must be in [-1, 1], got [{min_val}, {max_val}]"
        )
    return True


def load_models(weights_dir=None):
    """
    Build and load CycleGAN generators G (photo->sketch) and F (sketch->photo).
    Tries .weights.h5 first; falls back to .keras full model files if needed.
    Runs self-check and caches instances.
    """
    global _G_photo2sketch, _F_sketch2photo

    if _G_photo2sketch is not None and _F_sketch2photo is not None:
        return _G_photo2sketch, _F_sketch2photo

    if weights_dir is None:
        weights_dir = WEIGHTS_DIR
    else:
        weights_dir = Path(weights_dir)

    g_weights = weights_dir / "G_photo2sketch.weights.h5"
    f_weights = weights_dir / "F_sketch2photo.weights.h5"
    g_keras = weights_dir / "G_photo2sketch.keras"
    f_keras = weights_dir / "F_sketch2photo.keras"

    g_loaded = False
    f_loaded = False

    # Attempt 1: build architecture and load .weights.h5
    if g_weights.exists() and f_weights.exists():
        try:
            print(f"Building architectures and loading weights from {weights_dir}...")
            G = build_generator("photo_to_sketch", NUM_RESIDUAL_BLOCKS)
            G.load_weights(str(g_weights))
            g_loaded = True

            F = build_generator("sketch_to_photo", NUM_RESIDUAL_BLOCKS)
            F.load_weights(str(f_weights))
            f_loaded = True
            print("Successfully loaded weights from .weights.h5 files.")
        except Exception as e:
            print(f"Loading .weights.h5 failed ({e}). Checking for .keras fallback...")

    # Attempt 2: fallback to .keras full model files
    if not (g_loaded and f_loaded):
        custom_objs = {
            "InstanceNormalization": InstanceNormalization,
            "ReflectionPadding2D": ReflectionPadding2D,
        }
        if g_keras.exists() and f_keras.exists():
            print(f"Loading full models from .keras files...")
            G = tf.keras.models.load_model(str(g_keras), custom_objects=custom_objs)
            F = tf.keras.models.load_model(str(f_keras), custom_objects=custom_objs)
            g_loaded = True
            f_loaded = True
            print("Successfully loaded models from .keras files.")
        else:
            raise FileNotFoundError(
                f"Missing model files in {weights_dir}. Required either .weights.h5 or .keras files."
            )

    # Startup self-check
    print("Running generator self-checks...")
    run_self_check(G, "G_photo2sketch")
    run_self_check(F, "F_sketch2photo")
    print("Generator self-checks passed successfully.")

    _G_photo2sketch = G
    _F_sketch2photo = F
    return _G_photo2sketch, _F_sketch2photo


def generate_sketch(input_tensor):
    """
    Given an input tensor of shape (1, 128, 128, 3) normalized to [-1, 1],
    run G_photo2sketch under the thread lock and return output tensor.
    """
    global _G_photo2sketch
    if _G_photo2sketch is None:
        raise RuntimeError("Models must be loaded at server startup.")
    with inference_lock:
        return _G_photo2sketch(input_tensor, training=False)


def generate_photo(input_tensor):
    """
    Given an input tensor of shape (1, 128, 128, 3) normalized to [-1, 1],
    run F_sketch2photo under the thread lock and return output tensor.
    """
    global _F_sketch2photo
    if _F_sketch2photo is None:
        raise RuntimeError("Models must be loaded at server startup.")
    with inference_lock:
        return _F_sketch2photo(input_tensor, training=False)
