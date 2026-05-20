# 🚀 DEPLOYMENT INSTRUCTIONS - QUICK START

**Objetivo**: Desplegar tu API cuántica de Riesgo Crediticio en producción con Cloudflare Tunnel

---

## 📌 OPCIÓN 1: DEPLOY AUTOMÁTICO (RECOMENDADO)

### Paso 1: Abrir PowerShell

```bash
cd c:\Users\CAMILO\Documents\modo-bestia-vscode\.copilot_agentic_workspace
```

### Paso 2: Ejecutar script de deploy

```bash
python deploy.py
```

**Qué hace automáticamente:**
- ✅ Verifica dependencias
- ✅ Inicia API en puerto 8000
- ✅ Inicia Cloudflare Tunnel
- ✅ Verifica salud del API
- ✅ Muestra URL pública

**Esperado:**
```
✅ DEPLOYMENT SUCCESSFUL

📍 LOCAL ACCESS:
   http://localhost:8000
   http://localhost:8000/docs

🌍 PUBLIC ACCESS:
   https://encouraged-colleges-benjamin-magnitude.trycloudflare.com
   https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/docs
```

---

## 📌 OPCIÓN 2: DEPLOY MANUAL (Si prefieres control total)

### Terminal 1: Iniciar API

```bash
cd c:\Users\CAMILO\Documents\modo-bestia-vscode\.copilot_agentic_workspace

# Activar virtual environment
.\venv_quantum_ml\Scripts\activate

# Instalar dependencias (si es primera vez)
pip install -r requirements.txt

# Iniciar API
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Esperado:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Terminal 2: Iniciar Cloudflare Tunnel

```bash
cd c:\Users\CAMILO\Documents\modo-bestia-vscode\.copilot_agentic_workspace

# Ejecutar tunnel
.\cloudflared.exe tunnel --url http://localhost:8000
```

**Esperado:**
```
ACME certificate validation succeeded
https://encouraged-colleges-benjamin-magnitude.trycloudflare.com is now available!
```

### Terminal 3: Verificar que funciona

```bash
# Test local
curl http://localhost:8000/health

# Test público
curl https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/health
```

---

## ✅ VERIFIACIONES DE DEPLOY

### 1. Health Check Local

```bash
curl http://localhost:8000/health

# Response esperado:
# {
#   "status": "OK",
#   "timestamp": "2026-05-20T...",
#   "model": "XGBoost Credit Risk Classifier",
#   "threshold": 0.1160,
#   "auc_roc": 0.8983,
#   "version": "1.0.0"
# }
```

### 2. Health Check Público

```bash
curl https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/health
```

### 3. Test de Predicción

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "raw_features": [45, 55000, 2, 15000, 8.5, 0.25, 0, 10]
  }'

# Response esperado:
# {
#   "probability": 0.5771,
#   "default": false,
#   "recommendation": "REJECTED",
#   "financial_impact": {...},
#   "model_info": {...}
# }
```

### 4. Swagger UI (Documentación Interactiva)

```
Local:  http://localhost:8000/docs
Público: https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/docs
```

---

## 🔄 PRÓXIMOS PASOS: MEJORA A 200 MUESTRAS

**DESPUÉS de que el deploy esté funcionando:**

```bash
# Terminal 4: Ejecutar versión v4.0 (200 muestras)
python scripts/2_quantum_ml_pipeline_v4.py

# Tiempo estimado: ~13 horas
# Mejor AUC-ROC esperado: 78-82% (vs 53% con 100 muestras)
```

El API seguirá funcionando mientras se ejecuta la mejora en background.

---

## ⚠️ PROBLEMAS COMUNES

### "Port 8000 already in use"

```bash
# Opción 1: Terminar proceso anterior
netstat -ano | findstr :8000
taskkill /F /PID <PID>

# Opción 2: Usar puerto diferente
uvicorn src.main:app --port 8001
# Luego actualizar cloudflared:
.\cloudflared.exe tunnel --url http://localhost:8001
```

### "Cloudflare tunnel connection failed"

```bash
# Reintentar
.\cloudflared.exe tunnel logout
.\cloudflared.exe tunnel --url http://localhost:8000
```

### "API responde lentamente"

- Verificar si quantum pipeline está ejecutándose (usa mucha CPU)
- Esperar a que termine
- Normalizar después

---

## 📊 MONITOREO

### Ver logs locales

- Terminal 1: Logs de API
- Terminal 2: Logs de Tunnel
- Archivos: `logs/` en el workspace

### Ver estado público

```bash
# Ping a la URL pública cada 30 segundos
while ($true) {
  Write-Host "$(Get-Date -Format 'HH:mm:ss'): " -NoNewline
  (Invoke-WebRequest https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/health -ErrorAction SilentlyContinue).StatusCode
  Start-Sleep -Seconds 30
}
```

---

## 🏁 CHECKLIST FINAL

- [ ] API inicia sin errores
- [ ] Cloudflare tunnel establece conexión
- [ ] `/health` responde localmente
- [ ] `/health` responde públicamente  
- [ ] Swagger UI accesible
- [ ] `/predict` funciona con datos test
- [ ] URL pública compartible
- [ ] Listo para producción ✅

---

## 📞 SOPORTE

### Archivos clave

- `src/main.py` - Código del API
- `DEPLOY_GUIDE.md` - Guía completa
- `logs/` - Archivos de log

### Versiones del pipeline

- `scripts/2_quantum_ml_pipeline_OPTIMIZED.py` (100 muestras, v3.1)
- `scripts/2_quantum_ml_pipeline_v4.py` (200 muestras, v4.0)

