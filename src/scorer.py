"""Precarity Score calculation module"""

import pandas as pd

WEIGHTS = {
    'income_volatility': 0.30,
    'platform_dependence': 0.30,
    'benefits_gap': 0.25,
    'work_instability': 0.10,
    'asset_precarity': 0.05
}

def normalize_metric(series):
    """Normalize metric to 0-100 scale"""
    min_val = series.min()
    max_val = series.max()
    
    if max_val == min_val:
        return series * 0 + 50
    
    return ((series - min_val) / (max_val - min_val)) * 100

def calculate_precarity_score(metrics_df):
    """
    Calculate final Precarity Score (0-100)
    THIS IS THE FUNCTION THAT app.py IS LOOKING FOR
    """
    df = metrics_df.copy()
    
    for metric in WEIGHTS.keys():
        if metric in df.columns:
            df[f'{metric}_norm'] = normalize_metric(df[metric])
    
    df['precarity_score'] = 0
    for metric, weight in WEIGHTS.items():
        if f'{metric}_norm' in df.columns:
            df['precarity_score'] += df[f'{metric}_norm'] * weight
    
    df['risk_level'] = pd.cut(
        df['precarity_score'], 
        bins=[0, 30, 60, 101], 
        labels=['Low Risk 🟢', 'Medium Risk 🟡', 'High Risk 🔴'],
        right=False
    )
    
    return df

def get_aggregate_stats(df, results_df):
    """Get aggregate statistics"""
    return {
        'total_workers': len(df),
        'avg_precarity_score': results_df['precarity_score'].mean(),
        'high_risk_count': len(results_df[results_df['risk_level'] == 'High Risk 🔴']),
        'medium_risk_count': len(results_df[results_df['risk_level'] == 'Medium Risk 🟡']),
        'low_risk_count': len(results_df[results_df['risk_level'] == 'Low Risk 🟢']),
    }

def get_worker_score(results_df, worker_id):
    """Get precarity score for a specific worker"""
    worker_result = results_df[results_df['worker_id'] == worker_id]
    if len(worker_result) == 0:
        return None, None
    return worker_result.iloc[0]['precarity_score'], worker_result.iloc[0]['risk_level']