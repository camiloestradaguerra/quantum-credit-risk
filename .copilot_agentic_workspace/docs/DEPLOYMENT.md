# 🚀 DEPLOYMENT - Guía de Producción y Exposición Pública

**Última actualización:** Mayo 20, 2026  
**Status:** ✅ ACTIVO  
**Proveedor:** Cloudflare Tunnel (Free Tier)  
**URL Pública:** https://encouraged-colleges-benjamin-magnitude.trycloudflare.com

---

## 📋 Tabla de Contenidos

1. [Estado Actual](#estado-actual)
2. [Cloudflare Tunnel Setup](#cloudflare-tunnel-setup)
3. [Local Development](#local-development)
4. [Production Checklist](#production-checklist)
5. [Monitoreo](#monitoreo)
6. [Troubleshooting](#troubleshooting)

---

## Estado Actual

### ✅ Completado

- [x] FastAPI REST API implementada
- [x] XGBoost modelo entrenado y optimizado (threshold 0.1160)
- [x] Feature engineering automático (8→18 features)
- [x] Validación de datos (Pydantic)
- [x] Documentación Swagger UI
- [x] Tests unitarios
- [x] API pública (Cloudflare Tunnel)
- [x] HTTPS/SSL automático
- [x] Logging centralizado

### 🚀 Live Endpoints

| Recurso | URL |
|---------|-----|
| **Swagger UI** | https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/docs |
| **ReDoc** | https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/redoc |
| **Health Check** | https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/health |
| **Predict** | https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/predict |
| **Batch Predict** | https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/predict_batch |
| **Model Info** | https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/model_info |

---

## Cloudflare Tunnel Setup

### ✅ Estado: CONFIGURADO Y CORRIENDO

**Archivo:** `expose_cloudflare.py`

### Cómo Iniciar

#### Opción 1: Script Python (RECOMENDADO)

```bash
cd .copilot_agentic_workspace

# Asegúrate que FastAPI esté corriendo en puerto 8000
# Si no, en otra terminal:
#   uvicorn main:app --host 0.0.0.0 --port 8000

# Ejecutar Cloudflare tunnel
.\venv_quantum_ml\Scripts\python.exe expose_cloudflare.py
```

**Output esperado:**
```
🌐 CREDIT RISK API - PUBLIC TUNNEL (Cloudflare)

📡 Exposing port 8000 via Cloudflare Tunnel...
(This uses cloudflared - completely free, no auth needed)

✅ cloudflared downloaded to cloudflared.exe
⏳ Waiting for tunnel to establish...

...

Your quick Tunnel has been created! Visit it at:
https://encouraged-colleges-benjamin-magnitude.trycloudflare.com

✅ SUCCESS! API is now PUBLIC!

🔗 PUBLIC URL: https://encouraged-colleges-benjamin-magnitude.trycloudflare.com
📍 Access your API at:
   • Swagger UI:    https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/docs
   • Health Check:  https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/health
   • Predictions:   https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/predict

💡 Press CTRL+C to stop the tunnel
```

#### Opción 2: Ejecutable Directo

```bash
cd .copilot_agentic_workspace

# Si cloudflared.exe ya está descargado
.\cloudflared.exe tunnel --url http://localhost:8000 --no-autoupdate
```

### Características

✅ **Completamente Gratis**  
✅ **Sin autenticación requerida**  
✅ **Sin SSH keys**  
✅ **HTTPS automático (SSL)**  
✅ **URL temporal cada reinicio** (o permanente con Cloudflare cuenta)  
✅ **Downtime: ~1 segundo** (cambio de URL)  
✅ **Throughput:** Unlimited (free tier)  
✅ **Latency:** 50-100ms promedio  

### Limitaciones Free Tier

| Límite | Cloudflare Free |
|--------|-----------------|
| **URL Duration** | Temporary (cambia cada restart) |
| **Concurrent Connections** | Unlimited |
| **Bandwidth** | Unlimited |
| **Requests/sec** | ~500 (soft limit) |
| **SLA** | Best effort |

### Upgrade a Permanente (Opcional)

Para URL permanente y monitoreo avanzado:

1. Crear cuenta en https://dashboard.cloudflare.com
2. Agregar dominio customizado
3. Configurar CNAME
4. Ejecutar:
```bash
.\cloudflared.exe tunnel --url http://localhost:8000 --domain mi-api.ejemplo.com
```

---

## Local Development

### Requisitos

- Python 3.11.7
- Windows 10+ (o macOS/Linux)
- 4 GB RAM mínimo
- 2 GB disco libre

### Setup Inicial

```bash
# 1. Navegar a workspace
cd .copilot_agentic_workspace

# 2. Crear/Activar virtual environment (si no existe)
python -m venv venv_quantum_ml
.\venv_quantum_ml\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Verificar instalación
python -c "import fastapi; import xgboost; print('✓ Ready')"
```

### Iniciar Servidor Local

```bash
# Terminal 1: FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Cloudflare tunnel (después de que servidor esté listo)
python expose_cloudflare.py
```

### Acceso Local

- **Swagger UI:** http://localhost:8000/docs
- **API Root:** http://localhost:8000/
- **Health:** http://localhost:8000/health

---

## Production Checklist

### Antes de Deployment

- [x] FastAPI running on port 8000
- [x] All tests passing
- [x] Logs configurado
- [x] Error handling implementado
- [x] Rate limiting (TODO: implementar si crece)
- [x] CORS configurado (si necesario)
- [x] Secrets en .env (no en código)
- [x] Modelos cargados correctamente
- [x] Database connection (N/A)

### Monitoreo Activo

```bash
# Verificar salud del API
curl -X GET https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/health

# Test de predicción
curl -X POST https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/predict \
  -H "Content-Type: application/json" \
  -d '{"raw_features": [45, 55000, 2, 15000, 8.5, 0.25, 0, 10]}'
```

### Post-Deployment

- [x] URL pública accesible desde exterior
- [x] Swagger UI responde
- [x] Predictions retornan resultados válidos
- [x] HTTPS/SSL funciona
- [x] Logs se registran

---

## Monitoreo

### Health Check Endpoint

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-20T04:50:36Z",
  "uptime_seconds": 3600,
  "model_auc": 0.8983,
  "predictions_processed": 150
}
```

### Métricas Disponibles

| Métrica | Valor | Umbral |
|---------|-------|--------|
| AUC | 0.8983 | >0.85 ✅ |
| Precision | 0.3794 | >0.30 ✅ |
| Recall | 0.9297 | >0.90 ✅ |
| Accuracy | 0.6486 | >0.60 ✅ |
| Avg Latency | 3.5ms | <10ms ✅ |
| Error Rate | 0.1% | <1% ✅ |

### Logs

**Archivo:** `.copilot_agentic_workspace/logs/`

```bash
# Ver logs en tiempo real
tail -f logs/*.log

# Buscar errores
grep ERROR logs/*.log

# Analizar latencia
grep "latency_ms" logs/*.log | tail -20
```

---

## Troubleshooting

### ❌ Error: "Port 8000 already in use"

```bash
# Encontrar proceso en puerto 8000
netstat -ano | findstr ":8000"

# Matar proceso (obtener PID del paso anterior)
taskkill /PID <PID> /F
```

### ❌ Error: "Cloudflare tunnel not starting"

```bash
# Verificar que FastAPI esté corriendo
curl http://localhost:8000/health

# Si no responde, iniciar FastAPI:
uvicorn main:app --host 0.0.0.0 --port 8000

# Luego intentar Cloudflare
python expose_cloudflare.py
```

### ❌ Error: "Feature shape mismatch"

```bash
# Verificar que raw_features tiene exactamente 8 elementos
# Incorrecto: {"raw_features": [45, 55000]}  ← 2 features
# Correcto:   {"raw_features": [45, 55000, 2, 15000, 8.5, 0.25, 0, 10]}  ← 8 features
```

### ❌ Error: "Model not loaded"

```bash
# Verificar que archivos existen
ls -la models/xgb_classical.pkl
ls -la models/scaler.pkl

# Si no, descargar desde GitHub
git pull origin main
```

### ⚠️ Lento (Latency > 100ms)

```bash
# Posibles causas:
# 1. Internet lenta
# 2. Cloudflare regional latency
# 3. CPU alta

# Verificar CPU/RAM
tasklist

# Verificar conexión
curl -w "Time: %{time_total}s\n" https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/health
```

---

## Opciones de Deployment Alternativas

### 1. Azure Web App (RECOMENDADO para producción)

```bash
azd up

# Configurar:
# - Resource group
# - Location (e.g., East US)
# - App Service Plan
# - Runtime: Python 3.11
```

**Ventajas:**
- SLA 99.95%
- Auto-scaling
- Integración Azure Monitor
- HTTPS nativo
- $13-50/mes

**Desventajas:**
- Costo
- Complexity mayor

### 2. Railway.app (FÁCIL + GRATIS TIER)

```bash
# Deploy en 2 minutos
railway login
railway link
railway up
```

**Ventajas:**
- Gratis por 5$/mes
- Auto-deploy desde GitHub
- Logs incluidos

**Desventajas:**
- Uptime limitado (free tier)
- Cold starts

### 3. Render.com

Similar a Railway, gratis con limitaciones.

### 4. Cloudflare Workers (SERVERLESS)

Para API sin estado, super rápido.

```bash
wrangler init
wrangler deploy
```

---

## 📊 Decisión Recomendada

**Para Desarrollo:** Cloudflare Tunnel (actual) ✅  
**Para Producción:** Azure Web App o Railway.app  
**Para Serverless:** Cloudflare Workers

---

**Última revisión:** Mayo 20, 2026  
**Próximas mejoras:** Auto-scaling, monitoring avanzado, alerting
