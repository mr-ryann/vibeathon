#!/usr/bin/env python3
"""
Backend server launcher for VibeOS
Run this to start the backend API server
"""
import uvicorn

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Starting VibeOS Backend Server")
    print("=" * 80)
    print("\n📡 Backend will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("\n⚠️  Note: Backend requires API keys to function fully")
    print("   Add these to your Replit Secrets:")
    print("   - GEMINI_API_KEY")
    print("   - SERPER_API_KEY")
    print("\n" + "=" * 80 + "\n")
    
    uvicorn.run(
        "backend_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
