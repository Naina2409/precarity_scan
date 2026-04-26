"""Data cleaning and transformation module for PrecarityScan"""

import pandas as pd
import numpy as np
import re

def detect_and_map_columns(df):
    """
    Automatically detect and map column names to standard format
    """
    column_mapping = {}
    
    # Define mapping rules
    mapping_rules = {
        'worker_id': ['worker_id', 'workerid', 'id', 'user_id', 'employee_id', 'worker'],
        'age': ['age', 'worker_age', 'age_years', 'años', 'umur'],
        'city': ['city', 'location', 'city_name', 'work_city', 'area', 'district'],
        'platform': ['platform', 'company', 'app', 'platform_name', 'service', 'partner'],
        'months_experience': ['months_experience', 'experience', 'exp_months', 'tenure', 'months_on_platform'],
        'hours_per_day': ['hours_per_day', 'hours', 'hrs_per_day', 'working_hours', 'daily_hours', 'hours_day'],
        'days_per_week': ['days_per_week', 'days', 'weekly_days', 'work_days', 'days_week'],
        'monthly_income': ['monthly_income', 'income', 'salary', 'earnings', 'monthly_pay', 'pay', 'wages'],
        'has_health_insurance': ['has_health_insurance', 'health_insurance', 'insurance', 'medical_cover', 'health_cover'],
        'has_paid_leave': ['has_paid_leave', 'paid_leave', 'leave_benefit', 'annual_leave', 'sick_leave'],
        'has_retirement': ['has_retirement', 'retirement', 'pension', 'retirement_benefits', 'provident_fund'],
        'multiple_platforms': ['multiple_platforms', 'multi_platform', 'multiple_platform', 'multi_platforms', 'other_platforms'],
        'has_work_loan': ['has_work_loan', 'work_loan', 'vehicle_loan', 'equipment_loan', 'loan_for_work', 'asset_loan']
    }
    
    for standard_name, possible_names in mapping_rules.items():
        for col in df.columns:
            col_lower = col.lower().strip()
            for possible in possible_names:
                if possible in col_lower or col_lower in possible:
                    column_mapping[col] = standard_name
                    break
    
    return column_mapping

def clean_boolean_columns(df):
    """Convert various boolean formats to 0/1"""
    
    boolean_columns = ['has_health_insurance', 'has_paid_leave', 'has_retirement', 'multiple_platforms', 'has_work_loan']
    
    for col in boolean_columns:
        if col in df.columns:
            # Convert to string and lowercase
            df[col] = df[col].astype(str).str.lower().str.strip()
            
            # Mapping dictionary
            true_values = ['yes', 'true', '1', 'y', 't', 'ok', 'have', 'has', 'available']
            false_values = ['no', 'false', '0', 'n', 'f', 'not', 'none', 'na', '']
            
            df[col] = df[col].apply(lambda x: 1 if x in true_values else (0 if x in false_values else 0))
            df[col] = df[col].fillna(0).astype(int)
    
    return df

def clean_numeric_columns(df):
    """Clean and convert numeric columns"""
    
    numeric_columns = ['age', 'months_experience', 'hours_per_day', 'days_per_week', 'monthly_income']
    
    for col in numeric_columns:
        if col in df.columns:
            # Remove currency symbols and commas
            df[col] = df[col].astype(str).str.replace('₹', '').str.replace('$', '')
            df[col] = df[col].str.replace(',', '').str.replace('Rs', '')
            df[col] = df[col].str.extract('(\d+\.?\d*)').fillna(0)
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Apply reasonable limits and defaults
            if col == 'age':
                df[col] = df[col].clip(18, 80).fillna(30)
            elif col == 'months_experience':
                df[col] = df[col].clip(0, 240).fillna(12)
            elif col == 'hours_per_day':
                df[col] = df[col].clip(2, 18).fillna(8)
            elif col == 'days_per_week':
                df[col] = df[col].clip(1, 7).fillna(6)
            elif col == 'monthly_income':
                df[col] = df[col].clip(0, 200000).fillna(15000)
            
            df[col] = df[col].astype(int)
    
    return df

def add_missing_columns(df):
    """Add missing columns with default values"""
    
    default_values = {
        'worker_id': None,  # Will be generated
        'age': 30,
        'city': 'Unknown',
        'platform': 'Unknown',
        'months_experience': 12,
        'hours_per_day': 8,
        'days_per_week': 6,
        'monthly_income': 15000,
        'has_health_insurance': 0,
        'has_paid_leave': 0,
        'has_retirement': 0,
        'multiple_platforms': 0,
        'has_work_loan': 0
    }
    
    for col, default in default_values.items():
        if col not in df.columns and col != 'worker_id':
            df[col] = default
    
    return df

def generate_worker_ids(df):
    """Generate missing worker IDs"""
    
    # If worker_id column exists but has empty values
    if 'worker_id' in df.columns:
        # Generate IDs for missing ones
        next_id = 1
        for i, val in enumerate(df['worker_id']):
            if pd.isna(val) or str(val).strip() == '':
                df.loc[i, 'worker_id'] = f"GW{str(next_id).zfill(4)}"
                next_id += 1
    else:
        # Create new worker_id column
        df['worker_id'] = [f"GW{str(i+1).zfill(4)}" for i in range(len(df))]
    
    return df

def clean_city_names(df):
    """Standardize city names"""
    
    city_mapping = {
        'delhi': 'Delhi', 'new delhi': 'Delhi', 'ncr': 'Delhi',
        'mumbai': 'Mumbai', 'bombay': 'Mumbai',
        'bangalore': 'Bangalore', 'bengaluru': 'Bangalore',
        'chennai': 'Chennai', 'madras': 'Chennai',
        'kolkata': 'Kolkata', 'calcutta': 'Kolkata',
        'hyderabad': 'Hyderabad', 'pune': 'Pune', 'ahmedabad': 'Ahmedabad'
    }
    
    if 'city' in df.columns:
        df['city'] = df['city'].astype(str).str.lower().str.strip()
        df['city'] = df['city'].map(lambda x: city_mapping.get(x, x.title() if len(x) > 0 else 'Unknown'))
    
    return df

def clean_platform_names(df):
    """Standardize platform names"""
    
    platform_mapping = {
        'zomato': 'Zomato', 'zmt': 'Zomato',
        'swiggy': 'Swiggy', 'swigy': 'Swiggy',
        'uber': 'Uber', 'uber eats': 'Uber',
        'ola': 'Ola',
        'urban company': 'Urban Company', 'urbanclap': 'Urban Company',
        'amazon': 'Amazon Flex', 'amazon flex': 'Amazon Flex',
        'other': 'Other'
    }
    
    if 'platform' in df.columns:
        df['platform'] = df['platform'].astype(str).str.lower().str.strip()
        df['platform'] = df['platform'].map(lambda x: platform_mapping.get(x, x.title() if len(x) > 0 else 'Unknown'))
    
    return df

def validate_and_fix_data(df):
    """Validate and fix data quality issues"""
    
    # Remove duplicate worker_ids
    if 'worker_id' in df.columns:
        df = df.drop_duplicates(subset=['worker_id'], keep='first')
    
    # Remove rows with all null values
    df = df.dropna(how='all')
    
    # Fix negative values
    numeric_cols = ['age', 'months_experience', 'hours_per_day', 'days_per_week', 'monthly_income']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].clip(lower=0)
    
    return df

def clean_csv_file(file_path, output_path=None, existing_worker_ids=None):
    """
    Main function to clean any CSV file to PrecarityScan format
    
    Parameters:
    - file_path: Path to the input CSV file (can be file-like object from Streamlit)
    - output_path: Path to save cleaned CSV (optional)
    - existing_worker_ids: List of existing worker IDs to avoid duplicates
    
    Returns:
    - Cleaned DataFrame
    """
    
    print("🔍 Starting data cleaning process...")
    
    # Load the CSV
    try:
        df = pd.read_csv(file_path)
        print(f"✅ Loaded {len(df)} rows and {len(df.columns)} columns")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None
    
    print(f"📋 Original columns: {list(df.columns)}")
    
    # Detect and map columns
    column_mapping = detect_and_map_columns(df)
    if column_mapping:
        df = df.rename(columns=column_mapping)
        print(f"🔄 Mapped columns: {column_mapping}")
    
    # Clean boolean columns
    df = clean_boolean_columns(df)
    
    # Clean numeric columns
    df = clean_numeric_columns(df)
    
    # Add missing columns
    df = add_missing_columns(df)
    
    # Clean city names
    df = clean_city_names(df)
    
    # Clean platform names
    df = clean_platform_names(df)
    
    # Generate worker IDs for new workers only
    if existing_worker_ids:
        # Mark existing workers
        df['is_new'] = ~df['worker_id'].isin(existing_worker_ids) if 'worker_id' in df.columns else True
        # Generate IDs only for new workers
        df = generate_worker_ids(df)
        df = df.drop('is_new', axis=1)
    else:
        df = generate_worker_ids(df)
    
    # Validate and fix
    df = validate_and_fix_data(df)
    
    # Select only required columns in correct order
    required_columns = [
        'worker_id', 'age', 'city', 'platform', 'months_experience',
        'hours_per_day', 'days_per_week', 'monthly_income',
        'has_health_insurance', 'has_paid_leave', 'has_retirement',
        'multiple_platforms', 'has_work_loan'
    ]
    
    # Keep only columns that exist
    final_columns = [col for col in required_columns if col in df.columns]
    df = df[final_columns]
    
    print(f"✅ Cleaning complete! Final shape: {df.shape}")
    print(f"📋 Final columns: {list(df.columns)}")
    
    # Save if output path provided
    if output_path:
        df.to_csv(output_path, index=False)
        print(f"💾 Saved cleaned data to: {output_path}")
    
    return df

# Example of cleaning multiple file formats
def clean_excel_file(file_path, output_path=None, existing_worker_ids=None):
    """Clean Excel files (xlsx, xls)"""
    try:
        df = pd.read_excel(file_path)
        return clean_csv_file(df, output_path, existing_worker_ids)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def clean_json_file(file_path, output_path=None, existing_worker_ids=None):
    """Clean JSON files"""
    try:
        df = pd.read_json(file_path)
        return clean_csv_file(df, output_path, existing_worker_ids)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None