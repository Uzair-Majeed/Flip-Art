"""Start FlipArt from any working directory: python backend/run.py."""

from flipart import create_app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False)
