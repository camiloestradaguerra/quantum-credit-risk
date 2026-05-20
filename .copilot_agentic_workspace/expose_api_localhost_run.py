"""
Expose Credit Risk API publicly using localhost.run (SSH tunneling)
This is the simplest alternative - no installation needed!
"""

import subprocess
import time
import sys

print("=" * 70)
print("🌐 EXPOSING CREDIT RISK API PUBLICLY WITH LOCALHOST.RUN")
print("=" * 70)

print("""
This uses SSH tunneling - no installation required!

localhost.run provides a simple way to expose localhost to the internet:
- No account needed
- URLs are predictable
- Perfect for quick sharing and testing
""")

print("\n" + "=" * 70)
print("📋 COMMAND TO RUN:")
print("=" * 70)

cmd = "ssh -R 80:localhost:8000 ssh.localhost.run"

print(f"\nRun this command in PowerShell or Terminal:")
print(f"\n  {cmd}")

print("""

This will output something like:
    Connected to localhost.run
    Your URL is: https://something.lhrtunnel.link

Then you can access your API publicly:
    https://something.lhrtunnel.link/docs
    https://something.lhrtunnel.link/predict

CURL Example:
    curl -X POST https://something.lhrtunnel.link/predict \\
      -H "Content-Type: application/json" \\
      -d '{"raw_features": [45, 55000, 2, 15000, 8.5, 0.25, 0, 10]}'

Press CTRL+C to stop
""")

print("=" * 70)
print("\nAttempting to establish SSH tunnel...")
print("=" * 70)

try:
    # Try to run the SSH command
    subprocess.run(cmd, shell=True, check=False)
except KeyboardInterrupt:
    print("\n\n🛑 Tunnel stopped by user")
    sys.exit(0)
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n📌 If SSH is not available, use this Python alternative:")
    print("   pip install flask-cors")
    print("   Or deploy to a cloud service like Heroku, Railway, or Render")
