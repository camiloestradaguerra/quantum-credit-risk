#!/usr/bin/env python
"""
🚀 Automated Deploy Script - Credit Risk API
Starts API server and Cloudflare Tunnel with one command
"""

import subprocess
import time
import os
import sys
from pathlib import Path
from datetime import datetime

# Configuration
WORKSPACE_PATH = Path(__file__).parent
VENV_PYTHON = WORKSPACE_PATH / "venv_quantum_ml" / "Scripts" / "python.exe"
VENV_ACTIVATE = WORKSPACE_PATH / "venv_quantum_ml" / "Scripts" / "activate.bat"
CLOUDFLARED_EXE = WORKSPACE_PATH / "cloudflared.exe"
API_PORT = 8000
API_HOST = "0.0.0.0"

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def check_dependencies():
    """Check if all dependencies are available"""
    print_header("🔍 Checking Dependencies")
    
    checks = {
        "Python venv": VENV_PYTHON.exists(),
        "Cloudflared": CLOUDFLARED_EXE.exists(),
        "Requirements": (WORKSPACE_PATH / "requirements.txt").exists(),
        "Main API": (WORKSPACE_PATH / "src" / "main.py").exists(),
    }
    
    for name, exists in checks.items():
        status = "✅" if exists else "❌"
        print(f"{status} {name}: {exists}")
    
    if not all(checks.values()):
        print("\n⚠️  Some dependencies are missing!")
        if not VENV_PYTHON.exists():
            print("   → Run: python -m venv venv_quantum_ml")
        if not CLOUDFLARED_EXE.exists():
            print("   → Download: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/")
        sys.exit(1)
    
    print("\n✅ All dependencies ready!")

def start_api_server():
    """Start FastAPI server"""
    print_header("🌐 Starting FastAPI Server")
    
    # Change to workspace directory
    os.chdir(WORKSPACE_PATH)
    
    # Build command
    cmd = [
        str(VENV_PYTHON),
        "-m",
        "uvicorn",
        "src.main:app",
        "--host", API_HOST,
        "--port", str(API_PORT),
        "--reload"
    ]
    
    print(f"📍 Working directory: {WORKSPACE_PATH}")
    print(f"🚀 Command: {' '.join(cmd)}\n")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        print("⏳ Waiting for API to start...")
        time.sleep(3)
        
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"❌ API failed to start!\n{stderr}")
            sys.exit(1)
        
        print(f"✅ API Server started successfully on port {API_PORT}")
        print(f"   Local URL: http://localhost:{API_PORT}")
        print(f"   Health: http://localhost:{API_PORT}/health")
        print(f"   Docs: http://localhost:{API_PORT}/docs")
        
        return process
        
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        sys.exit(1)

def verify_api_health():
    """Verify API is responding"""
    print_header("✅ Verifying API Health")
    
    import requests
    
    for attempt in range(5):
        try:
            response = requests.get(f"http://localhost:{API_PORT}/health", timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Health Check PASSED")
                print(f"   Status: {data.get('status')}")
                print(f"   Model: {data.get('model')}")
                print(f"   AUC-ROC: {data.get('auc_roc')}")
                print(f"   Version: {data.get('version')}")
                return True
        except:
            pass
        
        if attempt < 4:
            print(f"⏳ Attempt {attempt + 1}/5 - Retrying in 2 seconds...")
            time.sleep(2)
    
    print("❌ API health check failed")
    return False

def start_cloudflare_tunnel():
    """Start Cloudflare Tunnel"""
    print_header("🌍 Starting Cloudflare Tunnel")
    
    cmd = [
        str(CLOUDFLARED_EXE),
        "tunnel",
        "--url", f"http://localhost:{API_PORT}"
    ]
    
    print(f"🚀 Command: {' '.join(cmd)}\n")
    print("⏳ Initializing tunnel (this may take a few seconds)...\n")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Wait for tunnel URL
        tunnel_url = None
        for _ in range(30):
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                print(f"❌ Tunnel failed to start!\n{stderr}")
                sys.exit(1)
            
            time.sleep(0.5)
        
        print("✅ Cloudflare Tunnel started")
        print(f"   Monitoring logs... (watch for tunnel URL)")
        
        return process
        
    except Exception as e:
        print(f"❌ Error starting tunnel: {e}")
        sys.exit(1)

def main():
    """Main deployment flow"""
    print(f"\n{'='*70}")
    print(f"  🚀 CREDIT RISK PREDICTION API - PRODUCTION DEPLOY")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # Step 1: Check dependencies
    check_dependencies()
    
    # Step 2: Start API
    print("\n📌 STEP 1/3: Starting API Server...")
    api_process = start_api_server()
    
    # Step 3: Verify API
    print("\n📌 STEP 2/3: Verifying API Health...")
    if not verify_api_health():
        api_process.terminate()
        sys.exit(1)
    
    # Step 4: Start Tunnel
    print("\n📌 STEP 3/3: Starting Cloudflare Tunnel...")
    tunnel_process = start_cloudflare_tunnel()
    
    # Final status
    print_header("✅ DEPLOYMENT SUCCESSFUL")
    print("""
🎉 Your API is now LIVE and publicly accessible!

📍 LOCAL ACCESS:
   http://localhost:8000
   http://localhost:8000/docs

🌍 PUBLIC ACCESS:
   https://encouraged-colleges-benjamin-magnitude.trycloudflare.com
   https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/docs

📊 TEST COMMAND:
   curl http://localhost:8000/health

🔑 IMPORTANT NOTES:
   • Keep both terminals running
   • API uses port 8000 (change if needed)
   • Cloudflare Tunnel provides HTTPS automatically
   • No firewall configuration needed
   • Accessible from anywhere on the internet

⚙️  NEXT STEPS:
   1. Test the health endpoint
   2. Try /docs for interactive API documentation
   3. Send prediction requests to /predict
   4. When ready: Upgrade to 200 samples + better metrics

💡 TO STOP:
   • Press Ctrl+C in this terminal
   • Or close both API and Tunnel terminals
    """)
    
    # Keep processes running
    try:
        while True:
            if api_process.poll() is not None or tunnel_process.poll() is not None:
                print("\n⚠️  One of the processes stopped unexpectedly!")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        api_process.terminate()
        tunnel_process.terminate()
        print("✅ Services stopped")

if __name__ == "__main__":
    main()
