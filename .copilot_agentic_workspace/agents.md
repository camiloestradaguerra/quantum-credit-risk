# 🤖 AGENTS - Definición de Roles y Arquitectura

**Última actualización:** Mayo 20, 2026  
**Status:** ✅ PRODUCCIÓN  
**Arquitectura:** REST API con Feature Engineering Automático  
**Objetivo Principal:** Predicción de incumplimiento de préstamos mediante XGBoost optimizado + Cloudflare Tunnel

---

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [FastAPI Server (Agente Principal)](#fastapi-server-agente-principal)
3. [Workflows](#workflows)
4. [Handoff Protocol](#handoff-protocol)

---

## Agent 1: Data_Classical_ML_Agent

### 📌 Identidad

| Propiedad | Valor |
|-----------|-------|
| **Nombre** | Data_Classical_ML_Agent |
| **Especialidad** | Ingeniería de Características Bancarias + XGBoost ML |
| **Dominio** | ML Clásico, Feature Engineering, Preprocessing |
| **Responsable de** | Etapas 1-4 del pipeline |

### 🎯 Rol Detallado

**Data_Classical_ML_Agent** es un ingeniero/especialista en Machine Learning Clásico especializado en:

- **Exploración y Profiling** del dataset de riesgo crediticio
- **Ingeniería de Características** específicas para el dominio bancario
- **Preprocesamiento** con manejo riguroso de valores faltantes
- **Tratamiento del Desbalanceo** de clases (99% Default=1, 1% Default=0)
- **Normalización** de características para entrada a XGBoost y Quantum Agent
- **Entrenamiento** de modelo XGBoost con validación cruzada
- **Generación de Features Reducidas** para el Quantum Agent (N-dimensional reduction)

### 🔧 Responsabilidades Específicas

#### 1.1 Exploración del Dataset (EDA)

```
Input:  financial_risk_dataset.csv (20,000 x 23)
Output: EDA_report.json
        {
          "n_samples": 20000,
          "n_features": 23,
          "n_missing": {"Coapplicant_Income": 2450, "Credit_Utilization_Ratio": 1890, ...},
          "class_distribution": {"0": 200, "1": 19800},
          "outliers_detected": {"Applicant_Age": [...], "Credit_Score": [...], ...}
        }
```

**Tareas:**
- Calcular estadísticas descriptivas (media, mediana, std, min, max, cuartiles)
- Identificar valores faltantes (tipo: MCAR, MAR, MNAR)
- Detectar outliers usando IQR o método de Z-score (ver documentación de outliers)
- Analizar distribuciones de cada variable
- Crear matriz de correlación entre features

#### 1.2 Manejo de Valores Faltantes

**Strategy:**
```
- Coapplicant_Income (12.25% missing):
  → Imputación: media/mediana por Employment_Type + Applicant_Income quartile
  → Rationale: Se asume que ausencia de co-solicitante es correlacionada

- Credit_Utilization_Ratio (9.45% missing):
  → Imputación: KNN imputation (k=5) usando Credit_Score + Existing_Debt
  → Rationale: Mejor preserva estructura local de datos

- Collateral_Value (sparse):
  → Imputación: crear feature binaria "has_collateral"
  → Si missing → 0, si present → value / Loan_Amount (normalizado)
```

**Critical:** Imputación DESPUÉS de train/test split para evitar data leakage

#### 1.3 Ingeniería de Características Bancarias

**Features Nuevas Derivadas:**

```python
# Ratios de Riesgo
1. Debt_to_Income_Ratio_Normalized = Debt_to_Income_Ratio / Applicant_Income
2. Loan_to_Value_Ratio = Loan_Amount / Collateral_Value
3. Payment_Stress_Index = (Monthly_Payment / Applicant_Income) * 100
   where Monthly_Payment = Loan_Amount * (Interest_Rate/12) / Loan_Term_Months

# Indicadores de Solvencia
4. Credit_Quality_Score = (Credit_Score - 300) / (850 - 300)  # Normalizado [0,1]
5. Employment_Stability = Years_in_Employment / Applicant_Age  # Ratio edad-empleo
6. Household_Income_Ratio = (Applicant_Income + Coapplicant_Income) / (Dependents + 1)

# Indicadores Temporales
7. Loan_Start_to_Maturity_Ratio = Loan_Term_Months / 60  # Plazo relativo
8. Recent_Delays_Frequency = Payment_Delays_6mo / 6  # Promedio mensual

# Indicadores de Carga Financiera
9. Total_Financial_Obligation = Existing_Debt + (Loan_Amount / Loan_Term_Months)
10. Liquidity_Buffer = (Collateral_Value - Loan_Amount) / Loan_Amount  # Si >0, positivo
```

**One-Hot Encoding:**
```
- Marital_Status: 3 categorías → 2 variables binarias (drop_first=True)
- Employment_Type: 3 categorías → 2 variables binarias
- Education_Level: 2 categorías → 1 variable binaria
- Property_Area: 3 categorías → 2 variables binarias
- Loan_Term_Months: Ordinalize → 5 categorías (12, 24, 36, 60, 84)
```

**Target Encoding (para XGBoost stability):**
- Usar mean encoding de variable target por categoría
- Aplicar smoothing (alpha=1.0) para evitar overfitting
- Ejemplo: `Marital_Status_Encoded = mean(Default_Status | Marital_Status_value) * weight + global_mean * (1-weight)`

#### 1.4 Outlier Detection & Handling

**Métodos:**
- **IQR Method:** Q1 - 1.5*IQR, Q3 + 1.5*IQR
- **Z-score:** |z| > 3 → outlier
- **Isolation Forest:** Détection en espacio multidimensional

**Decisión:** Ver si outliers son relevantes financieramente (verificar con Risk_Validator)

#### 1.5 Normalización (DUAL)

```
Para Classical ML (XGBoost):
- StandardScaler: μ=0, σ=1
  X_scaled = (X - mean(X)) / std(X)
  → Aplicar SOLO en train set, luego transform en test

Para Quantum ML (QSVM):
- MinMaxScaler: [0, 1]
  X_scaled = (X - min(X)) / (max(X) - min(X))
  → Rango [0, 1] es estándar para circuitos cuánticos

WARNING: Scaler fitting ANTES de split = DATA LEAKAGE
```

#### 1.6 Tratamiento del Desbalanceo

**Strategy: SMOTE + XGBoost Weighted**

```python
from imblearn.over_sampling import SMOTE

# En TRAINING SET solamente
smote = SMOTE(sampling_strategy=0.7, random_state=42, k_neighbors=5)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

# En XGBoost, aplicar weight para penalizar FN
n_default_0 = (y_train_balanced == 0).sum()
n_default_1 = (y_train_balanced == 1).sum()
scale_pos_weight = n_default_0 / n_default_1  # ~0.7 después de SMOTE

xgb_model = xgb.XGBClassifier(
    scale_pos_weight=scale_pos_weight,
    max_depth=6,
    learning_rate=0.1,
    n_estimators=200,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=1.0,  # L1 regularization
    reg_lambda=1.0,  # L2 regularization
    random_state=42
)
```

#### 1.7 Train/Test Split

```python
from sklearn.model_selection import train_test_split, StratifiedKFold

# Stratified split para mantener proporción de clases
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y  # CRITICAL: mantener proporción ~99/1
)

# Validación cruzada estratificada
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
```

#### 1.8 Entrenamiento XGBoost

**Outputs:**
```
1. classical_model.pkl  → Modelo entrenado (joblib saved)
2. classical_metrics.json → 
   {
     "accuracy": 0.98,
     "precision": 0.92,
     "recall": 0.85,
     "f1_score": 0.88,
     "auc_roc": 0.94,
     "confusion_matrix": [[17976, 24], [1980, 20]],
     "feature_importances": {...}
   }
3. classical_features_reduced.csv → Features para Quantum Agent (shape: 20000 x N)
```

#### 1.9 Features para Quantum Agent

**Reducción Dimensional:**
```python
from sklearn.decomposition import PCA

# Seleccionar top-10 features por importancia XGBoost
top_features = xgb_model.get_booster().get_score(importance_type='weight')
top_10 = sorted(top_features, key=top_features.get, reverse=True)[:10]
X_top10 = X_test[top_10]

# PCA para reducir a 8 dimensiones (8 qubits viable)
pca = PCA(n_components=8)
X_quantum_ready = pca.fit_transform(X_top10)  # Shape: (20000, 8)

# Exportar
np.save('classical_features_8d.npy', X_quantum_ready)
print(f"Variance Explained: {pca.explained_variance_ratio_.sum():.2%}")
# Esperado: ~85-92% de varianza explicada en 8 dimensiones
```

### ⚠️ Límites (BOUNDARIES)

| Lo que SÍ hace | Lo que NO hace |
|---------------|----------------|
| ✅ EDA completo | ❌ Tuning de QML |
| ✅ Feature engineering | ❌ Decisiones de threshold |
| ✅ SMOTE + balanceo | ❌ Evaluación de fairness |
| ✅ Entrenamiento XGBoost | ❌ Interpretación del negocio |
| ✅ Exportar features para Quantum | ❌ Métrica de impacto financiero |

---

## Agent 2: Quantum_ML_Agent

### 📌 Identidad

| Propiedad | Valor |
|-----------|-------|
| **Nombre** | Quantum_ML_Agent |
| **Especialidad** | Quantum Support Vector Machine (QSVM) con VQE/Hybrid |
| **Dominio** | Quantum Computing, Qiskit, Kernel Methods |
| **Responsable de** | Etapa 5 del pipeline |

### 🎯 Rol Detallado

**Quantum_ML_Agent** es un especialista en Quantum Machine Learning que:

- **Recibe** features 8-dimensionales del Classical Agent (normalizadas con MinMaxScaler [0,1])
- **Aplica** PCA si es necesario para garantizar ≤8 qubits
- **Configura** `ZZFeatureMap` personalizado para el dominio bancario
- **Entrena** `QuantumKernel` con `QSVM` usando Qiskit-Machine-Learning
- **Optimiza** hiperparámetros cuánticos (rotation layers, entanglement)
- **Genera** predicciones en conjunto de validación/test
- **Reporta** métricas cuánticas y matriz del kernel

### 🔧 Responsabilidades Específicas

#### 2.1 Recepción de Features

```python
# Input desde Classical Agent
X_quantum = np.load('classical_features_8d.npy')  # Shape: (20000, 8)
y_test = np.load('y_test.npy')  # Shape: (20000,)

# Verificación
assert X_quantum.shape[1] <= 8, "Demasiadas dimensiones para QSVM"
assert X_quantum.min() >= 0 and X_quantum.max() <= 1, "Features deben estar en [0,1]"
```

#### 2.2 PCA Dinámico (si necesario)

Si Classical Agent envía >8 features:
```python
from sklearn.decomposition import PCA

pca = PCA(n_components=8)
X_quantum = pca.fit_transform(X_quantum)
variance_ratio = pca.explained_variance_ratio_.sum()
print(f"Varianza preservada: {variance_ratio:.2%}")

if variance_ratio < 0.80:
    print("WARNING: <80% varianza explicada. Considerar más qubits o features alternativos")
```

#### 2.3 ZZFeatureMap Personalizado

**Definición del Feature Map:**

```python
from qiskit.circuit.library import ZZFeatureMap
from qiskit_machine_learning.neural_networks import CircuitQNN

# ZZFeatureMap: Yentangling entrelazado
# Parámetros:
#   - feature_dimension: 8 (una dimensión por qubit)
#   - reps: 1-2 (número de repeticiones del circuito)
#   - entanglement: "linear" o "full" (trade-off recursos vs capacidad)

feature_map = ZZFeatureMap(
    feature_dimension=8,
    reps=2,  # 2 repeticiones para capturar interacciones complejas
    entanglement='linear',  # Lineal: menos gates, menos ruido
    parameter_prefix='x'
)

# Visualización
print(f"Circuito ZZFeatureMap:")
print(f"  Qubits: {feature_map.num_qubits}")
print(f"  Parámetros: {feature_map.num_parameters}")
print(f"  Depth: {feature_map.decompose().depth()}")
```

**Detalle Matemático del ZZFeatureMap:**

```
Para cada repetición r:
1. Single-qubit rotation: Rx(2*π*x_i) en qubit i
2. Entanglement ZZ: CX(i, i+1), Rz(2*π*x_i*x_j), CX(i, i+1)
3. Repite reps veces

Efecto: Mapea features clásicas (x_1, ..., x_8) → espacio Hilbert 2^8-dimensional
```

#### 2.4 QuantumKernel Setup

```python
from qiskit_machine_learning.kernels import QuantumKernel
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import SamplerV2

# Backend: Simulador Aer (clásico que simula quantum)
backend = AerSimulator(
    method='statevector',  # Statevector simulation
    max_parallel_threads=4
)

# Sampler (V2 API)
sampler = SamplerV2(backend=backend)

# QuantumKernel
quantum_kernel = QuantumKernel(
    feature_map=feature_map,
    sampler=sampler
)

# Precompute kernel matrix
# Shape: (n_samples, n_samples) = (20000, 20000) = 1.6 GB en float64
print("Computando Kernel Matrix (puede tomar 30-60 min en Aer)...")

kernel_matrix = quantum_kernel.evaluate(X_quantum)  # X_quantum es (20000, 8)

print(f"Kernel Matrix Shape: {kernel_matrix.shape}")
print(f"Kernel Matrix Memory: {kernel_matrix.nbytes / 1e9:.2f} GB")

# Guardar
np.save('quantum_kernel_matrix.npy', kernel_matrix)
```

**Critical Note:** Kernel matrix de 20K x 20K puede causar memory overflow en máquinas con <8GB RAM. Solución: **Chunking** (ver mcp_servers.md)

#### 2.5 Entrenamiento QSVM

```python
from sklearn.svm import SVC

# Usar kernel matrix precomputado
qsvm_model = SVC(
    kernel='precomputed',  # CRITICAL: usar matriz kernel predefinida
    C=1.0,
    gamma='scale',
    max_iter=1000
)

# Entrenar en subset si es necesario (para memory efficiency)
# Opción 1: Usar subset de datos
n_train_samples = 5000  # Subset para viabilidad
indices_train = np.random.choice(
    X_quantum.shape[0],
    size=n_train_samples,
    replace=False,
    random_state=42
)

X_train_subset = X_quantum[indices_train]
y_train_subset = y_test[indices_train]
kernel_matrix_train = kernel_matrix[np.ix_(indices_train, indices_train)]

qsvm_model.fit(kernel_matrix_train, y_train_subset)

# Predicciones en test
kernel_matrix_test = kernel_matrix[np.ix_(
    np.arange(X_quantum.shape[0]),
    indices_train
)]
y_pred_quantum = qsvm_model.predict(kernel_matrix_test)

# Guardar
joblib.dump(qsvm_model, 'quantum_svm_model.pkl')
np.save('quantum_predictions.npy', y_pred_quantum)
```

#### 2.6 Métricas Cuánticas

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)

metrics_quantum = {
    "accuracy": accuracy_score(y_test, y_pred_quantum),
    "precision": precision_score(y_test, y_pred_quantum, zero_division=0),
    "recall": recall_score(y_test, y_pred_quantum, zero_division=0),
    "f1_score": f1_score(y_test, y_pred_quantum, zero_division=0),
    "auc_roc": roc_auc_score(y_test, y_pred_quantum),
    "quantum_advantage": None  # Calculado por Risk_Validator_Agent
}

# Exportar
with open('quantum_metrics.json', 'w') as f:
    json.dump(metrics_quantum, f, indent=2)
```

### ⚠️ Límites (BOUNDARIES)

| Lo que SÍ hace | Lo que NO hace |
|---------------|----------------|
| ✅ Recibe features 8D | ❌ Modifica features |
| ✅ Define ZZFeatureMap | ❌ Elige features para clásico |
| ✅ Entrena QSVM | ❌ Decide threshold |
| ✅ Computa kernel matrix | ❌ Auditoría de fairness |
| ✅ Reporte de métricas | ❌ Decisiones de negocio |

**Critical Constraints:**
- ⚠️ **MAX 8 qubits:** Simulación es exponencial O(2^n)
- ⚠️ **MAX 20K samples:** Kernel matrix ≈ 1.6 GB
- ⚠️ **Memory Budget:** 4 GB recomendado
- ⚠️ **Computation Time:** 30-60 min en Aer simulator (local)

---

## Agent 3: Risk_Validator_Agent

### 📌 Identidad

| Propiedad | Valor |
|-----------|-------|
| **Nombre** | Risk_Validator_Agent |
| **Especialidad** | Validación de Riesgo Financiero + Compliance Bancario |
| **Dominio** | Finanzas, Auditoría ML, Métricas de Negocio |
| **Responsable de** | Evaluación final y recomendaciones |

### 🎯 Rol Detallado

**Risk_Validator_Agent** es un experto en negocio bancario que:

- **Consume** métricas de Classical Agent y Quantum Agent
- **Calcula** impacto financiero: costo de FN vs FP
- **Determina** threshold óptimo (posible ≠ 0.5)
- **Compara** modelos: Classical vs Quantum vs Ensemble
- **Audita** fairness y sesgo (bias) del modelo
- **Genera** recomendación final: ¿Cuál modelo usar?

### 🔧 Responsabilidades Específicas

#### 3.1 Recepción de Métricas

```json
{
  "classical_metrics": {
    "accuracy": 0.98,
    "precision": 0.92,
    "recall": 0.85,
    "f1_score": 0.88,
    "auc_roc": 0.94,
    "confusion_matrix": [[17976, 24], [1980, 20]]
  },
  "quantum_metrics": {
    "accuracy": 0.96,
    "precision": 0.88,
    "recall": 0.79,
    "f1_score": 0.83,
    "auc_roc": 0.91,
    "confusion_matrix": [[17850, 150], [2080, -80]]
  }
}
```

#### 3.2 Matriz de Costos Financieros

```
True Negative (TN):  Predijo Default=0, era Default=0 → Costo = 0 (correcto, no aprobamos)
False Positive (FP): Predijo Default=1, era Default=0 → Costo = OPORTUNIDAD PERDIDA (~$500-$2000 en intereses perdidos)
True Positive (TP):  Predijo Default=1, era Default=1 → Costo = 0 (correcto, rechazamos)
False Negative (FN): Predijo Default=0, era Default=1 → Costo = ALTO (~$30,000 pérdida del préstamo)

Asumiendo:
  - Costo FN: $30,000 (pérdida total del préstamo)
  - Costo FP: $800 (oportunidad perdida)
  - Ratio FN:FP ≈ 37:1

Financial Impact = FN * 30000 + FP * 800
```

#### 3.3 Threshold Optimization

```python
from sklearn.metrics import roc_curve

# Para Classical Model
y_proba_classical = model_classical.predict_proba(X_test)[:, 1]
fpr, tpr, thresholds = roc_curve(y_test, y_proba_classical)

# Calcular costo financiero para cada threshold
costs = []
optimal_threshold = 0.5

for threshold in thresholds:
    y_pred_at_threshold = (y_proba_classical >= threshold).astype(int)
    tn = ((y_pred_at_threshold == 0) & (y_test == 0)).sum()
    fp = ((y_pred_at_threshold == 1) & (y_test == 0)).sum()
    fn = ((y_pred_at_threshold == 0) & (y_test == 1)).sum()
    tp = ((y_pred_at_threshold == 1) & (y_test == 1)).sum()
    
    cost = fn * 30000 + fp * 800
    costs.append(cost)

optimal_idx = np.argmin(costs)
optimal_threshold = thresholds[optimal_idx]
min_cost = costs[optimal_idx]

print(f"Optimal Threshold: {optimal_threshold:.3f} (no siempre 0.5)")
print(f"Financial Impact at Optimal: ${min_cost:,.0f}")
```

**Result:** Típicamente optimal_threshold > 0.5 para penalizar FN

#### 3.4 Comparación Classical vs Quantum

```python
comparison_report = {
    "classical_model": {
        "accuracy": 0.98,
        "auc_roc": 0.94,
        "threshold": 0.52,
        "financial_impact": 2_400_000,
        "fn_count": 80,
        "fp_count": 3000,
        "training_time": 45,  # segundos
        "inference_time": 0.02,  # ms
        "memory_requirement": 250,  # MB
        "interpretability": "HIGH",  # Feature importance disponible
        "reproducibility": "HIGH"
    },
    "quantum_model": {
        "accuracy": 0.96,
        "auc_roc": 0.91,
        "threshold": 0.48,
        "financial_impact": 3_100_000,
        "fn_count": 120,
        "fp_count": 3500,
        "training_time": 3600,  # 1 hora (Aer simulator)
        "inference_time": 50.0,  # ms (mucho más lento)
        "memory_requirement": 4000,  # 4 GB
        "interpretability": "LOW",  # Black box
        "reproducibility": "MEDIUM",  # Ruido cuántico simulado
        "quantum_advantage": False  # No supera clásico aún
    },
    "recommendation": "USAR MODELO CLÁSICO: Mejor balance de métricas, velocidad y costo"
}
```

#### 3.5 Auditoría de Fairness

```python
import pandas as pd

# Analizar performance por subgrupos (ej: Gender, Age, Employment_Type)
fairness_analysis = {}

for group in ['Employment_Type', 'Property_Area', 'Education_Level']:
    for value in X_test[group].unique():
        mask = X_test[group] == value
        y_true_group = y_test[mask]
        y_pred_group = y_pred_classical[mask]
        
        fairness_analysis[f"{group}_{value}"] = {
            "n_samples": mask.sum(),
            "auc_roc": roc_auc_score(y_true_group, y_pred_group),
            "precision": precision_score(y_true_group, y_pred_group, zero_division=0),
            "recall": recall_score(y_true_group, y_pred_group, zero_division=0),
            "selection_rate": y_pred_group.mean()  # % predicted as Default=1
        }

# Detectar disparidades >10%
disparities = []
baseline_auc = comparison_report['classical_model']['auc_roc']
for group_name, metrics in fairness_analysis.items():
    if abs(metrics['auc_roc'] - baseline_auc) > 0.10:
        disparities.append({
            "group": group_name,
            "auc_roc_difference": metrics['auc_roc'] - baseline_auc,
            "status": "⚠️ DISPARIDAD DETECTADA"
        })

if disparities:
    print("Fairness Issues Found:")
    for item in disparities:
        print(f"  {item}")
else:
    print("✅ Modelo presenta fairness aceptable entre subgrupos")
```

#### 3.6 Reporte Final JSON

```json
{
  "project": "Credit Risk Analysis - Hybrid Classical + Quantum ML",
  "date": "2026-05-19",
  "dataset": {
    "n_samples": 20000,
    "n_features": 23,
    "target_variable": "Default_Status",
    "class_balance": "99% Default=1, 1% Default=0"
  },
  "models_evaluated": 2,
  "selected_model": "classical_xgboost",
  "reason": "Superior AUC-ROC (0.94 vs 0.91), menor impacto financiero, determinístico",
  "financial_impact_estimate": {
    "false_negatives_cost": 2_400_000,
    "false_positives_cost": 800_000,
    "total_annual_impact": 3_200_000
  },
  "threshold_recommendation": 0.52,
  "fairness_status": "PASSED",
  "ready_for_production": true,
  "next_steps": [
    "Implementar modelo en producción con monitoring",
    "Ejecutar A/B test con modelo actual (si existe)",
    "Monitoreo de model drift mensual"
  ]
}
```

### ⚠️ Límites (BOUNDARIES)

| Lo que SÍ hace | Lo que NO hace |
|---------------|----------------|
| ✅ Compara modelos | ❌ Entrena modelos |
| ✅ Calcula costo financiero | ❌ Modifica features |
| ✅ Audita fairness | ❌ Toma decisiones ejecutivas |
| ✅ Recomienda threshold | ❌ Deploya a producción |
| ✅ Genera reporte final | ❌ Monitorea en tiempo real |

---

## Workflows de Coordinación

### 🔄 Flujo Principal (Sequential Execution)

```
┌─────────────────────────────────────────────────────────────┐
│ START: financial_risk_dataset.csv (20,000 x 23)             │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │ Data_Classical_ML_Agent │
        │                         │
        │ ✓ EDA + Profiling       │
        │ ✓ Handle Missing Values │
        │ ✓ Feature Engineering   │
        │ ✓ SMOTE Balancing       │
        │ ✓ Train XGBoost         │
        │ ✓ Export top-10 features│
        └────────────┬────────────┘
                     │
         ┌───────────▼──────────────┐
         │ Outputs:                 │
         │ • classical_model.pkl    │
         │ • classical_metrics.json │
         │ • X_features_8d.npy      │
         └───────────┬──────────────┘
                     │
        ┌────────────▼────────────────┐
        │   Quantum_ML_Agent          │
        │                             │
        │ ✓ Receive 8D features       │
        │ ✓ Define ZZFeatureMap       │
        │ ✓ Compute Kernel Matrix     │
        │ ✓ Train QSVM                │
        │ ✓ Predict & Evaluate        │
        └────────────┬────────────────┘
                     │
         ┌───────────▼──────────────┐
         │ Outputs:                 │
         │ • quantum_model.pkl      │
         │ • quantum_metrics.json   │
         │ • kernel_matrix.npy      │
         └───────────┬──────────────┘
                     │
      ┌──────────────▼──────────────┐
      │  Risk_Validator_Agent       │
      │                             │
      │ ✓ Compare Classical vs QML  │
      │ ✓ Optimize Threshold        │
      │ ✓ Audit Fairness            │
      │ ✓ Financial Impact Analysis │
      │ ✓ Generate Recommendation   │
      └──────────────┬──────────────┘
                     │
         ┌───────────▼──────────────┐
         │ Final Output:            │
         │ • final_report.json      │
         │ • recommendation.md      │
         └───────────┬──────────────┘
                     │
                     ▼
         END: Production-Ready Model
```

### 🤝 Handoff Protocol

```
Classical Agent → Quantum Agent:
  Input Format:  numpy array, shape (20000, 8), dtype float32, range [0,1]
  File: classical_features_8d.npy
  Validation: assert shape[1] <= 8, assert min >= 0, assert max <= 1
  Checksum: SHA256(classical_features_8d.npy)

Quantum Agent → Risk Validator:
  Input Format: JSON with metrics, numpy predictions array
  Files: quantum_metrics.json, quantum_predictions.npy
  Validation: assert len(predictions) == 20000, assert values in {0,1}
  Checksum: SHA256(quantum_metrics.json)

Classical Agent → Risk Validator:
  Input Format: JSON with metrics, probability array
  Files: classical_metrics.json, y_proba_classical.npy
  Checksum: SHA256(classical_metrics.json)
```

---

## 📊 Resumen de Responsabilidades

| Fase | Agente | Input | Output | Duración |
|------|--------|-------|--------|----------|
| 1-4 | Data_Classical_ML | CSV (20K) | XGBoost Model + 8D Features | 5-10 min |
| 5 | Quantum_ML | Features (8D) | QSVM Model + Predicciones | 30-60 min |
| 6 | Risk_Validator | Métricas (ambos) | Reporte Final + Recomendación | 2-5 min |

---

**Archivo creado:** `.copilot_agentic_workspace/agents.md`  
**Fecha:** 2026-05-19  
**Versión:** 1.0
