# FlipArt model weights

Place both trained generators in this folder:

- `G_photo2sketch.weights.h5`
- `F_sketch2photo.weights.h5`

Matching `G_photo2sketch.keras` and `F_sketch2photo.keras` full models are a fallback. Model binaries are intentionally excluded from Git. Obtain them separately, copy exports from `artifacts/model_exports/` if available locally, or export them from [the training notebook](../../training/train_cyclegan.ipynb).

See the [project setup](../../README.md) before starting `backend/run.py`.
