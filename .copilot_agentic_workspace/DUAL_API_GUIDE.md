# DUAL API DEPLOYMENT - Classical + Quantum
## Quantum Credit Risk Analysis

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     Your Application                        │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
    ┌──────────────────┐          ┌──────────────────┐
    │ Classical API    │          │  Quantum API     │
    │ (XGBoost)        │          │  (QSVM)          │
    │                  │          │                  │
    │ Port: 8000       │          │ Port: 8001       │
    │ URL: https://... │          │ URL: https://... │
    └────────┬─────────┘          └────────┬─────────┘
             │                             │
             ▼                             ▼
    ┌──────────────────┐          ┌──────────────────┐
    │  Cloudflare      │          │  Cloudflare      │
    │  Tunnel #1       │          │  Tunnel #2       │
    │                  │          │                  │
    │ INDEPENDENT URLs │          │ INDEPENDENT URLs │
    └──────────────────┘          └──────────────────┘
```

---

## QUICK START - TWO DEPLOYMENTS

### Step 1: Run Quantum Pipeline (First Time Only)
```powershell
cd c:\Users\CAMILO\Documents\modo-bestia-vscode\.copilot_agentic_workspace

# Activate venv
.\venv_quantum_ml\Scripts\Activate.ps1

# Run quantum pipeline (FIRST TIME)
python scripts/2_quantum_ml_pipeline_OPTIMIZED.py

# This generates:
#  - models/qsvm_model.pkl
#  - models/qsvm_K_train.pkl
#  - models/qsvm_X_train_kernel.npy
#  - models/qsvm_scaler.pkl
#  - models/quantum_metrics_optimized.json
```

**Expected time: ~7 hours for 100 samples**  
**Expected output: Test AUC-ROC ~0.53, F1 ~0.001**

---

### Step 2: Deploy BOTH APIs (Separate Terminals)

#### Terminal 1: Classical API (Port 8000)
```powershell
cd c:\Users\CAMILO\Documents\modo-bestia-vscode\.copilot_agentic_workspace
python deploy.py
```
**Output:**
```
[OK] API server is responding to health checks
[OK] Tunnel process started
Press Ctrl+C to stop deployment

URLs:
  Local:  http://localhost:8000
  Public: https://classical-url.trycloudflare.com
```

#### Terminal 2: Quantum API (Port 8001)
```powershell
cd c:\Users\CAMILO\Documents\modo-bestia-vscode\.copilot_agentic_workspace
python deploy_quantum.py
```
**Output:**
```
[OK] API server is responding to health checks
[OK] Tunnel process started
Press Ctrl+C to stop deployment

URLs:
  Local:  http://localhost:8001
  Public: https://quantum-url.trycloudflare.com
```

---

## USAGE - MAKE PREDICTIONS

### Classical API (XGBoost)
```bash
# Health check
curl http://localhost:8000/health

# Prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "income": 50000,
    "loan_amount": 10000,
    "interest_rate": 8.5,
    "employment_length": 5,
    "credit_history": 10,
    "default_on_file": 0,
    "loan_percent_income": 0.20
  }'

# Swagger UI
http://localhost:8000/docs
```

**Response:**
```json
{
  "prediction": 0,
  "probability": 0.15,
  "risk_score": 0.25,
  "risk_category": "LOW_RISK",
  "model": "XGBoost (Classical)",
  "timestamp": "2026-05-20T15:30:00.000Z"
}
```

---

### Quantum API (QSVM)
```bash
# Health check
curl http://localhost:8001/health

# Prediction (SAME 8 FEATURES)
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "income": 50000,
    "loan_amount": 10000,
    "interest_rate": 8.5,
    "employment_length": 5,
    "credit_history": 10,
    "default_on_file": 0,
    "loan_percent_income": 0.20
  }'

# Model metrics
curl http://localhost:8001/quantum-metrics

# Swagger UI
http://localhost:8001/docs
```

**Response:**
```json
{
  "prediction": 0,
  "probability": 0.35,
  "risk_score": 0.45,
  "risk_category": "LOW_RISK",
  "model": "QSVM (Quantum SVM)",
  "timestamp": "2026-05-20T15:30:00.000Z"
}
```

---

## ENDPOINTS COMPARISON

| Endpoint | Classical | Quantum | Purpose |
|----------|-----------|---------|---------|
| `/health` | ✓ | ✓ | Health check |
| `/predict` | ✓ | ✓ | Make prediction (POST with 8 features) |
| `/docs` | ✓ | ✓ | Swagger UI |
| `/metrics` | ✓ | ✓ | Model metrics |
| `/quantum-metrics` | ✗ | ✓ | Quantum-specific metrics |

---

## COMPARISON: Classical vs Quantum

### Classical (XGBoost) - Port 8000
- **Speed**: ~10ms per prediction
- **Accuracy**: AUC-ROC 0.8983
- **Model**: XGBoost (200 estimators)
- **Training samples**: 34,642 (all)
- **Features**: 18 engineered features

### Quantum (QSVM) - Port 8001
- **Speed**: ~30-60s per prediction (kernel computation)
- **Accuracy**: AUC-ROC 0.5319 (100 samples)
- **Model**: QSVM with FidelityQuantumKernel
- **Training samples**: 100 (downsampled)
- **Features**: 8 quantum features (normalized to [0, 2π])

---

## PUBLIC ACCESS

### Classical API
```
Public URL: https://encouraged-colleges-benjamin-magnitude.trycloudflare.com
```

### Quantum API
```
Public URL: https://[QUANTUM-TUNNEL-URL] (generated on first run)
```

Both URLs are HTTPS-secured and publicly accessible 24/7 while deployment is running.

---

## TROUBLESHOOTING

### "Port 8000/8001 already in use"
```powershell
# Find process using port
netstat -ano | findstr :8000
netstat -ano | findstr :8001

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### "Models not found" (Quantum API)
```powershell
# Run quantum pipeline first
python scripts/2_quantum_ml_pipeline_OPTIMIZED.py

# Wait for completion (~7 hours)
```

### "Cloudflared tunnel not starting"
```powershell
# Check if cloudflared.exe exists
Test-Path .\cloudflared.exe

# Download if missing:
# https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
```

### Tunnel URL not showing
```powershell
# Give it 3-5 seconds to initialize
# Check cloudflared.exe output for "Tunnel created" message
```

---

## NEXT STEPS - Improve Quantum Model

### Expected Improvement (v4.0)
- **Current**: 100 samples, AUC 0.5319
- **Target**: 200 samples + stratified sampling, AUC 0.78-0.82
- **Time**: ~13 hours

Run after verifying both APIs work:
```powershell
python scripts/2_quantum_ml_pipeline_v4.py
```

---

## KEEP BOTH RUNNING

**Important**: Keep both Terminal 1 and Terminal 2 running to maintain:
- ✓ Classical API on http://localhost:8000
- ✓ Quantum API on http://localhost:8001
- ✓ Public access via Cloudflare Tunnels

If either terminal stops, that API becomes unavailable.

---

## STOP DEPLOYMENT

Press `Ctrl+C` in either terminal to stop that specific deployment.
Both are independent, so stopping one doesn't affect the other.
