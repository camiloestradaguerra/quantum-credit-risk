# 📊 Credit Risk Model - Feature Mapping

## Input Format: 8 Features (Simplified)

The API automatically engineers the remaining 10 features. You only need to provide 8 original features:

### 8 Original Dataset Features (Input)
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

### 10 Engineered Features (Calculated Automatically)
| Index | Feature Name | Formula | Description |
|-------|--------------|---------|-------------|
| **8** | `debt_to_income` | Same as feature #5 | Debt burden ratio |
| **9** | `interest_rate_risk` | `loan_int_rate²` | Squared interest rate penalty |
| **10** | `loan_income_interaction` | `loan_amnt / (income + 1)` | Loan size relative to income |
| **11** | `emp_stability_log` | `log(person_emp_length + 1)` | Employment stability score |
| **12** | `credit_history_ratio` | `history_length / (age + 1)` | Credit maturity ratio |
| **13** | `default_risk_score` | `prior_default × debt_ratio` | Combined default indicator |
| **14** | `age_normalized` | `person_age / 100` | Normalized age (0-1) |
| **15** | `loan_amount_risk` | `log(loan_amnt + 1) × rate` | Loan amount-rate interaction |
| **16** | `income_age_ratio` | `person_income / (age + 1)` | Income maturity |
| **17** | `composite_risk` | Sum of debt, rate, interaction | Overall risk composite |

---

## Simple Request Example

```json
{
  "raw_features": [
    45,        // person_age (years)
               // The customer's age in years. Range: 18-144
               // Impact: Younger customers (18-35) have higher default risk
    
    55000,     // person_income (USD)
               // Annual gross income in dollars. Range: $9,600-$2,300,000
               // Impact: Higher income = lower risk. Used in debt ratios
    
    2,         // person_emp_length (years)
               // Years at current employer. Range: 0-164 years
               // Impact: Longer employment = more stability & lower default risk
    
    15000,     // loan_amnt (USD)
               // Total loan amount requested in dollars. Range: $500-$99,999
               // Impact: Larger loans relative to income = higher risk
    
    8.5,       // loan_int_rate (%)
               // Interest rate offered. Range: 5.42%-35.99%
               // Impact: Higher rates indicate lender's perception of risk
    
    0.25,      // loan_percent_income (0-1)
               // Debt-to-income ratio (loan / annual income). Range: 0.1%-89.5%
               // Impact: Most important feature. Values >0.30 = high risk
               // Formula: (monthly payment × 12) / annual income
    
    0,         // cb_person_default_on_file (0 or 1)
               // Has customer had a previous default/delinquency?
               // 0 = No prior default (good history)
               // 1 = Has prior default on record (major risk indicator)
    
    10         // cb_person_cred_hist_length (years)
               // Years of credit history. Range: 2-244 years
               // Impact: Longer history = more predictable behavior
  ]
}
```

**That's it!** The API will:
1. ✅ Engineer 10 risk features from these 8
2. ✅ Normalize all 18 features
3. ✅ Run XGBoost prediction
4. ✅ Return probability & recommendation

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

# Define client with ONLY 8 features
client = {
    "raw_features": [
        45,           # age
        55000,        # income
        2,            # employment_years
        15000,        # loan_amount
        8.5,          # interest_rate
        0.25,         # debt_to_income
        0,            # prior_default (0=no)
        10            # credit_history_years
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
print(f"Expected Financial Value: ${result['financial_impact']['expected_value']:,}")
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

