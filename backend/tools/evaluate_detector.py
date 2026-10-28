"""
Evaluation tool for sketch-vs-photo auto-detection.

Evaluates detector accuracy on dataset splits (val and test), outputs:
- Confusion matrix
- Accuracy, Precision, Recall, F1-score
- List of misclassified filenames with features
- Optional threshold search on the val split
"""

import argparse
import sys
from pathlib import Path
from PIL import Image

# Ensure parent directory is on sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
if str(REPO_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_DIR))

from flipart.services.image_detection import (
    detect_image_type,
    extract_detector_features,
    SATURATION_THRESHOLD,
    WHITE_FRACTION_THRESHOLD,
    WHITE_PIXEL_INTENSITY,
)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def collect_images_from_folder(folder_path):
    """Return list of image Path objects in a folder."""
    p = Path(folder_path)
    if not p.is_dir():
        return []
    return sorted(
        [f for f in p.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS]
    )


def evaluate_split(dataset_root, split_name="val", sat_thresh=SATURATION_THRESHOLD, white_thresh=WHITE_FRACTION_THRESHOLD):
    """
    Evaluate detector on a split: {dataset_root}/{split_name}/photos and sketches.
    """
    root = Path(dataset_root)
    photos_dir = root / split_name / "photos"
    sketches_dir = root / split_name / "sketches"

    if not (photos_dir.exists() and sketches_dir.exists()):
        # Check alternative flat structure
        alt_photos = root / "photos"
        alt_sketches = root / "sketches"
        if alt_photos.exists() and alt_sketches.exists():
            photos_dir = alt_photos
            sketches_dir = alt_sketches
        else:
            raise FileNotFoundError(
                f"Split directories not found in {root}. Expected {photos_dir} and {sketches_dir}"
            )

    photo_files = collect_images_from_folder(photos_dir)
    sketch_files = collect_images_from_folder(sketches_dir)

    print(f"\n==========================================")
    print(f"Evaluating split: {split_name.upper()}")
    print(f"Dataset root: {root}")
    print(f"Photos found: {len(photo_files)}, Sketches found: {len(sketch_files)}")
    print(f"Thresholds -> Saturation < {sat_thresh:.4f}, White Fraction > {white_thresh:.4f}")
    print(f"==========================================")

    if not photo_files and not sketch_files:
        print("Warning: No images found to evaluate.")
        return None

    # Confusion matrix counters:
    # Class 'sketch' is positive, 'photo' is negative
    tp = 0  # sketch correctly classified as sketch
    fn = 0  # sketch classified as photo
    tn = 0  # photo correctly classified as photo
    fp = 0  # photo classified as sketch

    misclassified = []

    # Evaluate photos (ground truth = photo)
    for f in photo_files:
        try:
            im = Image.open(f)
            feats = extract_detector_features(im)
            is_sketch = (feats["saturation"] < sat_thresh) and (feats["white_fraction"] > white_thresh)
            if is_sketch:
                fp += 1
                misclassified.append({
                    "file": str(f.relative_to(root)),
                    "true_label": "photo",
                    "predicted": "sketch",
                    "saturation": feats["saturation"],
                    "white_fraction": feats["white_fraction"],
                })
            else:
                tn += 1
        except Exception as e:
            print(f"Error reading {f}: {e}")

    # Evaluate sketches (ground truth = sketch)
    for f in sketch_files:
        try:
            im = Image.open(f)
            feats = extract_detector_features(im)
            is_sketch = (feats["saturation"] < sat_thresh) and (feats["white_fraction"] > white_thresh)
            if is_sketch:
                tp += 1
            else:
                fn += 1
                misclassified.append({
                    "file": str(f.relative_to(root)),
                    "true_label": "sketch",
                    "predicted": "photo",
                    "saturation": feats["saturation"],
                    "white_fraction": feats["white_fraction"],
                })
        except Exception as e:
            print(f"Error reading {f}: {e}")

    total = tp + tn + fp + fn
    accuracy = (tp + tn) / max(total, 1)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-6)

    photo_acc = tn / max(tn + fp, 1)
    sketch_acc = tp / max(tp + fn, 1)

    print("\n--- Confusion Matrix ---")
    print(f"                   Predicted Photo    Predicted Sketch")
    print(f"Actual Photo       {tn:<18} {fp:<16} (Acc: {photo_acc * 100:.2f}%)")
    print(f"Actual Sketch      {fn:<18} {tp:<16} (Acc: {sketch_acc * 100:.2f}%)")
    print("------------------------")
    print(f"Total Evaluated:   {total}")
    print(f"Overall Accuracy:  {accuracy * 100:.2f}% ({tp + tn}/{total})")
    print(f"Precision:         {precision * 100:.2f}%")
    print(f"Recall:            {recall * 100:.2f}%")
    print(f"F1 Score:          {f1 * 100:.2f}%")

    if misclassified:
        print(f"\nMisclassified files ({len(misclassified)} total):")
        for m in misclassified[:20]:
            print(
                f"  [{m['true_label']} -> {m['predicted']}] {m['file']} "
                f"(sat: {m['saturation']:.4f}, white_frac: {m['white_fraction']:.4f})"
            )
        if len(misclassified) > 20:
            print(f"  ... and {len(misclassified) - 20} more.")
    else:
        print("\nAll files classified perfectly! (0 misclassifications)")

    return {
        "split": split_name,
        "total": total,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "misclassified": misclassified,
    }


def tune_thresholds_on_val(dataset_root):
    """Grid search over saturation and white_fraction thresholds on val split."""
    root = Path(dataset_root)
    photos = collect_images_from_folder(root / "val" / "photos")
    sketches = collect_images_from_folder(root / "val" / "sketches")

    if not photos or not sketches:
        print("Val set photos or sketches not found for threshold tuning.")
        return

    print(f"Extracting features for {len(photos)} val photos and {len(sketches)} val sketches...")
    photo_feats = [extract_detector_features(Image.open(f)) for f in photos]
    sketch_feats = [extract_detector_features(Image.open(f)) for f in sketches]

    best_acc = -1.0
    best_params = (SATURATION_THRESHOLD, WHITE_FRACTION_THRESHOLD)

    sat_candidates = [0.03, 0.04, 0.05, 0.06, 0.08, 0.10]
    white_candidates = [0.40, 0.45, 0.50, 0.55, 0.60]

    for s_t in sat_candidates:
        for w_t in white_candidates:
            # TN: photos with sat >= s_t or white <= w_t
            tn = sum(1 for f in photo_feats if not (f["saturation"] < s_t and f["white_fraction"] > w_t))
            # TP: sketches with sat < s_t and white > w_t
            tp = sum(1 for f in sketch_feats if (f["saturation"] < s_t and f["white_fraction"] > w_t))
            acc = (tp + tn) / (len(photos) + len(sketches))
            if acc > best_acc:
                best_acc = acc
                best_params = (s_t, w_t)

    print(f"\nOptimal thresholds on val: Saturation < {best_params[0]}, White Fraction > {best_params[1]}")
    print(f"Best Val Accuracy: {best_acc * 100:.2f}%")
    return best_params


def main():
    parser = argparse.ArgumentParser(description="Evaluate sketch-vs-photo detector.")
    parser.add_argument(
        "--dataset-root",
        type=str,
        default="dataset",
        help="Path to dataset root folder containing train, val, and/or test splits.",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="all",
        choices=["val", "test", "train", "all"],
        help="Split to evaluate: 'val', 'test', or 'all' (default).",
    )
    parser.add_argument(
        "--tune",
        action="store_true",
        help="Run threshold tuning on val split before test evaluation.",
    )

    args = parser.parse_args()
    root = Path(args.dataset_root)

    if not root.exists():
        print(f"Error: Dataset root '{root}' does not exist.")
        print("Please point --dataset-root to the directory containing person-face-sketches.")
        print("Expected layout: {dataset-root}/(val|test)/photos and (val|test)/sketches")
        sys.exit(1)

    sat_thresh = SATURATION_THRESHOLD
    white_thresh = WHITE_FRACTION_THRESHOLD

    if args.tune:
        best_p = tune_thresholds_on_val(root)
        if best_p:
            sat_thresh, white_thresh = best_p

    if args.split in ("val", "all"):
        try:
            evaluate_split(root, "val", sat_thresh, white_thresh)
        except Exception as e:
            print(f"Could not evaluate 'val' split: {e}")

    if args.split in ("test", "all"):
        try:
            evaluate_split(root, "test", sat_thresh, white_thresh)
        except Exception as e:
            print(f"Could not evaluate 'test' split: {e}")


if __name__ == "__main__":
    main()
