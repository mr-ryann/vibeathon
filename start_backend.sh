#!/bin/bash
# Backend startup script for VibeOS

echo "🚀 Starting VibeOS Backend Server..."
uvicorn backend_server:app --host localhost --port 8000 --reload
