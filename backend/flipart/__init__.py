"""FlipArt backend package and Flask application factory."""


def create_app():
    """Load the generators once and register the HTTP routes."""
    from flask import Flask

    from .config import FRONTEND_DIST, MAX_REQUEST_BYTES, WEIGHTS_DIR
    from .errors import register_error_handlers
    from .models.inference import load_models
    from .routes import register_routes

    app = Flask(__name__, static_folder=None)
    app.config.update(
        MAX_CONTENT_LENGTH=MAX_REQUEST_BYTES,
        FRONTEND_DIST=FRONTEND_DIST,
        WEIGHTS_DIR=WEIGHTS_DIR,
    )

    print("Loading FlipArt CycleGAN generators...")
    try:
        load_models(app.config["WEIGHTS_DIR"])
    except Exception as exc:
        raise RuntimeError(
            "FlipArt startup failed. Check backend/weights/ and "
            f"TensorFlow compatibility: {exc}"
        ) from exc
    app.extensions["models_loaded"] = True

    register_routes(app)
    register_error_handlers(app)
    return app
