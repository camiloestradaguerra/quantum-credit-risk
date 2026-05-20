# 🛠️ SKILLS: Herramientas, Dependencias y Recursos Técnicos

**Última actualización:** Mayo 2026  
**Contexto:** Arquitectura Híbrida Quantum + Classical ML  
**Objetivo:** Especificar las dependencias técnicas exactas para cada agente

---

## 📋 Tabla de Contenidos

1. [Resumen Global de Dependencias](#resumen-global-de-dependencias)
2. [Skills del Data_Classical_ML_Agent](#skills-del-data_classical_ml_agent)
3. [Skills del Quantum_ML_Agent](#skills-del-quantum_ml_agent)
4. [Skills del Risk_Validator_Agent](#skills-del-risk_validator_agent)
5. [Dependencias Compartidas](#dependencias-compartidas)
6. [Environment Setup](#environment-setup)
7. [Resource Requirements](#resource-requirements)

---

## Resumen Global de Dependencias

```yaml
Python Version: 3.10 - 3.11 (recommended)

Core Data Science Stack:
  - numpy >= 1.23
  - pandas >= 1.5
  - scikit-learn >= 1.3

Classical ML:
  - xgboost >= 2.0
  - optuna >= 3.0
  - imbalanced-learn >= 0.10

Quantum ML:
  - qiskit >= 0.43
  - qiskit-machine-learning >= 0.7
  - qiskit-aer >= 0.12
  - qiskit-ibm-runtime >= 0.14 (optional)

Utilities:
  - joblib >= 1.3
  - matplotlib >= 3.7
  - seaborn >= 0.12
  - requests >= 2.31

Fairness (optional):
  - aif360 >= 0.5

Total Install Size: ~2.5 GB
```

---

## Skills del Data_Classical_ML_Agent

### 1️⃣ Core Libraries

#### pandas (>= 1.5)

**Purpose:** Manipulación, transformación y análisis de datos estructurados

**Skills Required:**
```python
# EDA
df.describe()
df.info()
df.isnull().sum()
df.corr()
df.groupby().agg()

# Data Cleaning
df.fillna(strategy)
df.drop_duplicates()
df[df['col'].between(q1, q3)]

# Feature Engineering
df['new_col'] = df['col1'] + df['col2']
df.astype()
df.replace()
pd.get_dummies()  # One-Hot Encoding
```

**Typical Usage Pattern:**
```python
import pandas as pd

# 1. Load
df = pd.read_csv('financial_risk_dataset.csv')  # 20,000 x 23

# 2. Explore
print(f"Shape: {df.shape}")
print(f"Missing: {df.isnull().sum()}")

# 3. Clean
df = df.dropna(subset=['critical_col'])
df['col'].fillna(df['col'].median(), inplace=True)

# 4. Transform
df['ratio'] = df['debt'] / df['income']
df = pd.get_dummies(df, columns=['category_col'], drop_first=True)

# 5. Export
X = df.drop('Default_Status', axis=1)
y = df['Default_Status']
```

#### numpy (>= 1.23)

**Purpose:** Operaciones numéricas, álgebra lineal, manejo de arrays

**Skills Required:**
```python
# Array creation
np.array()
np.zeros()
np.random.randn()

# Statistical operations
np.mean(), np.std(), np.percentile()
np.corrcoef()

# Indexing & Slicing
arr[mask]
arr[indices]
arr[start:end]

# Linear Algebra
np.linalg.svd()
np.dot()

# Memory efficient operations
arr.astype(np.float32)  # Reduce memory footprint
```

**Typical Usage Pattern:**
```python
import numpy as np

# 1. Convert from pandas
X_array = df.values.astype(np.float32)  # (20000, 22)

# 2. Compute statistics
mean_val = np.mean(X_array, axis=0)
std_val = np.std(X_array, axis=0)

# 3. Normalize
X_normalized = (X_array - mean_val) / (std_val + 1e-8)

# 4. Split & Save
np.save('X_train.npy', X_train)
X_loaded = np.load('X_train.npy')
```

#### scikit-learn (>= 1.3)

**Purpose:** Preprocessing, modeling, metrics, cross-validation

**Skills Required:**

**Preprocessing:**
```python
from sklearn.preprocessing import (
    StandardScaler,      # μ=0, σ=1
    MinMaxScaler,        # [0, 1]
    RobustScaler,        # Resiste outliers
    LabelEncoder,        # Categóricas → enteros
    OneHotEncoder        # Categóricas → binarias
)

from sklearn.decomposition import PCA

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)  # CRITICAL: fit en train, transform en test

# PCA
pca = PCA(n_components=8)
X_reduced = pca.fit_transform(X_train)
```

**Train/Test Split:**
```python
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y  # CRITICAL: Mantiene proporción de clases
)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for train_idx, val_idx in skf.split(X, y):
    X_train_fold = X[train_idx]
    X_val_fold = X[val_idx]
```

**Metrics:**
```python
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

acc = accuracy_score(y_true, y_pred)
prec = precision_score(y_true, y_pred, zero_division=0)
rec = recall_score(y_true, y_pred, zero_division=0)
f1 = f1_score(y_true, y_pred, zero_division=0)
auc = roc_auc_score(y_true, y_pred_proba)

cm = confusion_matrix(y_true, y_pred)
print(classification_report(y_true, y_pred))
```

#### xgboost (>= 2.0)

**Purpose:** Gradient Boosting Classifier para ML Clásico

**Skills Required:**
```python
import xgboost as xgb

# Definición del modelo
xgb_model = xgb.XGBClassifier(
    # Hiperparámetros críticos
    n_estimators=200,        # Número de árboles
    max_depth=6,             # Profundidad máxima
    learning_rate=0.1,       # Tasa de aprendizaje
    subsample=0.8,           # Fracción de muestras por árbol
    colsample_bytree=0.8,    # Fracción de features por árbol
    
    # Regularización
    reg_alpha=1.0,           # L1 (Lasso)
    reg_lambda=1.0,          # L2 (Ridge)
    
    # Manejo de desbalanceo
    scale_pos_weight=0.7,    # Penalizar menos a clase minoritaria
    
    # Otros
    tree_method='hist',      # 'auto', 'hist', 'gpu_hist'
    random_state=42,
    n_jobs=-1,               # Paralelizar
    verbosity=1              # Logging
)

# Entrenamiento
xgb_model.fit(X_train, y_train, eval_set=[(X_val, y_val)])

# Predicción
y_pred = xgb_model.predict(X_test)
y_proba = xgb_model.predict_proba(X_test)[:, 1]

# Feature Importance
importances = xgb_model.get_booster().get_score(importance_type='weight')
```

**Best Practices:**
```python
# 1. Cross-Validation Loop
from sklearn.model_selection import cross_validate

cv_results = cross_validate(
    xgb_model,
    X_train,
    y_train,
    cv=5,
    scoring=['accuracy', 'roc_auc', 'f1']
)

# 2. Hyperparameter Tuning (via Optuna)
# Ver sección imbalanced-learn
```

#### imbalanced-learn (>= 0.10)

**Purpose:** Manejo de desbalanceo de clases via SMOTE

**Skills Required:**
```python
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline

# SMOTE: Over-sampling de clase minoritaria
smote = SMOTE(
    sampling_strategy=0.7,   # Target ratio de minoritaria vs mayoritaria
    random_state=42,
    k_neighbors=5            # KNN para generar muestras sintéticas
)

X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
# y_train antes:  ~19800 default=1, ~200 default=0
# y_train después: ~19800 default=1, ~13860 default=0 (0.7 * 19800)

# CRITICAL: Aplicar SMOTE DESPUÉS del train/test split
# INCORRECTO: smote.fit_resample(X, y)  # todo dataset
# CORRECTO:   smote.fit_resample(X_train, y_train)  # solo train
```

#### optuna (>= 3.0)

**Purpose:** Hyperparameter Optimization

**Skills Required:**
```python
import optuna
from optuna.samplers import TPESampler

def objective(trial):
    # Sugerir hiperparámetros
    max_depth = trial.suggest_int('max_depth', 3, 10)
    learning_rate = trial.suggest_loguniform('learning_rate', 0.01, 0.3)
    n_estimators = trial.suggest_int('n_estimators', 100, 500)
    
    xgb_trial = xgb.XGBClassifier(
        max_depth=max_depth,
        learning_rate=learning_rate,
        n_estimators=n_estimators,
        random_state=42
    )
    
    # Evaluar con CV
    score = cross_val_score(
        xgb_trial,
        X_train,
        y_train,
        cv=5,
        scoring='roc_auc'
    ).mean()
    
    return score

# Optimización
sampler = TPESampler(seed=42)
study = optuna.create_study(
    direction='maximize',
    sampler=sampler
)
study.optimize(objective, n_trials=20)

best_params = study.best_params
print(f"Best AUC-ROC: {study.best_value:.4f}")
```

### 2️⃣ Specialized Skills

**Outlier Detection:**
```python
# IQR Method
Q1 = df['col'].quantile(0.25)
Q3 = df['col'].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df['col'] < Q1 - 1.5*IQR) | (df['col'] > Q3 + 1.5*IQR)]

# Z-score
from scipy import stats
z_scores = np.abs(stats.zscore(df['col']))
outliers_z = df[z_scores > 3]

# Isolation Forest
from sklearn.ensemble import IsolationForest
iso_forest = IsolationForest(contamination=0.05, random_state=42)
outlier_labels = iso_forest.fit_predict(X)  # -1 = outlier
```

**Memory Efficiency:**
```python
# Reducir footprint
X_float32 = X.astype(np.float32)  # float64 → float32 (50% memory saving)

# Chunking para datasets grandes
chunk_size = 5000
for i in range(0, len(df), chunk_size):
    df_chunk = df.iloc[i:i+chunk_size]
    # Procesar chunk
```

### 3️⃣ Memory Budget

```
Input: CSV (20,000 x 23)           ~  3.5 MB
Pandas DataFrame in memory        ~  20 MB
X_array (20000 x 23, float64)     ~ 3.7 GB
X_array (20000 x 23, float32)     ~ 1.8 GB
SMOTE Balanced set (after)        ~ 3.5 GB
XGBoost Model (serialized)        ~ 50 MB

TOTAL BUDGET: 500 MB (recommended minimum for Classical Agent)
```

---

## Skills del Quantum_ML_Agent

### 1️⃣ Qiskit Core (>= 0.43)

**Purpose:** Quantum circuits, gates, visualization

**Skills Required:**
```python
import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Parameter, ParameterVector

# Crear circuito
qc = QuantumCircuit(8, name='Banking Risk Circuit')  # 8 qubits, 0 classical

# Puertas single-qubit
qc.h(0)         # Hadamard
qc.x(1)         # Pauli-X
qc.ry(0.5, 2)   # RY rotation

# Puertas multi-qubit
qc.cx(0, 1)     # Controlled-X (CNOT)
qc.cz(1, 2)     # Controlled-Z
qc.swap(0, 2)   # Swap

# Puertas parametrizadas (para VQE/QAOA)
theta = Parameter('θ')
qc.ry(theta, 0)

# Visualización
qc.draw(output='text')
qc.draw(output='mpl')
```

**Critical Constraints:**
```
- Max qubits viable para simulación local: 20-25 qubits
- Max qubits para QSVM con 20K samples: 8 qubits
  Razón: Kernel matrix es (20000 x 20000), exponencial en # qubits

- Gate depth: Mantener < 100 para reducir errores en simulación
- Circuit complexity: O(n_qubits * feature_dimension)
```

### 2️⃣ Qiskit Machine Learning (>= 0.7)

**Purpose:** QSVM, QuantumKernel, Variational Algorithms

**Skills Required:**
```python
from qiskit_machine_learning.kernels import QuantumKernel
from qiskit_machine_learning.algorithms import QSVC
from qiskit.circuit.library import ZZFeatureMap, RealAmplitudes

# ZZFeatureMap: Feature map para datos clásicos
feature_map = ZZFeatureMap(
    feature_dimension=8,      # Dimensión de entrada
    reps=2,                   # Repeticiones del circuito
    entanglement='linear',    # linear, circular, full
    parameter_prefix='x'      # Nombre de parámetro
)

# Visualizar
print(f"Circuit depth: {feature_map.decompose().depth()}")
print(f"Number of qubits: {feature_map.num_qubits}")

# QuantumKernel: Computa kernel matrix (inner products entre estados cuánticos)
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import SamplerV2

backend = AerSimulator()
sampler = SamplerV2(backend=backend)

quantum_kernel = QuantumKernel(
    feature_map=feature_map,
    sampler=sampler,
    shots=128  # Número de mediciones (para ruido estadístico)
)

# Precompute kernel matrix
kernel_matrix = quantum_kernel.evaluate(X_quantum)
# Shape: (n_samples, n_samples) = (20000, 20000)

# Usar en SVM clásico con kernel precomputado
from sklearn.svm import SVC

svm = SVC(kernel='precomputed', C=1.0)
svm.fit(kernel_matrix_train, y_train)

# Predicción
kernel_matrix_test = quantum_kernel.evaluate(X_test, X_train)
y_pred = svm.predict(kernel_matrix_test)
```

**Best Practices:**
```python
# 1. Feature Normalization ANTES
assert X_quantum.min() >= 0 and X_quantum.max() <= 1

# 2. Batch processing si kernel matrix es grande
def batch_kernel_compute(X, batch_size=1000):
    n = X.shape[0]
    K = np.zeros((n, n))
    for i in range(0, n, batch_size):
        for j in range(0, n, batch_size):
            X_batch_i = X[i:i+batch_size]
            X_batch_j = X[j:j+batch_size]
            K[i:i+batch_size, j:j+batch_size] = (
                quantum_kernel.evaluate(X_batch_i, X_batch_j)
            )
    return K

# 3. Memory-efficient matrix storage
K = np.memmap('kernel_matrix.dat', dtype=np.float32, mode='w+', shape=(20000, 20000))
# ... compute y guardar en disk en lugar de RAM
```

### 3️⃣ Qiskit Aer Simulator (>= 0.12)

**Purpose:** Simulador cuántico clásico (sin hardware real)

**Skills Required:**
```python
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel

# Simulador básico (sin ruido)
simulator = AerSimulator(
    method='statevector',     # 'statevector', 'density_matrix', 'unitary'
    max_parallel_threads=4    # Paralelizar ejecuciones
)

# Con ruido simulado (más realista)
from qiskit_aer.noise import (
    pauli_error,
    depolarizing_error,
    thermal_relax_error
)

noise_model = NoiseModel()
p_error = 0.001  # 0.1% error rate

# Error en puertas de 1-qubit
error_1q = depolarizing_error(p_error, 1)
noise_model.add_all_qubit_quantum_error(error_1q, ['u1', 'u2', 'u3'])

# Error en puertas de 2-qubit
error_2q = depolarizing_error(p_error*2, 2)
noise_model.add_all_qubit_quantum_error(error_2q, ['cx', 'cz'])

# Usar
simulator = AerSimulator(
    method='statevector',
    noise_model=noise_model
)
```

**Performance Considerations:**
```
- Statevector method: Rápido, requiere 2^n memoria
- Density matrix: Más lento, maneja ruido mejor
- Unitary: Para circuitos sin medición

Tiempo estimado para 20K samples x 8 qubits:
  - Sin paralelización: 30-60 minutos
  - Con 4 threads: 8-15 minutos
  - Con GPU (si disponible): 2-5 minutos
```

### 4️⃣ Qiskit IBM Runtime (>= 0.14, OPCIONAL)

**Purpose:** Acceso a hardware cuántico real (IBM Quantum)

**Skills Required:**
```python
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Estimator

# Autentificación (requiere token IBM)
service = QiskitRuntimeService(channel='ibm_quantum', token='YOUR_TOKEN')

# Elegir backend disponible
backend = service.least_busy(
    simulator=False,  # Usar hardware real
    operational=True
)

# Usar runtime
with Sampler(backend) as sampler:
    result = sampler.run([qc]).result()
    quasi_dists = result.quasi_dists

# Notas:
# - Jobs en queue, esperan 1-24 horas
# - Costo en créditos IBM (limitados para usuarios gratuitos)
# - Resultados con ruido real del hardware
```

### 5️⃣ Memory Budget

```
Feature Map Circuit:        ~  5 MB
Kernel Matrix (20K x 20K, float64):  1.6 GB
Kernel Matrix (20K x 20K, float32):  0.8 GB
QSVM Model (serialized):    ~ 50 MB
Qiskit Environment:         ~ 200 MB

TOTAL BUDGET: 4 GB (recommended minimum for Quantum Agent)
```

---

## Skills del Risk_Validator_Agent

### 1️⃣ Metrics & Evaluation

**Purpose:** Evaluar modelos usando métricas de negocio

**Skills Required:**
```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, classification_report
)

# Métricas básicas
acc = accuracy_score(y_true, y_pred)
prec = precision_score(y_true, y_pred, zero_division=0)
rec = recall_score(y_true, y_pred, zero_division=0)
f1 = f1_score(y_true, y_pred, zero_division=0)
auc = roc_auc_score(y_true, y_pred_proba)

# Matriz de confusión
tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

# Curva ROC
fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)

# Reporte clasificación
print(classification_report(y_true, y_pred, digits=4))
```

### 2️⃣ Fairness Analysis (Optional: aif360)

**Purpose:** Detectar sesgo y disparidad en predicciones

**Skills Required:**
```python
# Manual fairness check
def fairness_analysis(y_true, y_pred, protected_attr):
    """
    Analiza disparidades por atributo protegido
    """
    fairness_report = {}
    
    for group_value in protected_attr.unique():
        mask = protected_attr == group_value
        y_true_group = y_true[mask]
        y_pred_group = y_pred[mask]
        
        fairness_report[group_value] = {
            'auc_roc': roc_auc_score(y_true_group, y_pred_group),
            'selection_rate': y_pred_group.mean(),
            'positive_rate': y_true_group.mean(),
            'n_samples': mask.sum()
        }
    
    return fairness_report

# Detección de disparidades
fairness_dict = fairness_analysis(y_test, y_pred, X_test['Employment_Type'])

# Reportar
for group, metrics in fairness_dict.items():
    print(f"{group}: AUC={metrics['auc_roc']:.3f}, Selection={metrics['selection_rate']:.1%}")
```

### 3️⃣ Visualization

**Purpose:** Crear gráficos informativos

**Skills Required:**
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Curva ROC
from sklearn.metrics import roc_curve, auc

fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)

plt.figure()
plt.plot(fpr, tpr, label=f'AUC={roc_auc:.3f}')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend()
plt.savefig('roc_curve.png')
plt.close()

# Matriz de confusión
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d')
plt.savefig('confusion_matrix.png')
plt.close()

# Feature Importance
importances = xgb_model.get_booster().get_score(importance_type='weight')
features = sorted(importances, key=importances.get, reverse=True)[:10]

plt.barh(features, [importances[f] for f in features])
plt.xlabel('Feature Importance')
plt.savefig('feature_importance.png')
plt.close()
```

### 4️⃣ Memory Budget

```
Métricas (JSON):            ~  1 MB
Visualizaciones (PNG):      ~ 10 MB
Comparación de modelos:     ~  2 MB

TOTAL BUDGET: 100 MB
```

---

## Dependencias Compartidas

```
joblib          >= 1.3      # Serialización de modelos
requests        >= 2.31     # HTTP requests
tqdm            >= 4.66     # Progress bars
python-dotenv   >= 1.0      # Manejo de .env
```

---

## Environment Setup

### requirements.txt

```
# Data Science & ML
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.1
scipy==1.11.2

# Classical ML
xgboost==2.0.1
optuna==3.0.5
imbalanced-learn==0.10.1

# Quantum ML
qiskit==0.43.0
qiskit-machine-learning==0.7.1
qiskit-aer==0.12.1
qiskit-ibm-runtime==0.14.0

# Utilities
joblib==1.3.1
matplotlib==3.7.2
seaborn==0.12.2
requests==2.31.0
python-dotenv==1.0.0
tqdm==4.66.1

# Fairness (optional)
aif360==0.5.0

# Development
jupyter==1.0.0
ipykernel==6.25.1
black==23.9.1
flake8==6.0.0
```

### Installation Commands

```bash
# 1. Create virtual environment
python -m venv venv_quantum_ml

# 2. Activate
# On Windows:
venv_quantum_ml\Scripts\activate
# On macOS/Linux:
source venv_quantum_ml/bin/activate

# 3. Upgrade pip
pip install --upgrade pip setuptools wheel

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify installation
python -c "import qiskit; print(qiskit.__version__)"
python -c "import xgboost; print(xgboost.__version__)"
```

---

## Resource Requirements

### Minimum Hardware

| Componente | Requerimiento |
|-----------|---------------|
| **RAM** | 8 GB (Classical), 4 GB adicional (Quantum) |
| **CPU** | 4 cores (recomendado 8+ para paralelización) |
| **Disk** | 5 GB (Qiskit + dependencias) |
| **GPU** | Opcional (acelera Qiskit si disponible) |

### Execution Time Estimates

| Etapa | Duración | Hardware |
|------|----------|----------|
| EDA + Preprocessing | 2-3 min | CPU |
| SMOTE + XGBoost Training | 3-5 min | CPU |
| PCA (8D) | < 1 min | CPU |
| Quantum Kernel Matrix | 30-60 min | CPU (Aer sim) / 5-10 min (GPU) |
| QSVM Training | 2-5 min | CPU |
| Risk Validation | 1-2 min | CPU |
| **Total** | **~40-75 min** | Single machine |

---

**Archivo creado:** `.copilot_agentic_workspace/skills.md`  
**Versión:** 1.0  
**Última actualización:** 2026-05-19
