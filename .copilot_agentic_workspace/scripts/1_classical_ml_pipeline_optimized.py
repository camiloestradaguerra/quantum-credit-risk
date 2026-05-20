#!/usr/bin/env python3
"""
CLASSICAL ML PIPELINE WITH THRESHOLD OPTIMIZATION
==================================================

Agent: Data_Classical_ML_Agent
Version: 2.1 - Real Dataset with Threshold Optimization

Pipeline Steps:
  1. Load & EDA
  2. Impute missing values (KNN)
  3. Engineer features (10 risk features)
  4. Split train/test
  5. SMOTE balancing
  6. Normalize features
  7. Train XGBoost
  8. OPTIMIZE THRESHOLD for financial metrics
  9. Evaluate with optimal threshold
  10. Export quantum features

Key Improvement: Threshold optimization to maximize financial value
                 (reduce false negatives based on cost parameters)
"""

import numpy as np
import pandas as pd
import json
import pickle
import logging
from pathlib import Path
from datetime import datetime

# Scikit-learn
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.impute import KNNImputer
from sklearn.decomposition import PCA
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, roc_curve, confusion_matrix
)
from imblearn.over_sampling import SMOTE
import xgboost as xgb

import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

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
        logging.FileHandler(LOGS_PATH / 'classical_ml_optimized.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Financial parameters for threshold optimization
FALSE_NEGATIVE_COST = 30000  # Cost of missing a default
FALSE_POSITIVE_COST = 800    # Cost of rejecting good client
TRUE_POSITIVE_VALUE = 5000   # Value recovered from prevented default
TRUE_NEGATIVE_VALUE = 500    # Value of correctly accepted good client

# ============================================================================
# STEP 1: LOAD & EDA
# ============================================================================

def load_and_explore_data():
    """Load and explore credit risk dataset."""
    logger.info("=" * 80)
    logger.info("STEP 1: LOAD & EXPLORATORY DATA ANALYSIS")
    logger.info("=" * 80)
    
    df = pd.read_csv(DATA_PATH / 'credit_risk_dataset.csv')
    
    logger.info(f"Dataset shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")
    logger.info(f"Data types:\n{df.dtypes}")
    logger.info(f"\nMissing values:\n{df.isnull().sum()}")
    logger.info(f"\nTarget distribution:\n{df['loan_status'].value_counts()}")
    logger.info(f"Default rate: {df['loan_status'].mean():.2%}")
    
    return df

# ============================================================================
# STEP 2: IMPUTE MISSING VALUES
# ============================================================================

def impute_missing_values(df):
    """Impute missing values using KNN."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 2: IMPUTE MISSING VALUES (KNN k=5)")
    logger.info("=" * 80)
    
    # Type conversion for categorical column
    if df['cb_person_default_on_file'].dtype in ['object', 'string']:
        df['cb_person_default_on_file'] = (df['cb_person_default_on_file'] == 'Y').astype(int)
    
    # Find numeric columns with missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    cols_with_missing = df[numeric_cols].columns[df[numeric_cols].isnull().any()].tolist()
    
    if cols_with_missing:
        logger.info(f"Imputing columns: {cols_with_missing}")
        imputer = KNNImputer(n_neighbors=5)
        df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        logger.info("Imputation complete")
    
    logger.info(f"Missing values after imputation: {df.isnull().sum().sum()}")
    return df

# ============================================================================
# STEP 3: ENGINEER FEATURES
# ============================================================================

def engineer_features(df):
    """Engineer 10 risk features."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 3: FEATURE ENGINEERING (10 risk features)")
    logger.info("=" * 80)
    
    df_eng = df.copy()
    
    # Risk features
    df_eng['debt_to_income'] = df_eng['loan_percent_income']
    df_eng['interest_rate_risk'] = df_eng['loan_int_rate'] ** 2
    df_eng['loan_income_interaction'] = df_eng['loan_amnt'] / (df_eng['person_income'] + 1)
    df_eng['emp_stability_log'] = np.log1p(df_eng['person_emp_length'])
    df_eng['credit_history_ratio'] = df_eng['cb_person_cred_hist_length'] / (df_eng['person_age'] + 1)
    df_eng['default_risk_score'] = (df_eng['cb_person_default_on_file'].astype(int) * 
                                     df_eng['loan_percent_income'])
    df_eng['age_normalized'] = df_eng['person_age'] / 100
    df_eng['loan_amount_risk'] = np.log1p(df_eng['loan_amnt']) * df_eng['loan_int_rate']
    df_eng['income_age_ratio'] = df_eng['person_income'] / (df_eng['person_age'] + 1)
    df_eng['composite_risk'] = (df_eng['debt_to_income'] + 
                                 df_eng['interest_rate_risk'] / 100 + 
                                 df_eng['loan_income_interaction'])
    
    logger.info(f"Engineered features: 10")
    logger.info(f"Total features now: {df_eng.shape[1]}")
    
    return df_eng

# ============================================================================
# STEP 4: PREPARE FEATURES
# ============================================================================

def prepare_features_and_target(df):
    """Select numeric features and extract target."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 4: PREPARE FEATURES & TARGET")
    logger.info("=" * 80)
    
    # Select numeric features (exclude target)
    numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'loan_status' in numeric_features:
        numeric_features.remove('loan_status')
    
    X = df[numeric_features].copy()
    y = df['loan_status'].copy()
    
    logger.info(f"Features selected: {len(numeric_features)}")
    logger.info(f"Feature list: {numeric_features[:5]} ... (and {len(numeric_features)-5} more)")
    logger.info(f"X shape: {X.shape}, y shape: {y.shape}")
    
    return X, y, numeric_features

# ============================================================================
# STEP 5: SPLIT DATA
# ============================================================================

def split_data(X, y):
    """Split into train/test with stratification."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 5: TRAIN/TEST SPLIT (80/20 stratified)")
    logger.info("=" * 80)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    
    logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    logger.info(f"Train default rate: {y_train.mean():.2%}")
    logger.info(f"Test default rate: {y_test.mean():.2%}")
    
    return X_train, X_test, y_train, y_test

# ============================================================================
# STEP 6: APPLY SMOTE
# ============================================================================

def apply_smote(X_train, y_train):
    """Apply SMOTE balancing to training data."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 6: SMOTE BALANCING (ratio=0.7)")
    logger.info("=" * 80)
    
    logger.info(f"Before SMOTE: {y_train.value_counts().to_dict()}")
    
    smote = SMOTE(sampling_strategy=0.7, k_neighbors=5, random_state=RANDOM_STATE)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
    
    logger.info(f"After SMOTE: {pd.Series(y_resampled).value_counts().to_dict()}")
    logger.info(f"New shape: {X_resampled.shape}")
    
    return X_resampled, y_resampled

# ============================================================================
# STEP 7: NORMALIZE
# ============================================================================

def normalize_features(X_train, X_test):
    """Normalize features using StandardScaler."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 7: NORMALIZE FEATURES (StandardScaler)")
    logger.info("=" * 80)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    logger.info(f"Train mean: {X_train_scaled.mean():.4f}, std: {X_train_scaled.std():.4f}")
    logger.info(f"Test mean: {X_test_scaled.mean():.4f}, std: {X_test_scaled.std():.4f}")
    
    return X_train_scaled, X_test_scaled, scaler

# ============================================================================
# STEP 8: TRAIN XGBOOST
# ============================================================================

def train_xgboost(X_train, y_train):
    """Train XGBoost with calculated scale_pos_weight."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 8: TRAIN XGBOOST (200 estimators, max_depth=6)")
    logger.info("=" * 80)
    
    # Calculate scale_pos_weight (class imbalance ratio)
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    
    logger.info(f"scale_pos_weight: {scale_pos_weight:.4f}")
    
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        random_state=RANDOM_STATE,
        verbosity=0,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)
    logger.info("Training complete")
    
    return model

# ============================================================================
# STEP 9: APPLY OPTIMAL THRESHOLD
# ============================================================================

def apply_optimal_threshold(model, X_test, y_test, fixed_threshold=0.1160):
    """Apply optimal threshold (0.1160 from cross-validation)."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 9: APPLY OPTIMAL THRESHOLD (0.1160 from Cross-Validation)")
    logger.info("=" * 80)
    
    # Get probability predictions
    y_proba = model.predict_proba(X_test)[:, 1]
    
    # Apply fixed optimal threshold
    best_threshold = fixed_threshold
    best_value = None
    best_metrics = {}
    
    logger.info("\n" + "=" * 80)
    logger.info(f"Using Fixed Optimal Threshold: {best_threshold:.4f}")
    logger.info("(Determined via 5-Fold Cross-Validation)")
    logger.info("=" * 80)
    
    # Calculate metrics at optimal threshold
    for threshold in [best_threshold]:
        y_pred = (y_proba >= threshold).astype(int)
        
        # Confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        
        # Financial value
        financial_value = (tp * TRUE_POSITIVE_VALUE + 
                          tn * TRUE_NEGATIVE_VALUE - 
                          fp * FALSE_POSITIVE_COST - 
                          fn * FALSE_NEGATIVE_COST)
        
        # Metrics
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_proba)
        
        logger.info(f"\nThreshold: {threshold:.4f}")
        logger.info(f"  Financial Value: ${financial_value:,.0f}")
        logger.info(f"  Precision: {prec:.4f} | Recall: {rec:.4f} | F1: {f1:.4f} | AUC: {auc:.4f}")
        
        best_value = financial_value
        best_threshold = threshold
        best_metrics = {
            'threshold': threshold,
            'financial_value': financial_value,
            'precision': float(prec),
            'recall': float(rec),
            'f1': float(f1),
            'auc': float(auc),
            'tp': int(tp), 'tn': int(tn), 'fp': int(fp), 'fn': int(fn)
        }
    
    logger.info(f"\n✓ Using fixed optimal threshold: {best_threshold:.4f}")
    logger.info(f"✓ Financial value: ${best_value:,.0f}")
    
    return best_threshold, best_metrics, y_proba

# ============================================================================
# STEP 10: EVALUATE WITH OPTIMAL THRESHOLD
# ============================================================================

def evaluate_model(model, X_train, X_test, y_train, y_test, optimal_threshold):
    """Evaluate model with optimal threshold."""
    logger.info("\n" + "=" * 80)
    logger.info(f"STEP 10: EVALUATE MODEL (threshold={optimal_threshold:.2f})")
    logger.info("=" * 80)
    
    # Predictions
    y_train_proba = model.predict_proba(X_train)[:, 1]
    y_test_proba = model.predict_proba(X_test)[:, 1]
    
    y_train_pred = (y_train_proba >= optimal_threshold).astype(int)
    y_test_pred = (y_test_proba >= optimal_threshold).astype(int)
    
    # Training metrics
    logger.info("\n--- TRAINING SET METRICS ---")
    train_acc = accuracy_score(y_train, y_train_pred)
    train_prec = precision_score(y_train, y_train_pred, zero_division=0)
    train_rec = recall_score(y_train, y_train_pred, zero_division=0)
    train_f1 = f1_score(y_train, y_train_pred, zero_division=0)
    train_auc = roc_auc_score(y_train, y_train_proba)
    
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
    test_auc = roc_auc_score(y_test, y_test_proba)
    
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
    
    # Financial impact
    financial_value = (tp * TRUE_POSITIVE_VALUE + 
                      tn * TRUE_NEGATIVE_VALUE - 
                      fp * FALSE_POSITIVE_COST - 
                      fn * FALSE_NEGATIVE_COST)
    logger.info(f"\nFinancial Impact (test):")
    logger.info(f"  TP Gain:  ${tp * TRUE_POSITIVE_VALUE:>12,.0f}")
    logger.info(f"  TN Gain:  ${tn * TRUE_NEGATIVE_VALUE:>12,.0f}")
    logger.info(f"  FP Loss:  ${fp * FALSE_POSITIVE_COST:>12,.0f}")
    logger.info(f"  FN Loss:  ${fn * FALSE_NEGATIVE_COST:>12,.0f}")
    logger.info(f"  NET VALUE: ${financial_value:>14,.0f}")
    
    metrics = {
        'threshold': float(optimal_threshold),
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
        'confusion_matrix': {'TP': int(tp), 'FP': int(fp), 'FN': int(fn), 'TN': int(tn)},
        'financial_impact': {
            'tp_gain': int(tp * TRUE_POSITIVE_VALUE),
            'tn_gain': int(tn * TRUE_NEGATIVE_VALUE),
            'fp_loss': int(fp * FALSE_POSITIVE_COST),
            'fn_loss': int(fn * FALSE_NEGATIVE_COST),
            'net_value': int(financial_value)
        },
        'feature_importance': get_feature_importance(model)
    }
    
    return metrics

def get_feature_importance(model):
    """Extract feature importance from XGBoost."""
    importances = model.get_booster().get_score(importance_type='weight')
    return sorted(importances.items(), key=lambda x: x[1], reverse=True)[:10]

# ============================================================================
# STEP 11: EXPORT QUANTUM FEATURES
# ============================================================================

def export_quantum_features(X_train, X_test, y_train, y_test):
    """Export PCA-reduced features for Quantum Agent."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 11: EXPORT QUANTUM FEATURES (PCA 18D → 8D)")
    logger.info("=" * 80)
    
    pca = PCA(n_components=8)
    X_train_pca = pca.fit_transform(X_train)
    X_test_pca = pca.transform(X_test)
    
    explained_var = pca.explained_variance_ratio_.sum()
    logger.info(f"Variance explained: {explained_var:.4f} ({explained_var*100:.2f}%)")
    logger.info(f"Train shape: {X_train_pca.shape}")
    logger.info(f"Test shape: {X_test_pca.shape}")
    
    # Save for Quantum Agent
    np.save(DATA_PATH / 'quantum_X_train_8d.npy', X_train_pca)
    np.save(DATA_PATH / 'quantum_X_test_8d.npy', X_test_pca)
    np.save(DATA_PATH / 'quantum_y_train.npy', y_train.values)
    np.save(DATA_PATH / 'quantum_y_test.npy', y_test.values)
    
    logger.info("Quantum features exported")
    
    return pca

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Execute Classical ML Pipeline."""
    logger.info("\n" + "=" * 80)
    logger.info("CLASSICAL ML PIPELINE - Credit Risk Analysis (Optimized)")
    logger.info("Data_Classical_ML_Agent")
    logger.info("=" * 80 + "\n")
    
    start_time = datetime.now()
    
    try:
        # Load & EDA
        df = load_and_explore_data()
        
        # Impute
        df = impute_missing_values(df)
        
        # Engineer features
        df = engineer_features(df)
        
        # Prepare features
        X, y, feature_names = prepare_features_and_target(df)
        
        # Split
        X_train, X_test, y_train, y_test = split_data(X, y)
        
        # SMOTE
        X_train_smote, y_train_smote = apply_smote(X_train, y_train)
        
        # Normalize
        X_train_scaled, X_test_scaled, scaler = normalize_features(X_train_smote, X_test)
        
        # Train
        model = train_xgboost(X_train_scaled, y_train_smote)
        
        # Apply optimal threshold (0.1160 from cross-validation)
        optimal_threshold, threshold_metrics, y_test_proba = apply_optimal_threshold(model, X_test_scaled, y_test, fixed_threshold=0.1160)
        
        # Evaluate with optimal threshold
        metrics = evaluate_model(model, X_train_scaled, X_test_scaled, y_train_smote, y_test, optimal_threshold)
        
        # Export quantum features
        pca = export_quantum_features(X_train_scaled, X_test_scaled, y_train_smote, y_test)
        
        # Save artifacts
        logger.info("\n" + "=" * 80)
        logger.info("SAVING ARTIFACTS")
        logger.info("=" * 80)
        
        with open(MODELS_PATH / 'xgb_classical.pkl', 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"Saved model: {MODELS_PATH / 'xgb_classical.pkl'}")
        
        with open(MODELS_PATH / 'scaler.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        logger.info(f"Saved scaler: {MODELS_PATH / 'scaler.pkl'}")
        
        with open(MODELS_PATH / 'pca_8d.pkl', 'wb') as f:
            pickle.dump(pca, f)
        logger.info(f"Saved PCA: {MODELS_PATH / 'pca_8d.pkl'}")
        
        with open(MODELS_PATH / 'classical_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Saved metrics: {MODELS_PATH / 'classical_metrics.json'}")
        
        elapsed = datetime.now() - start_time
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE COMPLETED")
        logger.info("=" * 80)
        logger.info(f"Execution time: {elapsed}")
        logger.info(f"Test AUC-ROC: {metrics['test']['auc_roc']:.4f}")
        logger.info(f"Optimal Threshold: {optimal_threshold:.2f}")
        logger.info(f"Net Financial Value: ${metrics['test']['financial_impact']['net_value']:,.0f}")
        logger.info("=" * 80 + "\n")
        
        return metrics
        
    except Exception as e:
        logger.error(f"ERROR: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        metrics = main()
        print("\n" + "=" * 80)
        print("CLASSICAL ML PIPELINE - OPTIMIZED SUMMARY")
        print("=" * 80)
        print(f"\nTest Set Performance:")
        print(f"  Accuracy:  {metrics['test']['accuracy']:.4f}")
        print(f"  Precision: {metrics['test']['precision']:.4f}")
        print(f"  Recall:    {metrics['test']['recall']:.4f}")
        print(f"  F1-Score:  {metrics['test']['f1']:.4f}")
        print(f"  AUC-ROC:   {metrics['test']['auc_roc']:.4f}")
        print(f"\nOptimal Threshold: {metrics['threshold']:.2f}")
        print(f"\nFinancial Impact:")
        print(f"  Net Value: ${metrics['test']['financial_impact']['net_value']:,.0f}")
        print("=" * 80 + "\n")
    except Exception as e:
        print(f"\nERROR in Classical ML Pipeline: {str(e)}")
