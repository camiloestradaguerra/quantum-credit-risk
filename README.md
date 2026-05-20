# 🎯 Quantum Credit Risk

**Hybrid Quantum-Classical Machine Learning for Credit Risk Prediction & Financial Impact Optimization**

A production-ready credit risk assessment system combining classical XGBoost models with quantum machine learning (Qiskit) for enhanced financial decision-making. Includes REST API for real-time predictions and comprehensive financial modeling.

---

## 🎓 Executive Summary

### 🚀 Key Capabilities

| Feature | Details |
|---------|---------|
| **Classical ML** | XGBoost with optimal threshold optimization (0.1160) via cross-validation |
| **Quantum ML** | Qiskit FidelityQuantumKernel SVM with 8-qubit ZZFeatureMap circuit |
| **API Server** | FastAPI REST endpoints for single/batch predictions |
| **Financial Model** | Cost matrix-driven optimization: TP=$5K, TN=$500, FP=-$800, FN=-$30K |
| **Dataset** | 32,581 credit profiles, 21.82% default rate, real financial metrics |

### 📊 Performance (Classical @ Threshold=0.1160)

```
Accuracy:  64.86%
Precision: 37.98%
Recall:    93.04%  ← Maximize problem detection (minimize defaults)
F1 Score:  0.5380
AUC-ROC:   0.8983

Financial Impact: $3,346,900 NET GAIN
  ✓ True Positives:  1,322 × $5,000 = $6,610,000
  ✓ True Negatives:  2,933 × $500   = $1,466,500
  ✗ False Positives: 2,162 × $800   = $1,729,600
  ✗ False Negatives: 100 × $30,000  = $3,000,000
```

---

## 📁 Project Structure

```
quantum-credit-risk/
├── scripts/
│   ├── 1_classical_ml_pipeline_optimized.py    # XGBoost classifier
│   ├── 2_quantum_ml_pipeline.py               # Quantum SVM training
│   └── threshold_optimization_comparison.py    # CV vs Bayesian vs Optuna
├── main.py                                     # FastAPI server
├── models/
│   ├── xgb_classical.pkl                      # Trained XGBoost
│   ├── scaler.pkl                             # StandardScaler
│   ├── pca_8d.pkl                             # PCA reducer (18D→8D)
│   └── classical_metrics.json                 # Performance metrics
├── data/
│   └── financial_risk_dataset.csv             # Input data (32.5K records)
├── requirements.txt                           # Python dependencies
├── .gitignore
├── README.md
└── .env.example
```

---

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.11+**
- **pip/conda** for package management
- **Git** for version control

### 1️⃣ Clone Repository
```bash
git clone https://github.com/yourusername/quantum-credit-risk.git
cd quantum-credit-risk
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings (if needed for external services)
```

---

## 🚀 Quick Start

### Option A: Run Classical Pipeline
```bash
cd scripts
python 1_classical_ml_pipeline_optimized.py
```
**Output:** Trained model, metrics, PCA transformer saved to `models/`

### Option B: Run Quantum Pipeline
```bash
cd scripts
python 2_quantum_ml_pipeline.py
```
**Output:** Quantum kernel matrices, quantum SVM model, comparison metrics

### Option C: Start FastAPI Server
```bash
python main.py
```
Server starts on `http://localhost:8000`

- 📖 **Swagger Docs:** `http://localhost:8000/docs`
- ❤️ **Health Check:** `http://localhost:8000/health`
- 🔮 **Make Prediction:** `POST /predict`

---

## 📡 API Endpoints

### 1. Health Check
```bash
curl http://localhost:8000/health
```
**Response:**
```json
{
  "status": "OK",
  "model": "XGBoost Credit Risk Classifier",
  "threshold": 0.1160,
  "auc_roc": 0.8983,
  "timestamp": "2026-05-19T19:37:42.326142"
}
```

### 2. Get Model Info
```bash
curl http://localhost:8000/model_info
```
**Response:** Full model metadata, metrics, financial parameters

### 3. Single Prediction
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"raw_features": [45, 55000, 2, 15000, 8.5, 0.25, 5, 0, 0, 0.5, 0.3, 0.2, 0.1, 0.4, 0.6, 0.2, 0.3, 0.15]}'
```

### 4. Batch Predictions
```bash
curl -X POST http://localhost:8000/predict_batch \
  -H "Content-Type: application/json" \
  -d '{"samples": [[...], [...]]}'
```

---

## 🔧 Feature Engineering

**18 Features** (10 engineered + 8 original):

### Original Features
1. Age, Income, Employment Length, Loan Amount
2. Interest Rate, Loan Status, Loan Purpose, Loan Grade
3. Loan Percent Income, Default History

### Engineered Features
- `debt_to_income_ratio`
- `interest_rate_risk`
- `employment_stability_score`
- `income_loan_ratio`
- `default_probability_estimate`
- `credit_behavior_score`
- `debt_burden_index`
- `income_stability_index`
- `recent_default_history`
- `composite_risk_score`

**Dimensionality Reduction:** PCA reduces 18D → 8D (97.88% variance retained)

---

## 🎯 Threshold Optimization

Three optimization methods compared:

| Method | Threshold | Financial Value | Strategy |
|--------|-----------|-----------------|----------|
| **Cross-Validation** | 0.1160 | $13.35M | ✅ **CHOSEN** - Robust across folds |
| **Bayesian** | 0.0632 | $4.19M | Test-specific overfitting |
| **Optuna** | 0.0620 | $4.16M | Test-specific overfitting |

**Rationale:** 0.1160 (CV) selected for production robustness despite lower test-specific value (0.08 @ $4.18M), prevents overfitting on test set.

---

## 🌌 Quantum ML Implementation

### Quantum Circuit
- **Type:** ZZFeatureMap (entangling feature map)
- **Qubits:** 8 (PCA-reduced features)
- **Repetitions:** 2
- **Circuit Depth:** 67
- **Backend:** Qiskit Aer Simulator (statevector)

### Training Data
- **Samples:** 200 (downsampled from 34,642 due to memory constraints)
- **Kernel Matrix:** 200×200 (computed in ~13 minutes)
- **Fidelity Range:** [0.0000, 1.0000] (very sparse, mean=0.0137)

### Test Data
- **Samples:** 6,517 (full test set)
- **Kernel Matrix:** 6,517×200 (computing, ~30 min estimated)

---

## 📊 Financial Cost Matrix

| Classification | Value | Rationale |
|---|---|---|
| **TP (Default Caught)** | +$5,000 | Prevented loss |
| **TN (Good Approved)** | +$500 | Interest revenue |
| **FP (Good Rejected)** | -$800 | Lost opportunity + admin |
| **FN (Default Missed)** | -$30,000 | **Most expensive** - actual default |

**Impact:** High recall (93.04%) prioritizes catching defaults over false positives.

---

## 🔬 Dependencies

```
Core ML:
  - numpy==1.24.3
  - pandas==2.0.3
  - scikit-learn==1.8.0
  - xgboost==3.2.0
  - imbalanced-learn (SMOTE)

Quantum:
  - qiskit==2.4.1
  - qiskit-aer (simulator)

API:
  - fastapi
  - uvicorn
  - pydantic

Optimization:
  - optuna==3.0.5
  - scipy
  - statsmodels

Utilities:
  - matplotlib
  - seaborn
  - joblib
```

See `requirements.txt` for exact versions.

---

## 📈 Workflow

```
1. Load & Explore Data
   └─ 32,581 records, 21.82% default rate
   
2. Preprocess
   └─ KNNImputer(k=5) → SMOTE(0.7) → StandardScaler → PCA(18D→8D)
   
3. Train Classical Model
   └─ XGBoost (n_estimators=200, max_depth=6, scale_pos_weight=1.4286)
   
4. Optimize Threshold (3 methods)
   └─ CV: 0.1160 ✅ | Bayesian: 0.0632 | Optuna: 0.0620
   
5. Train Quantum Model (Parallel)
   └─ FidelityQuantumKernel SVM on 8D features
   
6. Deploy FastAPI Server
   └─ Real-time predictions, batch processing
   
7. Compare Results
   └─ Classical vs Quantum performance metrics
```

---

## 🧪 Testing

```bash
# Test classical pipeline
python -m pytest scripts/1_classical_ml_pipeline_optimized.py -v

# Test API endpoints
pytest tests/test_api.py -v

# Test predictions
python -c "from main import app; print('API OK')"
```

---

## 📊 Results Summary

### Classical ML (XGBoost)
- ✅ AUC-ROC: 0.8983
- ✅ Recall: 93.04% (strong default detection)
- ✅ Financial Value: $3.35M

### Quantum ML (FidelityQuantumKernel SVM)
- ⏳ **Status:** Training in progress
- 📝 Training kernel: ✅ Complete (13 min)
- 📝 Test kernel: ⏳ Computing (30 min estimated)
- 📊 **Comparison:** Results available upon completion

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👤 Author

Created as part of hybrid Quantum+Classical ML credit risk analysis research.

---

## 🔗 Resources

- **Qiskit Documentation:** https://qiskit.org/documentation
- **FastAPI:** https://fastapi.tiangolo.com
- **XGBoost:** https://xgboost.readthedocs.io
- **Scikit-learn:** https://scikit-learn.org

---

## ⚠️ Disclaimer

This model is for demonstration purposes. For production financial systems:
- Validate against regulatory requirements (Fair Lending, FCRA, etc.)
- Include explainability/interpretability (SHAP, LIME)
- Implement monitoring and retraining pipelines
- Conduct fairness audits across demographic groups

---

**Last Updated:** May 19, 2026  
**Status:** 🟢 Active Development  
**Python Version:** 3.11.7  
**Quantum Execution:** In Progress ⏳
