"""
Main Application Entry Point

Launch Nexus - Your AI Content Co-Founder
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
gemini_key = os.getenv('GEMINI_API_KEY')

if not gemini_key:
    print("\n⚠️  WARNING: Missing GEMINI_API_KEY")
    print("   Nexus requires a Gemini API key to function.")
    print("\nCreate a .env file with: GEMINI_API_KEY=your_key_here")
    print("Get your key at: https://makersuite.google.com/app/apikey\n")

# Import and run Streamlit app
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    
    # Launch Nexus UI
    ui_file = Path(__file__).parent / "nexus_ui.py"
    print("🌊 Launching Nexus - Your AI Content Co-Founder")
    print(f"📋 UI: {ui_file}")
    print(f"🌐 Open: http://localhost:8501")
    print("\n" + "=" * 60 + "\n")
    
    # Run Streamlit
    sys.argv = ["streamlit", "run", str(ui_file), "--server.port=8501", "--server.headless=true"]
    sys.exit(stcli.main())
