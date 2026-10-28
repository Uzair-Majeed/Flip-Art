"""Model readiness endpoint."""

from flask import Blueprint, current_app, jsonify

health = Blueprint("health", __name__)


@health.get("/health")
def model_health():
    return jsonify(
        status="healthy",
        models_loaded=current_app.extensions["models_loaded"],
        model_version="ResNet-6 (128x128)",
    )
