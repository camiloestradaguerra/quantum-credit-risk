#!/usr/bin/env python3
"""
ngrok tunnel for FastAPI server
Exposes local port 8000 to public internet
"""

import time
from pyngrok import ngrok
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Start ngrok tunnel
logger.info("🚀 Starting ngrok tunnel...")
try:
    public_url = ngrok.connect(8000)
    logger.info(f"✅ ngrok tunnel active!")
    logger.info(f"🌐 Public URL: {public_url}")
    logger.info(f"\n📍 Your API is accessible at: {public_url}")
    logger.info(f"📘 API Documentation: {public_url}/docs")
    logger.info(f"🔍 Health check: {public_url}/health")
    logger.info("\n💡 Press Ctrl+C to stop")
    
    # Keep tunnel alive
    ngrok_process = ngrok.get_ngrok_process()
    ngrok_process.proc.wait()
    
except KeyboardInterrupt:
    logger.info("\n⏹️  Stopping ngrok tunnel...")
    ngrok.kill()
    logger.info("✅ Tunnel closed")
except Exception as e:
    logger.error(f"❌ Error: {e}")
    ngrok.kill()
