# FlipArt backend

Flask serves the image API and the compiled React app. The [root README](../README.md) covers complete installation, weights, and startup.

## Commands

Run from the project root in PowerShell:

```powershell
# Start the API and built frontend
.\venv\Scripts\python.exe backend\run.py

# In another terminal while Flask runs
.\venv\Scripts\python.exe -m pytest backend\tests -q
Invoke-RestMethod http://127.0.0.1:5000/health
```

From inside `backend/`, use `..\venv\Scripts\python.exe run.py`. Paths to weights and frontend assets are independent of the working directory. Build the frontend with `npm.cmd --prefix frontend run build` from the project root.

## Module responsibilities

| Module | Responsibility |
| --- | --- |
| `run.py` | Local server startup on 127.0.0.1:5000 |
| `flipart/__init__.py` | Application factory, generator loading, route registration |
| `flipart/config.py` | Project paths, image dimensions, request limits |
| `flipart/errors.py` | JSON error handling |
| `flipart/routes/images.py` | Preview and conversion HTTP endpoints |
| `flipart/routes/requests.py` | Multipart/JSON parsing and option validation |
| `flipart/routes/frontend.py` / `health.py` | Built frontend/assets and readiness endpoint |
| `flipart/services/conversion.py` | Detection, preprocessing, and inference orchestration |
| `flipart/services/image_io.py` | Safe image decoding and PNG/base64 encoding |
| `flipart/services/image_cropping.py` | Face detection and square crops |
| `flipart/services/image_processing.py` | Cleanup, normalization, output processing |
| `flipart/services/image_detection.py` | Photo/sketch heuristic and confidence |
| `flipart/models/layers.py` / `generator.py` | Custom Keras layers and ResNet-6 architecture |
| `flipart/models/inference.py` | Cached weights, self-checks, locked inference |

## Model files

Place `G_photo2sketch.weights.h5` and `F_sketch2photo.weights.h5` in `backend/weights/`. Matching `.keras` full models are a fallback. Binaries are ignored by Git; setup and export instructions are in the root README and [training notebook](../training/train_cyclegan.ipynb).

Generators load once at startup and run shape/range self-checks. Inference uses `training=False` under a shared lock. Startup fails if the models cannot be loaded.

The pinned requirements use TensorFlow 2.20.0; use Python 3.12 for that installation. The supplied local environment instead uses Python 3.14 with TensorFlow 2.22.0-rc0.

## API

| Route | Response |
| --- | --- |
| `GET /health` | Model readiness and architecture version |
| `POST /api/preview` | Detection metadata and prepared input preview |
| `POST /api/convert` | Preview metadata plus output image and inference time |
| `GET /` | Compiled React frontend |
| `GET /assets/<filename>` | Compiled frontend assets |
| `GET /samples/<filename>` | Bundled demo image |

Both POST endpoints accept a multipart `image` file or a JSON `image` field containing a base64 data URL. Supported formats: PNG, JPG/JPEG, BMP, and WebP; maximum decoded upload size: 10 MB.

| Option | Default | Meaning |
| --- | --- | --- |
| `mode` | `auto` | `auto`, `photo` (photo to sketch), or `sketch` (sketch to photo) |
| `face_crop` | `true` | Crop the largest detected face; otherwise use a center crop |
| `grayscale_sketch` | `true` | Remove color tint from generated sketches |
| `enhance_contrast` | `false` | Apply contrast enhancement to generated sketches |
| `clean_sketch` | `false` | Clean up sketch inputs before resizing |

Responses include `detected_type`, `effective_input_type`, `direction`, `detection_confidence`, `manual_override`, `face_found`, `cleanup_applied`, and `input_preview`. Conversion adds `output_image` and `inference_ms`. Images are PNG data URLs. Invalid input returns HTTP 400, oversized requests 413, and unexpected failures 500 with a JSON `error` message.

## Preprocessing

1. Decode, apply EXIF orientation, and convert to RGB (transparency blends onto white).
2. Detect the input type before cropping or cleanup, including manual direction overrides.
3. For photos, crop the largest face or use a center square. Disabling face crop keeps the whole image. Sketches use a center-square crop.
4. Apply optional cleanup only to sketch inputs resolved to sketch-to-photo conversion.
5. Resize with TensorFlow bilinear antialiasing to 128 x 128 and normalize using `x / 127.5 - 1`.
6. Run the appropriate generator, convert its output to RGB pixels, optionally adjust sketch output, and enlarge to 512 x 512 for display/download.

Cleanup cannot recover missing facial details. Its quality benefit has not been established against the dataset.

## Detector evaluation

```powershell
.\venv\Scripts\python.exe backend\tools\evaluate_detector.py --dataset-root C:\path\to\person-face-sketches --tune
```

The dataset should contain `val/photos`, `val/sketches`, `test/photos`, and `test/sketches`. Threshold tuning uses validation data. The full dataset is not included, so no detector accuracy is claimed. Current sketch thresholds are saturation below 0.05 and white fraction above 0.50, where white pixels exceed 0.85 intensity. Confidence is a heuristic score rather than a calibrated probability; use manual direction selection for ambiguous inputs.

Reported FID values shown in the UI describe the supplied model, not detector accuracy: validation 135.8 / 68.5 and test 142.1 / 76.5 (photo-to-sketch / sketch-to-photo).
