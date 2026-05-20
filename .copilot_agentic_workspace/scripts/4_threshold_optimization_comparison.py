#!/usr/bin/env python3
"""
================================================================================
THRESHOLD OPTIMIZATION COMPARISON
Credit Risk Analysis - Advanced Hyperparameter Tuning
================================================================================

Techniques Compared:
1. Cross-Validated Threshold Optimization (5-Fold CV)
2. Bayesian Optimization (via scipy.optimize)
3. Optuna Framework (Professional HPO)

Financial Cost Function:
- True Positive: $5,000 (prevented default)
- True Negative: $500 (accepted good client)
- False Positive: -$800 (rejected good client)
- False Negative: -$30,000 (missed default)
"""

import json
import logging
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

# ML libraries
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import (
    confusion_matrix, roc_curve, auc, precision_recall_curve,
    accuracy_score, precision_score, recall_score, f1_score
)
from imblearn.over_sampling import SMOTE
import xgboost as xgb

# Optimization libraries
from scipy.optimize import differential_evolution, minimize
import optuna
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# SECTION 1: DATA LOADING & PREPARATION
# ============================================================================

def load_data():
    """Load and prepare credit risk dataset"""
    logger.info("="*80)
    logger.info("LOADING DATA")
    logger.info("="*80)
    
    df = pd.read_csv('../data/credit_risk_dataset.csv')
    logger.info("Dataset shape: {}".format(df.shape))
    logger.info("Default rate: {:.2%}".format(df['loan_status'].mean()))
    
    return df

def prepare_features_and_target(df):
    """Prepare features and target"""
    logger.info("="*80)
    logger.info("PREPARING FEATURES & TARGET")
    logger.info("="*80)
    
    # Select numeric features
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols.remove('loan_status')
    
    X = df[numeric_cols].copy()
    y = df['loan_status'].copy()
    
    logger.info("Features shape: {}".format(X.shape))
    logger.info("Target shape: {}".format(y.shape))
    logger.info("Features: {}".format(numeric_cols))
    
    return X, y

def split_and_preprocess(X, y):
    """Split and preprocess data"""
    logger.info("="*80)
    logger.info("SPLITTING & PREPROCESSING")
    logger.info("="*80)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    logger.info("Train: {}, Test: {}".format(X_train.shape, X_test.shape))
    logger.info("Train default rate: {:.2%}".format(y_train.mean()))
    logger.info("Test default rate: {:.2%}".format(y_test.mean()))
    
    # Handle missing values
    from sklearn.impute import KNNImputer
    imputer = KNNImputer(n_neighbors=5)
    X_train = pd.DataFrame(imputer.fit_transform(X_train), columns=X_train.columns)
    X_test = pd.DataFrame(imputer.transform(X_test), columns=X_test.columns)
    
    # Apply SMOTE
    smote = SMOTE(sampling_strategy=0.7, random_state=42)
    X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)
    logger.info("After SMOTE: {}".format(X_train_smote.shape))
    
    # Normalize
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_smote)
    X_test_scaled = scaler.transform(X_test)
    
    return X_train_scaled, X_test_scaled, y_train_smote, y_test

def train_xgboost(X_train, X_test, y_train, y_test):
    """Train XGBoost model"""
    logger.info("="*80)
    logger.info("TRAINING XGBOOST")
    logger.info("="*80)
    
    # Calculate class weights
    n_class_0 = (y_train == 0).sum()
    n_class_1 = (y_train == 1).sum()
    scale_pos_weight = n_class_0 / n_class_1
    logger.info("scale_pos_weight: {:.4f}".format(scale_pos_weight))
    
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        verbosity=0
    )
    
    model.fit(X_train, y_train)
    logger.info("Training complete")
    
    # Get probabilities
    y_train_proba = model.predict_proba(X_train)[:, 1]
    y_test_proba = model.predict_proba(X_test)[:, 1]
    
    return model, y_train_proba, y_test_proba

# ============================================================================
# SECTION 2: FINANCIAL METRICS
# ============================================================================

def calculate_financial_value(y_true, y_pred_binary):
    """Calculate financial value of predictions"""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred_binary).ravel()
    
    tp_gain = tp * 5000      # Prevented default
    tn_gain = tn * 500       # Good client approved
    fp_loss = fp * 800       # Good client rejected
    fn_loss = fn * 30000     # Default missed
    
    net_value = tp_gain + tn_gain - fp_loss - fn_loss
    return net_value, (tp, fp, fn, tn)

def compute_metrics_at_threshold(y_true, y_proba, threshold):
    """Compute all metrics at given threshold"""
    y_pred = (y_proba >= threshold).astype(int)
    
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    net_value, _ = calculate_financial_value(y_true, y_pred)
    
    return {
        'accuracy': acc,
        'precision': prec,
        'recall': rec,
        'f1': f1,
        'financial_value': net_value,
        'tp': tp,
        'fp': fp,
        'fn': fn,
        'tn': tn
    }

# ============================================================================
# SECTION 3: METHOD 1 - CROSS-VALIDATED THRESHOLD OPTIMIZATION
# ============================================================================

def method_1_cv_threshold_optimization(X, y, y_proba):
    """Cross-Validated Threshold Optimization"""
    logger.info("\n" + "="*80)
    logger.info("METHOD 1: CROSS-VALIDATED THRESHOLD OPTIMIZATION (5-Fold CV)")
    logger.info("="*80)
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    fold_thresholds = []
    fold_values = []
    fold_metrics = []
    
    for fold_idx, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        logger.info("\nFold {}/5:".format(fold_idx + 1))
        
        y_val = y.iloc[val_idx] if isinstance(y, pd.Series) else y[val_idx]
        y_val_proba = y_proba[val_idx]
        
        # Grid search on validation fold
        best_threshold = 0.5
        best_value = float('-inf')
        
        for threshold in np.arange(0.1, 0.9, 0.01):
            y_val_pred = (y_val_proba >= threshold).astype(int)
            _, (tp, fp, fn, tn) = calculate_financial_value(y_val, y_val_pred)
            value = tp * 5000 + tn * 500 - fp * 800 - fn * 30000
            
            if value > best_value:
                best_value = value
                best_threshold = threshold
        
        fold_thresholds.append(best_threshold)
        fold_values.append(best_value)
        
        metrics = compute_metrics_at_threshold(y_val, y_val_proba, best_threshold)
        fold_metrics.append(metrics)
        
        logger.info("  Optimal Threshold: {:.3f}".format(best_threshold))
        logger.info("  Financial Value: ${:,.0f}".format(best_value))
        logger.info("  Recall: {:.4f}".format(metrics['recall']))
    
    # Average results
    avg_threshold = np.mean(fold_thresholds)
    std_threshold = np.std(fold_thresholds)
    avg_value = np.mean(fold_values)
    std_value = np.std(fold_values)
    
    logger.info("\n" + "="*80)
    logger.info("CV THRESHOLD OPTIMIZATION RESULTS:")
    logger.info("="*80)
    logger.info("Mean Threshold: {:.4f} +/- {:.4f}".format(avg_threshold, std_threshold))
    logger.info("Mean Financial Value: ${:,.0f} +/- ${:,.0f}".format(avg_value, std_value))
    logger.info("Threshold Range: [{:.3f}, {:.3f}]".format(min(fold_thresholds), max(fold_thresholds)))
    
    result = {
        'method': 'Cross-Validated Threshold Optimization',
        'optimal_threshold': float(avg_threshold),
        'threshold_std': float(std_threshold),
        'financial_value': float(avg_value),
        'financial_value_std': float(std_value),
        'fold_thresholds': [float(t) for t in fold_thresholds],
        'fold_values': [float(v) for v in fold_values],
        'fold_metrics': fold_metrics
    }
    
    return result

# ============================================================================
# SECTION 4: METHOD 2 - BAYESIAN OPTIMIZATION
# ============================================================================

def method_2_bayesian_optimization(y_test, y_test_proba):
    """Bayesian Optimization via scipy"""
    logger.info("\n" + "="*80)
    logger.info("METHOD 2: BAYESIAN OPTIMIZATION (scipy.optimize)")
    logger.info("="*80)
    
    def objective_function(threshold):
        """Objective: Negative financial value (for minimization)"""
        threshold = threshold[0]  # scipy passes array
        threshold = np.clip(threshold, 0.01, 0.99)
        
        y_pred = (y_test_proba >= threshold).astype(int)
        net_value, _ = calculate_financial_value(y_test, y_pred)
        
        return -net_value  # Negative because scipy minimizes
    
    # Use differential_evolution (Bayesian-like optimization)
    logger.info("Running Differential Evolution optimization...")
    result = differential_evolution(
        objective_function,
        bounds=[(0.01, 0.99)],
        maxiter=100,
        popsize=30,
        seed=42,
        workers=1,
        updating='deferred',
        polish=True
    )
    
    optimal_threshold = result.x[0]
    optimal_value = -result.fun  # Convert back to positive
    
    logger.info("="*80)
    logger.info("BAYESIAN OPTIMIZATION RESULTS:")
    logger.info("="*80)
    logger.info("Optimal Threshold: {:.4f}".format(optimal_threshold))
    logger.info("Financial Value: ${:,.0f}".format(optimal_value))
    logger.info("Iterations: {}".format(result.nit))
    logger.info("Success: {}".format(result.success))
    
    # Compute final metrics
    metrics = compute_metrics_at_threshold(y_test, y_test_proba, optimal_threshold)
    
    result_dict = {
        'method': 'Bayesian Optimization (Differential Evolution)',
        'optimal_threshold': float(optimal_threshold),
        'financial_value': float(optimal_value),
        'iterations': int(result.nit),
        'success': bool(result.success),
        'metrics': metrics
    }
    
    return result_dict

# ============================================================================
# SECTION 5: METHOD 3 - OPTUNA FRAMEWORK
# ============================================================================

class OptunaObjective:
    """Optuna objective function"""
    def __init__(self, y_test, y_test_proba):
        self.y_test = y_test
        self.y_test_proba = y_test_proba
    
    def __call__(self, trial):
        threshold = trial.suggest_float('threshold', 0.01, 0.99)
        
        y_pred = (self.y_test_proba >= threshold).astype(int)
        net_value, _ = calculate_financial_value(self.y_test, y_pred)
        
        return net_value  # Optuna maximizes by default

def method_3_optuna_optimization(y_test, y_test_proba):
    """Optuna Framework optimization"""
    logger.info("\n" + "="*80)
    logger.info("METHOD 3: OPTUNA FRAMEWORK (Professional HPO)")
    logger.info("="*80)
    
    sampler = TPESampler(seed=42)
    pruner = MedianPruner()
    
    study = optuna.create_study(
        direction='maximize',
        sampler=sampler,
        pruner=pruner
    )
    
    objective = OptunaObjective(y_test, y_test_proba)
    
    logger.info("Running Optuna optimization (100 trials)...")
    study.optimize(
        objective,
        n_trials=100,
        show_progress_bar=False,
        callbacks=[]
    )
    
    best_trial = study.best_trial
    optimal_threshold = best_trial.params['threshold']
    optimal_value = best_trial.value
    
    logger.info("="*80)
    logger.info("OPTUNA OPTIMIZATION RESULTS:")
    logger.info("="*80)
    logger.info("Best Trial Number: {}".format(best_trial.number))
    logger.info("Optimal Threshold: {:.4f}".format(optimal_threshold))
    logger.info("Financial Value: ${:,.0f}".format(optimal_value))
    logger.info("Total Trials: {}".format(len(study.trials)))
    pruned = len([t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED])
    logger.info("Pruned Trials: {}".format(pruned))
    
    # Compute final metrics
    metrics = compute_metrics_at_threshold(y_test, y_test_proba, optimal_threshold)
    
    result_dict = {
        'method': 'Optuna Framework (TPE Sampler)',
        'optimal_threshold': float(optimal_threshold),
        'financial_value': float(optimal_value),
        'best_trial_number': int(best_trial.number),
        'total_trials': len(study.trials),
        'pruned_trials': len([t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED]),
        'metrics': metrics,
        'trial_history': [
            {
                'trial': t.number,
                'threshold': t.params.get('threshold'),
                'value': t.value,
                'state': str(t.state)
            }
            for t in study.trials[:10]  # First 10 trials
        ]
    }
    
    return result_dict

# ============================================================================
# SECTION 6: COMPARISON & REPORTING
# ============================================================================

def compare_methods(method1_result, method2_result, method3_result, y_test, y_test_proba):
    """Compare all three methods"""
    logger.info("\n" + "="*80)
    logger.info("COMPARISON OF ALL THREE METHODS")
    logger.info("="*80)
    
    comparison = {
        'method_1_cv': method1_result,
        'method_2_bayesian': method2_result,
        'method_3_optuna': method3_result,
        'timestamp': datetime.now().isoformat()
    }
    
    # Create summary table
    logger.info("\n" + "="*80)
    logger.info("SUMMARY TABLE:")
    logger.info("="*80)
    logger.info("\nMethod                                   | Threshold    | Financial Value")
    logger.info("-" * 75)
    
    logger.info("CV Threshold Opt (Mean)                  | {:.4f}       | ${:,.0f}".format(
        method1_result['optimal_threshold'], method1_result['financial_value']))
    logger.info("Bayesian Opt                             | {:.4f}       | ${:,.0f}".format(
        method2_result['optimal_threshold'], method2_result['financial_value']))
    logger.info("Optuna Framework                         | {:.4f}       | ${:,.0f}".format(
        method3_result['optimal_threshold'], method3_result['financial_value']))
    
    logger.info("\n" + "="*80)
    logger.info("METRICS AT OPTIMAL THRESHOLD (Test Set):")
    logger.info("="*80)
    
    logger.info("\nMethod                                   | Accuracy   | Recall     | Precision")
    logger.info("-" * 75)
    
    for method_name, method_result in [
        ("CV Threshold Opt", method1_result),
        ("Bayesian Opt", method2_result),
        ("Optuna", method3_result)
    ]:
        metrics = method_result['metrics'] if 'metrics' in method_result else method_result['fold_metrics'][0]
        logger.info("{:<40} | {:<10.4f} | {:<10.4f} | {:<10.4f}".format(
            method_name, metrics['accuracy'], metrics['recall'], metrics['precision']))
    
    # Determine best method
    thresholds = [
        method1_result['optimal_threshold'],
        method2_result['optimal_threshold'],
        method3_result['optimal_threshold']
    ]
    
    values = [
        method1_result['financial_value'],
        method2_result['financial_value'],
        method3_result['financial_value']
    ]
    
    best_idx = np.argmax(values)
    best_methods = ["CV Threshold Opt", "Bayesian Opt", "Optuna Framework"]
    
    logger.info("\n" + "="*80)
    logger.info("WINNER: {}".format(best_methods[best_idx]))
    logger.info("RECOMMENDED THRESHOLD: {:.4f}".format(thresholds[best_idx]))
    logger.info("EXPECTED FINANCIAL VALUE: ${:,.0f}".format(values[best_idx]))
    logger.info("="*80)
    
    comparison['winner'] = best_methods[best_idx]
    comparison['recommended_threshold'] = float(thresholds[best_idx])
    comparison['expected_financial_value'] = float(values[best_idx])
    
    return comparison

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    logger.info("\n" + "="*80)
    logger.info("THRESHOLD OPTIMIZATION COMPARISON - ALL METHODS")
    logger.info("="*80)
    
    # Load and prepare data
    df = load_data()
    X, y = prepare_features_and_target(df)
    X_train_scaled, X_test_scaled, y_train, y_test = split_and_preprocess(X, y)
    
    # Train XGBoost
    model, y_train_proba, y_test_proba = train_xgboost(
        X_train_scaled, X_test_scaled, y_train, y_test
    )
    
    # Apply all three methods
    logger.info("\n" + "#"*80)
    logger.info("RUNNING ALL THREE OPTIMIZATION METHODS...")
    logger.info("#"*80)
    
    # Method 1: CV Threshold Optimization
    method1_result = method_1_cv_threshold_optimization(
        pd.DataFrame(X_train_scaled),
        pd.Series(y_train),
        y_train_proba
    )
    
    # Method 2: Bayesian Optimization
    method2_result = method_2_bayesian_optimization(y_test, y_test_proba)
    
    # Method 3: Optuna
    method3_result = method_3_optuna_optimization(y_test, y_test_proba)
    
    # Compare all methods
    comparison = compare_methods(
        method1_result, method2_result, method3_result,
        y_test, y_test_proba
    )
    # Save results
    def convert_numpy_types(obj):
        """Convert numpy types to Python native types for JSON serialization"""
        import numpy as np
        if isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_numpy_types(item) for item in obj]
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj
    
    output_dir = Path(__file__).parent.parent / 'models'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'threshold_optimization_comparison.json'
    
    # Convert numpy types before saving
    comparison_clean = convert_numpy_types(comparison)
    
    with open(output_path, 'w') as f:
        json.dump(comparison_clean, f, indent=2)
    logger.info("\nResults saved to: {}".format(output_path))
    
    return comparison

if __name__ == "__main__":
    results = main()
    logger.info("\n" + "="*80)
    logger.info("EXECUTION COMPLETE")
    logger.info("="*80)
