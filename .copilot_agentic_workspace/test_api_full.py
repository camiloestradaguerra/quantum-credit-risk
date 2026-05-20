import requests
import json

print('=' * 60)
print('TEST: LOW RISK CLIENT (should be approved)')
print('=' * 60)

# Example 18D features for a LOW RISK client
payload = {
    'raw_features': [25, 80000, 10, 50000, 3.5, 0.15, 1, 1, 1, 0.1, 0.05, 0.05, 0.02, 0.08, 0.2, 0.05, 0.1, 0.03]
}
print(f'Sending {len(payload["raw_features"])}D features...')
response = requests.post('http://localhost:8000/predict', json=payload)
print(f'Status: {response.status_code}')
if response.status_code == 200:
    result = response.json()
    print(f'\n✅ Response received')
    print(f'Probability: {result["probability"]:.4f}')
    print(f'Default: {result["default"]}')
    print(f'Recommendation: {result["recommendation"]}')
    print(f'Expected Value: ${result["financial_impact"]["expected_value"]:,}')
else:
    print(f'Error: {json.dumps(response.json(), indent=2)}')

print('\n' + '=' * 60)
print('TEST: HIGH RISK CLIENT (should be rejected)')
print('=' * 60)

# Example 18D features for a HIGH RISK client
payload = {
    'raw_features': [55, 20000, 1, 5000, 18.5, 0.85, 15, 1, 0, 0.9, 0.95, 0.8, 0.7, 0.88, 0.15, 0.92, 0.75, 0.85]
}
print(f'Sending {len(payload["raw_features"])}D features...')
response = requests.post('http://localhost:8000/predict', json=payload)
print(f'Status: {response.status_code}')
if response.status_code == 200:
    result = response.json()
    print(f'\n✅ Response received')
    print(f'Probability: {result["probability"]:.4f}')
    print(f'Default: {result["default"]}')
    print(f'Recommendation: {result["recommendation"]}')
    print(f'Expected Value: ${result["financial_impact"]["expected_value"]:,}')
else:
    print(f'Error: {json.dumps(response.json(), indent=2)}')
