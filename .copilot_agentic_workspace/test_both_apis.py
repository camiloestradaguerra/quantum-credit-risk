#!/usr/bin/env python3
"""
TEST BOTH APIs - Classical vs Quantum
======================================

Makes identical requests to both APIs and compares predictions.
Run AFTER both APIs are deployed:
  Terminal 1: python deploy.py (port 8000)
  Terminal 2: python deploy_quantum.py (port 8001)

Usage:
  python test_both_apis.py
"""

import requests
import json
from datetime import datetime
import time

# ============================================================================
# TEST DATA - Same example for both APIs
# ============================================================================

TEST_CASES = [
    {
        "name": "Low Risk Profile",
        "data": {
            "age": 35,
            "income": 50000,
            "loan_amount": 10000,
            "interest_rate": 8.5,
            "employment_length": 5,
            "credit_history": 10,
            "default_on_file": 0,
            "loan_percent_income": 0.20
        }
    },
    {
        "name": "Medium Risk Profile",
        "data": {
            "age": 28,
            "income": 35000,
            "loan_amount": 15000,
            "interest_rate": 12.5,
            "employment_length": 1,
            "credit_history": 3,
            "default_on_file": 1,
            "loan_percent_income": 0.43
        }
    },
    {
        "name": "High Risk Profile",
        "data": {
            "age": 45,
            "income": 25000,
            "loan_amount": 20000,
            "interest_rate": 15.0,
            "employment_length": 0.5,
            "credit_history": 1,
            "default_on_file": 1,
            "loan_percent_income": 0.80
        }
    }
]

# ============================================================================
# API ENDPOINTS
# ============================================================================

CLASSICAL_API_URL = "http://localhost:8000"
QUANTUM_API_URL = "http://localhost:8001"

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def check_api_health(url, name):
    """Check if API is running."""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print(f"[OK] {name} is healthy")
            return True
        else:
            print(f"[FAIL] {name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] {name} is not responding: {e}")
        return False

def test_prediction(url, api_name, test_case):
    """Make prediction request to API."""
    try:
        response = requests.post(
            f"{url}/predict",
            json=test_case["data"],
            timeout=120  # Quantum takes longer
        )
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return {"error": f"Status {response.status_code}: {response.text}"}
    except requests.Timeout:
        return {"error": "Request timeout (Quantum API kernel computation may take 30-60 seconds)"}
    except Exception as e:
        return {"error": str(e)}

def format_result(result):
    """Pretty print result."""
    if "error" in result:
        return f"  ERROR: {result['error']}"
    
    lines = [
        f"  Prediction:    {result.get('prediction', 'N/A')} ({'Default' if result.get('prediction') == 1 else 'Non-Default'})",
        f"  Probability:   {result.get('probability', 'N/A'):.4f}",
        f"  Risk Score:    {result.get('risk_score', 'N/A'):.4f}",
        f"  Risk Category: {result.get('risk_category', 'N/A')}",
        f"  Model:         {result.get('model', 'N/A')}",
        f"  Timestamp:     {result.get('timestamp', 'N/A')}"
    ]
    return "\n".join(lines)

# ============================================================================
# MAIN TEST
# ============================================================================

def main():
    """Run tests against both APIs."""
    print("\n" + "=" * 80)
    print("TEST BOTH APIs - Classical vs Quantum")
    print("=" * 80 + "\n")
    
    # Check health
    print("HEALTH CHECKS:")
    print("-" * 80)
    classical_ok = check_api_health(CLASSICAL_API_URL, "Classical API (8000)")
    quantum_ok = check_api_health(QUANTUM_API_URL, "Quantum API (8001)")
    print()
    
    if not classical_ok or not quantum_ok:
        print("[FAIL] One or both APIs not running")
        print("\nStart them with:")
        print("  Terminal 1: python deploy.py")
        print("  Terminal 2: python deploy_quantum.py")
        return False
    
    # Run test cases
    print("\nTEST PREDICTIONS:")
    print("=" * 80 + "\n")
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"Test Case {i}: {test_case['name']}")
        print("-" * 80)
        
        print("\nInput Features:")
        for key, value in test_case['data'].items():
            print(f"  {key:.<25} {value}")
        
        print("\n[Classical API - XGBoost (Fast)]")
        classical_result = test_prediction(CLASSICAL_API_URL, "Classical", test_case)
        print(format_result(classical_result))
        
        print("\n[Quantum API - QSVM (Kernel Computation)]")
        print("  (This may take 30-60 seconds for kernel computation...)")
        start_time = time.time()
        quantum_result = test_prediction(QUANTUM_API_URL, "Quantum", test_case)
        elapsed = time.time() - start_time
        print(format_result(quantum_result))
        print(f"  Response time: {elapsed:.2f}s")
        
        print("\n[COMPARISON]")
        if "error" not in classical_result and "error" not in quantum_result:
            agree = classical_result['prediction'] == quantum_result['prediction']
            print(f"  Predictions agree: {['NO', 'YES'][agree]}")
            print(f"  Classical risk: {classical_result['risk_category']}")
            print(f"  Quantum risk:   {quantum_result['risk_category']}")
        
        print("\n" + "=" * 80 + "\n")
    
    # Get metrics
    print("\nMODEL METRICS:")
    print("=" * 80)
    
    print("\n[Classical API - XGBoost]")
    try:
        response = requests.get(f"{CLASSICAL_API_URL}/metrics", timeout=5)
        if response.status_code == 200:
            metrics = response.json()
            print(f"  Test AUC-ROC:  {metrics.get('test_auc_roc', 'N/A')}")
            print(f"  Test F1-Score: {metrics.get('test_f1', 'N/A')}")
        else:
            print("  [Could not retrieve metrics]")
    except Exception as e:
        print(f"  [Error: {e}]")
    
    print("\n[Quantum API - QSVM]")
    try:
        response = requests.get(f"{QUANTUM_API_URL}/quantum-metrics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('metrics', {})
            print(f"  Test AUC-ROC:  {metrics.get('test', {}).get('auc_roc', 'N/A')}")
            print(f"  Test F1-Score: {metrics.get('test', {}).get('f1', 'N/A')}")
            print(f"  Training Samples: {data.get('training_samples', 'N/A')}")
        else:
            print("  [Could not retrieve metrics]")
    except Exception as e:
        print(f"  [Error: {e}]")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
