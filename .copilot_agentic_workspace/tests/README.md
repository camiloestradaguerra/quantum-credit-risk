# Test Suite Documentation

## Overview

This directory contains the comprehensive test suite for the Classical ML Pipeline algorithm.

## Test Structure

```
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Pytest fixtures and configuration
├── test_classical_ml.py     # Main test suite
└── README.md                # This file
```

## Test Categories

### 1. **TestDataLoading** (4 tests)
Tests for data loading and validation:
- ✅ Sample dataset structure validation
- ✅ Target column existence and validity
- ✅ No null values in critical columns
- ✅ Default rate within reasonable bounds

### 2. **TestFeatureEngineering** (3 tests)
Tests for feature engineering pipeline:
- ✅ Engineered features creation (10 risk metrics)
- ✅ Engineered features are numeric and no NaN
- ✅ Feature ranges are reasonable

### 3. **TestDataPreprocessing** (3 tests)
Tests for data preprocessing steps:
- ✅ KNN imputation handles missing values
- ✅ StandardScaler normalization (mean=0, std=1)
- ✅ SMOTE balancing increases minority class

### 4. **TestModelTraining** (3 tests)
Tests for model training and evaluation:
- ✅ XGBoost training completes successfully
- ✅ Model produces valid probability predictions (0-1)
- ✅ Model achieves reasonable AUC (>0.50)

### 5. **TestThresholdOptimization** (4 tests)
Tests for threshold optimization:
- ✅ Threshold values are valid (0-1)
- ✅ Different thresholds affect metrics
- ✅ Optimal threshold (0.1160) works correctly
- ✅ Financial impact calculation is valid

### 6. **TestRobustness** (4 tests)
Tests for robustness and edge cases:
- ✅ Handles missing values gracefully
- ✅ Handles imbalanced classes
- ✅ Handles outliers without crashing
- ✅ Reproducible results with seed

### 7. **TestEndToEndPipeline** (2 tests)
End-to-end integration tests:
- ✅ Full pipeline executes without errors
- ✅ Pipeline produces required business metrics

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Class
```bash
pytest tests/test_classical_ml.py::TestDataLoading -v
```

### Run Specific Test
```bash
pytest tests/test_classical_ml.py::TestModelTraining::test_xgboost_training -v
```

### Run with Coverage Report
```bash
pytest --cov=scripts --cov-report=html
```

### Run Only Fast Tests (Skip Slow)
```bash
pytest -m "not slow"
```

### Run Specific Category
```bash
pytest -m classical_ml -v
```

## Fixtures

Available fixtures in `conftest.py`:

- **sample_credit_data**: 100-row sample dataset with realistic features
- **real_credit_data**: Real dataset from data/credit_risk_dataset.csv
- **engineered_features_sample**: 50x18 matrix of engineered features
- **sample_predictions**: Probability predictions (50 samples)
- **sample_true_labels**: Binary true labels (50 samples)

## Expected Test Results

All tests should pass with the optimized classical ML pipeline:

```
✅ TestDataLoading: 4/4 passed
✅ TestFeatureEngineering: 3/3 passed
✅ TestDataPreprocessing: 3/3 passed
✅ TestModelTraining: 3/3 passed
✅ TestThresholdOptimization: 4/4 passed
✅ TestRobustness: 4/4 passed
✅ TestEndToEndPipeline: 2/2 passed

TOTAL: 23/23 passed ✅
```

## Test Metrics

Each test validates:
1. **Correctness** - Produces expected output
2. **Validity** - Output meets business constraints
3. **Robustness** - Handles edge cases
4. **Performance** - Executes within reasonable time

## Adding New Tests

To add new tests:

1. Create test function in appropriate class
2. Use existing fixtures or create new ones in `conftest.py`
3. Name function as `test_<description>`
4. Add docstring explaining test purpose
5. Use assertions to validate behavior

Example:
```python
def test_new_feature(sample_credit_data):
    """Test description."""
    assert condition, "Error message"
```

## Integration with CI/CD

These tests are designed to run in continuous integration pipelines:

```yaml
# Example CI/CD configuration
test:
  script:
    - pip install -r requirements.txt
    - pytest --cov --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

## Troubleshooting

### Test Failures
- Check data file exists: `data/credit_risk_dataset.csv`
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check Python version: >= 3.8

### Missing Fixtures
- Ensure `conftest.py` is in tests directory
- Fixtures must be defined before use

### Import Errors
- Verify `__init__.py` exists in tests directory
- Check sys.path includes parent directory

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)
- [Classical ML Pipeline](../scripts/1_classical_ml_pipeline_optimized.py)

---

**Last Updated:** May 20, 2026  
**Maintainer:** Project Team  
**Status:** ✅ Production Ready
