#!/usr/bin/env python3
"""
Expose API with Cloudflare Tunnel (cloudflared)
Most reliable free option - no auth needed, no SSH keys
"""

import subprocess
import sys
import platform

def check_cloudflared_installed():
    """Check if cloudflared is installed"""
    try:
        result = subprocess.run(
            ["cloudflared", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def install_cloudflared():
    """Download and install cloudflared"""
    print("📥 Downloading cloudflared...")
    
    if platform.system() == "Windows":
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        dest = "cloudflared.exe"
    elif platform.system() == "Darwin":
        print("❌ macOS: Please install via: brew install cloudflare/cloudflare/cloudflared")
        return False
    else:
        print("❌ Linux: Please install via: sudo apt install cloudflared")
        return False
    
    try:
        subprocess.run(
            ["powershell", "-Command", f'Invoke-WebRequest -Uri "{url}" -OutFile "{dest}" -UseBasicParsing'],
            check=True,
            timeout=60
        )
        print(f"✅ cloudflared downloaded to {dest}")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def expose_with_cloudflare():
    """Use Cloudflare Tunnel"""
    print("=" * 80)
    print("🌐 CREDIT RISK API - PUBLIC TUNNEL (Cloudflare)")
    print("=" * 80)
    print("\n📡 Exposing port 8000 via Cloudflare Tunnel...")
    print("(This uses cloudflared - completely free, no auth needed)\n")
    
    if not check_cloudflared_installed():
        print("⚠️  cloudflared not found. Installing...")
        if not install_cloudflared():
            print("\n❌ Could not install cloudflared automatically")
            print("\n📥 Manual installation:")
            print("   Windows: Download from https://github.com/cloudflare/cloudflared/releases")
            print("   Then extract cloudflared.exe and run: .\\cloudflared.exe tunnel --url http://localhost:8000")
            return False
    
    try:
        cmd = ["cloudflared", "tunnel", "--url", "http://localhost:8000", "--no-autoupdate"]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        print("⏳ Waiting for tunnel to establish...\n")
        
        # Read output and look for the public URL
        for line in process.stdout:
            print(line.rstrip())
            
            # Look for the tunnel URL
            if "your url is" in line.lower() or "https://" in line:
                # Try to extract URL
                if "https://" in line:
                    parts = line.split()
                    for part in parts:
                        if "https://" in part and ".trycloudflare.com" in part:
                            public_url = part.strip()
                            print_success_info(public_url)
        
        process.wait()
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Closing tunnel...")
        process.terminate()
        print("✅ Tunnel closed")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def print_success_info(url):
    """Print success message with URL"""
    print("\n" + "=" * 80)
    print("✅ SUCCESS! API is now PUBLIC!")
    print("=" * 80)
    print(f"\n🔗 PUBLIC URL: {url}")
    print(f"\n📍 Access your API at:")
    print(f"   • Swagger UI:    {url}/docs")
    print(f"   • Health Check:  {url}/health")
    print(f"   • Predictions:   {url}/predict")
    print(f"\n📋 Test with cURL:")
    print(f"""
curl -X POST {url}/predict \\
  -H "Content-Type: application/json" \\
  -d '{{"raw_features": [45, 55000, 2, 15000, 8.5, 0.25, 0, 10]}}'
""")
    print("=" * 80)
    print("💡 Press CTRL+C to stop the tunnel")
    print("=" * 80)

if __name__ == "__main__":
    expose_with_cloudflare()
