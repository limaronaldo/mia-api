"""
Main entry point for the presentation API module.
This allows running the FastAPI application as a module using: python -m src.presentation.api
"""

import uvicorn

from .main import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True, log_level="info")
