# 🌐 Expose Your API Publicly

Your Credit Risk Prediction API is running on `http://localhost:8000`. Here are the **EASIEST** ways to expose it publicly:

---

## 🥇 **Option 1: Railway.app** (Recommended - Easiest! ✅)

**Why:** One-click deployment from GitHub, free tier generous, automatic CI/CD

**Steps:**
1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub"**
4. Connect your GitHub account
5. Select **`quantum-credit-risk`** repository
6. Railway auto-detects Python + FastAPI
7. **DONE!** Your API is live in 2 minutes

**You get:**
- Live URL: `https://your-project.railway.app`
- Swagger UI: `https://your-project.railway.app/docs`
- Automatic HTTPS
- $5/month free credits (plenty for testing)

**No code changes needed!** Just click and deploy.

---

## 🥈 **Option 2: Render** (Also Easy ✅)

**Why:** Free tier, Swagger UI works perfectly, simple interface

**Steps:**
1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repo
4. Railway auto-fills settings
5. Click **"Create Web Service"**
6. Wait 2 minutes...
7. **DONE!**

**You get:**
- Live URL: `https://quantum-credit-risk.onrender.com`
- Free tier: 0.5GB RAM, auto-sleep after 15 min inactivity
- Upgrade anytime if needed

---

## 🥉 **Option 3: Azure Web App** (If you have Azure account)

```bash
az webapp up --name quantum-credit-risk --location eastus
```

---

## 📊 Comparison

| Platform | Setup Time | Difficulty | Cost | Notes |
|----------|-----------|-----------|------|-------|
| **Railway** | 2 min | Super Easy | Free* | ✅ RECOMMENDED |
| **Render** | 3 min | Super Easy | Free* | Also great |
| **Azure** | 5 min | Easy | $$ | If already using Azure |
| **Heroku** | 5 min | Easy | $$ | Classic option |

*Free tier with limits (enough for testing)

---

## ⚡ Quick Start: Railway (Recommended)

### Step 1: Push to GitHub (Already Done ✅)
Your repo is at: https://github.com/camiloestradaguerra/quantum-credit-risk

### Step 2: Go to Railway
```
https://railway.app
```

### Step 3: Connect & Deploy
1. Click **"New Project"**
2. Select **"Deploy from GitHub"**
3. Choose **quantum-credit-risk**
4. Railway auto-detects everything
5. Click **"Deploy"**
6. Wait ~2 minutes
7. **Done!** 🎉

### Step 4: Test Your Live API
```bash
# Get your Railway URL from dashboard, then:
curl -X POST https://YOUR-RAILWAY-URL.railway.app/predict \
  -H "Content-Type: application/json" \
  -d '{"raw_features": [45, 55000, 2, 15000, 8.5, 0.25, 0, 10]}'
```

---

## 🔗 Current Status

✅ **Local API:** http://localhost:8000  
✅ **Swagger UI:** http://localhost:8000/docs  
✅ **FastAPI Server:** Running on port 8000  
✅ **GitHub Repo:** Public, ready to deploy  
✅ **Ready for public exposure!**

---

## 🎯 Next Steps

1. **Choose a platform** (Railway recommended)
2. **Click deploy**
3. **Share your public URL**
4. **Anyone can use it!**

Your API includes:
- ✅ 8-feature simplified input
- ✅ Auto feature engineering  
- ✅ Complete Swagger documentation
- ✅ Financial impact calculations
- ✅ Model performance metrics

Go to **Railway.app** and deploy in 2 minutes! 🚀
