"""
pytest configuration and shared fixtures for test suite.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_credit_data():
    """Create sample credit risk dataset for testing."""
    np.random.seed(42)
    n_samples = 100
    
    data = {
        'person_age': np.random.randint(18, 80, n_samples),
        'person_income': np.random.randint(20000, 150000, n_samples),
        'person_emp_length': np.random.uniform(0, 60, n_samples),
        'loan_amnt': np.random.randint(500, 50000, n_samples),
        'loan_int_rate': np.random.uniform(5, 25, n_samples),
        'loan_percent_income': np.random.uniform(0.02, 0.5, n_samples),
        'cb_person_default_on_file': np.random.choice([0, 1], n_samples),
        'cb_person_cred_hist_length': np.random.uniform(1, 80, n_samples),
        'loan_status': np.random.choice([0, 1], n_samples, p=[0.78, 0.22])  # ~22% default rate
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def real_credit_data():
    """Load real credit risk dataset if available."""
    data_path = Path(__file__).parent.parent / 'data' / 'credit_risk_dataset.csv'
    
    if data_path.exists():
        return pd.read_csv(data_path)
    else:
        pytest.skip("Real dataset not available")


@pytest.fixture
def engineered_features_sample():
    """Sample engineered features (18 features)."""
    np.random.seed(42)
    n_samples = 50
    
    features = np.random.randn(n_samples, 18) * np.array([
        30, 50000, 20, 20000, 10, 0.3, 0.5, 40,  # Original 8
        0.3, 100, 1, 3.5, 0.1, 0.5, 0.5, 5, 2000, 1  # Engineered 10
    ])
    
    return features


@pytest.fixture
def sample_predictions():
    """Sample probability predictions."""
    np.random.seed(42)
    return np.random.uniform(0, 1, 50)


@pytest.fixture
def sample_true_labels():
    """Sample true binary labels."""
    np.random.seed(42)
    return np.random.binomial(1, 0.22, 50)
