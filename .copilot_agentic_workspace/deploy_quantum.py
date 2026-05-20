#!/usr/bin/env python3
"""
QUANTUM API DEPLOYMENT - AUTOMATED
===================================

Deploy Quantum Machine Learning API with Cloudflare Tunnel.

Features:
  - Starts FastAPI server on port 8001
  - Creates Cloudflare Tunnel for public access
  - Monitors both processes
  - Graceful shutdown with Ctrl+C
  - Independent from classical API (port 8000)

Usage:
  python deploy_quantum.py

Architecture:
  [FastAPI on 8001] --> [Cloudflare Tunnel] --> [Public HTTPS URL]
  (Independent from classical API on 8000)
"""

import subprocess
import time
import sys
import signal
import os
from pathlib import Path
import logging
import socket

# ============================================================================
# CONFIGURATION
# ============================================================================

QUANTUM_API_PORT = 8001
QUANTUM_API_SCRIPT = "src/quantum_main.py"
WORKSPACE_ROOT = Path(__file__).parent
VENV_PATH = WORKSPACE_ROOT / 'venv_quantum_ml'
VENV_PYTHON = VENV_PATH / 'Scripts' / 'python.exe'
CLOUDFLARED_PATH = WORKSPACE_ROOT / 'cloudflared.exe'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global process handles
API_PROCESS = None
TUNNEL_PROCESS = None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def check_python_env():
    """Verify Python environment is available."""
    if not VENV_PYTHON.exists():
        logger.error(f"[FAIL] Virtual environment not found: {VENV_PYTHON}")
        logger.error("Create with: python -m venv venv_quantum_ml")
        return False
    
    logger.info(f"[OK] Python environment: {VENV_PYTHON}")
    return True

def check_cloudflared():
    """Check if cloudflared binary exists."""
    if not CLOUDFLARED_PATH.exists():
        logger.warning(f"[FAIL] cloudflared.exe not found at {CLOUDFLARED_PATH}")
        logger.warning("Download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/")
        return False
    
    logger.info(f"[OK] Cloudflared found: {CLOUDFLARED_PATH}")
    return True

def check_api_script():
    """Check if API script exists."""
    api_path = WORKSPACE_ROOT / QUANTUM_API_SCRIPT
    if not api_path.exists():
        logger.error(f"[FAIL] API script not found: {api_path}")
        logger.error("Create with: python scripts/2_quantum_ml_pipeline_OPTIMIZED.py")
        return False
    
    logger.info(f"[OK] API script found: {api_path}")
    return True

def is_port_available(port):
    """Check if port is available."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    
    if result == 0:
        logger.warning(f"[WARN] Port {port} is already in use (API might already be running)")
        return False
    
    logger.info(f"[OK] Port {port} is available")
    return True

def start_api_server():
    """Start FastAPI server on port 8001."""
    global API_PROCESS
    
    logger.info("\n" + "=" * 80)
    logger.info("STARTING QUANTUM API SERVER (Port 8001)")
    logger.info("=" * 80)
    
    try:
        cmd = [
            str(VENV_PYTHON),
            "-m", "uvicorn",
            "src.quantum_main:app",
            "--host", "0.0.0.0",
            "--port", str(QUANTUM_API_PORT),
            "--reload"
        ]
        
        logger.info(f"Command: {' '.join(cmd)}")
        API_PROCESS = subprocess.Popen(
            cmd,
            cwd=WORKSPACE_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        logger.info(f"[OK] API process started (PID: {API_PROCESS.pid})")
        
        # Wait for server to be ready
        logger.info("Waiting for server to start...")
        time.sleep(3)
        
        # Check health
        for attempt in range(10):
            try:
                import urllib.request
                response = urllib.request.urlopen('http://localhost:8001/health', timeout=5)
                if response.status == 200:
                    logger.info("[OK] API server is responding to health checks")
                    return True
            except Exception:
                if attempt < 9:
                    logger.info(f"  Attempt {attempt+1}/10: Waiting for server...")
                    time.sleep(1)
                else:
                    logger.warning("Server started but health check failed (may still be initializing)")
                    return True
        
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] Error starting API server: {e}")
        return False

def start_cloudflare_tunnel():
    """Start Cloudflare Tunnel for port 8001."""
    global TUNNEL_PROCESS
    
    logger.info("\n" + "=" * 80)
    logger.info("STARTING CLOUDFLARE TUNNEL (Port 8001 → HTTPS)")
    logger.info("=" * 80)
    
    try:
        cmd = [
            str(CLOUDFLARED_PATH),
            "tunnel",
            "run",
            "--url", f"http://localhost:{QUANTUM_API_PORT}"
        ]
        
        logger.info(f"Command: {' '.join(cmd)}")
        TUNNEL_PROCESS = subprocess.Popen(
            cmd,
            cwd=WORKSPACE_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        logger.info(f"[OK] Tunnel process started (PID: {TUNNEL_PROCESS.pid})")
        logger.info("Tunnel creating (usually 3-5 seconds)...")
        
        # Wait for tunnel URL in logs
        time.sleep(5)
        
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] Error starting tunnel: {e}")
        return False

def monitor_processes():
    """Monitor API and tunnel processes."""
    logger.info("\n" + "=" * 80)
    logger.info("MONITORING PROCESSES")
    logger.info("=" * 80)
    logger.info("\nURLs:")
    logger.info(f"  Local:  http://localhost:{QUANTUM_API_PORT}")
    logger.info(f"  Public: Check cloudflared output above")
    logger.info("\nEndpoints:")
    logger.info(f"  /health              - Health check")
    logger.info(f"  /predict             - Make quantum prediction (POST)")
    logger.info(f"  /quantum-metrics     - Model metrics")
    logger.info(f"  /docs                - Swagger UI")
    logger.info("\nPress Ctrl+C to stop deployment\n")
    logger.info("=" * 80 + "\n")
    
    try:
        while True:
            # Check API process
            if API_PROCESS and API_PROCESS.poll() is not None:
                logger.error("[FAIL] API server crashed")
                return False
            
            # Check tunnel process
            if TUNNEL_PROCESS and TUNNEL_PROCESS.poll() is not None:
                logger.error("[FAIL] Cloudflare Tunnel crashed")
                return False
            
            # Read any available output (non-blocking)
            if API_PROCESS and API_PROCESS.stdout:
                try:
                    line = API_PROCESS.stdout.readline()
                    if line:
                        logger.info(f"[API] {line.strip()}")
                except:
                    pass
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("\n\nShutdown signal received (Ctrl+C)")
        return None

def shutdown_processes():
    """Gracefully shutdown all processes."""
    logger.info("\n" + "=" * 80)
    logger.info("SHUTTING DOWN DEPLOYMENT")
    logger.info("=" * 80)
    
    # Terminate tunnel first
    if TUNNEL_PROCESS:
        try:
            logger.info("Terminating Cloudflare Tunnel...")
            TUNNEL_PROCESS.terminate()
            TUNNEL_PROCESS.wait(timeout=5)
            logger.info("[OK] Tunnel stopped")
        except Exception as e:
            logger.warning(f"Error stopping tunnel: {e}")
            try:
                TUNNEL_PROCESS.kill()
            except:
                pass
    
    # Terminate API
    if API_PROCESS:
        try:
            logger.info("Terminating API server...")
            API_PROCESS.terminate()
            API_PROCESS.wait(timeout=5)
            logger.info("[OK] API stopped")
        except Exception as e:
            logger.warning(f"Error stopping API: {e}")
            try:
                API_PROCESS.kill()
            except:
                pass
    
    logger.info("=" * 80)
    logger.info("Deployment shutdown complete")
    logger.info("=" * 80)

def signal_handler(sig, frame):
    """Handle Ctrl+C signal."""
    shutdown_processes()
    sys.exit(0)

# ============================================================================
# MAIN DEPLOYMENT
# ============================================================================

def main():
    """Main deployment orchestrator."""
    logger.info("\n" + "=" * 80)
    logger.info("QUANTUM API DEPLOYMENT - AUTOMATED")
    logger.info("=" * 80 + "\n")
    
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Pre-flight checks
    logger.info("PRE-FLIGHT CHECKS:")
    logger.info("-" * 80)
    
    checks = [
        ("Python environment", check_python_env()),
        ("Cloudflared binary", check_cloudflared()),
        ("API script", check_api_script()),
        ("Port 8001 available", is_port_available(QUANTUM_API_PORT))
    ]
    
    failed = [name for name, result in checks if not result]
    if failed:
        logger.error(f"\n[FAIL] Pre-flight checks failed: {', '.join(failed)}")
        return False
    
    logger.info("[OK] All pre-flight checks passed\n")
    
    # Start services
    if not start_api_server():
        logger.error("Failed to start API server")
        return False
    
    if not start_cloudflare_tunnel():
        logger.error("Failed to start Cloudflare Tunnel")
        shutdown_processes()
        return False
    
    # Monitor
    result = monitor_processes()
    
    if result is False:
        logger.error("\nDeployment encountered an error")
        shutdown_processes()
        return False
    else:
        shutdown_processes()
        return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success is not False else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        shutdown_processes()
        sys.exit(1)
