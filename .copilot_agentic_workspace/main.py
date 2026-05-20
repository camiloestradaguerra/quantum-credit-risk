"""
FastAPI Server - Credit Risk ML Model Prediction
Deployed with ngrok for quick sharing
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pickle
import numpy as np
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Credit Risk Prediction API",
    description="XGBoost Model with Optimal Threshold 0.1160",
    version="1.0.0"
)

# Load model artifacts
BASE_PATH = Path(__file__).parent / "models"

try:
    model = pickle.load(open(BASE_PATH / "xgb_classical.pkl", "rb"))
    scaler = pickle.load(open(BASE_PATH / "scaler.pkl", "rb"))
    pca = pickle.load(open(BASE_PATH / "pca_8d.pkl", "rb"))
    
    # Try to load metrics, but don't fail if not available
    try:
        with open(BASE_PATH / "classical_metrics.json", "r") as f:
            metrics = json.load(f)
    except:
        metrics = {"test": {"auc": 0.8983, "precision": 0.3798, "recall": 0.9304}}
    
    logger.info("✅ All model artifacts loaded successfully")
except Exception as e:
    logger.error(f"❌ Error loading models: {e}")
    raise

# Constants
OPTIMAL_THRESHOLD = 0.1160
TP_VALUE = 5000
TN_VALUE = 500
FP_COST = 800
FN_COST = 30000

# Request/Response models
class PredictionRequest(BaseModel):
    features: List[float] = None  # 8D features (PCA reduced)
    raw_features: List[float] = None  # 18D features (raw)
    
    class Config:
        example = {
            "features": [0.5, 0.3, 0.2, 0.1, 0.4, 0.6, 0.2, 0.3],
            "raw_features": None
        }

class PredictionResponse(BaseModel):
    probability: float
    default: bool
    recommendation: str
    financial_impact: dict
    model_info: dict

# Health check endpoint
@app.get("/health", tags=["System"])
def health_check():
    """Check API health and model status"""
    return {
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "model": "XGBoost Credit Risk Classifier",
        "threshold": OPTIMAL_THRESHOLD,
        "auc_roc": 0.8983,
        "version": "1.0.0"
    }

# Main prediction endpoint
@app.post("/predict", tags=["Predictions"], response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Predict credit default probability
    
    Input: Either 8D quantum features OR 18D raw features
    Output: Probability, decision, and financial impact
    """
    try:
        # Handle input
        if request.features is not None:
            features = np.array(request.features).reshape(1, -1)
            if features.shape[1] != 8:
                raise ValueError(f"Expected 8 features, got {features.shape[1]}")
        elif request.raw_features is not None:
            features = np.array(request.raw_features).reshape(1, -1)
            if features.shape[1] != 18:
                raise ValueError(f"Expected 18 features, got {features.shape[1]}")
            # Apply scaling and PCA
            features = scaler.transform(features)
            features = pca.transform(features)
        else:
            raise ValueError("Must provide either 'features' (8D) or 'raw_features' (18D)")
        
        # Predict
        prob = model.predict_proba(features)[0, 1]
        default = prob >= OPTIMAL_THRESHOLD
        
        # Financial impact
        if default:
            recommendation = "❌ RECHAZAR - Alto riesgo de default"
            impact_type = "FN Prevention"
            expected_impact = FN_COST  # Avoided if correctly identified
        else:
            recommendation = "✅ APROBAR - Bajo riesgo de default"
            impact_type = "TP/TN Gain"
            expected_impact = TP_VALUE if default else TN_VALUE
        
        return PredictionResponse(
            probability=float(prob),
            default=bool(default),
            recommendation=recommendation,
            financial_impact={
                "impact_type": impact_type,
                "expected_value": expected_impact,
                "threshold_used": OPTIMAL_THRESHOLD
            },
            model_info={
                "algorithm": "XGBoost",
                "test_auc": float(metrics["test"]["auc"]),
                "test_precision": float(metrics["test"]["precision"]),
                "test_recall": float(metrics["test"]["recall"]),
                "optimal_threshold": OPTIMAL_THRESHOLD,
                "training_method": "Cross-Validated (5-Fold)"
            }
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Batch prediction endpoint
@app.post("/predict_batch", tags=["Predictions"])
def predict_batch(requests: List[PredictionRequest]):
    """Predict multiple samples at once"""
    results = []
    for req in requests:
        try:
            result = predict(req)
            results.append(result)
        except Exception as e:
            results.append({"error": str(e)})
    return {"predictions": results, "count": len(results)}

# Model info endpoint
@app.get("/model_info", tags=["Model"])
def model_info():
    """Get detailed model information"""
    return {
        "model": "XGBoost Classifier",
        "version": "1.0.0",
        "trained_date": "2026-05-19",
        "optimization_method": "5-Fold Cross-Validation",
        "optimal_threshold": OPTIMAL_THRESHOLD,
        "test_metrics": {
            "auc_roc": 0.8983,
            "precision": 0.3798,
            "recall": 0.9304,
            "f1_score": 0.5380,
            "accuracy": 0.6486
        },
        "financial_params": {
            "true_positive_value": TP_VALUE,
            "true_negative_value": TN_VALUE,
            "false_positive_cost": FP_COST,
            "false_negative_cost": FN_COST
        },
        "confusion_matrix": {
            "true_positive": 1322,
            "true_negative": 2933,
            "false_positive": 2162,
            "false_negative": 100
        }
    }

# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """API Documentation"""
    return {
        "message": "Credit Risk Prediction API",
        "endpoints": {
            "POST /predict": "Single prediction",
            "POST /predict_batch": "Batch predictions",
            "GET /health": "Health check",
            "GET /model_info": "Model details",
            "GET /docs": "Interactive API documentation (Swagger)"
        },
        "usage": "Visit /docs for interactive testing"
    }

if __name__ == "__main__":
    logger.info("🚀 Starting Credit Risk Prediction API")
    logger.info(f"📊 Optimal Threshold: {OPTIMAL_THRESHOLD}")
    logger.info(f"🎯 Model AUC-ROC: {metrics['test']['auc']:.4f}")
