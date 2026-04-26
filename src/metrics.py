"""Precarity metrics calculation module"""

import pandas as pd
import numpy as np

def calculate_income_volatility(earnings_series):
    """Calculate income volatility"""
    if len(earnings_series) < 2:
        return 0.5
    mean = earnings_series.mean()
    if mean == 0:
        return 1.0
    cv = earnings_series.std() / mean
    return min(cv, 1.0)


def calculate_platform_dependence(worker):
    """Calculate platform dependence"""
    if worker.get('multiple_platforms', 0) == 1:
        return 0.6
    return 1.0


def calculate_benefits_gap(worker):
    """Calculate benefits gap"""
    benefits = ['has_health_insurance', 'has_paid_leave', 'has_retirement']
    missing = sum([1 for b in benefits if not worker.get(b, False)])
    return missing / len(benefits)


def calculate_work_instability(worker):
    """Calculate work instability"""
    hours_per_day = worker.get('hours_per_day', 8)
    days_per_week = worker.get('days_per_week', 6)
    
    if hours_per_day == 0 or days_per_week == 0:
        return 1.0
    
    weekly_hours = hours_per_day * days_per_week
    ideal_hours = 40
    
    if weekly_hours > ideal_hours:
        instability = min((weekly_hours - ideal_hours) / 40, 0.5)
    else:
        instability = (ideal_hours - weekly_hours) / ideal_hours
    
    return min(instability + 0.2, 1.0)


def calculate_asset_precarity(worker):
    """Calculate asset precarity"""
    return worker.get('has_work_loan', 0) * 0.5


def calculate_all_metrics(df):
    """Calculate all precarity metrics for all workers"""
    results = []
    
    for idx, worker in df.iterrows():
        metrics = {
            'worker_id': worker['worker_id'],
            'income_volatility': calculate_income_volatility(pd.Series([worker['monthly_income']])),
            'platform_dependence': calculate_platform_dependence(worker),
            'benefits_gap': calculate_benefits_gap(worker),
            'work_instability': calculate_work_instability(worker),
            'asset_precarity': calculate_asset_precarity(worker)
        }
        results.append(metrics)
    
    return pd.DataFrame(results)