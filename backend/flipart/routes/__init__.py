"""HTTP endpoint registration."""

from .frontend import frontend
from .health import health
from .images import images


def register_routes(app):
    for blueprint in (frontend, health, images):
        app.register_blueprint(blueprint)
