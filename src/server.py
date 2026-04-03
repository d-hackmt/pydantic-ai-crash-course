"""
server.py
This file defines the FastAPI web server that powers Alia's Real-time Dashboard.
It serves the HTML frontend and exposes a `/state` endpoint for the UI to poll data dynamically.
FastAPI operations are perfectly traced and monitored by Logfire.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json
import os
import logfire

app = FastAPI(title="Alia Dashboard")

import logging

# Filter out the noisy /state polling endpoint from the native Uvicorn terminal output
class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.args and len(record.args) >= 3 and record.args[2] != "/state"

logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

# Instrument the entire FastAPI server, ignoring the noise of the UI polling loop
logfire.instrument_fastapi(app, excluded_urls=["/state"])

templates = Jinja2Templates(directory="src/templates")
DATA_DIR = 'data'

def _read_json(filename: str) -> dict | list:
    """Helper function to safely read a JSON file without crashing the web thread."""
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logfire.warn(f"Failed to read json '{filename}': {e}")
            return {}
    return {}

def _read_text(filename: str) -> str:
    """Helper function to safely read a text/markdown file without crashing the web thread."""
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logfire.warn(f"Failed to read text '{filename}': {e}")
            return ""
    return ""

@app.get("/", response_class=HTMLResponse)
async def dashboard_ui(request: Request):
    """Serve the main Glassmorphism HTML interface."""
    logfire.info("Dashboard accessed by user.")
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/state")
async def get_state():
    """Endpoint polled repeatedly by the frontend to fetch all persistent memories, logs, and stats."""
    return JSONResponse(content={
        "heart": _read_json('heart.json'),
        "chat": _read_json('chat_log.json'),
        "diary": _read_text('diary.md'),
        "lifecycle": _read_text('lifecycle.md'),
        "twitter": _read_text('twitter_sim.md')
    })

# if __name__ == "__main__":
#     import uvicorn
#     logfire.info("Starting manual hot-reload web server instance...")
#     uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
