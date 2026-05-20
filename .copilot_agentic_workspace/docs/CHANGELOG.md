# 📝 CHANGELOG CENTRALIZADO - Credit Risk Prediction API

**Proyecto:** Credit Risk Prediction API (FastAPI + XGBoost)  
**Última Actualización:** Mayo 20, 2026  
**Autor:** Camilo Estrada Guerra  
**Estado:** ✅ PRODUCCIÓN - API Pública Expuesta

---

## 📋 CHANGELOG - Historial Completo

### ✅ FASE 5: DESPLIEGUE PÚBLICO (Mayo 20, 2026)

#### 5.1 Exposición Pública de API
- **Problema:** API corriendo en localhost, no accesible desde internet
- **Soluciones Intentadas:**
  - ❌ ngrok (pyngrok wrapper falló - requería dev domain)
  - ❌ localhost.run (SSH requería auth key)
  - ✅ **Cloudflare Tunnel (EXITOSA)**
- **Resultado:** API pública en `https://encouraged-colleges-benjamin-magnitude.trycloudflare.com`
- **Beneficio:** Acceso global, testing remoto, integración con otros servicios
- **Archivos Creados:**
  - `expose_cloudflare.py` - Script para iniciar tunnel Cloudflare
  - `cloudflared.exe` - Binary de Cloudflare descargado automáticamente
- **Status:** ✅ COMPLETADO

#### 5.2 Actualización de Documentación
- **Cambios:**
  - Eliminada referencia a ngrok (NGROK_QUICK_START.md obsoleto)
  - Actualizado README.md con URL pública de Cloudflare
  - Creado DEPLOYMENT.md con guía de producción
- **Archivos Descartados:**
  - `expose_api_ngrok.py` (pyngrok no funciona)
  - `ngrok_public_tunnel.py` (no aplicable)
  - `start_ngrok.py` (deprecated)
  - `NGROK_QUICK_START.md` (outdated)
- **Status:** ✅ EN PROGRESO

---

### ✅ FASE 4: SIMPLIFICACIÓN DE API (Mayo 19, 2026)

#### 4.1 Refactorización de Endpoint /predict
- **Problema:** API aceptaba 18 features (incluidas engineered), confuso para usuarios
- **Solución:** 
  - API ahora acepta SOLO 8 features originales
  - Servidor auto-calcula 10 features adicionales con `engineer_features()`
  - PCA (18→8) removido del pipeline (era para quantum ML experimental)
- **Fórmulas de Features Engineered:**
  ```
  f8:  debt_to_income (duplicado)
  f9:  interest_rate² (interest_rate_risk)
  f10: loan_amount / (income + 1) (loan_income_interaction)
  f11: log(emp_length + 1) (emp_stability_log)
  f12: credit_history / (age + 1) (credit_history_ratio)
  f13: prior_default × debt_to_income (default_risk_score)
  f14: age / 100 (age_normalized)
  f15: log(loan_amount + 1) × interest_rate (loan_amount_risk)
  f16: income / (age + 1) (income_age_ratio)
  f17: debt_to_income + (interest_rate²/100) + (loan_amount/(income+1)) (composite_risk)
  ```
- **Resultado:** 
  - API más intuitiva para usuarios
  - Documentación clara en Swagger UI (55+ líneas)
  - Predicciones correctas sin mismatch de features
- **Archivos Modificados:**
  - `main.py` - endpoint /predict refactorizado
  - `FEATURES_MAPPING.md` - documentación completa
  - `README.md` - ejemplos actualizados
- **Status:** ✅ COMPLETADO

#### 4.2 Pruebas de API
- **Archivo:** `test_8_features.py`
- **Entrada:** [45, 55000, 2, 15000, 8.5, 0.25, 0, 10]
- **Salida:** 
  - Probability: 0.5771
  - Recommendation: REJECTED
  - Financial Impact: -$30,000 (default risk)
- **Status:** ✅ VALIDADO

---

### ✅ FASE 3: DOCUMENTACIÓN COMPLETA (Mayo 19, 2026)

#### 3.1 Documentación de Features
- **Archivo:** `FEATURES_MAPPING.md`
- **Contenido:**
  - 8 features de entrada (edad, ingresos, antigüedad, etc.)
  - 10 features engineered (ratios, logaritmos, interacciones)
  - Rangos, unidades, impacto en riesgo
  - Ejemplos de uso en Python/cURL
- **Status:** ✅ COMPLETADO

#### 3.2 API Documentation
- **README.md:** Actualizado con ejemplos en 3 lenguajes (Python, JavaScript, cURL)
- **Swagger UI:** Auto-generado en `/docs` con docstring de 55+ líneas
- **Endpoints Documentados:**
  - `POST /predict` - Predicción individual
  - `POST /predict_batch` - Predicciones en lote
  - `GET /health` - Estado del servidor
  - `GET /model_info` - Métricas del modelo
- **Status:** ✅ COMPLETADO

---

### ✅ FASE 2: INFRAESTRUCTURA FASTAPI (Mayo 19, 2026)

#### 2.1 Setup de FastAPI
- **Framework:** FastAPI + Uvicorn
- **Puerto:** 8000 (http://0.0.0.0:8000)
- **Archivo:** `main.py`
- **Servidor:** Uvicorn ASGI
- **Status:** ✅ EJECUTÁNDOSE

#### 2.2 Carga de Modelos
- **Modelos Cargados:**
  - `xgb_classical.pkl` - Modelo XGBoost entrenado (18 features)
  - `scaler.pkl` - StandardScaler (normalización)
  - `pca_8d.pkl` - PCA (no usado en predicción, legacy)
- **Metrics:** `classical_metrics.json` con AUC, precision, recall, F1
- **Status:** ✅ COMPLETADO

#### 2.3 Validación de Requests
- **Pydantic Models:**
  - `PredictionRequest` - Valida 8 features exactamente
  - `PredictionResponse` - Retorna probability, decision, recommendation
  - `BatchRequest` - Para predicciones en lote
- **Validación Automática:**
  - ✅ Rango de valores
  - ✅ Tipos de datos
  - ✅ Valores faltantes (NaN)
  - ✅ Tamaño de features
- **Status:** ✅ COMPLETADO

---

### ✅ FASE 1: ARQUITECTURA QUANTUM+CLASSICAL (Mayo 18-19, 2026)

#### 1.1 Training Clásico (XGBoost)
- **Dataset:** 32,581 registros, 21.82% default rate
- **Features:** 12 originales → 18 engineered
- **Modelo:** XGBoost (200 estimadores, max_depth=6, learning_rate=0.1)
- **Data Augmentation:** SMOTE (sampling_strategy=0.7)
- **Threshold Óptimo:** 0.1160 (fin-tuning multi-objective)
- **Performance:**
  - AUC: 0.8983
  - Precision: 37.94%
  - Recall: 92.97%
  - Accuracy: 64.86%
  - Financial Impact: $3,346,900 net value
- **Status:** ✅ COMPLETADO

#### 1.2 Data Preprocessing
- **StandardScaler:** Normalización de 18 features
- **KNNImputer:** Imputación de valores faltantes (k=5)
- **Outlier Detection:** Análisis de anomalías
- **PCA:** Reducción 18D → 8D (97.88% variance) - para Quantum ML
- **Status:** ✅ COMPLETADO

#### 1.3 Quantum ML Experimental
- **Framework:** Qiskit 2.4.1
- **Algoritmo:** Quantum SVM (QSVM)
- **Feature Map:** ZZFeatureMap (2 qubits, reps=2)
- **Sampler:** Aer Simulator
- **Status:** ⏳ EXPERIMENTAL (no productivo)

---

## 📊 ESTADO ACTUAL DEL PROYECTO

### ✅ Completado
- [x] Modelo XGBoost entrenado y optimizado
- [x] FastAPI REST API implementada
- [x] Feature engineering automático (8→18)
- [x] Documentación completa
- [x] Tests unitarios
- [x] API pública (Cloudflare Tunnel)
- [x] Swagger UI disponible

### ⏳ En Progreso
- [ ] Integración con sistemas backend
- [ ] Monitoring y alerting en producción
- [ ] Dashboard de métricas (Real-time)

### 📋 Próximas Fases
- [ ] Modelo Quantum productivo
- [ ] CI/CD Pipeline
- [ ] Horizontal scaling
- [ ] Rate limiting y autenticación

---

## 🔧 STACK TÉCNICO VIGENTE

| Componente | Versión | Propósito |
|-----------|---------|----------|
| **FastAPI** | 0.109.0+ | REST API Framework |
| **Uvicorn** | 0.27.0+ | ASGI Server |
| **XGBoost** | 2.0.3 | Modelo de predicción |
| **scikit-learn** | 1.3.0+ | Preprocessing, métricas |
| **Pydantic** | 2.0.0+ | Validación de datos |
| **Cloudflare Tunnel** | 2026.5.0 | Exposición pública |
| **Python** | 3.11.7 | Runtime |

---

## 🚀 URLs DE REFERENCIA

| Recurso | URL |
|---------|-----|
| **API Pública** | https://encouraged-colleges-benjamin-magnitude.trycloudflare.com |
| **Swagger UI** | https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/docs |
| **Health Check** | https://encouraged-colleges-benjamin-magnitude.trycloudflare.com/health |
| **GitHub** | https://github.com/camiloestradaguerra/quantum-credit-risk |

---

## 📌 NOTAS IMPORTANTES

1. **Cloudflare Tunnel:** URL cambia cada reinicio (gratis). Para URL permanente, crear cuenta Cloudflare.
2. **XGBoost Model:** Reentrenamiento necesario si distribución de datos cambia significativamente.
3. **Feature Engineering:** Implementado server-side - clientes envían 8 features, servidor calcula 18.
4. **Threshold:** Actualmente en 0.1160 (optimizado para máximo financial value, no accuracy).

---

## 👤 Autor
**Camilo Estrada Guerra**  
GitHub: [@camiloestradaguerra](https://github.com/camiloestradaguerra)

---

**Última revisión:** Mayo 20, 2026 @ 04:50 UTC
