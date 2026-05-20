#!/usr/bin/env python3
"""
QUANTUM API - Credit Risk Prediction
=====================================

FastAPI server for quantum machine learning predictions.
Uses QSVM (Quantum SVM) with FidelityQuantumKernel.

Endpoints:
  GET  /health           - Health check
  POST /predict          - Quantum prediction (8 features)
  GET  /docs             - Swagger UI
  GET  /quantum-metrics  - Model metrics

Port: 8001 (independent from classical API on 8000)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pickle
import json
import logging
from pathlib import Path
from datetime import datetime
import sys

# Qiskit
from qiskit.circuit.library import ZZFeatureMap
from qiskit_aer import AerSimulator
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from sklearn.preprocessing import MinMaxScaler

import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

APP_NAME = "Quantum Credit Risk API"
APP_VERSION = "1.0.0"
QUANTUM_MODEL_PORT = 8001

# Paths
SCRIPT_DIR = Path(__file__).parent.parent
MODELS_PATH = SCRIPT_DIR / 'models'
LOGS_PATH = SCRIPT_DIR / 'logs'

LOGS_PATH.mkdir(exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_PATH / 'quantum_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Quantum parameters (must match training)
N_QUBITS = 8
FEATURE_MAP_REPS = 2

# ============================================================================
# LOAD MODELS
# ============================================================================

def load_quantum_models():
    """Load QSVM model, kernel matrices, and scaler."""
    logger.info("Loading quantum models...")
    
    try:
        # Load QSVM model
        with open(MODELS_PATH / 'qsvm_model.pkl', 'rb') as f:
            qsvm = pickle.load(f)
        logger.info("[OK] Loaded QSVM model")
        
        # Load training kernel matrix
        with open(MODELS_PATH / 'qsvm_K_train.pkl', 'rb') as f:
            K_train = pickle.load(f)
        logger.info(f"[OK] Loaded K_train shape: {K_train.shape}")
        
        # Load training features (for kernel computation)
        X_train_kernel = np.load(MODELS_PATH / 'qsvm_X_train_kernel.npy')
        logger.info(f"[OK] Loaded X_train_kernel shape: {X_train_kernel.shape}")
        
        # Load scaler
        with open(MODELS_PATH / 'qsvm_scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        logger.info("[OK] Loaded feature scaler")
        
        # Load metrics
        with open(MODELS_PATH / 'quantum_metrics_optimized.json', 'r') as f:
            metrics = json.load(f)
        logger.info("[OK] Loaded metrics")
        
        # Create quantum kernel
        feature_map = ZZFeatureMap(feature_dimension=N_QUBITS, reps=FEATURE_MAP_REPS)
        quantum_kernel = FidelityQuantumKernel(feature_map=feature_map)
        logger.info(f"[OK] Created quantum kernel (ZZFeatureMap, {N_QUBITS} qubits, {FEATURE_MAP_REPS} reps)")
        
        return qsvm, K_train, X_train_kernel, scaler, quantum_kernel, metrics
        
    except FileNotFoundError as e:
        logger.error(f"[FAIL] Model files not found: {e}")
        logger.error("Ensure quantum pipeline has been executed: python scripts/2_quantum_ml_pipeline_OPTIMIZED.py")
        raise
    except Exception as e:
        logger.error(f"[FAIL] Error loading models: {e}", exc_info=True)
        raise

# ============================================================================
# INITIALIZE APP & MODELS
# ============================================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Quantum Machine Learning API for Credit Risk Prediction"
)

# Load models at startup
try:
    QSVM, K_TRAIN, X_TRAIN_KERNEL, SCALER, QUANTUM_KERNEL, METRICS = load_quantum_models()
    MODELS_LOADED = True
    logger.info("=" * 80)
    logger.info(f"QUANTUM API READY - Port {QUANTUM_MODEL_PORT}")
    logger.info(f"Model: QSVM with {len(K_TRAIN)} training samples")
    logger.info(f"Quantum Circuit: ZZFeatureMap ({N_QUBITS} qubits, {FEATURE_MAP_REPS} reps)")
    logger.info(f"Test AUC-ROC: {METRICS['test']['auc_roc']:.4f}")
    logger.info("=" * 80)
except Exception as e:
    logger.error(f"Failed to load models: {e}")
    MODELS_LOADED = False

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    models_loaded: bool
    api_version: str

class PredictionRequest(BaseModel):
    """Credit risk prediction request."""
    age: float
    income: float
    loan_amount: float
    interest_rate: float
    employment_length: float
    credit_history: float
    default_on_file: int  # 0 or 1
    loan_percent_income: float

    class Config:
        example = {
            "age": 35.0,
            "income": 50000.0,
            "loan_amount": 10000.0,
            "interest_rate": 8.5,
            "employment_length": 5.0,
            "credit_history": 10.0,
            "default_on_file": 0,
            "loan_percent_income": 0.20
        }

class PredictionResponse(BaseModel):
    """Credit risk prediction response."""
    prediction: int  # 0 = non-default, 1 = default
    probability: float
    risk_score: float
    risk_category: str
    model: str
    timestamp: str

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if MODELS_LOADED else "degraded",
        timestamp=datetime.now().isoformat(),
        models_loaded=MODELS_LOADED,
        api_version=APP_VERSION
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Quantum SVM prediction for credit risk.
    
    Input: 8 financial features
    Process: 
      1. Normalize features to [0, 2π]
      2. Compute quantum kernel against training samples
      3. Predict using QSVM
    Output: Prediction (0/1) with probability
    """
    if not MODELS_LOADED:
        raise HTTPException(status_code=503, detail="Models not loaded. Check server logs.")
    
    try:
        # Feature vector (8 features)
        X_sample = np.array([[
            request.age,
            request.income,
            request.loan_amount,
            request.interest_rate,
            request.employment_length,
            request.credit_history,
            request.default_on_file,
            request.loan_percent_income
        ]])
        
        # Normalize to [0, 2*pi]
        X_sample_norm = SCALER.transform(X_sample)
        
        # Compute quantum kernel (sample vs training)
        logger.info(f"Computing quantum kernel for sample prediction...")
        K_sample = QUANTUM_KERNEL.evaluate(X_sample_norm, X_train_kernel)
        
        # Predict
        y_pred = QSVM.predict(K_sample)[0]
        y_score = QSVM.decision_function(K_sample)[0]
        
        # Risk score (distance from hyperplane)
        risk_score = float(np.abs(y_score))
        
        # Risk category
        if y_pred == 1:
            if risk_score > 0.7:
                risk_category = "HIGH_RISK"
            elif risk_score > 0.3:
                risk_category = "MEDIUM_RISK"
            else:
                risk_category = "LOW_RISK_DEFAULT"
        else:
            if risk_score > 0.7:
                risk_category = "LOW_RISK"
            else:
                risk_category = "VERY_LOW_RISK"
        
        logger.info(f"Prediction: {y_pred} (score: {y_score:.4f}, category: {risk_category})")
        
        return PredictionResponse(
            prediction=int(y_pred),
            probability=float(np.clip(y_score, 0, 1)),
            risk_score=risk_score,
            risk_category=risk_category,
            model="QSVM (Quantum SVM)",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/quantum-metrics")
async def get_metrics():
    """Get trained model metrics."""
    if not MODELS_LOADED:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    return {
        "model": "QSVM (Quantum SVM)",
        "training_samples": len(K_TRAIN),
        "quantum_circuit": f"ZZFeatureMap({N_QUBITS} qubits, {FEATURE_MAP_REPS} reps)",
        "metrics": METRICS
    }

@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "healthy" if MODELS_LOADED else "degraded",
        "port": QUANTUM_MODEL_PORT,
        "endpoints": {
            "/health": "Health check",
            "/predict": "Make prediction (POST)",
            "/quantum-metrics": "Model metrics",
            "/docs": "Swagger UI"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=QUANTUM_MODEL_PORT,
        log_level="info"
    )
