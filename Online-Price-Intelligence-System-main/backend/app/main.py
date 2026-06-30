"""
Canonical FastAPI entrypoint.

Keep this module stable so existing run commands like:
  `uvicorn backend.app.main:app`
continue to work while we evolve the optimized implementation.
"""

from backend.app.main_optimized import app  # noqa: F401

