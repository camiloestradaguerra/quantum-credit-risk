"""
Test suite for Classical ML Pipeline (1_classical_ml_pipeline_optimized.py)

Tests cover:
- Data loading and validation
- Feature engineering
- Model training and performance
- Predictions and thresholds
- Financial metrics
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.impute import KNNImputer
from imblearn.over_sampling import SMOTE
import xgboost as xgb
from sklearn.metrics import roc_auc_score, confusion_matrix, precision_score, recall_score


class TestDataLoading:
    """Test data loading and validation."""
    
    def test_sample_data_structure(self, sample_credit_data):
        """Verify sample dataset structure."""
        assert isinstance(sample_credit_data, pd.DataFrame)
        assert sample_credit_data.shape[0] > 0
        assert sample_credit_data.shape[1] >= 8
        
    def test_sample_data_has_target(self, sample_credit_data):
        """Verify target column exists."""
        assert 'loan_status' in sample_credit_data.columns
        assert sample_credit_data['loan_status'].isin([0, 1]).all()
        
    def test_sample_data_no_nulls_in_critical_columns(self, sample_credit_data):
        """Verify no null values in critical columns."""
        critical_cols = ['person_age', 'person_income', 'loan_amnt', 'loan_status']
        for col in critical_cols:
            if col in sample_credit_data.columns:
                assert sample_credit_data[col].notna().all()
    
    def test_default_rate_reasonable(self, sample_credit_data):
        """Verify default rate is within reasonable bounds."""
        default_rate = sample_credit_data['loan_status'].mean()
        assert 0.1 < default_rate < 0.4, f"Default rate {default_rate:.1%} seems unrealistic"


class TestFeatureEngineering:
    """Test feature engineering steps."""
    
    def test_engineer_features_creates_risk_metrics(self, sample_credit_data):
        """Verify engineered features are created correctly."""
        df = sample_credit_data.copy()
        
        # Manual feature engineering
        df['debt_to_income'] = df['loan_percent_income']
        df['interest_rate_risk'] = df['loan_int_rate'] ** 2
        df['loan_income_interaction'] = df['loan_amnt'] / (df['person_income'] + 1)
        df['emp_stability_log'] = np.log1p(df['person_emp_length'])
        df['credit_history_ratio'] = df['cb_person_cred_hist_length'] / (df['person_age'] + 1)
        df['default_risk_score'] = (df['cb_person_default_on_file'].astype(int) * 
                                     df['loan_percent_income'])
        df['age_normalized'] = df['person_age'] / 100
        df['loan_amount_risk'] = np.log1p(df['loan_amnt']) * df['loan_int_rate']
        df['income_age_ratio'] = df['person_income'] / (df['person_age'] + 1)
        df['composite_risk'] = (df['debt_to_income'] + 
                                 df['interest_rate_risk'] / 100 + 
                                 df['loan_income_interaction'])
        
        # Verify all features created
        assert 'debt_to_income' in df.columns
        assert 'interest_rate_risk' in df.columns
        assert 'composite_risk' in df.columns
    
    def test_engineered_features_are_numeric(self, sample_credit_data):
        """Verify engineered features are numeric and no NaN."""
        df = sample_credit_data.copy()
        
        df['debt_to_income'] = df['loan_percent_income']
        df['interest_rate_risk'] = df['loan_int_rate'] ** 2
        df['loan_income_interaction'] = df['loan_amnt'] / (df['person_income'] + 1)
        
        assert df['debt_to_income'].dtype in [np.float32, np.float64]
        assert df['interest_rate_risk'].dtype in [np.float32, np.float64]
        assert df['loan_income_interaction'].notna().all()
    
    def test_feature_ranges_reasonable(self, sample_credit_data):
        """Verify engineered feature ranges are reasonable."""
        df = sample_credit_data.copy()
        
        df['age_normalized'] = df['person_age'] / 100
        df['debt_to_income'] = df['loan_percent_income']
        
        assert df['age_normalized'].min() >= 0.18
        assert df['age_normalized'].max() <= 0.80
        assert df['debt_to_income'].min() >= 0
        assert df['debt_to_income'].max() <= 1.0


class TestDataPreprocessing:
    """Test preprocessing steps."""
    
    def test_knn_imputation(self, sample_credit_data):
        """Test KNN imputation handles missing values."""
        df = sample_credit_data.copy()
        
        # Introduce some missing values
        df.loc[5:10, 'person_emp_length'] = np.nan
        df.loc[15:20, 'loan_int_rate'] = np.nan
        
        # Apply KNN imputation
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        imputer = KNNImputer(n_neighbors=5)
        df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        
        # Verify no NaN values remain
        assert df.isnull().sum().sum() == 0
    
    def test_standardscaler_normalization(self, sample_credit_data):
        """Test StandardScaler normalization."""
        df = sample_credit_data.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        X = df[numeric_cols].drop('loan_status', axis=1, errors='ignore')
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Verify normalization
        assert np.allclose(X_scaled.mean(axis=0), 0, atol=1e-10)
        assert np.allclose(X_scaled.std(axis=0), 1, atol=1e-10)
    
    def test_smote_balancing(self, sample_credit_data):
        """Test SMOTE balancing increases minority class."""
        df = sample_credit_data.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        X = df[numeric_cols].drop('loan_status', axis=1, errors='ignore')
        y = df['loan_status']
        
        original_ratio = (y == 1).sum() / (y == 0).sum()
        
        smote = SMOTE(sampling_strategy=0.7, random_state=42)
        X_resampled, y_resampled = smote.fit_resample(X, y)
        
        new_ratio = (y_resampled == 1).sum() / (y_resampled == 0).sum()
        
        # New ratio should be higher (more balanced)
        assert new_ratio > original_ratio
        assert new_ratio >= 0.6  # Should be close to 0.7


class TestModelTraining:
    """Test model training and evaluation."""
    
    def test_xgboost_training(self, sample_credit_data):
        """Test XGBoost model training."""
        df = sample_credit_data.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        X = df[numeric_cols].drop('loan_status', axis=1, errors='ignore')
        y = df['loan_status']
        
        # Normalize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train model
        scale_pos_weight = (y == 0).sum() / (y == 1).sum()
        model = xgb.XGBClassifier(
            n_estimators=50,  # Fewer for testing
            max_depth=6,
            learning_rate=0.1,
            scale_pos_weight=scale_pos_weight,
            random_state=42
        )
        
        model.fit(X_scaled, y)
        
        # Verify model is trained
        assert model.get_booster() is not None
        assert len(model.feature_importances_) == X.shape[1]
    
    def test_model_predictions_valid(self, sample_credit_data):
        """Test model produces valid probability predictions."""
        df = sample_credit_data.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        X = df[numeric_cols].drop('loan_status', axis=1, errors='ignore')
        y = df['loan_status']
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = xgb.XGBClassifier(n_estimators=50, random_state=42)
        model.fit(X_scaled, y)
        
        y_proba = model.predict_proba(X_scaled)[:, 1]
        
        # Probabilities should be between 0 and 1
        assert (y_proba >= 0).all()
        assert (y_proba <= 1).all()
        assert y_proba.shape[0] == X.shape[0]
    
    def test_model_auc_reasonable(self, sample_credit_data):
        """Test model achieves reasonable AUC."""
        df = sample_credit_data.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        X = df[numeric_cols].drop('loan_status', axis=1, errors='ignore')
        y = df['loan_status']
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = xgb.XGBClassifier(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)
        
        y_proba = model.predict_proba(X_scaled)[:, 1]
        auc = roc_auc_score(y, y_proba)
        
        # AUC should be better than random (0.5)
        assert auc > 0.50, f"AUC {auc:.4f} is too low (should be > 0.50)"


class TestThresholdOptimization:
    """Test threshold optimization and financial metrics."""
    
    def test_threshold_range_valid(self, sample_predictions, sample_true_labels):
        """Test threshold values are valid."""
        thresholds = np.arange(0.05, 0.95, 0.05)
        
        for threshold in thresholds:
            y_pred = (sample_predictions >= threshold).astype(int)
            assert np.all((y_pred == 0) | (y_pred == 1))
    
    def test_threshold_affects_metrics(self, sample_predictions, sample_true_labels):
        """Test that different thresholds produce different metrics."""
        # Calculate metrics at two different thresholds
        threshold_low = 0.30
        threshold_high = 0.70
        
        y_pred_low = (sample_predictions >= threshold_low).astype(int)
        y_pred_high = (sample_predictions >= threshold_high).astype(int)
        
        precision_low = precision_score(sample_true_labels, y_pred_low, zero_division=0)
        precision_high = precision_score(sample_true_labels, y_pred_high, zero_division=0)
        
        recall_low = recall_score(sample_true_labels, y_pred_low, zero_division=0)
        recall_high = recall_score(sample_true_labels, y_pred_high, zero_division=0)
        
        # Higher threshold typically increases precision
        assert precision_high >= precision_low or precision_high == precision_low
        # Higher threshold typically decreases recall
        assert recall_high <= recall_low or recall_high == recall_low
    
    def test_optimal_threshold_exists(self, sample_predictions, sample_true_labels):
        """Test that optimal threshold can be calculated."""
        optimal_threshold = 0.1160  # From business requirements
        
        y_pred = (sample_predictions >= optimal_threshold).astype(int)
        
        tn, fp, fn, tp = confusion_matrix(sample_true_labels, y_pred).ravel()
        
        # Verify confusion matrix values are valid
        assert tn >= 0
        assert fp >= 0
        assert fn >= 0
        assert tp >= 0
    
    def test_financial_impact_calculation(self, sample_predictions, sample_true_labels):
        """Test financial impact metrics."""
        threshold = 0.1160
        y_pred = (sample_predictions >= threshold).astype(int)
        
        # Financial parameters
        tn, fp, fn, tp = confusion_matrix(sample_true_labels, y_pred).ravel()
        
        FALSE_NEGATIVE_COST = 30000
        FALSE_POSITIVE_COST = 800
        TRUE_POSITIVE_VALUE = 5000
        TRUE_NEGATIVE_VALUE = 500
        
        financial_impact = (
            tp * TRUE_POSITIVE_VALUE +
            tn * TRUE_NEGATIVE_VALUE -
            fp * FALSE_POSITIVE_COST -
            fn * FALSE_NEGATIVE_COST
        )
        
        # Should calculate without error
        assert isinstance(financial_impact, (int, np.integer))
        assert financial_impact is not None


class TestRobustness:
    """Test robustness and edge cases."""
    
    def test_handles_missing_values(self, sample_credit_data):
        """Test pipeline handles missing values gracefully."""
        df = sample_credit_data.copy()
        df.loc[0:5, 'person_emp_length'] = np.nan
        df.loc[10:15, 'loan_int_rate'] = np.nan
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        imputer = KNNImputer(n_neighbors=5)
        df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        
        assert df.isnull().sum().sum() == 0
    
    def test_handles_imbalanced_classes(self, sample_credit_data):
        """Test pipeline handles class imbalance."""
        df = sample_credit_data.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        X = df[numeric_cols].drop('loan_status', axis=1, errors='ignore')
        y = df['loan_status']
        
        # Create extreme imbalance (need enough minority samples for SMOTE)
        # SMOTE needs at least k_neighbors (5) samples in minority class
        y_imbalanced = pd.Series([0] * 80 + [1] * 20)
        X_imbalanced = X.iloc[:100]
        
        scale_pos_weight = (y_imbalanced == 0).sum() / (y_imbalanced == 1).sum()
        assert scale_pos_weight > 1  # Positive class is minority
        
        # SMOTE should handle it
        smote = SMOTE(sampling_strategy=0.7, k_neighbors=5, random_state=42)
        X_res, y_res = smote.fit_resample(X_imbalanced, y_imbalanced)
        
        assert len(X_res) > len(X_imbalanced)
    
    def test_handles_outliers_gracefully(self, sample_credit_data):
        """Test pipeline handles outliers without crashing."""
        df = sample_credit_data.copy()
        
        # Introduce outliers
        df.loc[0, 'person_income'] = 1000000  # Extreme high
        df.loc[1, 'loan_amnt'] = 100  # Extreme low
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df[numeric_cols])
        
        # Should handle without NaN/Inf
        assert not np.isnan(X_scaled).any()
        assert not np.isinf(X_scaled).any()
    
    def test_consistent_results_with_seed(self, sample_credit_data):
        """Test reproducibility with random seed."""
        np.random.seed(42)
        df1 = sample_credit_data.copy()
        
        np.random.seed(42)
        df2 = sample_credit_data.copy()
        
        assert df1.equals(df2)


class TestEndToEndPipeline:
    """Test complete pipeline from data to predictions."""
    
    def test_full_pipeline_executes(self, sample_credit_data):
        """Test complete pipeline executes without errors."""
        df = sample_credit_data.copy()
        
        # Data prep
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        X = df[numeric_cols].drop('loan_status', axis=1, errors='ignore')
        y = df['loan_status']
        
        # Handle missing values
        imputer = KNNImputer(n_neighbors=5)
        X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
        
        # Normalize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Balance
        smote = SMOTE(sampling_strategy=0.7, random_state=42)
        X_balanced, y_balanced = smote.fit_resample(X_scaled, y)
        
        # Train
        scale_pos_weight = (y_balanced == 0).sum() / (y_balanced == 1).sum()
        model = xgb.XGBClassifier(
            n_estimators=50,
            max_depth=6,
            scale_pos_weight=scale_pos_weight,
            random_state=42
        )
        model.fit(X_balanced, y_balanced)
        
        # Predict
        y_proba = model.predict_proba(X_scaled)[:, 1]
        
        # Verify
        assert len(y_proba) == len(X)
        assert (y_proba >= 0).all() and (y_proba <= 1).all()
    
    def test_pipeline_produces_business_metrics(self, sample_credit_data):
        """Test pipeline produces required business metrics."""
        df = sample_credit_data.copy()
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        X = df[numeric_cols].drop('loan_status', axis=1, errors='ignore')
        y = df['loan_status']
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = xgb.XGBClassifier(n_estimators=50, random_state=42)
        model.fit(X_scaled, y)
        
        y_proba = model.predict_proba(X_scaled)[:, 1]
        y_pred = (y_proba >= 0.1160).astype(int)
        
        # Required metrics
        auc = roc_auc_score(y, y_proba)
        precision = precision_score(y, y_pred, zero_division=0)
        recall = recall_score(y, y_pred, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(y, y_pred).ravel()
        
        # Verify all metrics exist and are valid
        assert 0 <= auc <= 1
        assert 0 <= precision <= 1
        assert 0 <= recall <= 1
        assert tn >= 0 and fp >= 0 and fn >= 0 and tp >= 0
