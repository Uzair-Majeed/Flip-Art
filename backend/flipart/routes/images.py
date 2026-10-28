"""Thin HTTP handlers for image preview and conversion."""

from flask import Blueprint, jsonify

from ..services.conversion import convert_image, prepare_image
from .requests import read_image_request

images = Blueprint("images", __name__, url_prefix="/api")


@images.post("/preview")
def preview():
    image, options = read_image_request()
    _, metadata = prepare_image(image, options)
    return jsonify(metadata)


@images.post("/convert")
def convert():
    image, options = read_image_request()
    return jsonify(convert_image(image, options))
