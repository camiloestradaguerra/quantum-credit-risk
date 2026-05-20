# 🚀 QUANTUM API - QUICK START

**Status:** Pipeline en ejecución (~7 horas)  
**Expected Completion:** ~16:10 UTC (Mayo 20, 2026)

---

## ⏱️ MIENTRAS CORRE EL PIPELINE

El script `2_quantum_ml_pipeline_OPTIMIZED.py` está guardando:
- ✓ `qsvm_model.pkl` - Modelo QSVM entrenado
- ✓ `qsvm_K_train.pkl` - Matriz de kernel de entrenamiento  
- ✓ `qsvm_X_train_kernel.npy` - Muestras de entrenamiento
- ✓ `qsvm_scaler.pkl` - Normalizador de features

---

## 🎯 CUANDO TERMINE (en ~7 horas)

### PASO 1: Verificar que los archivos existen
```powershell
ls c:\Users\CAMILO\Documents\modo-bestia-vscode\.copilot_agentic_workspace\models\qsvm*.pkl
```

Deberías ver 3 archivos:
- qsvm_model.pkl ✓
- qsvm_K_train.pkl ✓  
- qsvm_scaler.pkl ✓

### PASO 2: Terminal 1 - Ejecutar API Clásica (si no corre)
```powershell
cd c:\Users\CAMILO\Documents\modo-bestia-vscode\.copilot_agentic_workspace
python deploy.py
```

**Espera la salida:**
```
[OK] API server is responding to health checks
[OK] Tunnel process started
URLs:
  Local:  http://localhost:8000
  Public: https://...trycloudflare.com
```

### PASO 3: Terminal 2 - Ejecutar API Cuántica (NUEVA)
```powershell
cd c:\Users\CAMILO\Documents\modo-bestia-vscode\.copilot_agentic_workspace
python deploy_quantum.py
```

**Espera la salida:**
```
[OK] API server is responding to health checks
[OK] Tunnel process started
URLs:
  Local:  http://localhost:8001
  Public: https://...trycloudflare.com
```

### PASO 4: Terminal 3 - Ejecutar Tests
```powershell
cd c:\Users\CAMILO\Documents\modo-bestia-vscode\.copilot_agentic_workspace
python test_both_apis.py
```

**Verás:**
- ✓ Test Case 1: Low Risk Profile
- ✓ Test Case 2: Medium Risk Profile  
- ✓ Test Case 3: High Risk Profile
- Predicciones de ambas APIs
- Comparación de resultados

---

## 📊 EJEMPLO DE SALIDA (ESPERADA)

```
TEST CASE 1: Low Risk Profile
---
Input Features:
  age........................... 35
  income....................... 50000
  loan_amount.................. 10000
  interest_rate.................. 8.5
  ...

[Classical API - XGBoost (Fast)]
  Prediction:    0 (Non-Default)
  Probability:   0.1500
  Risk Score:    0.2500
  Risk Category: LOW_RISK
  Model:         XGBoost (Classical)

[Quantum API - QSVM (Kernel Computation)]
  Prediction:    0 (Non-Default)
  Probability:   0.3500
  Risk Score:    0.4500
  Risk Category: LOW_RISK
  Response time: 45.32s

[COMPARISON]
  Predictions agree: YES
  Classical risk: LOW_RISK
  Quantum risk:   LOW_RISK
```

---

## ⚡ FAST VERIFICATION

Si no quieres esperar a los tests completos:

### Health Checks (30 segundos)
```bash
# Classical API
curl http://localhost:8000/health

# Quantum API
curl http://localhost:8001/health
```

### Simple Prediction (Classical - instant)
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age":35,"income":50000,"loan_amount":10000,"interest_rate":8.5,"employment_length":5,"credit_history":10,"default_on_file":0,"loan_percent_income":0.20}'
```

### Simple Prediction (Quantum - 30-60 segundos)
```bash
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"age":35,"income":50000,"loan_amount":10000,"interest_rate":8.5,"employment_length":5,"credit_history":10,"default_on_file":0,"loan_percent_income":0.20}'
```

---

## 🔗 URLS PÚBLICAS (Cuando corran)

### Classical API
- Local: http://localhost:8000
- Public: https://encouraged-colleges-benjamin-magnitude.trycloudflare.com

### Quantum API  
- Local: http://localhost:8001
- Public: https://[NEW-URL].trycloudflare.com (generado en deploy)

---

## 📝 NOTAS

- **Classical es RÁPIDO**: ~10ms por predicción
- **Quantum es LENTO**: ~30-60s por predicción (kernel computation)
- **Ambas usan los MISMOS 8 features** (entrada)
- **Pero generan DIFERENTES resultados** (modelos diferentes)
- **Ambas son INDEPENDIENTES**: puedes parar una sin afectar la otra

---

## ❌ SI ALGO FALLA

### "Models not found" (Quantum API)
```
El pipeline no terminó. Revisa:
  cd c:\Users\CAMILO\Documents\modo-bestia-vscode\.copilot_agentic_workspace
  tail -f logs/quantum_ml_pipeline_optimized.log
```

### "Port 8000/8001 already in use"
```powershell
# Kill existing process
Get-Process python | Stop-Process -Force

# Or specific port
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

### API not responding
```bash
# Check local first
curl http://localhost:8001/health

# If that fails, check logs
cat logs/quantum_api.log
```

---

**Pipeline Status:** ⏳ En progreso (puede dejar corriendo)  
**Next Action:** Revisar este archivo cuando el pipeline termine
