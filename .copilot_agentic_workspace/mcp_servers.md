# 🔗 MCP SERVERS: Arquitectura de Contexto Distribuido (MCP-Style)

**Última actualización:** Mayo 2026  
**Concepto:** Modelar el workspace de VS Code como servidores MCP (Model Context Protocol) para mantener coherencia absoluta del dataset y trazabilidad de transformaciones

---

## 📋 Tabla de Contenidos

1. [Resumen Conceptual](#resumen-conceptual)
2. [File System Server (FSS)](#file-system-server-fss)
3. [Terminal Server (TS)](#terminal-server-ts)
4. [Indexing Server (IS)](#indexing-server-is)
5. [Registry & Metadata Management](#registry--metadata-management)
6. [Cross-Agent Communication Protocol](#cross-agent-communication-protocol)
7. [Auditing & Reproducibility](#auditing--reproducibility)

---

## Resumen Conceptual

El workspace de VS Code se organiza como un **sistema de servidores MCP virtuales** donde:

```
┌─────────────────────────────────────────────────────────────┐
│                  VS CODE WORKSPACE (ROOT)                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ File System Server (FSS)                             │   │
│  │ - Gestiona datasets, modelos, features               │   │
│  │ - Versionado de datos                                │   │
│  │ - Checksums SHA256 para integridad                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Terminal Server (TS)                                 │   │
│  │ - Ejecuta scripts con logging stderr/stdout          │   │
│  │ - Monitoreo de recursos (RAM, CPU)                   │   │
│  │ - Control de dependencias instaladas                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Indexing Server (IS)                                 │   │
│  │ - Índice de transformaciones aplicadas               │   │
│  │ - Rastreo de qué agente modificó qué                 │   │
│  │ - Detección de data leakage                          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Registry & Metadata                                  │   │
│  │ - Punto central de verdad (SSOT)                     │   │
│  │ - Auditoría de todas las operaciones                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## File System Server (FSS)

### 📁 Arquitectura de Directorios

```
.copilot_agentic_workspace/
│
├── data/                           # Datasets y features
│   ├── financial_risk_dataset.csv  # Dataset original (20K x 23)
│   ├── dataset_metadata.json       # Schema, shapes, checksums
│   │
│   ├── classical_features_8d.npy   # Features reducidas para Quantum
│   ├── classical_features_8d.json  # Metadata (shape, dtype, checksum)
│   │
│   ├── X_train_scaled.npy          # Training set escalado
│   ├── X_test_scaled.npy           # Test set escalado
│   ├── y_train.npy                 # Labels training
│   ├── y_test.npy                  # Labels test
│   │
│   ├── outliers_report.json        # Análisis de outliers
│   ├── missing_values_report.json  # Valores faltantes detectados
│   │
│   └── data_lineage.json           # Rastreo de transformaciones
│
├── models/                         # Modelos entrenados y métricas
│   ├── xgb_classical.pkl           # Modelo XGBoost
│   ├── classical_metrics.json      # Métricas Classical Agent
│   │
│   ├── qsvm_model.pkl              # Modelo QSVM
│   ├── quantum_metrics.json        # Métricas Quantum Agent
│   ├── kernel_matrix.npy           # Matriz kernel cuántica (1.6 GB)
│   │
│   ├── final_report.json           # Reporte final Risk_Validator
│   ├── model_comparison.json       # Comparación Classical vs Quantum
│   │
│   └── models_registry.json        # Registry de todos los modelos
│
├── scripts/                        # Scripts ejecutables
│   ├── 1_classical_ml_pipeline.py  # Script Data_Classical_ML_Agent
│   ├── 2_quantum_ml_pipeline.py    # Script Quantum_ML_Agent
│   ├── 3_risk_validator.py         # Script Risk_Validator_Agent
│   ├── 4_outlier_analysis.py       # Script análisis de outliers
│   │
│   └── scripts_log.json            # Registro de ejecución de scripts
│
├── documentation/                  # Documentación técnica
│   ├── CLASSICAL_ML_MODEL.md       # Documentación modelo clásico (matemática)
│   ├── QUANTUM_ML_MODEL.md         # Documentación modelo cuántico (física-matemática)
│   ├── MODEL_COMPARISON.md         # Comparación teórica
│   │
│   ├── zz_feature_map.png          # Visualización circuito cuántico
│   ├── roc_comparison.png          # Curvas ROC comparadas
│   ├── feature_importance.png      # Feature importance XGBoost
│   │
│   └── ARCHITECTURE.md             # Este archivo
│
├── agents.md                       # Definición de agentes
├── skills.md                       # Skills y dependencias
├── prompts_and_instructions.md     # System prompts
├── mcp_servers.md                  # Este archivo
│
├── .env                            # Variables de ambiente
├── requirements.txt                # Dependencias Python
└── README.md                       # Guía rápida de uso
```

### 🔍 File Integrity Protocol

Cada archivo en `data/` tiene un archivo `.metadata.json`:

```json
{
  "filename": "classical_features_8d.npy",
  "created_at": "2026-05-19T10:30:45Z",
  "created_by": "Data_Classical_ML_Agent",
  "shape": [20000, 8],
  "dtype": "float32",
  "file_size_bytes": 640000000,
  "sha256_checksum": "abc123def456...",
  "description": "PCA-reduced features (top-10 from XGBoost)",
  "source_files": ["financial_risk_dataset.csv"],
  "transformations_applied": [
    "missing_value_imputation",
    "feature_engineering_10_derived_features",
    "one_hot_encoding_3_categorical",
    "smote_balancing",
    "standardscaler_normalization",
    "pca_reduction_to_8_dimensions"
  ],
  "quality_checks": {
    "nan_count": 0,
    "inf_count": 0,
    "range_min": 0.0,
    "range_max": 1.0
  }
}
```

### 💾 Data Versioning

```
.copilot_agentic_workspace/data/.versions/
├── v1/
│   ├── classical_features_8d.npy
│   └── metadata.json
├── v2/
│   ├── classical_features_8d.npy  # Si se reejecuta con parámetros diferentes
│   └── metadata.json
└── LATEST -> v2/  # Symlink al versión más reciente
```

---

## Terminal Server (TS)

### 🖥️ Protocolo de Ejecución de Scripts

**Objetivo:** Ejecutar cada script (agente) en ambiente aislado, registrar outputs, monitorear recursos

```python
# Pseudocódigo para TS
class TerminalServer:
    def execute_agent_script(self, script_path, agent_name):
        """
        Ejecuta script de agente con logging y monitoreo
        """
        # 1. Pre-execution checks
        self.verify_environment()
        self.verify_dependencies()
        self.verify_input_files()
        
        # 2. Setup logging
        log_file = f".copilot_agentic_workspace/logs/{agent_name}_{timestamp}.log"
        
        # 3. Execute con monitoreo de recursos
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        process = subprocess.Popen(
            [f"venv_quantum_ml/bin/python", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        # 4. Log outputs
        with open(log_file, 'w') as f:
            f.write(f"=== {agent_name} EXECUTION LOG ===\n")
            f.write(f"Start: {start_time}\n")
            f.write(f"Duration: {time.time() - start_time:.1f}s\n")
            f.write(f"\nSTDOUT:\n{stdout}\n")
            if stderr:
                f.write(f"\nSTDERR:\n{stderr}\n")
        
        # 5. Validate execution
        if process.returncode != 0:
            raise Exception(f"{agent_name} failed with code {process.returncode}")
        
        # 6. Post-execution checks
        self.verify_output_files()
        self.verify_file_checksums()
        
        # 7. Update registry
        self.update_execution_registry(agent_name, success=True, duration=...)
        
        return True
```

### 📋 Execution Order & Dependencies

```
Step 1: Data_Classical_ML_Agent
├── Input:  financial_risk_dataset.csv
├── Output: classical_metrics.json
│          classical_features_8d.npy
│          y_test.npy
│
└─→ Validation: Check output files exist and have correct checksums

Step 2: Quantum_ML_Agent
├── Dependency: classical_features_8d.npy from Step 1 ✓
├── Input:  classical_features_8d.npy, y_test.npy
├── Output: quantum_metrics.json
│          quantum_predictions.npy
│          kernel_matrix.npy
│
└─→ Validation: Verify quantum_features shape <= 8

Step 3: Risk_Validator_Agent
├── Dependency: classical_metrics.json from Step 1 ✓
├── Dependency: quantum_metrics.json from Step 2 ✓
├── Input:  both metrics files
├── Output: final_report.json
│          model_comparison.json
│
└─→ Validation: Ensure recommendation is clear

Step 4 (Optional): Outlier Analysis
├── Dependency: None (pero puede usar X_train, X_test)
├── Input:  financial_risk_dataset.csv or preprocessed data
├── Output: outliers_report.json, outliers_visualization.png
│
└─→ Validation: Report must contain actionable insights
```

### 📊 Resource Monitoring

```python
# Registrar consumo de recursos durante ejecución
{
  "agent": "Data_Classical_ML_Agent",
  "start_time": "2026-05-19T10:30:00Z",
  "end_time": "2026-05-19T10:35:30Z",
  "duration_seconds": 330,
  "resources": {
    "peak_memory_mb": 1256,
    "peak_cpu_percent": 87,
    "avg_cpu_percent": 65
  },
  "exit_code": 0,
  "output_files_created": 5,
  "output_files_size_mb": 1234,
  "checksum_validation": "PASSED"
}
```

---

## Indexing Server (IS)

### 🔗 Índice de Transformaciones

Mantener **registro detallado** de cada transformación aplicada al dataset:

```json
{
  "dataset_name": "financial_risk_dataset.csv",
  "original_shape": [20000, 23],
  "original_sha256": "xyz789...",
  
  "transformations": [
    {
      "id": "txn_001",
      "agent": "Data_Classical_ML_Agent",
      "operation": "missing_value_imputation",
      "timestamp": "2026-05-19T10:30:15Z",
      "parameters": {
        "method": "KNNImputer",
        "k_neighbors": 5,
        "columns": ["Credit_Utilization_Ratio", "Collateral_Value"]
      },
      "input_shape": [20000, 23],
      "output_shape": [20000, 23],
      "nan_before": 4340,
      "nan_after": 0,
      "output_file": "data/imputed_dataset.csv",
      "status": "COMPLETED"
    },
    {
      "id": "txn_002",
      "agent": "Data_Classical_ML_Agent",
      "operation": "feature_engineering",
      "timestamp": "2026-05-19T10:31:00Z",
      "parameters": {
        "new_features": 10,
        "method": "domain_specific_banking_ratios"
      },
      "input_shape": [20000, 23],
      "output_shape": [20000, 33],
      "status": "COMPLETED"
    },
    {
      "id": "txn_003",
      "agent": "Data_Classical_ML_Agent",
      "operation": "train_test_split",
      "timestamp": "2026-05-19T10:31:30Z",
      "parameters": {
        "test_size": 0.2,
        "random_state": 42,
        "stratification": "y"
      },
      "split_ratio": "80/20",
      "train_samples": 16000,
      "test_samples": 4000,
      "status": "COMPLETED"
    },
    {
      "id": "txn_004",
      "agent": "Data_Classical_ML_Agent",
      "operation": "smote_balancing",
      "timestamp": "2026-05-19T10:32:00Z",
      "parameters": {
        "sampling_strategy": 0.7,
        "k_neighbors": 5
      },
      "input_shape": [16000, 33],
      "output_shape": [29360, 33],  # Synthetic samples added
      "class_distribution_before": {"0": 160, "1": 15840},
      "class_distribution_after": {"0": 11152, "1": 18208},
      "status": "COMPLETED"
    },
    {
      "id": "txn_005",
      "agent": "Data_Classical_ML_Agent",
      "operation": "normalization",
      "timestamp": "2026-05-19T10:32:30Z",
      "parameters": {
        "scaler_type": "StandardScaler",
        "fitted_on": "train_set_only"
      },
      "input_range": ["-5.2", "8.7"],
      "output_range": ["-2.5", "3.1"],
      "status": "COMPLETED"
    },
    {
      "id": "txn_006",
      "agent": "Data_Classical_ML_Agent",
      "operation": "pca_reduction",
      "timestamp": "2026-05-19T10:33:00Z",
      "parameters": {
        "target_components": 8,
        "variance_threshold": 0.85
      },
      "input_shape": [4000, 10],
      "output_shape": [4000, 8],
      "variance_explained": 0.917,
      "status": "COMPLETED"
    }
  ],
  
  "data_lineage_graph": {
    "nodes": [
      {"id": "original", "label": "financial_risk_dataset.csv", "type": "input"},
      {"id": "txn_001", "label": "Missing Value Imputation", "type": "transform"},
      {"id": "txn_002", "label": "Feature Engineering", "type": "transform"},
      {"id": "txn_003", "label": "Train/Test Split", "type": "transform"},
      {"id": "txn_004", "label": "SMOTE Balancing", "type": "transform"},
      {"id": "txn_005", "label": "Normalization", "type": "transform"},
      {"id": "txn_006", "label": "PCA Reduction", "type": "transform"},
      {"id": "quantum_features", "label": "8D Features (Quantum)", "type": "output"}
    ],
    "edges": [
      {"from": "original", "to": "txn_001"},
      {"from": "txn_001", "to": "txn_002"},
      {"from": "txn_002", "to": "txn_003"},
      {"from": "txn_003", "to": "txn_004"},
      {"from": "txn_004", "to": "txn_005"},
      {"from": "txn_005", "to": "txn_006"},
      {"from": "txn_006", "to": "quantum_features"}
    ]
  }
}
```

### 🚨 Data Leakage Detection

```python
class DataLeakageDetector:
    def check_leakage(self, transformation_index):
        """
        Detectar patrones comunes de data leakage
        """
        issues = []
        
        # Issue 1: Scaling antes de split
        for txn in transformation_index:
            if txn['operation'] == 'normalization' and \
               txn['timestamp'] < transformation_index[
                   next(i for i, t in enumerate(transformation_index) 
                        if t['operation'] == 'train_test_split')
               ]['timestamp']:
                issues.append({
                    'severity': 'CRITICAL',
                    'type': 'SCALING_BEFORE_SPLIT',
                    'message': 'Scaling applied before train/test split → DATA LEAKAGE'
                })
        
        # Issue 2: SMOTE en dataset completo
        for txn in transformation_index:
            if txn['operation'] == 'smote_balancing' and \
               txn['input_shape'] == self.original_shape:
                issues.append({
                    'severity': 'CRITICAL',
                    'type': 'SMOTE_ON_FULL_DATASET',
                    'message': 'SMOTE applied to full dataset → DATA LEAKAGE'
                })
        
        # Issue 3: Feature engineering con estadísticas globales
        if any(t['operation'] == 'feature_engineering' for t in transformation_index):
            # Verificar que no usó min/max/mean/std del dataset completo
            pass
        
        return issues
```

---

## Registry & Metadata Management

### 🗂️ Central Registry (SSOT - Single Source of Truth)

Archivo central: `.copilot_agentic_workspace/REGISTRY.json`

```json
{
  "project": "Credit Risk Analysis - Hybrid Classical + Quantum ML",
  "created_at": "2026-05-19T10:00:00Z",
  "updated_at": "2026-05-19T11:15:30Z",
  
  "agents": {
    "Data_Classical_ML_Agent": {
      "status": "COMPLETED",
      "last_execution": "2026-05-19T10:35:30Z",
      "execution_time_seconds": 330,
      "exit_code": 0,
      "output_files": [
        "models/xgb_classical.pkl",
        "models/classical_metrics.json",
        "data/classical_features_8d.npy"
      ],
      "checksums_validated": true
    },
    "Quantum_ML_Agent": {
      "status": "COMPLETED",
      "last_execution": "2026-05-19T11:00:45Z",
      "execution_time_seconds": 1815,
      "exit_code": 0,
      "output_files": [
        "models/qsvm_model.pkl",
        "models/quantum_metrics.json",
        "data/kernel_matrix.npy"
      ],
      "checksums_validated": true
    },
    "Risk_Validator_Agent": {
      "status": "COMPLETED",
      "last_execution": "2026-05-19T11:15:30Z",
      "execution_time_seconds": 120,
      "exit_code": 0,
      "output_files": [
        "models/final_report.json",
        "models/model_comparison.json"
      ],
      "checksums_validated": true
    }
  },
  
  "datasets": {
    "financial_risk_dataset.csv": {
      "original_shape": [20000, 23],
      "original_sha256": "xyz789...",
      "last_modified": "2026-05-19T10:00:00Z",
      "status": "IMMUTABLE"
    }
  },
  
  "data_quality": {
    "missing_values_found": true,
    "outliers_detected": 127,
    "outliers_percentage": 0.64,
    "class_imbalance_ratio": "99:1",
    "action_taken": "SMOTE balancing applied"
  },
  
  "execution_pipeline": {
    "step_1": {
      "agent": "Data_Classical_ML_Agent",
      "status": "✓ PASSED",
      "timestamp": "2026-05-19T10:35:30Z"
    },
    "step_2": {
      "agent": "Quantum_ML_Agent",
      "dependency_on": "step_1",
      "status": "✓ PASSED",
      "timestamp": "2026-05-19T11:00:45Z"
    },
    "step_3": {
      "agent": "Risk_Validator_Agent",
      "dependency_on": ["step_1", "step_2"],
      "status": "✓ PASSED",
      "timestamp": "2026-05-19T11:15:30Z"
    }
  },
  
  "final_recommendation": {
    "selected_model": "classical_xgboost",
    "auc_roc": 0.9421,
    "ready_for_production": true,
    "timestamp": "2026-05-19T11:15:30Z"
  }
}
```

---

## Cross-Agent Communication Protocol

### 📡 Handoff Format (JSON Schema)

Cuando Agent A entrega output a Agent B:

```json
{
  "handoff": {
    "from_agent": "Data_Classical_ML_Agent",
    "to_agent": "Quantum_ML_Agent",
    "timestamp": "2026-05-19T10:35:30Z",
    
    "data_transfer": {
      "file": "classical_features_8d.npy",
      "checksum_sha256": "abc123def456...",
      "file_size_bytes": 640000000,
      "shape": [20000, 8],
      "dtype": "float32"
    },
    
    "validation_rules": {
      "shape_constraint": "= (20000, 8)",
      "dtype_constraint": "float32",
      "range_constraint": "[0, 1]",
      "nan_constraint": "0",
      "inf_constraint": "0"
    },
    
    "validation_results": {
      "shape_valid": true,
      "dtype_valid": true,
      "range_valid": true,
      "nan_check_passed": true,
      "inf_check_passed": true,
      "checksum_verified": true,
      "overall_status": "✓ READY_FOR_PROCESSING"
    },
    
    "metadata": {
      "source_agent_version": "1.0",
      "receiving_agent_version": "1.0",
      "protocol_version": "1.0",
      "communication_timestamp": "2026-05-19T10:35:31Z"
    }
  }
}
```

### 🔄 Dependency Resolution

```python
class DependencyResolver:
    def resolve_dependencies(self, target_agent):
        """
        Verificar que todas las dependencias están satisfechas
        """
        dependencies = {
            "Data_Classical_ML_Agent": [],  # No tiene dependencias
            "Quantum_ML_Agent": [
                {
                    "file": "classical_features_8d.npy",
                    "source_agent": "Data_Classical_ML_Agent",
                    "required_fields": ["shape", "dtype", "range"]
                }
            ],
            "Risk_Validator_Agent": [
                {
                    "file": "classical_metrics.json",
                    "source_agent": "Data_Classical_ML_Agent"
                },
                {
                    "file": "quantum_metrics.json",
                    "source_agent": "Quantum_ML_Agent"
                }
            ]
        }
        
        for dep in dependencies.get(target_agent, []):
            if not self.file_exists(dep['file']):
                raise DependencyError(
                    f"Missing: {dep['file']} from {dep['source_agent']}"
                )
            
            if not self.validate_handoff(dep['file']):
                raise ValidationError(
                    f"Invalid: {dep['file']} failed validation"
                )
        
        return True
```

---

## Auditing & Reproducibility

### 📝 Audit Trail (Immutable Log)

```
.copilot_agentic_workspace/audit_trail.jsonl
```

Cada línea es un JSON event:

```json
{"timestamp": "2026-05-19T10:30:00Z", "event": "PROJECT_INITIALIZED", "actor": "system"}
{"timestamp": "2026-05-19T10:30:15Z", "event": "DATA_LOADED", "actor": "Data_Classical_ML_Agent", "file": "financial_risk_dataset.csv", "records": 20000}
{"timestamp": "2026-05-19T10:32:00Z", "event": "SMOTE_APPLIED", "actor": "Data_Classical_ML_Agent", "training_samples_before": 16000, "training_samples_after": 29360}
{"timestamp": "2026-05-19T10:35:30Z", "event": "MODEL_TRAINED", "actor": "Data_Classical_ML_Agent", "model_type": "XGBoost", "auc_roc": 0.9421}
{"timestamp": "2026-05-19T10:35:31Z", "event": "HANDOFF_INITIATED", "actor": "Data_Classical_ML_Agent", "to_agent": "Quantum_ML_Agent", "file": "classical_features_8d.npy"}
{"timestamp": "2026-05-19T11:00:45Z", "event": "MODEL_TRAINED", "actor": "Quantum_ML_Agent", "model_type": "QSVM", "auc_roc": 0.9134}
{"timestamp": "2026-05-19T11:15:30Z", "event": "RECOMMENDATION_ISSUED", "actor": "Risk_Validator_Agent", "selected_model": "classical_xgboost"}
{"timestamp": "2026-05-19T11:15:31Z", "event": "PROJECT_COMPLETED", "actor": "system"}
```

### ✨ Reproducibility Checklist

Para reproducir exactamente los mismos resultados:

```python
class ReproducibilityController:
    def verify_reproducibility(self):
        """
        Verificar que todo es reproducible
        """
        checks = {
            "random_states_fixed": {
                "numpy.random.seed(42)": True,
                "random.seed(42)": True,
                "qiskit seed": True
            },
            "dependencies_pinned": {
                "requirements.txt exists": True,
                "all versions explicit": True
            },
            "data_immutable": {
                "original dataset checksummed": True,
                "no modifications to original": True
            },
            "train_test_split_stratified": True,
            "scalers_fitted_on_train_only": True,
            "smote_applied_to_train_only": True,
            "cross_validation_seeded": True,
            "audit_trail_complete": True
        }
        
        return all(checks.values())
```

---

## Resumen de Garantías

| Garantía | Mecanismo | Verificación |
|----------|-----------|--------------|
| **Integridad de Datos** | SHA256 checksums | `.metadata.json` de cada archivo |
| **Trazabilidad Completa** | `audit_trail.jsonl` | Evento inmutable por cada operación |
| **No Data Leakage** | Índice de transformaciones | `DataLeakageDetector` |
| **Reproducibilidad** | Seeds fijos + Audit trail | `ReproducibilityController` |
| **Coherencia entre Agentes** | Handoff validation | Cross-agent checksum verification |
| **Resource Monitoring** | Logging en TS | `.logs/` directory |
| **Versioning** | `.versions/` directory | Histórico de cambios |

---

**Archivo creado:** `.copilot_agentic_workspace/mcp_servers.md`  
**Versión:** 1.0  
**Última actualización:** 2026-05-19
