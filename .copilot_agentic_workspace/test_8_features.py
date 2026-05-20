import requests
import json

print('=' * 70)
print('TEST 1: ONLY 8 ORIGINAL FEATURES (should work now!)')
print('=' * 70)

# Only 8 original features - API should engineer the other 10
payload = {
    'raw_features': [
        45,        # person_age (years) - Customer age. Range: 18-144. Younger customers have higher default risk
        55000,     # person_income (USD) - Annual gross income. Range: $9.6K-$2.3M. Higher income = lower risk
        2,         # person_emp_length (years) - Years at current job. Range: 0-164. Longer employment = more stable
        15000,     # loan_amnt (USD) - Loan amount requested. Range: $500-$99.9K. Larger loans = higher risk
        8.5,       # loan_int_rate (%) - Interest rate offered. Range: 5.42%-35.99%. Higher rate = higher perceived risk
        0.25,      # loan_percent_income (0-1) - Debt-to-income ratio. Range: 0.1%-89.5%. Most critical, >0.30 = high risk
        0,         # cb_person_default_on_file (0 or 1) - Prior default? 0=No (good), 1=Yes (major risk indicator)
        10         # cb_person_cred_hist_length (years) - Credit history years. Range: 2-244. Longer = more predictable
    ]
}

print(f'\nSending {len(payload["raw_features"])} features (simplified input)...')
response = requests.post('http://localhost:8000/predict', json=payload)
print(f'Status: {response.status_code}')

if response.status_code == 200:
    result = response.json()
    print(f'\n✅ SUCCESS! API works with 8 features')
    print(f'Probability: {result["probability"]:.4f}')
    print(f'Default: {result["default"]}')
    print(f'Recommendation: {result["recommendation"]}')
    print(f'Expected Value: ${result["financial_impact"]["expected_value"]:,}')
else:
    print(f'Error: {json.dumps(response.json(), indent=2)}')

print('\n' + '=' * 70)
print('TEST 2: LOW RISK CLIENT (8 features only)')
print('=' * 70)

payload2 = {
    'raw_features': [
        35,        # person_age (years) - younger age
        80000,     # person_income (USD) - higher income
        10,        # person_emp_length (years) - longer employment
        20000,     # loan_amnt (USD) - larger loan
        3.5,       # loan_int_rate (%) - lower rate
        0.15,      # loan_percent_income (0-1) - lower debt ratio
        0,         # cb_person_default_on_file - no prior default
        15         # cb_person_cred_hist_length (years) - longer credit history
    ]
}

print(f'\nSending low-risk profile with 8 features...')
response = requests.post('http://localhost:8000/predict', json=payload2)

if response.status_code == 200:
    result = response.json()
    print(f'✅ Probability: {result["probability"]:.4f} - {result["recommendation"]}')
else:
    print(f'Error: {response.json()}')
