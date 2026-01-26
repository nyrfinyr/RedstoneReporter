#!/usr/bin/env python3
"""Entry point for RedstoneReporter server.

Usage:
    Development: python run.py
    Production:  uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
"""

import uvicorn
from app.config import settings


def main():
    """Start the RedstoneReporter server."""
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # Auto-reload on code changes (development mode)
        log_level="info"
    )


if __name__ == "__main__":
    main()
