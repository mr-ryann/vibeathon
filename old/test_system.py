#!/usr/bin/env python3
"""
System Verification Test
Quickly verify all components are working
"""

import os
import sys

print("=" * 80)
print("🧪 CREATORFORGE NEXUS - SYSTEM VERIFICATION TEST")
print("=" * 80)

# Color codes for terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def test(name, condition, message=""):
    if condition:
        print(f"{GREEN}✅{RESET} {name}")
        return True
    else:
        print(f"{RED}❌{RESET} {name}")
        if message:
            print(f"   {YELLOW}→{RESET} {message}")
        return False

results = []

# Test 1: Environment
print("\n📋 Testing Environment...")
results.append(test(
    "Python 3.7+",
    sys.version_info >= (3, 7),
    f"Current: {sys.version_info.major}.{sys.version_info.minor}"
))

results.append(test(
    "API Key in .env",
    os.path.exists('.env') and 'GEMINI_API_KEY' in open('.env').read(),
    "Check .env file exists with GEMINI_API_KEY"
))

# Test 2: Required Packages
print("\n📦 Testing Packages...")
packages = [
    ('streamlit', 'pip install streamlit'),
    ('google.generativeai', 'pip install google-generativeai'),
    ('langgraph', 'pip install langgraph'),
    ('fastapi', 'pip install fastapi'),
    ('uvicorn', 'pip install uvicorn'),
    ('dotenv', 'pip install python-dotenv')
]

for package, install_cmd in packages:
    try:
        __import__(package.replace('.', '_').split('_')[0])
        results.append(test(f"Package: {package}", True))
    except ImportError:
        results.append(test(f"Package: {package}", False, f"Run: {install_cmd}"))

# Test 3: Agent Files
print("\n🤖 Testing Agent Files...")
agent_files = [
    'agent_trendscout.py',
    'agent_forgemaster.py',
    'agent_engagebot.py',
    'nexus_core.py',
    'api_server.py'
]

for file in agent_files:
    exists = os.path.exists(file)
    results.append(test(f"File: {file}", exists, f"Missing: {file}"))

# Test 4: Import Agents
print("\n🔌 Testing Imports...")
try:
    from agent_trendscout import run_trendscout, GraphState
    results.append(test("Import: TrendScout", True))
except Exception as e:
    results.append(test("Import: TrendScout", False, str(e)[:50]))

try:
    from agent_forgemaster import run_forgemaster
    results.append(test("Import: ForgeMaster", True))
except Exception as e:
    results.append(test("Import: ForgeMaster", False, str(e)[:50]))

try:
    from agent_engagebot import run_engagebot
    results.append(test("Import: EngageBot", True))
except Exception as e:
    results.append(test("Import: EngageBot", False, str(e)[:50]))

try:
    from nexus_core import nexus_app, run_nexus
    results.append(test("Import: NexusCore", True))
except Exception as e:
    results.append(test("Import: NexusCore", False, str(e)[:50]))

# Test 5: UI Files
print("\n🎨 Testing UI Files...")
ui_files = [
    'app_langgraph.py',
    'app_multi_agent.py',
    'app_ui.py'
]

for file in ui_files:
    exists = os.path.exists(file)
    results.append(test(f"UI: {file}", exists))

# Test 6: Documentation
print("\n📚 Testing Documentation...")
doc_files = [
    'QUICKSTART.md',
    'NEXUSCORE_COMPLETE.md',
    'FINAL_SUMMARY.md'
]

for file in doc_files:
    exists = os.path.exists(file)
    results.append(test(f"Docs: {file}", exists))

# Summary
print("\n" + "=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)

passed = sum(results)
total = len(results)
percentage = (passed / total) * 100

print(f"\nTests Passed: {GREEN}{passed}/{total}{RESET} ({percentage:.1f}%)")

if percentage == 100:
    print(f"\n{GREEN}🎉 ALL TESTS PASSED!{RESET}")
    print("\n✨ Your system is ready to use!")
    print("\n🚀 Quick Start Commands:")
    print("   • Test core:    python nexus_core.py")
    print("   • Launch UI:    streamlit run app_langgraph.py")
    print("   • Start API:    python api_server.py")
elif percentage >= 80:
    print(f"\n{YELLOW}⚠️  MOSTLY WORKING{RESET}")
    print("\nMost components are ready. Check failed tests above.")
else:
    print(f"\n{RED}❌ NEEDS ATTENTION{RESET}")
    print("\nSeveral components need to be fixed. See errors above.")

print("\n" + "=" * 80)

# Exit code
sys.exit(0 if percentage == 100 else 1)
