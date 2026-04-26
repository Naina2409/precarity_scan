"""User authentication module for PrecarityScan"""

import streamlit as st
import pandas as pd
import hashlib
import os
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).parent.parent
USER_DB_FILE = BASE_DIR / "data" / "users.csv"

def init_user_db():
    """Initialize user database if it doesn't exist"""
    os.makedirs(BASE_DIR / "data", exist_ok=True)
    
    if not os.path.exists(USER_DB_FILE):
        # Create default users with hashed passwords (password: "password123")
        default_users = pd.DataFrame({
            'username': ['researcher', 'policymaker', 'worker1', 'worker2', 'worker3'],
            'password_hash': [
                '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',
                '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',
                '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',
                '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',
                '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'
            ],
            'role': ['researcher', 'policymaker', 'worker', 'worker', 'worker'],
            'worker_id': ['', '', 'GW0001', 'GW0002', 'GW0003']
        })
        default_users.to_csv(USER_DB_FILE, index=False)

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    """Verify user credentials"""
    try:
        users_df = pd.read_csv(USER_DB_FILE)
        user = users_df[users_df['username'] == username]
        
        if len(user) == 0:
            return None, "User not found"
        
        if user.iloc[0]['password_hash'] == hash_password(password):
            return {
                'username': username,
                'role': user.iloc[0]['role'],
                'worker_id': user.iloc[0]['worker_id'] if pd.notna(user.iloc[0]['worker_id']) else None
            }, None
        else:
            return None, "Incorrect password"
    except Exception as e:
        return None, f"Error: {str(e)}"

def get_current_user():
    """Get current logged in user from session"""
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        return {
            'username': st.session_state.get('username'),
            'role': st.session_state.get('role'),
            'worker_id': st.session_state.get('worker_id')
        }
    return None