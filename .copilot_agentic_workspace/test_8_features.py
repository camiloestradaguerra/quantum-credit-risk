import requests
import json

print('=' * 70)
print('TEST 1: ONLY 8 ORIGINAL FEATURES (should work now!)')
print('=' * 70)

# Only 8 original features - API should engineer the other 10
payload = {
    'raw_features': [
        45,        # person_age
        55000,     # person_income
        2,         # person_emp_length
        15000,     # loan_amnt
        8.5,       # loan_int_rate
        0.25,      # loan_percent_income
        0,         # cb_person_default_on_file
        10         # cb_person_cred_hist_length
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
        35,        # younger age
        80000,     # higher income
        10,        # longer employment
        20000,     # larger loan
        3.5,       # lower rate
        0.15,      # lower debt ratio
        0,         # no prior default
        15         # longer credit history
    ]
}

print(f'\nSending low-risk profile with 8 features...')
response = requests.post('http://localhost:8000/predict', json=payload2)

if response.status_code == 200:
    result = response.json()
    print(f'✅ Probability: {result["probability"]:.4f} - {result["recommendation"]}')
else:
    print(f'Error: {response.json()}')
