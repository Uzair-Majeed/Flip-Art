"""Serve the compiled React application and its public assets."""

from flask import Blueprint, current_app, send_from_directory

frontend = Blueprint("frontend", __name__)


@frontend.get("/")
def index():
    dist = current_app.config["FRONTEND_DIST"]
    if not (dist / "index.html").is_file():
        return (
            "React build missing. From the project root, run "
            "npm.cmd --prefix frontend ci and npm.cmd --prefix frontend run build.",
            503,
        )
    return send_from_directory(dist, "index.html")


@frontend.get("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(current_app.config["FRONTEND_DIST"] / "assets", filename)


@frontend.get("/samples/<path:filename>")
def samples(filename):
    return send_from_directory(current_app.config["FRONTEND_DIST"] / "samples", filename)


@frontend.get("/favicon.svg")
def favicon():
    return send_from_directory(current_app.config["FRONTEND_DIST"], "favicon.svg")
