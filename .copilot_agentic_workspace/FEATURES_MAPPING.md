# 📊 Credit Risk Model - Feature Mapping

## 18 Features Used by the XGBoost Model

The API expects 18 raw features in this exact order:

### Original Dataset Features (8)
| Index | Feature Name | Description | Type | Unit/Range |
|-------|--------------|-------------|------|-----------|
| **0** | `person_age` | Customer age | Integer | years (18-144) |
| **1** | `person_income` | Annual income | Float | USD ($9,600-$2.3M) |
| **2** | `person_emp_length` | Employment tenure | Float | years (0-164) |
| **3** | `loan_amnt` | Loan amount | Float | USD ($500-$99,999) |
| **4** | `loan_int_rate` | Interest rate | Float | % (5.42%-35.99%) |
| **5** | `loan_percent_income` | Debt-to-income ratio | Float | % (0.1%-89.5%) |
| **6** | `cb_person_default_on_file` | Has prior default | Binary | 0=No, 1=Yes |
| **7** | `cb_person_cred_hist_length` | Credit history years | Integer | years (2-244) |

### Engineered Risk Features (10)
| Index | Feature Name | Formula | Description |
|-------|--------------|---------|-------------|
| **8** | `debt_to_income` | Same as feature #5 | Debt burden ratio |
| **9** | `interest_rate_risk` | `loan_int_rate²` | Squared interest rate penalty |
| **10** | `loan_income_interaction` | `loan_amnt / (person_income + 1)` | Loan size relative to income |
| **11** | `emp_stability_log` | `log(person_emp_length + 1)` | Employment stability score |
| **12** | `credit_history_ratio` | `cb_person_cred_hist_length / (person_age + 1)` | Credit maturity ratio |
| **13** | `default_risk_score` | `prior_default × debt_ratio` | Combined default indicator |
| **14** | `age_normalized` | `person_age / 100` | Normalized age (0-1) |
| **15** | `loan_amount_risk` | `log(loan_amnt + 1) × rate` | Loan amount-rate interaction |
| **16** | `income_age_ratio` | `person_income / (person_age + 1)` | Income maturity |
| **17** | `composite_risk` | Sum of debt, rate, and interaction | Overall risk composite |

---

## Example Request

```json
{
  "raw_features": [
    45,        // person_age
    55000,     // person_income
    5,         // person_emp_length
    15000,     // loan_amnt
    8.5,       // loan_int_rate
    0.25,      // loan_percent_income
    0,         // cb_person_default_on_file (0=No default history)
    10,        // cb_person_cred_hist_length
    0.25,      // debt_to_income (same as feature 5)
    72.25,     // interest_rate_risk (8.5²)
    0.273,     // loan_income_interaction
    1.79,      // emp_stability_log
    0.222,     // credit_history_ratio
    0.0,       // default_risk_score (0 × 0.25)
    0.45,      // age_normalized
    1.235,     // loan_amount_risk
    1222.22,   // income_age_ratio
    0.598      // composite_risk
  ]
}
```

---

## Feature Normalization

**Important:** The API internally normalizes these features using StandardScaler fitted on training data. You can send raw values - the model handles the scaling automatically.

### Training Data Statistics
| Feature | Mean | Std Dev | Min | Max |
|---------|------|---------|-----|-----|
| person_age | 27.7 | 6.4 | 18 | 144 |
| person_income | 66,234 | 61,265 | 9,600 | 2,300,000 |
| person_emp_length | 4.8 | 6.7 | 0 | 164 |
| loan_amnt | 10,356 | 10,814 | 500 | 99,999 |
| loan_int_rate | 10.6 | 6.2 | 5.42 | 35.99 |
| loan_percent_income | 0.178 | 0.243 | 0.0001 | 0.895 |
| cb_person_default_on_file | 0.059 | 0.235 | 0 | 1 |
| cb_person_cred_hist_length | 5.8 | 7.3 | 2 | 244 |

---

## Model Performance

- **Algorithm:** XGBoost (200 estimators, depth=6)
- **Test AUC-ROC:** 0.8983
- **Test Precision:** 37.94%
- **Test Recall:** 92.97%
- **Optimal Threshold:** 0.116
- **Test Samples:** 6,517

---

## Python Code Example

```python
import requests

# Define client
client = {
    "raw_features": [
        45,           # age
        55000,        # income
        5,            # emp_length
        15000,        # loan_amount
        8.5,          # interest_rate
        0.25,         # debt_to_income
        0,            # has_default (0=no)
        10,           # credit_history_years
        0.25,         # debt_to_income (repeat)
        72.25,        # interest_rate_risk
        0.273,        # loan_income_interaction
        1.79,         # emp_stability_log
        0.222,        # credit_history_ratio
        0.0,          # default_risk_score
        0.45,         # age_normalized
        1.235,        # loan_amount_risk
        1222.22,      # income_age_ratio
        0.598         # composite_risk
    ]
}

# Make prediction
response = requests.post(
    'http://localhost:8000/predict',
    json=client
)

result = response.json()
print(f"Default Probability: {result['probability']:.2%}")
print(f"Decision: {result['recommendation']}")
```

---

## Data Collection Tips

When integrating with a real CRM/banking system:

1. **Collect the 8 original features** directly from the customer database
2. **The API will automatically engineer the 10 risk features** using the model's preprocessing pipeline
3. **No need to manually calculate** the engineered features - the server handles it

### Feature Collection Checklist
- [ ] Customer age (years)
- [ ] Annual income (USD)
- [ ] Years employed (current job)
- [ ] Requested loan amount (USD)
- [ ] Interest rate offered (%)
- [ ] Debt-to-income ratio (% or decimal 0-1)
- [ ] Prior defaults on file (Y/N or 0/1)
- [ ] Credit history length (years)

