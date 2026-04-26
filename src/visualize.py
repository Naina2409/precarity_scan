"""Visualization functions for PrecarityScan"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_precarity_distribution_chart(results_df):
    """Create pie chart for risk distribution"""
    risk_counts = results_df['risk_level'].value_counts()
    
    colors = {
        'Low Risk 🟢': '#10b981',
        'Medium Risk 🟡': '#f59e0b', 
        'High Risk 🔴': '#ef4444'
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=risk_counts.index,
        values=risk_counts.values,
        marker_colors=[colors.get(r, '#6b7280') for r in risk_counts.index],
        hole=0.4,
        textinfo='label+percent'
    )])
    
    fig.update_layout(title='Worker Risk Distribution', height=450)
    return fig

def create_precarity_gauge(score):
    """Create gauge chart for precarity score"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Precarity Score"},
        gauge={
            'axis': {'range': [0, 100]},
            'steps': [
                {'range': [0, 30], 'color': '#10b981'},
                {'range': [30, 60], 'color': '#f59e0b'},
                {'range': [60, 100], 'color': '#ef4444'}
            ]
        }
    ))
    fig.update_layout(height=300)
    return fig

def create_income_volatility_chart(df, metrics_df):
    """Create bar chart for income volatility"""
    merged = df.merge(metrics_df, on='worker_id')
    avg_volatility = merged.groupby('risk_level')['income_volatility'].mean().reset_index()
    
    fig = px.bar(
        avg_volatility, 
        x='risk_level', 
        y='income_volatility',
        color='risk_level',
        title='Income Volatility by Risk Level'
    )
    return fig

def create_earnings_by_platform(df):
    """Create box plot for earnings by platform"""
    fig = px.box(
        df,
        x='platform',
        y='monthly_income',
        title='Monthly Earnings by Platform',
        color='platform'
    )
    return fig