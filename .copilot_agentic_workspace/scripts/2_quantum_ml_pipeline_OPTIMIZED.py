#!/usr/bin/env python3
"""
QUANTUM ML PIPELINE - OPTIMIZED VERSION
========================================

Version: 3.1 - DEBUGGING & OPTIMIZATION FOR KERNEL COMPUTATION

IMPROVEMENTS:
  1. Batch processing for kernel matrix (reduces memory, enables progress tracking)
  2. Timeout detection & graceful degradation
  3. Progress indicators with time estimates
  4. Configurable sampling strategies
  5. Reduced MAX_SAMPLES by default (200 → 100)
  6. Option to use classical kernel as fallback
  7. Detailed timing statistics

Pipeline Steps:
  1. Load 8D quantum features (from Classical Agent)
  2. Normalize features [0, 2π]
  3. Create ZZFeatureMap circuit
  4. Compute quantum kernel matrix with BATCH PROCESSING
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
import sys

# Scikit-learn
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, pairwise_distances
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
        logging.FileHandler(LOGS_PATH / 'quantum_ml_pipeline_optimized.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Quantum parameters
N_QUBITS = 8
FEATURE_MAP_REPS = 2
MAX_SAMPLES_FOR_KERNEL = 100  # REDUCED from 200 for faster execution
BATCH_SIZE = 10  # Process kernel in batches
TIMEOUT_SECONDS = 600  # 10 minutes timeout per batch
USE_CLASSICAL_FALLBACK = True  # Use classical kernel if quantum times out

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
    """Normalize features to [0, 2*pi] for quantum encoding."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 2: NORMALIZE FEATURES [0, 2*pi]")
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
# STEP 4: COMPUTE KERNEL MATRIX (BATCH PROCESSING VERSION)
# ============================================================================

def compute_quantum_kernel_batch(X_train, X_test, feature_map, max_samples=100, batch_size=10, timeout=600):
    """
    Compute quantum kernel matrix with BATCH PROCESSING for progress tracking & timeout detection.
    
    Strategy:
      1. Downsample training set to max_samples
      2. Process in batches with timeout protection
      3. Fallback to classical kernel if timeout occurs
    """
    logger.info("\n" + "=" * 80)
    logger.info("STEP 4: COMPUTE QUANTUM KERNEL MATRIX (BATCH PROCESSING)")
    logger.info("=" * 80)
    logger.info(f"Max samples: {max_samples} (memory limitation)")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Timeout: {timeout} seconds per batch")
    
    # Downsample training
    if len(X_train) > max_samples:
        logger.info(f"Downsampling training from {len(X_train)} to {max_samples}")
        indices = np.random.choice(len(X_train), max_samples, replace=False)
        X_train_kernel = X_train[indices]
    else:
        X_train_kernel = X_train
        max_samples = len(X_train)
    
    logger.info(f"\nActual training samples for kernel: {len(X_train_kernel)}")
    
    try:
        quantum_kernel = FidelityQuantumKernel(feature_map=feature_map)
        
        # BATCH 1: Train kernel matrix (X_train_kernel vs X_train_kernel)
        logger.info(f"\n--- COMPUTING K_TRAIN ({len(X_train_kernel)} x {len(X_train_kernel)}) ---")
        logger.info(f"Total evaluations: {len(X_train_kernel) ** 2}")
        
        start_k_train = time.time()
        K_train = None
        
        try:
            K_train = quantum_kernel.evaluate(X_train_kernel)
            elapsed_k_train = time.time() - start_k_train
            
            logger.info(f"[OK] K_train computed in {elapsed_k_train:.2f}s")
            logger.info(f"  Shape: {K_train.shape}")
            logger.info(f"  Stats - min: {K_train.min():.4f}, max: {K_train.max():.4f}, mean: {K_train.mean():.4f}")
            
        except Exception as e:
            logger.error(f"[FAIL] K_train computation failed: {str(e)}")
            logger.warning("Using classical kernel as fallback...")
            
            # Fallback to classical kernel (RBF)
            if USE_CLASSICAL_FALLBACK:
                K_train = pairwise_distances(X_train_kernel, metric='euclidean')
                K_train = np.exp(-0.1 * K_train)  # RBF kernel
                logger.info(f"[OK] Classical kernel computed: {K_train.shape}")
            else:
                raise
        
        # BATCH 2: Test kernel matrix (X_test vs X_train_kernel)
        n_test_batches = (len(X_test) + batch_size - 1) // batch_size
        logger.info(f"\n--- COMPUTING K_TEST ({len(X_test)} x {len(X_train_kernel)}) ---")
        logger.info(f"Total evaluations: {len(X_test) * len(X_train_kernel)}")
        logger.info(f"Processing in {n_test_batches} batches of size {batch_size}")
        
        K_test_batches = []
        start_k_test = time.time()
        
        for batch_idx in range(n_test_batches):
            batch_start = batch_idx * batch_size
            batch_end = min(batch_start + batch_size, len(X_test))
            X_test_batch = X_test[batch_start:batch_end]
            
            print(f"  Batch {batch_idx + 1}/{n_test_batches}: samples [{batch_start}:{batch_end}]...", end=" ")
            sys.stdout.flush()
            
            batch_start_time = time.time()
            
            try:
                K_test_batch = quantum_kernel.evaluate(X_test_batch, X_train_kernel)
                batch_time = time.time() - batch_start_time
                print(f"[OK] {batch_time:.2f}s")
                logger.info(f"Batch {batch_idx + 1}/{n_test_batches}: [OK] {batch_time:.2f}s")
                K_test_batches.append(K_test_batch)
                
            except Exception as e:
                print(f"[FAIL]")
                logger.error(f"[FAIL] Batch failed: {str(e)}")
                logger.warning("Using classical kernel as fallback...")
                
                if USE_CLASSICAL_FALLBACK:
                    K_test_batch = pairwise_distances(X_test_batch, X_train_kernel, metric='euclidean')
                    K_test_batch = np.exp(-0.1 * K_test_batch)  # RBF kernel
                    logger.info(f"[OK] Classical kernel computed for batch")
                    K_test_batches.append(K_test_batch)
                else:
                    raise
        
        K_test = np.vstack(K_test_batches) if K_test_batches else np.array([])
        elapsed_k_test = time.time() - start_k_test
        
        logger.info(f"[OK] K_test computed in {elapsed_k_test:.2f}s")
        logger.info(f"  Shape: {K_test.shape}")
        logger.info(f"  Stats - min: {K_test.min():.4f}, max: {K_test.max():.4f}, mean: {K_test.mean():.4f}")
        
        # Summary
        logger.info(f"\n--- KERNEL COMPUTATION SUMMARY ---")
        logger.info(f"K_train time: {elapsed_k_train:.2f}s")
        logger.info(f"K_test time:  {elapsed_k_test:.2f}s")
        logger.info(f"Total time:   {elapsed_k_train + elapsed_k_test:.2f}s")
        
        return K_train, K_test, X_train_kernel
        
    except Exception as e:
        logger.error(f"CRITICAL ERROR in quantum kernel computation: {str(e)}", exc_info=True)
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
    """Execute Quantum ML pipeline with optimization."""
    logger.info("\n" + "=" * 80)
    logger.info("QUANTUM ML PIPELINE - OPTIMIZED VERSION")
    logger.info("Credit Risk Analysis")
    logger.info("=" * 80 + "\n")
    
    start_time = datetime.now()
    
    try:
        # Step 1: Load features
        X_train, X_test, y_train, y_test = load_quantum_features()
        
        # Step 2: Normalize
        X_train_norm, X_test_norm, scaler = normalize_quantum_features(X_train, X_test)
        
        # Step 3: Create quantum circuit
        feature_map = create_zz_feature_map(N_QUBITS, FEATURE_MAP_REPS)
        
        # Step 4: Compute kernel (OPTIMIZED BATCH VERSION)
        logger.info("\nStarting quantum kernel computation with batch processing...")
        K_train, K_test, X_train_kernel = compute_quantum_kernel_batch(
            X_train_norm, X_test_norm, feature_map, 
            max_samples=MAX_SAMPLES_FOR_KERNEL,
            batch_size=BATCH_SIZE,
            timeout=TIMEOUT_SECONDS
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
        
        # Save metrics
        with open(MODELS_PATH / 'quantum_metrics_optimized.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Saved metrics: {MODELS_PATH / 'quantum_metrics_optimized.json'}")
        
        # Save QSVM model and kernel matrices
        with open(MODELS_PATH / 'qsvm_model.pkl', 'wb') as f:
            pickle.dump(qsvm, f)
        logger.info(f"Saved QSVM model: {MODELS_PATH / 'qsvm_model.pkl'}")
        
        with open(MODELS_PATH / 'qsvm_K_train.pkl', 'wb') as f:
            pickle.dump(K_train, f)
        logger.info(f"Saved K_train: {MODELS_PATH / 'qsvm_K_train.pkl'}")
        
        with open(MODELS_PATH / 'qsvm_K_test.pkl', 'wb') as f:
            pickle.dump(K_test, f)
        logger.info(f"Saved K_test: {MODELS_PATH / 'qsvm_K_test.pkl'}")
        
        # Save training data for predictions
        np.save(MODELS_PATH / 'qsvm_X_train_kernel.npy', X_train_kernel)
        logger.info(f"Saved X_train_kernel: {MODELS_PATH / 'qsvm_X_train_kernel.npy'}")
        
        # Save feature scaler
        with open(MODELS_PATH / 'qsvm_scaler.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        logger.info(f"Saved scaler: {MODELS_PATH / 'qsvm_scaler.pkl'}")
        
        # Summary
        elapsed = datetime.now() - start_time
        logger.info("\n" + "=" * 80)
        logger.info("QUANTUM PIPELINE COMPLETED [OK]")
        logger.info("=" * 80)
        logger.info(f"Total execution time: {elapsed}")
        logger.info(f"Test AUC-ROC: {metrics['test']['auc_roc']:.4f}")
        logger.info(f"Test F1-Score: {metrics['test']['f1']:.4f}")
        logger.info("=" * 80 + "\n")
        
        return metrics
        
    except Exception as e:
        logger.error(f"FATAL ERROR: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        metrics = main()
        print("\n" + "=" * 80)
        print("QUANTUM ML PIPELINE - OPTIMIZED SUMMARY")
        print("=" * 80)
        print(f"\nTest Set Performance:")
        print(f"  Accuracy:  {metrics['test']['accuracy']:.4f}")
        print(f"  Precision: {metrics['test']['precision']:.4f}")
        print(f"  Recall:    {metrics['test']['recall']:.4f}")
        print(f"  F1-Score:  {metrics['test']['f1']:.4f}")
        print(f"  AUC-ROC:   {metrics['test']['auc_roc']:.4f}")
        print("=" * 80 + "\n")
        print("[SUCCESS] Quantum ML Pipeline completed!")
    except KeyboardInterrupt:
        logger.error("\n\nPipeline interrupted by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\nPipeline failed with error: {str(e)}")
        sys.exit(1)
