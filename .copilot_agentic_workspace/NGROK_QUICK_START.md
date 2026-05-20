# 🌐 NGROK - FREE & EASY!

## Quick Start (2 pasos)

### Step 1: Download ngrok
- Go to: https://ngrok.com/download
- Download Windows version
- Extract the .zip file
- You get: `ngrok.exe`

### Step 2: Run ngrok
In PowerShell:

```powershell
# Navigate to where you extracted ngrok
cd "C:\path\to\ngrok"

# Start tunnel on port 8000
.\ngrok.exe http 8000
```

That's it! 🎉

---

## What You'll See

```
ngrok                                                  (Ctrl+C to quit)

Session Status                online
Account                       [Your Account]
Version                       3.7.0
Region                        us (United States)
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123-def456.ngrok-free.app -> http://localhost:8000

Connections                   ttl    opn    rt1    rt5    p50    p95
                              0      0      0.00   0.00   0.00   0.00
```

---

## Use Your Public URL

**Your API is now public at:**
```
https://abc123-def456.ngrok-free.app
```

### Access:
- **Swagger UI:** https://abc123-def456.ngrok-free.app/docs
- **Predictions:** https://abc123-def456.ngrok-free.app/predict
- **Health Check:** https://abc123-def456.ngrok-free.app/health

### Test with cURL:
```bash
curl -X POST https://abc123-def456.ngrok-free.app/predict \
  -H "Content-Type: application/json" \
  -d '{"raw_features": [45, 55000, 2, 15000, 8.5, 0.25, 0, 10]}'
```

### Test with Python:
```python
import requests

response = requests.post(
    'https://abc123-def456.ngrok-free.app/predict',
    json={'raw_features': [45, 55000, 2, 15000, 8.5, 0.25, 0, 10]}
)
print(response.json())
```

---

## ℹ️ Important Notes

✅ **FREE:** No credit card needed!  
✅ **URL changes** each time you restart ngrok  
✅ **Web Interface:** Visit http://127.0.0.1:4040 to see all requests  
⏱️ **Limits:** Free tier has some limits but perfect for testing  

---

## Pro Tips

### 1. Keep the URL stable (if you get ngrok account):
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
ngrok http 8000
```

### 2. See all requests:
Open: http://127.0.0.1:4040
Live request/response inspection! 🔍

### 3. Share your API:
Just copy the ngrok URL and send it to anyone:
```
https://abc123-def456.ngrok-free.app/docs
```

---

## Install ngrok Properly (Alternative)

If download doesn't work, try:

**Option A: Using Windows Package Manager** (if you have it)
```powershell
winget install ngrok.ngrok
```

**Option B: Manual Setup**
1. Download from: https://ngrok.com/download
2. Extract to: `C:\ngrok` (create folder)
3. Add to PATH:
   - Right-click "This PC" → Properties
   - Advanced system settings
   - Environment Variables
   - PATH → Edit → Add `C:\ngrok`
4. Restart PowerShell
5. Now you can run `ngrok http 8000` from anywhere

---

## Troubleshooting

**Error: "ngrok: The term 'ngrok' is not recognized"**
- Make sure ngrok.exe is in your PATH
- Restart PowerShell after adding to PATH

**Want a permanent/custom URL?**
- Sign up for ngrok account
- Get auth token
- Use: `ngrok config add-authtoken TOKEN`

---

That's it! **ngrok is perfect for quick testing and demos** 🚀
