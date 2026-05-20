import requests
import json

print('=== TEST: Sending 18D raw features ===')
# Example 18D features
payload = {
    'raw_features': [45, 55000, 2, 15000, 8.5, 0.25, 5, 0, 0, 0.5, 0.3, 0.2, 0.1, 0.4, 0.6, 0.2, 0.3, 0.15]
}
print(f'Sending {len(payload["raw_features"])}D features...')
response = requests.post('http://localhost:8000/predict', json=payload)
print(f'Status: {response.status_code}')
if response.status_code == 200:
    result = response.json()
    print(f'\n✅ SUCCESS!')
    print(f'Probability: {result["probability"]:.4f}')
    print(f'Default: {result["default"]}')
    print(f'Recommendation: {result["recommendation"]}')
    print(f'Expected Value: ${result["financial_impact"]["expected_value"]:,}')
    print(f'\nFull Response:')
    print(json.dumps(result, indent=2))
else:
    print(f'Error: {json.dumps(response.json(), indent=2)}')
