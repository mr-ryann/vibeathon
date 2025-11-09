# VibeOS - AI Content Creation Platform

## Overview
VibeOS is an AI-powered content creation platform that helps creators build their brand on autopilot. The platform combines trend hunting, AI-generated content, and sponsor outreach to help creators grow their audience and revenue.

**Current State:** Successfully imported and configured for Replit environment.

## Recent Changes
- **2025-11-08**: Initial Replit setup completed
  - Configured frontend to run on port 5000 for Replit webview
  - Updated Vite config to allow all hosts for Replit proxy
  - Fixed backend server syntax errors
  - Created backend startup script
  - Configured deployment settings

## Project Architecture

### Frontend (React + Vite)
- **Location:** `/frontend` directory
- **Port:** 5000 (Replit webview)
- **Tech Stack:** React 18, Vite 5, Axios, React Router
- **Entry Point:** `frontend/src/main.jsx`
- **Key Components:**
  - Dashboard, Trends, Script Generator, Upload, Analytics pages
  - AI-powered script generation interface
  - Sponsor outreach tools

### Backend (FastAPI)
- **Location:** `backend_server.py`
- **Port:** 8000 (localhost only)
- **Tech Stack:** FastAPI, LangGraph, LangChain, Google Gemini AI
- **Key Features:**
  - Trend hunting via Google Serper API
  - AI content generation in user's voice
  - Sponsor matching and email outreach
  - Video processing and clipping

### Alternative UI (Streamlit)
- **Location:** `nexus_ui.py`, `ui.py`, `main.py`
- **Port:** 8501
- **Note:** This is an alternative interface to the React frontend

## Running the Project

### Development Mode
The frontend is already running via the configured workflow on port 5000.

**To start the backend**, open a new Shell tab and run:

```bash
python run_backend.py
```

This will start the backend API server on port 8000. The frontend will automatically connect to it.

### Required Environment Variables
The project requires several API keys to function:

- `GEMINI_API_KEY` - Google Gemini AI (required)
- `GROQ_API_KEY` - Groq API for LLaMA models
- `SERPER_API_KEY` - Google Serper for trend hunting
- `TWITTER_API_KEY`, `TWITTER_API_SECRET` - Twitter posting (optional)
- `GMAIL_CREDENTIALS` - Gmail API for sponsor emails (optional)

Create a `.env` file with these keys or add them via Replit Secrets.

## Project Structure

```
vibeos/
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API client
│   │   └── styles/        # CSS files
│   ├── package.json
│   └── vite.config.js
├── backend_server.py      # FastAPI backend server
├── api_server.py          # Alternative API server
├── main.py                # Streamlit app entry point
├── nexus_ui.py            # Streamlit UI
├── agents.py              # AI agent implementations
├── tools.py               # External API tools
├── utils.py               # Utility functions
├── workflow.py            # LangGraph orchestration
├── start_backend.sh       # Backend startup script
└── requirements.txt       # Python dependencies
```

## Deployment
The project is configured for Replit Autoscale deployment:
- Frontend builds via `npm run build`
- Backend runs on internal port 8000
- Frontend serves on public port 5000

## Known Issues
- Backend requires manual startup (use `start_backend.sh`)
- Some Python dependencies may need API keys to function fully
- Video processing requires FFmpeg (available in Replit)

## User Preferences
None specified yet.
