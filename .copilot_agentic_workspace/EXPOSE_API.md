# 🌐 Expose Your API Publicly

Your Credit Risk Prediction API is running on `http://localhost:8000`. Here are the best ways to expose it publicly:

---

## Option 1: **localhost.run** (Easiest ✅)

**Requirements:** SSH (usually pre-installed on Windows 10+)

**Command:**
```bash
ssh -R 80:localhost:8000 ssh.localhost.run
```

**Output will be:**
```
Connected to localhost.run
Your URL is: https://abcd1234.lhrtunnel.link
```

**Access your API:**
- **Swagger UI:** `https://abcd1234.lhrtunnel.link/docs`
- **Predictions:** `https://abcd1234.lhrtunnel.link/predict`
- **Health Check:** `https://abcd1234.lhrtunnel.link/health`

**Example cURL:**
```bash
curl -X POST https://abcd1234.lhrtunnel.link/predict \
  -H "Content-Type: application/json" \
  -d '{"raw_features": [45, 55000, 2, 15000, 8.5, 0.25, 0, 10]}'
```

**Pros:** No installation, no account, instant
**Cons:** URL changes each time, limited concurrency

---

## Option 2: **ngrok** (Most Popular)

### 2a. Install ngrok Standalone (No Python needed)

1. Download from: https://ngrok.com/download
2. Extract to a folder
3. Run:
   ```bash
   ngrok http 8000
   ```

### 2b. Install via Scoop (Windows Package Manager)
```powershell
scoop install ngrok
ngrok http 8000
```

### 2c. Use with Python (pyngrok)
Already installed! Create `.ngrok-token` in your workspace root with your token, then run:
```bash
cd .copilot_agentic_workspace
python expose_api_ngrok.py
```

**Output will be:**
```
Session Status    online
Version           3.0.0
Web Interface     http://127.0.0.1:4040
Forwarding        https://12ab-34cd-5efg.ngrok.io -> http://localhost:8000
```

**Access your API:**
- **Swagger UI:** `https://12ab-34cd-5efg.ngrok.io/docs`
- **Predictions:** `https://12ab-34cd-5efg.ngrok.io/predict`

**Pros:** Stable, good infrastructure, beautiful UI
**Cons:** Requires account for longer tunnels

---

## Option 3: **CloudFlare Tunnel** (Most Secure)

1. Install Cloudflare CLI:
   ```bash
   scoop install cloudflare-wrangler
   # OR download from https://github.com/cloudflare/wrangler2
   ```

2. Run:
   ```bash
   cloudflared tunnel --url http://localhost:8000
   ```

**Pros:** Enterprise-grade security, free tier generous
**Cons:** Requires Cloudflare account

---

## Option 4: **Cloud Deployment** (Production ⭐)

For production use, deploy to:

### **Railway.app** (Recommended for Python)
```bash
npm install -g railway
railway init
railway deploy
```

### **Render** (Free tier available)
1. Connect GitHub: https://render.com
2. Create Web Service
3. Deploy from your repo

### **Azure Web App**
```bash
az webapp up --name quantum-credit-risk --location eastus
```

### **Heroku** (Legacy but still works)
```bash
heroku login
heroku create quantum-credit-risk
git push heroku main
```

---

## 📝 Quick Reference

| Method | Complexity | Setup Time | Cost | Max Users |
|--------|-----------|-----------|------|-----------|
| localhost.run | Easy | 1 min | Free | Low |
| ngrok free | Easy | 5 min | Free | Low |
| ngrok pro | Medium | 5 min | $5/mo | High |
| CloudFlare Tunnel | Medium | 10 min | Free | Medium |
| Railway | Medium | 15 min | Free* | High |
| Render | Medium | 15 min | Free* | High |
| Azure | Hard | 20 min | $$ | High |

*Free tier with limitations

---

## 🔗 Current Status

✅ **Local API:** http://localhost:8000
✅ **Swagger UI:** http://localhost:8000/docs
✅ **FastAPI Server:** Running on port 8000
✅ **Ready to expose!**

Pick your method above and start sharing your API! 🚀
