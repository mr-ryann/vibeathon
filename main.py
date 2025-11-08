"""
VibeOS - Main Application Entry Point
Launches the Streamlit dashboard
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Environment setup
from dotenv import load_dotenv
load_dotenv()

# Check for required environment variables
required_vars = ['GROQ_API_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print("\n⚠️  WARNING: Missing required environment variables:")
    for var in missing_vars:
        print(f"   - {var}")
    print("\nCreate a .env file with your API keys to enable full functionality.")
    print("See .env.example for required variables.\n")

# Import and run Streamlit app
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import sys
    
    # Get the UI file path
    ui_file = Path(__file__).parent / "ui.py"
    
    # Run Streamlit
    sys.argv = ["streamlit", "run", str(ui_file), "--server.port=8501", "--server.headless=true"]
    sys.exit(stcli.main())
