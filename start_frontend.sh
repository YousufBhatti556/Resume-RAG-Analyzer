#!/bin/bash
# Frontend server start script

cd "$(dirname "$0")/frontend"
echo "Starting frontend server..."
echo "Open http://127.0.0.1:5500/index.html in your browser"
echo "Press Ctrl+C to stop"
python3 -m http.server 5500
