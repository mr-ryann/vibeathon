# Nexus - AI Content Creation Platform

## Overview
Nexus is an AI-powered content creation platform that helps creators build their brand on autopilot. The platform combines trend hunting, AI-generated content, and sponsor outreach to help creators grow their audience and revenue.

**Current State:** Successfully imported and configured for Replit environment.

## Recent Changes
- **2025-11-09**: Complete agent naming integration + Session storage
  - Renamed all AI agents to new branded names:
    - ripple (trend scout & vibe analyzer)
    - quill (script generator)
    - pulse (engagement & sponsor outreach)
    - envoy (brand partnership finder)
    - core (strategic orchestrator)
  - Updated frontend UI to display agent names directly:
    - Dashboard cards now show: agent_ripple, agent_quill, agent_core, agent_pulse + agent_envoy
    - Page titles updated: "agent_ripple: Trend Intelligence", "agent_quill: Creative Engine", etc.
    - Loading indicators reference specific agents (e.g., "ripple agent scouting live trends")
  - Fixed Gemini model name to "gemini-2.0-flash-exp" for script generation
  - Added session storage to preserve text inputs across page reloads:
    - TrendsPage: niche and growth goal inputs persist
    - ScriptPage: vibe input persists
    - ScriptPage: selected trend now persists in dropdown menu
  - Fixed backend SponsorFinder API call: changed incorrect `content_type` parameter to `num_sponsors`
  - Enhanced Partner Radar with real sponsor data:
    - Uses Serper API to search for relevant sponsors based on trend/niche
    - Extracts real contact emails using regex pattern matching and intelligent search
    - Detects sponsor category from search snippets
    - Generates personalized email templates tailored to each sponsor's business
  - Fixed TrendHunter.get_best_trends() to accept limit parameter
  - Fixed SERPER_API_KEY environment variable references
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

### AI Agents
Nexus uses five specialized AI agents:

1. **ripple** - Trend Scout & Vibe Analyzer
   - Analyzes content samples to extract creator's unique voice
   - Like ripples spreading outward, detects unique patterns in content
   - Class: `VibeAnalyzerAgent`

2. **quill** - Script Generator
   - Generates viral scripts, captions, and hooks in creator's voice
   - The writer's tool, crafting stories from raw trends
   - Class: `ContentGeneratorAgent`

3. **pulse** - Engagement & Sponsor Outreach
   - Writes personalized sponsor pitch emails
   - Generates authentic comment replies
   - The steady heartbeat of engagement and outreach
   - Classes: `SponsorPitchAgent`, `ReplyGeneratorAgent`

4. **envoy** - Brand Partnership Finder
   - Finds relevant brand deals using Gemini Pro API
   - The ambassador, forging partnerships and deals
   - Class: `DealHunterAgent`

5. **core** - Strategic Orchestrator
   - Makes high-level content strategy decisions
   - Analyzes performance and provides optimization recommendations
   - The central brain of the operation
   - Class: `StrategyAgent`

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
