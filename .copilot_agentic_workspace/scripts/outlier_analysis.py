#!/usr/bin/env python3
"""
OUTLIER ANALYSIS SCRIPT - Credit Risk Dataset
=============================================

Purpose: Comprehensive outlier detection and analysis for financial risk dataset
Author: Risk Analysis Team
Date: 2026-05-19

Detects outliers using:
  1. IQR Method (Interquartile Range)
  2. Z-Score Method (Standard deviation)
  3. Isolation Forest (Unsupervised anomaly detection)

Analyzes:
  - Distribution of outliers
  - Relevance to Default Status
  - Financial impact
  - Whether to keep or remove outliers
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
from sklearn.ensemble import IsolationForest
from scipy import stats
import logging

# ============================================================================
# CONFIGURATION
# ============================================================================

# Setup paths (works from any directory)
SCRIPT_DIR = Path(__file__).parent.parent  # Go up from scripts/
DATA_PATH = SCRIPT_DIR / 'data' / 'financial_risk_dataset.csv'
REPORT_PATH = SCRIPT_DIR / 'data' / 'outliers_report.json'
PLOTS_PATH = SCRIPT_DIR / 'documentation'
LOGS_PATH = SCRIPT_DIR / 'logs'
LOGS_PATH.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_PATH / 'outlier_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
PLOTS_PATH.mkdir(exist_ok=True)

# Numeric columns to analyze
NUMERIC_COLS = [
    'Applicant_Age', 'Years_in_Employment', 'Applicant_Income',
    'Coapplicant_Income', 'Credit_Score', 'Existing_Debt', 'Loan_Amount',
    'Interest_Rate', 'Collateral_Value', 'Payment_Delays_6mo',
    'Credit_Utilization_Ratio', 'Debt_to_Income_Ratio'
]

# ============================================================================
# 1. IQR METHOD (Interquartile Range)
# ============================================================================

def detect_outliers_iqr(df, column, multiplier=1.5):
    """
    Detect outliers using IQR method.
    
    Args:
        df (pd.DataFrame): Input dataframe
        column (str): Column name
        multiplier (float): IQR multiplier (default 1.5 for outliers, 3.0 for extreme)
    
    Returns:
        dict: Outlier information
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
    outliers = df[outlier_mask]
    
    return {
        'method': 'IQR',
        'column': column,
        'Q1': float(Q1),
        'Q3': float(Q3),
        'IQR': float(IQR),
        'lower_bound': float(lower_bound),
        'upper_bound': float(upper_bound),
        'outlier_count': int(outlier_mask.sum()),
        'outlier_percentage': float(100 * outlier_mask.sum() / len(df)),
        'outlier_indices': outlier_mask.index[outlier_mask].tolist()[:100]  # First 100
    }

# ============================================================================
# 2. Z-SCORE METHOD (Standard Deviation)
# ============================================================================

def detect_outliers_zscore(df, column, threshold=3.0):
    """
    Detect outliers using Z-score method.
    
    Args:
        df (pd.DataFrame): Input dataframe
        column (str): Column name
        threshold (float): Z-score threshold (default 3.0 for |z| > 3)
    
    Returns:
        dict: Outlier information
    """
    z_scores = np.abs(stats.zscore(df[column].dropna()))
    outlier_mask = np.abs(stats.zscore(df[column])) > threshold
    
    return {
        'method': 'Z-Score',
        'column': column,
        'mean': float(df[column].mean()),
        'std': float(df[column].std()),
        'threshold': threshold,
        'outlier_count': int(outlier_mask.sum()),
        'outlier_percentage': float(100 * outlier_mask.sum() / len(df)),
        'outlier_indices': df.index[outlier_mask].tolist()[:100]
    }

# ============================================================================
# 3. ISOLATION FOREST METHOD (Unsupervised)
# ============================================================================

def detect_outliers_isolation_forest(df, numeric_cols, contamination=0.05):
    """
    Detect outliers using Isolation Forest.
    
    Args:
        df (pd.DataFrame): Input dataframe
        numeric_cols (list): Numeric columns to use
        contamination (float): Expected proportion of outliers
    
    Returns:
        dict: Outlier information
    """
    # Handle missing values
    X = df[numeric_cols].fillna(df[numeric_cols].mean())
    
    # Fit Isolation Forest
    iso_forest = IsolationForest(contamination=contamination, random_state=42)
    outlier_labels = iso_forest.fit_predict(X)
    
    outlier_mask = outlier_labels == -1
    
    return {
        'method': 'Isolation Forest',
        'contamination': contamination,
        'n_features': len(numeric_cols),
        'outlier_count': int(outlier_mask.sum()),
        'outlier_percentage': float(100 * outlier_mask.sum() / len(df)),
        'outlier_indices': df.index[outlier_mask].tolist()[:100],
        'anomaly_scores': iso_forest.score_samples(X).tolist()[:100]  # Sample scores
    }

# ============================================================================
# 4. FINANCIAL RELEVANCE ANALYSIS
# ============================================================================

def analyze_outlier_relevance(df, outlier_indices):
    """
    Analyze if outliers are relevant to Default Status.
    
    Args:
        df (pd.DataFrame): Input dataframe
        outlier_indices (list): Indices of outliers
    
    Returns:
        dict: Relevance analysis
    """
    if not outlier_indices:
        return {'status': 'No outliers to analyze'}
    
    outliers_df = df.loc[outlier_indices]
    normal_df = df.drop(outlier_indices)
    
    # Default rate comparison
    outlier_default_rate = outliers_df['Default_Status'].mean()
    normal_default_rate = normal_df['Default_Status'].mean()
    
    # Financial metrics comparison
    outlier_avg_loan = outliers_df['Loan_Amount'].mean()
    normal_avg_loan = normal_df['Loan_Amount'].mean()
    
    outlier_avg_income = outliers_df['Applicant_Income'].mean()
    normal_avg_income = normal_df['Applicant_Income'].mean()
    
    return {
        'outlier_default_rate': float(outlier_default_rate),
        'normal_default_rate': float(normal_default_rate),
        'default_rate_difference': float(outlier_default_rate - normal_default_rate),
        'outlier_avg_loan': float(outlier_avg_loan),
        'normal_avg_loan': float(normal_avg_loan),
        'outlier_avg_income': float(outlier_avg_income),
        'normal_avg_income': float(normal_avg_income),
        'recommendation': (
            'KEEP_OUTLIERS' if abs(outlier_default_rate - normal_default_rate) > 0.05
            else 'REMOVE_OUTLIERS'
        )
    }

# ============================================================================
# 5. VISUALIZATION
# ============================================================================

def plot_outlier_distributions(df, numeric_cols, outlier_mask):
    """
    Create visualizations of outliers.
    
    Args:
        df (pd.DataFrame): Input dataframe
        numeric_cols (list): Numeric columns
        outlier_mask (pd.Series): Boolean mask of outliers
    """
    # Select 6 most important columns
    important_cols = numeric_cols[:6]
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.ravel()
    
    for idx, col in enumerate(important_cols):
        # Remove NaN for plotting
        data = df[col].dropna()
        outlier_data = data[outlier_mask[data.index]]
        normal_data = data[~outlier_mask[data.index]]
        
        # Box plot
        axes[idx].boxplot([normal_data, outlier_data], labels=['Normal', 'Outlier'])
        axes[idx].set_ylabel(col)
        axes[idx].set_title(f'{col} Distribution')
        axes[idx].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / 'outlier_distributions.png', dpi=300, bbox_inches='tight')
    logger.info(f"Visualization saved: {PLOTS_PATH / 'outlier_distributions.png'}")
    plt.close()

# ============================================================================
# 6. MAIN EXECUTION
# ============================================================================

def main():
    logger.info("=" * 70)
    logger.info("OUTLIER ANALYSIS - Credit Risk Dataset")
    logger.info("=" * 70)
    
    # Load dataset
    logger.info(f"Loading dataset from {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    logger.info(f"Dataset shape: {df.shape}")
    
    # Initialize report
    report = {
        'dataset_info': {
            'n_samples': len(df),
            'n_features': len(df.columns),
            'numeric_columns': len(NUMERIC_COLS)
        },
        'iqr_analysis': {},
        'zscore_analysis': {},
        'isolation_forest': None,
        'summary': None
    }
    
    # ===== IQR Analysis =====
    logger.info("\n1. IQR METHOD ANALYSIS")
    logger.info("-" * 70)
    iqr_results = {}
    for col in NUMERIC_COLS:
        if col in df.columns and df[col].dtype in [np.float64, np.int64]:
            result = detect_outliers_iqr(df, col)
            iqr_results[col] = result
            logger.info(f"{col}: {result['outlier_count']} outliers ({result['outlier_percentage']:.2f}%)")
    
    report['iqr_analysis'] = iqr_results
    
    # ===== Z-Score Analysis =====
    logger.info("\n2. Z-SCORE METHOD ANALYSIS")
    logger.info("-" * 70)
    zscore_results = {}
    for col in NUMERIC_COLS:
        if col in df.columns and df[col].dtype in [np.float64, np.int64]:
            result = detect_outliers_zscore(df, col)
            zscore_results[col] = result
            logger.info(f"{col}: {result['outlier_count']} outliers ({result['outlier_percentage']:.2f}%)")
    
    report['zscore_analysis'] = zscore_results
    
    # ===== Isolation Forest Analysis =====
    logger.info("\n3. ISOLATION FOREST METHOD ANALYSIS")
    logger.info("-" * 70)
    available_numeric = [c for c in NUMERIC_COLS if c in df.columns]
    iso_result = detect_outliers_isolation_forest(df, available_numeric, contamination=0.05)
    report['isolation_forest'] = iso_result
    logger.info(f"Outliers detected: {iso_result['outlier_count']} ({iso_result['outlier_percentage']:.2f}%)")
    
    # ===== Relevance Analysis =====
    logger.info("\n4. FINANCIAL RELEVANCE ANALYSIS")
    logger.info("-" * 70)
    
    # Use IQR outliers (typically most conservative)
    all_outlier_indices = set()
    for col, result in iqr_results.items():
        all_outlier_indices.update(result['outlier_indices'])
    
    relevance = analyze_outlier_relevance(df, list(all_outlier_indices))
    report['summary'] = relevance
    
    logger.info(f"Outlier default rate: {relevance['outlier_default_rate']:.2%}")
    logger.info(f"Normal default rate: {relevance['normal_default_rate']:.2%}")
    logger.info(f"Difference: {relevance['default_rate_difference']:+.2%}")
    logger.info(f"Recommendation: {relevance['recommendation']}")
    
    # ===== Visualization =====
    logger.info("\n5. GENERATING VISUALIZATIONS")
    logger.info("-" * 70)
    outlier_mask = pd.Series(False, index=df.index)
    for idx in all_outlier_indices:
        if idx < len(df):
            outlier_mask.iloc[idx] = True
    
    plot_outlier_distributions(df, available_numeric, outlier_mask)
    
    # ===== Save Report =====
    logger.info("\n6. SAVING REPORT")
    logger.info("-" * 70)
    with open(REPORT_PATH, 'w') as f:
        json.dump(report, f, indent=2)
    logger.info(f"Report saved: {REPORT_PATH}")
    
    logger.info("\n" + "=" * 70)
    logger.info("OUTLIER ANALYSIS COMPLETED")
    logger.info("=" * 70)
    
    return report

if __name__ == '__main__':
    report = main()
    
    # Print summary
    print("\n" + "=" * 70)
    print("OUTLIER ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"IQR Outliers: {sum(r['outlier_count'] for r in report['iqr_analysis'].values())} total")
    print(f"Isolation Forest Outliers: {report['isolation_forest']['outlier_count']}")
    print(f"\nFinancial Relevance:")
    print(f"  Default rate (outliers): {report['summary']['outlier_default_rate']:.2%}")
    print(f"  Default rate (normal): {report['summary']['normal_default_rate']:.2%}")
    print(f"  Recommendation: {report['summary']['recommendation']}")
    print("=" * 70)
