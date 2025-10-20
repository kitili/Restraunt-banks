#!/usr/bin/env bash
source .venv/bin/activate && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
