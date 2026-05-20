#!/usr/bin/env python3
"""
CLASSICAL ML PIPELINE - Data_Classical_ML_Agent (Real Dataset)
==============================================================

Agent: Data_Classical_ML_Agent
Version: 2.0 - Real Credit Risk Dataset

Pipeline Steps:
  1. Load & EDA (32,581 records x 12 features, 21.8% default)
  2. Impute missing values (KNN k=5)
  3. Engineer 10 advanced risk features
  4. Prepare numeric features & target
  5. Train/test split (80/20, stratified)
  6. SMOTE balancing (0.7 ratio)
  7. StandardScaler normalization
  8. Train XGBoost (200 trees, depth=6)
  9. Evaluate metrics (AUC-ROC, F1, precision, recall)
  10. Export 8D features for Quantum Agent (PCA)

Output: xgb_classical.pkl, classical_metrics.json, quantum features (8D)
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
    roc_auc_score, confusion_matrix
)

# Imbalanced-learn
from imblearn.over_sampling import SMOTE

# XGBoost
import xgboost as xgb

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# Setup paths
SCRIPT_DIR = Path(__file__).parent.parent
DATA_PATH = SCRIPT_DIR / 'data' / 'credit_risk_dataset.csv'
MODELS_PATH = SCRIPT_DIR / 'models'
LOGS_PATH = SCRIPT_DIR / 'logs'
MODELS_PATH.mkdir(exist_ok=True)
LOGS_PATH.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_PATH / 'classical_ml_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# XGBoost Hyperparameters
XGB_PARAMS = {
    'n_estimators': 200,
    'max_depth': 6,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'reg_alpha': 1.0,
    'reg_lambda': 1.0,
    'random_state': RANDOM_STATE,
    'n_jobs': -1,
    'verbosity': 1
}

# Feature engineering parameters
N_PCA_COMPONENTS = 8

# SMOTE parameters
SMOTE_SAMPLING_RATIO = 0.7
SMOTE_K_NEIGHBORS = 5

# Data split
TEST_SIZE = 0.2

# ============================================================================
# STEP 1: LOAD & EDA
# ============================================================================

def load_and_explore_data():
    """Load dataset and perform exploratory data analysis."""
    logger.info("=" * 80)
    logger.info("STEP 1: LOAD & EXPLORATORY DATA ANALYSIS")
    logger.info("=" * 80)
    
    logger.info(f"Loading dataset from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    
    logger.info(f"Dataset shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")
    logger.info(f"\nData types:\n{df.dtypes}")
    logger.info(f"\nMissing values:\n{df.isnull().sum()}")
    logger.info(f"\nBasic statistics:\n{df.describe()}")
    
    # Target variable analysis
    default_rate = df['loan_status'].mean()
    logger.info(f"\nDefault rate: {default_rate:.2%}")
    logger.info(f"Class distribution:\n{df['loan_status'].value_counts()}")
    
    return df

# ============================================================================
# STEP 2: HANDLE MISSING VALUES
# ============================================================================

def impute_missing_values(df):
    """Handle missing values using KNN imputation."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 2: IMPUTE MISSING VALUES (KNN k=5)")
    logger.info("=" * 80)
    
    # Convert string columns to numeric FIRST
    if df['cb_person_default_on_file'].dtype in ['object', 'string']:
        df['cb_person_default_on_file'] = (df['cb_person_default_on_file'] == 'Y').astype(int)
        logger.info("Converted cb_person_default_on_file (Y/N) to numeric (1/0)")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    logger.info(f"Numeric columns: {len(numeric_cols)}")
    
    # KNN Imputation
    imputer = KNNImputer(n_neighbors=5, weights='distance')
    df_numeric = df[numeric_cols].copy()
    df_imputed = imputer.fit_transform(df_numeric)
    df[numeric_cols] = df_imputed
    
    logger.info(f"After imputation - Missing values: {df.isnull().sum().sum()}")
    
    return df

# ============================================================================
# STEP 3: FEATURE ENGINEERING
# ============================================================================

def engineer_features(df):
    """Engineer 10 credit risk features from real dataset."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 3: FEATURE ENGINEERING (10 Risk Features)")
    logger.info("=" * 80)
    
    df_eng = df.copy()
    
    # Feature 1: Debt-to-Income Ratio
    df_eng['debt_to_income'] = df_eng['loan_amnt'] / (df_eng['person_income'] + 1)
    logger.info("Feature 1: debt_to_income = loan_amnt / person_income")
    
    # Feature 2: Interest Rate Risk
    df_eng['interest_rate_risk'] = df_eng['loan_int_rate'] * (1 + df_eng['loan_percent_income'])
    logger.info("Feature 2: interest_rate_risk")
    
    # Feature 3: Loan-to-Income Advanced
    df_eng['loan_income_interaction'] = (df_eng['loan_amnt'] / (df_eng['person_income'] + 1)) * df_eng['loan_int_rate']
    logger.info("Feature 3: loan_income_interaction")
    
    # Feature 4: Employment Stability
    df_eng['emp_stability_log'] = np.log1p(df_eng['person_emp_length'] + 1)
    logger.info("Feature 4: emp_stability_log")
    
    # Feature 5: Credit History Impact
    df_eng['credit_history_ratio'] = df_eng['cb_person_cred_hist_length'] / (df_eng['person_age'] + 1)
    logger.info("Feature 5: credit_history_ratio")
    
    # Feature 6: Historical Default Risk
    df_eng['default_risk_score'] = df_eng['cb_person_default_on_file'].astype(int) * df_eng['loan_percent_income']
    logger.info("Feature 6: default_risk_score")
    
    # Feature 7: Age-Normalized
    df_eng['age_normalized'] = df_eng['person_age'] / (df_eng['person_age'].max() + 1)
    logger.info("Feature 7: age_normalized")
    
    # Feature 8: Loan Amount Risk
    df_eng['loan_amount_risk'] = np.log1p(df_eng['loan_amnt']) * df_eng['loan_int_rate']
    logger.info("Feature 8: loan_amount_risk")
    
    # Feature 9: Income Stability Index
    df_eng['income_age_ratio'] = df_eng['person_income'] / (df_eng['person_age'] + 1)
    logger.info("Feature 9: income_age_ratio")
    
    # Feature 10: Composite Risk Score
    df_eng['composite_risk'] = (
        df_eng['loan_percent_income'] * 0.35 +
        (df_eng['loan_int_rate'] / 20) * 0.35 +
        df_eng['default_risk_score'] * 0.20 +
        (df_eng['cb_person_default_on_file'].astype(int) * 0.10)
    )
    logger.info("Feature 10: composite_risk")
    
    logger.info(f"Total features after engineering: {df_eng.shape[1]}")
    
    return df_eng

# ============================================================================
# STEP 4: PREPARE FEATURES & TARGET
# ============================================================================

def prepare_features_and_target(df):
    """Select numeric features and prepare X, y."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 4: PREPARE FEATURES & TARGET")
    logger.info("=" * 80)
    
    # Target variable
    y = df['loan_status'].astype(int).values
    logger.info(f"Target distribution: {np.bincount(y)}")
    
    # Drop non-numeric and target columns
    drop_cols = ['loan_status', 'person_home_ownership', 'loan_intent', 'loan_grade']
    X = df.drop(columns=drop_cols, errors='ignore')
    
    # Keep only numeric columns
    X = X.select_dtypes(include=[np.number])
    
    logger.info(f"Features shape: {X.shape}")
    logger.info(f"Numeric features: {list(X.columns)[:10]}...")
    
    return X.values, y

# ============================================================================
# STEP 5: TRAIN/TEST SPLIT
# ============================================================================

def split_data(X, y):
    """Split data with stratification (80/20)."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 5: TRAIN/TEST SPLIT (80/20 stratified)")
    logger.info("=" * 80)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=RANDOM_STATE
    )
    
    logger.info(f"Training set: {X_train.shape}")
    logger.info(f"Test set: {X_test.shape}")
    logger.info(f"Train default rate: {y_train.mean():.2%}")
    logger.info(f"Test default rate: {y_test.mean():.2%}")
    
    return X_train, X_test, y_train, y_test

# ============================================================================
# STEP 6: SMOTE BALANCING
# ============================================================================

def apply_smote(X_train, y_train):
    """Apply SMOTE to balance training data."""
    logger.info("\n" + "=" * 80)
    logger.info(f"STEP 6: SMOTE BALANCING (ratio={SMOTE_SAMPLING_RATIO})")
    logger.info("=" * 80)
    
    logger.info(f"Before SMOTE: {np.bincount(y_train)}")
    
    smote = SMOTE(
        sampling_strategy=SMOTE_SAMPLING_RATIO,
        k_neighbors=SMOTE_K_NEIGHBORS,
        random_state=RANDOM_STATE
    )
    X_balanced, y_balanced = smote.fit_resample(X_train, y_train)
    
    logger.info(f"After SMOTE: {np.bincount(y_balanced)}")
    logger.info(f"Balanced training shape: {X_balanced.shape}")
    
    return X_balanced, y_balanced

# ============================================================================
# STEP 7: NORMALIZE FEATURES
# ============================================================================

def normalize_features(X_train, X_test):
    """Normalize using StandardScaler."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 7: NORMALIZE FEATURES (StandardScaler)")
    logger.info("=" * 80)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    logger.info(f"Scaled train mean: {X_train_scaled.mean():.4f}, std: {X_train_scaled.std():.4f}")
    logger.info(f"Scaled test mean: {X_test_scaled.mean():.4f}, std: {X_test_scaled.std():.4f}")
    
    return X_train_scaled, X_test_scaled, scaler

# ============================================================================
# STEP 8: TRAIN XGBOOST
# ============================================================================

def train_xgboost(X_train, y_train):
    """Train XGBoost classifier."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 8: TRAIN XGBOOST CLASSIFIER")
    logger.info("=" * 80)
    logger.info(f"Hyperparameters: {XGB_PARAMS}")
    
    # Calculate scale_pos_weight for class imbalance
    neg_count = np.sum(y_train == 0)
    pos_count = np.sum(y_train == 1)
    scale_pos_weight = neg_count / pos_count
    logger.info(f"scale_pos_weight: {scale_pos_weight:.4f}")
    
    XGB_PARAMS['scale_pos_weight'] = scale_pos_weight
    
    # Create classifier
    xgb_model = xgb.XGBClassifier(**XGB_PARAMS)
    
    # Train
    xgb_model.fit(X_train, y_train)
    
    logger.info(f"Training completed")
    
    return xgb_model

# ============================================================================
# STEP 9: EVALUATE MODEL
# ============================================================================

def evaluate_model(model, X_train, X_test, y_train, y_test):
    """Evaluate model on train and test sets."""
    logger.info("\n" + "=" * 80)
    logger.info("STEP 9: EVALUATE MODEL")
    logger.info("=" * 80)
    
    # Predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    y_train_proba = model.predict_proba(X_train)[:, 1]
    y_test_proba = model.predict_proba(X_test)[:, 1]
    
    # Training metrics
    logger.info("\n--- TRAINING SET METRICS ---")
    train_acc = accuracy_score(y_train, y_train_pred)
    train_prec = precision_score(y_train, y_train_pred)
    train_rec = recall_score(y_train, y_train_pred)
    train_f1 = f1_score(y_train, y_train_pred)
    train_auc = roc_auc_score(y_train, y_train_proba)
    
    logger.info(f"Accuracy:  {train_acc:.4f}")
    logger.info(f"Precision: {train_prec:.4f}")
    logger.info(f"Recall:    {train_rec:.4f}")
    logger.info(f"F1-Score:  {train_f1:.4f}")
    logger.info(f"AUC-ROC:   {train_auc:.4f}")
    
    # Test metrics
    logger.info("\n--- TEST SET METRICS ---")
    test_acc = accuracy_score(y_test, y_test_pred)
    test_prec = precision_score(y_test, y_test_pred)
    test_rec = recall_score(y_test, y_test_pred)
    test_f1 = f1_score(y_test, y_test_pred)
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
    
    # Feature importance
    logger.info("\n--- TOP 10 FEATURE IMPORTANCE ---")
    feature_importance = pd.DataFrame({
        'feature': range(X_train.shape[1]),
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False).head(10)
    logger.info(f"\n{feature_importance}")
    
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
        'confusion_matrix': {'TP': int(tp), 'FP': int(fp), 'FN': int(fn), 'TN': int(tn)},
        'feature_importance': feature_importance.to_dict('records')
    }
    
    return metrics

# ============================================================================
# STEP 10: EXPORT FOR QUANTUM AGENT
# ============================================================================

def export_quantum_features(X_train_scaled, X_test_scaled, y_train, y_test):
    """Reduce to 8D features for Quantum Agent and export."""
    logger.info("\n" + "=" * 80)
    logger.info(f"STEP 10: EXPORT 8D FEATURES FOR QUANTUM AGENT (PCA)")
    logger.info("=" * 80)
    
    # PCA to 8 components
    pca = PCA(n_components=N_PCA_COMPONENTS, random_state=RANDOM_STATE)
    X_train_8d = pca.fit_transform(X_train_scaled)
    X_test_8d = pca.transform(X_test_scaled)
    
    logger.info(f"Original shape: {X_train_scaled.shape}")
    logger.info(f"Reduced shape: {X_train_8d.shape}")
    logger.info(f"Explained variance ratio: {pca.explained_variance_ratio_.sum():.4f}")
    logger.info(f"Variance per component: {pca.explained_variance_ratio_}")
    
    # Save as NumPy files
    np.save(SCRIPT_DIR / 'data' / 'quantum_X_train_8d.npy', X_train_8d)
    np.save(SCRIPT_DIR / 'data' / 'quantum_X_test_8d.npy', X_test_8d)
    np.save(SCRIPT_DIR / 'data' / 'quantum_y_train.npy', y_train)
    np.save(SCRIPT_DIR / 'data' / 'quantum_y_test.npy', y_test)
    
    logger.info(f"Exported quantum features to data/ directory")
    
    return pca

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Execute full classical ML pipeline."""
    logger.info("\n" + "=" * 80)
    logger.info("CLASSICAL ML PIPELINE - Credit Risk Analysis")
    logger.info("Data_Classical_ML_Agent")
    logger.info("=" * 80 + "\n")
    
    start_time = datetime.now()
    
    try:
        # Step 1: Load & EDA
        df = load_and_explore_data()
        
        # Step 2: Impute
        df = impute_missing_values(df)
        
        # Step 3: Feature engineering
        df = engineer_features(df)
        
        # Step 4: Prepare
        X, y = prepare_features_and_target(df)
        
        # Step 5: Split
        X_train, X_test, y_train, y_test = split_data(X, y)
        
        # Step 6: SMOTE
        X_train_balanced, y_train_balanced = apply_smote(X_train, y_train)
        
        # Step 7: Normalize
        X_train_scaled, X_test_scaled, scaler = normalize_features(X_train_balanced, X_test)
        
        # Step 8: Train XGBoost
        xgb_model = train_xgboost(X_train_scaled, y_train_balanced)
        
        # Step 9: Evaluate
        metrics = evaluate_model(xgb_model, X_train_scaled, X_test_scaled, y_train_balanced, y_test)
        
        # Step 10: Export for Quantum
        pca = export_quantum_features(X_train_scaled, X_test_scaled, y_train_balanced, y_test)
        
        # Save artifacts
        logger.info("\n" + "=" * 80)
        logger.info("SAVING ARTIFACTS")
        logger.info("=" * 80)
        
        # Save model
        with open(MODELS_PATH / 'xgb_classical.pkl', 'wb') as f:
            pickle.dump(xgb_model, f)
        logger.info(f"Saved model: {MODELS_PATH / 'xgb_classical.pkl'}")
        
        # Save scaler
        with open(MODELS_PATH / 'scaler.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        logger.info(f"Saved scaler: {MODELS_PATH / 'scaler.pkl'}")
        
        # Save PCA
        with open(MODELS_PATH / 'pca_8d.pkl', 'wb') as f:
            pickle.dump(pca, f)
        logger.info(f"Saved PCA: {MODELS_PATH / 'pca_8d.pkl'}")
        
        # Save metrics
        with open(MODELS_PATH / 'classical_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Saved metrics: {MODELS_PATH / 'classical_metrics.json'}")
        
        # Execution summary
        elapsed = datetime.now() - start_time
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Execution time: {elapsed}")
        logger.info(f"Test AUC-ROC: {metrics['test']['auc_roc']:.4f}")
        logger.info(f"Test F1-Score: {metrics['test']['f1']:.4f}")
        logger.info("\nNext: Run Quantum ML Agent (2_quantum_ml_pipeline.py)")
        logger.info("=" * 80 + "\n")
        
        return metrics
        
    except Exception as e:
        logger.error(f"ERROR: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    metrics = main()
    
    # Print summary
    print("\n" + "=" * 80)
    print("CLASSICAL ML PIPELINE - SUMMARY")
    print("=" * 80)
    print(f"\nTest Set Performance:")
    print(f"  Accuracy:  {metrics['test']['accuracy']:.4f}")
    print(f"  Precision: {metrics['test']['precision']:.4f}")
    print(f"  Recall:    {metrics['test']['recall']:.4f}")
    print(f"  F1-Score:  {metrics['test']['f1']:.4f}")
    print(f"  AUC-ROC:   {metrics['test']['auc_roc']:.4f}")
    print("\nArtifacts saved:")
    print(f"  - {MODELS_PATH / 'xgb_classical.pkl'}")
    print(f"  - {MODELS_PATH / 'classical_metrics.json'}")
    print(f"  - Quantum features in data/ (8D)")
    print("=" * 80 + "\n")
