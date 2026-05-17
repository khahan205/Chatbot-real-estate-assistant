"""ASGI entrypoint for Vercel and local uvicorn runs.

Vercel's Python runtime looks for a top-level ASGI/WSGI object named
``app`` in root entrypoints such as ``app.py``. The real FastAPI
application remains in ``backend.api`` so the backend package structure
can stay unchanged.
"""

from backend.api import app

__all__ = ["app"]
