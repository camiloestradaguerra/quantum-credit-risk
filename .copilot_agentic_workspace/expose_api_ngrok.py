"""
Expose Credit Risk API publicly using ngrok
"""

from pyngrok import ngrok
import time
import os

# Configure ngrok
# Note: You can set your ngrok auth token here if you have one
# ngrok.set_auth_token("YOUR_NGROK_TOKEN")

print("=" * 70)
print("🌐 EXPOSING CREDIT RISK API PUBLICLY WITH NGROK")
print("=" * 70)

try:
    # Start ngrok tunnel on port 8000
    print("\n📡 Starting ngrok tunnel on localhost:8000...")
    public_url = ngrok.connect(8000, "http")
    
    print(f"\n✅ SUCCESS! API is now publicly accessible:")
    print(f"\n🔗 Public URL: {public_url}")
    print(f"\n📚 API Documentation: {public_url}/docs")
    print(f"🏥 Health Check: {public_url}/health")
    print(f"🔮 Predictions: {public_url}/predict")
    
    print("\n" + "=" * 70)
    print("📋 EXAMPLE CURL COMMAND:")
    print("=" * 70)
    print(f"""
curl -X POST {public_url}/predict \\
  -H "Content-Type: application/json" \\
  -d '{{"raw_features": [45, 55000, 2, 15000, 8.5, 0.25, 0, 10]}}'
    """)
    
    print("\n" + "=" * 70)
    print("🐍 EXAMPLE PYTHON CODE:")
    print("=" * 70)
    print(f"""
import requests

response = requests.post(
    '{public_url}/predict',
    json={{"raw_features": [45, 55000, 2, 15000, 8.5, 0.25, 0, 10]}}
)
print(response.json())
    """)
    
    print("\n" + "=" * 70)
    print("ℹ️  IMPORTANT:")
    print("=" * 70)
    print("""
• This ngrok URL will expire when this script stops
• ngrok URLs are randomized each time (unless you use a paid plan)
• For production, consider using:
  - Cloud deployment (AWS, Azure, GCP)
  - Docker containerization
  - Dedicated API hosting service
  
• Share this URL with others to let them test your API
• Press CTRL+C to stop the tunnel
    """)
    
    print("\n🔄 Tunnel is running... Press CTRL+C to exit\n")
    
    # Keep the tunnel open
    while True:
        time.sleep(1)

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure FastAPI server is running on port 8000")
    print("2. Check: http://localhost:8000/health")
    print("3. If needed, get your ngrok auth token from: https://dashboard.ngrok.com")
    print("4. Then set it with: ngrok.set_auth_token('YOUR_TOKEN')")

finally:
    print("\n🛑 Shutting down ngrok tunnel...")
    ngrok.kill()
