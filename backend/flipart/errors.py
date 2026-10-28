"""Consistent JSON error responses for the Flask API."""

from flask import current_app, jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    app.register_error_handler(ValueError, invalid_input)
    app.register_error_handler(HTTPException, http_error)
    app.register_error_handler(Exception, unexpected_error)


def invalid_input(error):
    return jsonify(error=str(error)), 400


def http_error(error):
    message = "Image exceeds the 10 MB limit." if error.code == 413 else error.description
    return jsonify(error=message), error.code


def unexpected_error(error):
    current_app.logger.exception("Conversion request failed")
    return jsonify(error="Conversion failed. Check the server log and try another image."), 500
