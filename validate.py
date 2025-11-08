"""
VibeOS - Validation & Setup Script
Quick verification that everything is ready to launch
"""

import os
import sys
from pathlib import Path

def print_status(message, status="info"):
    """Print colored status message"""
    colors = {
        "success": "\033[92m✓",
        "error": "\033[91m✗",
        "warning": "\033[93m⚠",
        "info": "\033[94mℹ"
    }
    reset = "\033[0m"
    print(f"{colors.get(status, colors['info'])} {message}{reset}")

def check_files():
    """Verify all required files exist"""
    print("\n" + "="*60)
    print("CHECKING PROJECT FILES")
    print("="*60 + "\n")
    
    required_files = [
        # Core code
        ("main.py", "Application entry point"),
        ("ui.py", "Streamlit dashboard"),
        ("workflow.py", "LangGraph workflow orchestration"),
        ("agents.py", "AI agents (vibe, content, sponsor)"),
        ("tools.py", "External API integrations"),
        ("utils.py", "Utilities and database"),
        ("requirements.txt", "Python dependencies"),
        
        # Documentation
        ("README.md", "Main documentation"),
        ("PRD.md", "Product Requirements Document"),
        ("PITCH_DECK.md", "Investor pitch deck"),
        ("DEMO_SCRIPT.md", "90-second Loom script"),
        ("VIRAL_POST.md", "Social media content"),
        ("QUICKSTART.md", "5-minute setup guide"),
        ("PACKAGE_SUMMARY.md", "Complete overview"),
        
        # Configuration
        (".env.example", "Environment template"),
        (".gitignore", "Git ignore rules")
    ]
    
    all_exist = True
    for filename, description in required_files:
        path = Path(filename)
        if path.exists():
            size = path.stat().st_size
            print_status(f"{filename:25s} - {description} ({size:,} bytes)", "success")
        else:
            print_status(f"{filename:25s} - MISSING!", "error")
            all_exist = False
    
    return all_exist

def check_environment():
    """Check environment setup"""
    print("\n" + "="*60)
    print("CHECKING ENVIRONMENT")
    print("="*60 + "\n")
    
    # Check Python version
    py_version = sys.version_info
    if py_version >= (3, 10):
        print_status(f"Python version: {py_version.major}.{py_version.minor}.{py_version.micro}", "success")
    else:
        print_status(f"Python {py_version.major}.{py_version.minor} - Need 3.10+", "error")
        return False
    
    # Check .env file
    if Path(".env").exists():
        print_status(".env file exists", "success")
        
        # Load and check keys
        from dotenv import load_dotenv
        load_dotenv()
        
        required_keys = {
            "GROQ_API_KEY": "Required for AI content generation",
            "SERPER_API_KEY": "Required for trend hunting"
        }
        
        optional_keys = {
            "TWITTER_BEARER_TOKEN": "Optional for Twitter posting",
            "GMAIL_CREDENTIALS_PATH": "Optional for sponsor emails"
        }
        
        print("\nRequired API Keys:")
        all_keys_present = True
        for key, description in required_keys.items():
            if os.getenv(key):
                print_status(f"  {key}: Configured", "success")
            else:
                print_status(f"  {key}: MISSING - {description}", "error")
                all_keys_present = False
        
        print("\nOptional API Keys:")
        for key, description in optional_keys.items():
            if os.getenv(key):
                print_status(f"  {key}: Configured", "success")
            else:
                print_status(f"  {key}: Not set - {description}", "warning")
        
        return all_keys_present
    else:
        print_status(".env file not found", "error")
        print_status("  → Copy .env.example to .env and add your API keys", "info")
        return False

def check_dependencies():
    """Check if dependencies are installed"""
    print("\n" + "="*60)
    print("CHECKING DEPENDENCIES")
    print("="*60 + "\n")
    
    required_packages = [
        "streamlit",
        "langgraph",
        "langchain",
        "langchain_groq",
        "tweepy",
        "google-api-python-client",
        "plotly",
        "pandas",
        "sqlalchemy",
        "pydantic",
        "python-dotenv"
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_status(f"{package:30s} - Installed", "success")
        except ImportError:
            print_status(f"{package:30s} - NOT INSTALLED", "error")
            all_installed = False
    
    if not all_installed:
        print_status("\n→ Run: pip install -r requirements.txt", "info")
    
    return all_installed

def show_quick_start():
    """Show quick start instructions"""
    print("\n" + "="*60)
    print("QUICK START")
    print("="*60 + "\n")
    
    print("""
🚀 TO RUN VIBEOS:

1. Ensure API keys are in .env file:
   cp .env.example .env
   nano .env  # Add your GROQ_API_KEY and SERPER_API_KEY

2. Install dependencies (if not done):
   pip install -r requirements.txt

3. Launch the app:
   python main.py
   
   Or directly:
   streamlit run ui.py

4. Open browser:
   http://localhost:8501

5. Upload 3-5 content samples and click "Launch VibeOS"!

📚 DOCUMENTATION:
   - README.md         - Complete guide
   - QUICKSTART.md     - 5-minute setup
   - PRD.md           - Product details
   - PITCH_DECK.md    - Investor deck

🐛 TROUBLESHOOTING:
   - Check .env has API keys
   - Ensure virtual environment is active
   - Run: pip install --upgrade streamlit

💬 SUPPORT:
   - GitHub Issues
   - Twitter: @vibeos
   - Email: support@vibeos.io
""")

def main():
    """Run all validation checks"""
    print("\n" + "🚀 "*30)
    print("VIBEOS - VALIDATION & SETUP")
    print("🚀 "*30 + "\n")
    
    files_ok = check_files()
    env_ok = check_environment()
    deps_ok = check_dependencies()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60 + "\n")
    
    if files_ok:
        print_status("All project files present", "success")
    else:
        print_status("Some files are missing", "error")
    
    if env_ok:
        print_status("Environment configured correctly", "success")
    else:
        print_status("Environment needs setup", "warning")
    
    if deps_ok:
        print_status("All dependencies installed", "success")
    else:
        print_status("Some dependencies missing", "error")
    
    print("\n" + "="*60)
    
    if files_ok and env_ok and deps_ok:
        print_status("\n✅ VIBEOS IS READY TO LAUNCH! 🚀\n", "success")
        show_quick_start()
    elif files_ok and deps_ok:
        print_status("\n⚠️  Almost ready! Just add API keys to .env\n", "warning")
        print("Get FREE API keys:")
        print("  • Groq: https://console.groq.com")
        print("  • Serper: https://serper.dev")
        print("\nThen run: python main.py")
    else:
        print_status("\n❌ Setup incomplete. Follow the steps above.\n", "error")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
