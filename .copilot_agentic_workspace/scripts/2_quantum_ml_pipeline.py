#!/usr/bin/env python3
"""
QUANTUM ML PIPELINE - Quantum_ML_Agent
======================================

Agent: Quantum_ML_Agent
Version: 3.0 - Real Dataset with FidelityQuantumKernel

Pipeline Steps:
  1. Load 8D quantum features (from Classical Agent)
  2. Normalize features [0, 2π]
  3. Create ZZFeatureMap circuit
  4. Compute quantum kernel matrix with FidelityQuantumKernel
  5. Train Quantum SVM
  6. Evaluate QSVM
  7. Compare with Classical XGBoost

Input: quantum_X_train_8d.npy, quantum_X_test_8d.npy
Output: quantum_metrics.json
"""

import numpy as np
import json
import pickle
import logging
from pathlib import Path
from datetime import datetime
import time

# Scikit-learn
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix
)

# Qiskit
from qiskit.circuit.library import ZZFeatureMap
from qiskit_aer import AerSimulator
from qiskit_machine_learning.kernels import FidelityQuantumKernel

import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# Setup paths
SCRIPT_DIR = Path(__file__).parent.parent
DATA_PATH = SCRIPT_DIR / 'data'
MODELS_PATH = SCRIPT_DIR / 'models'
LOGS_PATH = SCRIPT_DIR / 'logs'

MODELS_PATH.mkdir(exist_ok=True)
LOGS_PATH.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_PATH / 'quantum_ml_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Quantum parameters
N_QUBITS = 8
FEATURE_MAP_REPS = 2
MAX_SAMPLES_FOR_KERNEL = 200  # Limit for memory

# ============================================================================
# STEP 1: LOAD FEATURES
# ============================================================================

def load_quantum_features():
    """Load 8D features exported by Classical Agent."""
    logger.info("=" * 80)
    logger.info("STEP 1: LOAD 8D QUANTUM FEATURES")
    logger.info("=" * 80)
    
    X_train = np.load(DATA_PATH / 'quantum_X_train_8d.npy')
    X_test = np.load(DATA_PATH / 'quantum_X_test_8d.npy')
    y_train = np.load(DATA_PATH / 'quantum_y_train.npy')
    y_test = np.load(DATA_PATH / 'quantum_y_test.npy')
    
    logger.info(f"X_train shape: {X_train.shape}")
    logger.info(f"X_test shape: {X_test.shape}")
    logger.info(f"y_train shape: {y_train.shape}")
    logger.info(f"y_test shape: {y_test.shape}")
    logger.info(f"Train default rate: {y_train.mean():.2%}")
    logger.info(f"Test default rate: {y_test.mean():.2%}")
    
    return X_train, X_test, y_train, y_test

# ============================================================================
# STEP 2: NORMALIZE FEATURES
# ============================================================================

def normalize_quantum_features(X_train, X_test):
    """Normalize features to [0, 2π] for quantum encoding."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 2: NORMALIZE FEATURES [0, 2π]")
    logger.info("=" * 80)
    
    scaler = MinMaxScaler(feature_range=(0, 2 * np.pi))
    X_train_norm = scaler.fit_transform(X_train)
    X_test_norm = scaler.transform(X_test)
    
    logger.info(f"Train range: [{X_train_norm.min():.4f}, {X_train_norm.max():.4f}]")
    logger.info(f"Test range: [{X_test_norm.min():.4f}, {X_test_norm.max():.4f}]")
    
    return X_train_norm, X_test_norm, scaler

# ============================================================================
# STEP 3: CREATE QUANTUM CIRCUIT
# ============================================================================

def create_zz_feature_map(n_qubits, reps):
    """Create ZZFeatureMap quantum circuit."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 3: CREATE QUANTUM CIRCUIT (ZZFeatureMap)")
    logger.info("=" * 80)
    
    feature_map = ZZFeatureMap(feature_dimension=n_qubits, reps=reps)
    
    logger.info(f"Circuit: ZZFeatureMap")
    logger.info(f"Qubits: {n_qubits}")
    logger.info(f"Reps: {reps}")
    logger.info(f"Circuit depth: {feature_map.decompose().depth()}")
    
    return feature_map

# ============================================================================
# STEP 4: COMPUTE KERNEL MATRIX
# ============================================================================

def compute_quantum_kernel(X_train, X_test, feature_map, max_samples=200):
    """Compute quantum kernel matrix with FidelityQuantumKernel."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 4: COMPUTE QUANTUM KERNEL MATRIX")
    logger.info("=" * 80)
    logger.info(f"Max samples: {max_samples} (memory limitation)")
    
    # Limit training samples for memory
    if len(X_train) > max_samples:
        logger.info(f"Downsampling training from {len(X_train)} to {max_samples}")
        indices = np.random.choice(len(X_train), max_samples, replace=False)
        X_train_kernel = X_train[indices]
    else:
        X_train_kernel = X_train
    
    logger.info("Creating FidelityQuantumKernel...")
    try:
        # Create FidelityQuantumKernel (uses default StatevectorFidelity)
        quantum_kernel = FidelityQuantumKernel(feature_map=feature_map)
        
        logger.info(f"Computing training kernel matrix ({len(X_train_kernel)} x {len(X_train_kernel)})...")
        logger.info("This may take several minutes...")
        start_kernel_time = datetime.now()
        
        K_train = quantum_kernel.evaluate(X_train_kernel)
        
        elapsed_kernel = datetime.now() - start_kernel_time
        logger.info(f"Training kernel computed in {elapsed_kernel}")
        logger.info(f"Training kernel shape: {K_train.shape}")
        logger.info(f"Kernel matrix stats - min: {K_train.min():.4f}, max: {K_train.max():.4f}, mean: {K_train.mean():.4f}")
        
        logger.info(f"Computing test kernel matrix ({len(X_test)} x {len(X_train_kernel)})...")
        K_test = quantum_kernel.evaluate(X_test, X_train_kernel)
        logger.info(f"Test kernel shape: {K_test.shape}")
        logger.info(f"Test kernel matrix stats - min: {K_test.min():.4f}, max: {K_test.max():.4f}, mean: {K_test.mean():.4f}")
        
        return K_train, K_test, X_train_kernel
        
    except Exception as e:
        logger.error(f"Error in quantum kernel computation: {str(e)}", exc_info=True)
        raise

# ============================================================================
# STEP 5: TRAIN QSVM
# ============================================================================

def train_quantum_svm(K_train, y_train_kernel):
    """Train Quantum SVM using precomputed kernel."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 5: TRAIN QUANTUM SVM")
    logger.info("=" * 80)
    
    logger.info(f"Training SVM with kernel matrix...")
    logger.info(f"Train samples: {len(K_train)}, Default rate: {y_train_kernel.mean():.2%}")
    
    # Train SVM with precomputed kernel
    qsvm = SVC(kernel='precomputed', C=1.0)
    qsvm.fit(K_train, y_train_kernel)
    
    logger.info(f"Support vectors: {len(qsvm.support_vectors_)}")
    
    return qsvm

# ============================================================================
# STEP 6: EVALUATE QSVM
# ============================================================================

def evaluate_qsvm(qsvm, K_train, K_test, y_train, y_test):
    """Evaluate Quantum SVM."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 6: EVALUATE QUANTUM SVM")
    logger.info("=" * 80)
    
    # Predictions
    y_train_pred = qsvm.predict(K_train)
    y_test_pred = qsvm.predict(K_test)
    y_train_score = qsvm.decision_function(K_train)
    y_test_score = qsvm.decision_function(K_test)
    
    # Training metrics
    logger.info("\n--- TRAINING SET METRICS ---")
    train_acc = accuracy_score(y_train, y_train_pred)
    train_prec = precision_score(y_train, y_train_pred, zero_division=0)
    train_rec = recall_score(y_train, y_train_pred, zero_division=0)
    train_f1 = f1_score(y_train, y_train_pred, zero_division=0)
    train_auc = roc_auc_score(y_train, y_train_score)
    
    logger.info(f"Accuracy:  {train_acc:.4f}")
    logger.info(f"Precision: {train_prec:.4f}")
    logger.info(f"Recall:    {train_rec:.4f}")
    logger.info(f"F1-Score:  {train_f1:.4f}")
    logger.info(f"AUC-ROC:   {train_auc:.4f}")
    
    # Test metrics
    logger.info("\n--- TEST SET METRICS ---")
    test_acc = accuracy_score(y_test, y_test_pred)
    test_prec = precision_score(y_test, y_test_pred, zero_division=0)
    test_rec = recall_score(y_test, y_test_pred, zero_division=0)
    test_f1 = f1_score(y_test, y_test_pred, zero_division=0)
    test_auc = roc_auc_score(y_test, y_test_score)
    
    logger.info(f"Accuracy:  {test_acc:.4f}")
    logger.info(f"Precision: {test_prec:.4f}")
    logger.info(f"Recall:    {test_rec:.4f}")
    logger.info(f"F1-Score:  {test_f1:.4f}")
    logger.info(f"AUC-ROC:   {test_auc:.4f}")
    
    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_test, y_test_pred).ravel()
    logger.info(f"\nConfusion Matrix (test):")
    logger.info(f"  TP: {tp}, FP: {fp}")
    logger.info(f"  FN: {fn}, TN: {tn}")
    
    metrics = {
        'train': {
            'accuracy': float(train_acc),
            'precision': float(train_prec),
            'recall': float(train_rec),
            'f1': float(train_f1),
            'auc_roc': float(train_auc)
        },
        'test': {
            'accuracy': float(test_acc),
            'precision': float(test_prec),
            'recall': float(test_rec),
            'f1': float(test_f1),
            'auc_roc': float(test_auc)
        },
        'confusion_matrix': {'TP': int(tp), 'FP': int(fp), 'FN': int(fn), 'TN': int(tn)}
    }
    
    return metrics

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Execute Quantum ML pipeline."""
    logger.info("\n" + "=" * 80)
    logger.info("QUANTUM ML PIPELINE - Credit Risk Analysis")
    logger.info("Quantum_ML_Agent")
    logger.info("=" * 80 + "\n")
    
    start_time = datetime.now()
    
    try:
        # Step 1: Load features
        X_train, X_test, y_train, y_test = load_quantum_features()
        
        # Step 2: Normalize
        X_train_norm, X_test_norm, scaler = normalize_quantum_features(X_train, X_test)
        
        # Step 3: Create quantum circuit
        feature_map = create_zz_feature_map(N_QUBITS, FEATURE_MAP_REPS)
        
        # Step 4: Compute kernel
        logger.info("\nStarting quantum kernel computation (this may take several minutes)...")
        K_train, K_test, X_train_kernel = compute_quantum_kernel(
            X_train_norm, X_test_norm, feature_map, max_samples=MAX_SAMPLES_FOR_KERNEL
        )
        
        # Step 5: Train QSVM with subset of labels
        y_train_kernel = y_train[:len(X_train_kernel)]
        qsvm = train_quantum_svm(K_train, y_train_kernel)
        
        # Step 6: Evaluate
        metrics = evaluate_qsvm(qsvm, K_train, K_test, y_train_kernel, y_test)
        
        # Save artifacts
        logger.info("\n" + "=" * 80)
        logger.info("SAVING ARTIFACTS")
        logger.info("=" * 80)
        
        with open(MODELS_PATH / 'quantum_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Saved metrics: {MODELS_PATH / 'quantum_metrics.json'}")
        
        # Summary
        elapsed = datetime.now() - start_time
        logger.info("\n" + "=" * 80)
        logger.info("QUANTUM PIPELINE COMPLETED")
        logger.info("=" * 80)
        logger.info(f"Execution time: {elapsed}")
        logger.info(f"Test AUC-ROC: {metrics['test']['auc_roc']:.4f}")
        logger.info(f"Test F1-Score: {metrics['test']['f1']:.4f}")
        logger.info("\nNext: Run Risk Validator (3_risk_validator.py)")
        logger.info("=" * 80 + "\n")
        
        return metrics
        
    except Exception as e:
        logger.error(f"ERROR: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        metrics = main()
        print("\n" + "=" * 80)
        print("QUANTUM ML PIPELINE - SUMMARY")
        print("=" * 80)
        print(f"\nTest Set Performance:")
        print(f"  Accuracy:  {metrics['test']['accuracy']:.4f}")
        print(f"  Precision: {metrics['test']['precision']:.4f}")
        print(f"  Recall:    {metrics['test']['recall']:.4f}")
        print(f"  F1-Score:  {metrics['test']['f1']:.4f}")
        print(f"  AUC-ROC:   {metrics['test']['auc_roc']:.4f}")
        print("=" * 80 + "\n")
    except Exception as e:
        print(f"\nERROR in Quantum ML Pipeline: {str(e)}")
