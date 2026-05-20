# 🚀 DEPLOY GUIDE - Credit Risk Quantum ML API

**ESTADO ACTUAL**: Listo para producción  
**FECHA**: May 20, 2026  
**URL PÚBLICA**: https://encouraged-colleges-benjamin-magnitude.trycloudflare.com

---

## 📋 ARQUITECTURA DE DEPLOY

```
┌─────────────────────────────────────────────────────────┐
│        LOCAL: FastAPI (puerto 8000)                      │
│        ├─ src/main.py (API REST)                        │
│        ├─ models/xgb_classical.pkl (modelo)            │
│        └─ scripts/2_quantum_ml_pipeline_OPTIMIZED.py   │
├─────────────────────────────────────────────────────────┤
│        CLOUDFLARE TUNNEL (cloudflared)                   │
│        └─ Expone localhost:8000 → HTTPS público        │
├─────────────────────────────────────────────────────────┤
│        INTERNET PÚBLICO (HTTPS)                          │
│        └─ https://encouraged-colleges-benjamin-\        │
│           magnitude.trycloudflare.com                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 PASOS DE DEPLOY

### PASO 1: Verificar Dependencias

```bash
# En el workspace
python -m venv venv_quantum_ml
.\venv_quantum_ml\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### PASO 2: Iniciar API Local (Terminal 1)

```bash
cd c:\Users\CAMILO\Documents\modo-bestia-vscode\.copilot_agentic_workspace

# Activar venv
.\venv_quantum_ml\Scripts\activate

# Iniciar servidor
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Esperado:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### PASO 3: Verificar API Local (Terminal 2)

```bash
# Test de salud
curl http://localhost:8000/health

# Response:
# {
#   "status": "OK",
#   "model": "XGBoost Credit Risk Classifier",
#   "auc_roc": 0.8983
# }
```

### PASO 4: Iniciar Cloudflare Tunnel (Terminal 3)

```bash
cd c:\Users\CAMILO\Documents\modo-bestia-vscode\.copilot_agentic_workspace

# Ejecutar Cloudflare Tunnel
.\cloudflared.exe tunnel --url http://localhost:8000
```

**Esperado:**
```
ACME certificate validation succeeded
https://encouraged-colleges-benjamin-magnitude.trycloudflare.com is now available!
```

### PASO 5: Probar API Pública

```bash
# Desde cualquier lugar (incluido otro PC/celular)
curl https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/health

# O abrir en navegador:
# https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/docs
```

---

## 📊 ENDPOINTS DISPONIBLES

### 🏥 Health Check

```bash
GET /health

Response:
{
  "status": "OK",
  "timestamp": "2026-05-20T07:36:39.123456",
  "model": "XGBoost Credit Risk Classifier",
  "threshold": 0.1160,
  "auc_roc": 0.8983,
  "version": "1.0.0"
}
```

### 🎯 Predicción

```bash
POST /predict

Request:
{
  "raw_features": [45, 55000, 2, 15000, 8.5, 0.25, 0, 10]
}

Response:
{
  "probability": 0.5771,
  "default": false,
  "recommendation": "REJECTED",
  "financial_impact": {
    "loan_value": 5000,
    "expected_loss": 2884.55
  },
  "model_info": {
    "name": "XGBoost v2.0.1",
    "threshold": 0.1160,
    "auc": 0.8983
  }
}
```

---

## 🔄 CICLO DE PRODUCCIÓN

### DESARROLLO
```
1. Editar scripts locales
2. Ejecutar tests locales
3. Verificar con Python script
```

### DEPLOY
```
1. Terminal 1: uvicorn (API)
2. Terminal 2: cloudflared (Tunnel)
3. Terminal 3: Monitorar logs
```

### MONITOREO
```
- Logs de API: Terminal 1
- Acceso público: HTTPS (con SSL automático)
- Disponibilidad: 24/7 mientras Terminal 1 y 2 estén activas
```

---

## ⚠️ CUIDADOS IMPORTANTES

### 1. MANTENER VIVAS LAS TERMINALS
- **Terminal 1** (uvicorn): Debe estar corriendo siempre
- **Terminal 2** (cloudflared): Debe estar corriendo siempre
- Si se cierran, la API se vuelve inaccesible

### 2. PUERTO 8000 DEBE ESTAR LIBRE
```bash
# Verificar quién usa puerto 8000
netstat -ano | findstr :8000

# Si está ocupado, cambiar en uvicorn:
uvicorn src.main:app --host 0.0.0.0 --port 8001
# Luego actualizar cloudflared
```

### 3. FIREWALL
- Cloudflare Tunnel usa puerto HTTPS (443) saliente
- No requiere abrir puertos en firewall
- **Perfectamente seguro**

---

## 🔐 SEGURIDAD

### ✅ Lo que tenemos
- HTTPS automático (certificado Cloudflare)
- Tunnel encrypted (conexión segura)
- Sin exposición de IP local
- No requiere port forwarding

### ⚠️ Para producción seria
- Agregar autenticación (API Key)
- Rate limiting
- CORS configurado
- Logging de auditoría

---

## 📈 PRÓXIMAS MEJORAS (DESPUÉS DEL DEPLOY)

### FASE 2: Aumentar a 200 Muestras
```
1. Modificar MAX_SAMPLES_FOR_KERNEL = 200
2. Agregar stratified sampling
3. Re-ejecutar quantum pipeline
4. Actualizar modelos en /models/
5. Redeploy (API restarts automáticamente)
```

### FASE 3: Agregar Endpoint Quantum
```
POST /predict-quantum
├─ Usa quantum kernel en lugar de XGBoost
├─ Tardará más (quantum evaluation)
└─ Resultados comparables o mejores
```

---

## 🆘 TROUBLESHOOTING

### "Port 8000 already in use"
```bash
# Terminar proceso anterior
taskkill /F /PID <PID>

# O cambiar puerto en uvicorn
uvicorn src.main:app --port 8001
```

### "cloudflared tunnel fails"
```bash
# Logout y re-login
.\cloudflared.exe tunnel logout

# Reintentar
.\cloudflared.exe tunnel --url http://localhost:8000
```

### "API responde lentamente"
```bash
# Verificar carga de sistema
# Si es alta, posiblemente quantum pipeline está corriendo
# Esperar a que termine
```

---

## 📝 COMANDOS RÁPIDOS

```bash
# 1. Configurar environment
set PYTHONPATH=%cd%
set PYTHONUNBUFFERED=1

# 2. Instalar deps
pip install -r requirements.txt

# 3. Iniciar API
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 4. En otra terminal: Cloudflare
.\cloudflared.exe tunnel --url http://localhost:8000

# 5. Probar (otra terminal)
curl http://localhost:8000/health
curl https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/health
```

---

## ✅ CHECKLIST DE DEPLOY

- [ ] Venv activado
- [ ] Requirements instalados
- [ ] API inicia sin errores (Terminal 1)
- [ ] Cloudflare Tunnel inicia (Terminal 2)
- [ ] `GET /health` responde en localhost:8000
- [ ] `GET /health` responde en URL pública
- [ ] `POST /predict` funciona con datos test
- [ ] Swagger UI accesible (/docs)
- [ ] Documentación actualizada
- [ ] Listo para producción ✅

