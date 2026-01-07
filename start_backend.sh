#!/bin/bash
# Backend server start script

cd "$(dirname "$0")"
echo "Starting backend server..."
echo "Backend will be available at http://127.0.0.1:8000"
echo "Press Ctrl+C to stop"
uvicorn backend.main:app --reload
