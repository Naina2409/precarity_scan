"""PrecarityScan - Complete Working Version"""
from src.data_cleaner import clean_csv_file
import streamlit as st
import pandas as pd
import hashlib
from pathlib import Path
import os
import numpy as np

# Page config
st.set_page_config(page_title="PrecarityScan", page_icon="🔍", layout="wide")

# File paths
DATA_DIR = Path(__file__).parent / "data"
USER_DB = DATA_DIR / "users.csv"
WORKER_DATA = DATA_DIR / "sample_data.csv"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# ========== HELPER FUNCTIONS ==========

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_and_create_files():
    """Check if files exist and are valid"""
    
    if not USER_DB.exists():
        df = pd.DataFrame({
            'username': ['researcher', 'policymaker', 'worker1', 'worker2', 'worker3'],
            'password_hash': [
                hash_password('password123'),
                hash_password('password123'),
                hash_password('password123'),
                hash_password('password123'),
                hash_password('password123')
            ],
            'role': ['researcher', 'policymaker', 'worker', 'worker', 'worker'],
            'worker_id': ['', '', 'GW0001', 'GW0002', 'GW0003']
        })
        df.to_csv(USER_DB, index=False)
    
    if not WORKER_DATA.exists():
        df = pd.DataFrame({
            'worker_id': ['GW0001', 'GW0002', 'GW0003'],
            'age': [24, 31, 28],
            'city': ['Delhi', 'Mumbai', 'Bangalore'],
            'platform': ['Zomato', 'Swiggy', 'Uber'],
            'months_experience': [18, 24, 36],
            'hours_per_day': [8, 10, 12],
            'days_per_week': [6, 7, 6],
            'monthly_income': [18500, 22000, 31000],
            'has_health_insurance': [0, 0, 1],
            'has_paid_leave': [0, 0, 0],
            'has_retirement': [0, 0, 0],
            'multiple_platforms': [0, 0, 1],
            'has_work_loan': [1, 1, 0]
        })
        df.to_csv(WORKER_DATA, index=False)

def authenticate_user(username, password):
    try:
        df = pd.read_csv(USER_DB)
        user = df[df['username'] == username]
        if len(user) == 0:
            return None, "User not found"
        if user.iloc[0]['password_hash'] == hash_password(password):
            return {
                'username': username,
                'role': user.iloc[0]['role'],
                'worker_id': user.iloc[0]['worker_id']
            }, None
        return None, "Wrong password"
    except Exception as e:
        return None, str(e)

def register_worker(username, password):
    try:
        users_df = pd.read_csv(USER_DB)
        
        if username in users_df['username'].values:
            return False, "Username exists"
        
        worker_df = pd.read_csv(WORKER_DATA)
        existing_ids = worker_df['worker_id'].tolist()
        
        max_num = 0
        for wid in existing_ids:
            if str(wid).startswith('GW'):
                num = int(str(wid).replace('GW', ''))
                if num > max_num:
                    max_num = num
        
        new_worker_id = f"GW{str(max_num + 1).zfill(4)}"
        
        new_row = pd.DataFrame([{
            'username': username,
            'password_hash': hash_password(password),
            'role': 'worker',
            'worker_id': new_worker_id
        }])
        
        updated_df = pd.concat([users_df, new_row], ignore_index=True)
        updated_df.to_csv(USER_DB, index=False)
        
        return True, new_worker_id
    except Exception as e:
        return False, str(e)

def add_worker_data(worker_id, data):
    """Add new worker data to the dataset"""
    try:
        existing_df = pd.read_csv(WORKER_DATA)
        
        new_row = pd.DataFrame([{
            'worker_id': worker_id,
            'age': data['age'],
            'city': data['city'],
            'platform': data['platform'],
            'months_experience': data['months_experience'],
            'hours_per_day': data['hours_per_day'],
            'days_per_week': data['days_per_week'],
            'monthly_income': data['monthly_income'],
            'has_health_insurance': 1 if data['has_health_insurance'] else 0,
            'has_paid_leave': 1 if data['has_paid_leave'] else 0,
            'has_retirement': 1 if data['has_retirement'] else 0,
            'multiple_platforms': 1 if data['multiple_platforms'] else 0,
            'has_work_loan': 1 if data['has_work_loan'] else 0
        }])
        
        updated_df = pd.concat([existing_df, new_row], ignore_index=True)
        updated_df.to_csv(WORKER_DATA, index=False)
        return True
    except Exception as e:
        print(f"Error adding data: {e}")
        return False

# ========== PRECARITY SCORE CALCULATION ==========

def calculate_precarity_score_for_worker(worker_data):
    """
    Calculate precarity score for a single worker (0-100)
    Lower score = better, Higher score = more precarious
    """
    score = 0
    
    # 1. Income Level (30% weight) - Lower income = higher score
    monthly_income = worker_data.get('monthly_income', 15000)
    if monthly_income < 10000:
        income_score = 100
    elif monthly_income < 15000:
        income_score = 75
    elif monthly_income < 20000:
        income_score = 50
    elif monthly_income < 30000:
        income_score = 25
    else:
        income_score = 0
    score += income_score * 0.30
    
    # 2. Working Hours (20% weight) - More hours = higher score (precarity)
    hours = worker_data.get('hours_per_day', 8) * worker_data.get('days_per_week', 6)
    if hours > 60:
        hours_score = 100
    elif hours > 50:
        hours_score = 75
    elif hours > 40:
        hours_score = 50
    elif hours > 30:
        hours_score = 25
    else:
        hours_score = 0
    score += hours_score * 0.20
    
    # 3. Benefits Gap (25% weight) - Missing benefits = higher score
    benefits = 0
    if worker_data.get('has_health_insurance', False):
        benefits += 1
    if worker_data.get('has_paid_leave', False):
        benefits += 1
    if worker_data.get('has_retirement', False):
        benefits += 1
    benefits_score = (3 - benefits) / 3 * 100
    score += benefits_score * 0.25
    
    # 4. Work Loan (15% weight) - Having loan = higher score
    loan_score = 100 if worker_data.get('has_work_loan', False) else 0
    score += loan_score * 0.15
    
    # 5. Platform Dependence (10% weight) - Single platform = higher score
    dependence_score = 100 if not worker_data.get('multiple_platforms', False) else 0
    score += dependence_score * 0.10
    
    return round(score, 1)

def get_risk_level(score):
    """Get risk level based on score"""
    if score <= 30:
        return "Low Risk 🟢", "Your financial health looks stable. Keep tracking your data!"
    elif score <= 60:
        return "Medium Risk 🟡", "Some signs of precarity. Consider improving income stability and benefits."
    else:
        return "High Risk 🔴", "High precarity detected. Urgent attention needed for financial stability."

# Check files
check_and_create_files()

# Session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'worker_id' not in st.session_state:
    st.session_state['worker_id'] = None

# ========== LOGIN PAGE ==========
if not st.session_state['logged_in']:
    st.markdown("""
    <style>
    .main-title {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #0f172a, #1e293b);
        border-radius: 20px;
        margin-bottom: 30px;
        color: white;
    }
    .login-box {
        max-width: 450px;
        margin: 0 auto;
        padding: 30px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-title"><h1>🔍 PrecarityScan</h1><p>Gig Worker Financial Health Dashboard</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
        
        with tab1:
            username = st.text_input("Username", placeholder="researcher / policymaker / worker1")
            password = st.text_input("Password", type="password", placeholder="password123")
            
            if st.button("Login", use_container_width=True):
                if username and password:
                    user, error = authenticate_user(username, password)
                    if user:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = user['username']
                        st.session_state['role'] = user['role']
                        st.session_state['worker_id'] = user['worker_id']
                        st.rerun()
                    else:
                        st.error(error)
                else:
                    st.warning("Enter username and password")
        
        with tab2:
            st.markdown("### Register as Worker")
            new_user = st.text_input("Username", placeholder="Choose username", key="reg_user")
            new_pass = st.text_input("Password", type="password", placeholder="Choose password", key="reg_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="reg_confirm")
            
            if st.button("Register", use_container_width=True, key="reg_btn"):
                if not new_user or not new_pass:
                    st.warning("Fill all fields")
                elif new_pass != confirm_pass:
                    st.error("Passwords don't match")
                else:
                    success, result = register_worker(new_user, new_pass)
                    if success:
                        st.success(f"✅ Registered! Your Worker ID: {result}")
                        st.info("Please login with your credentials")
                    else:
                        st.error(f"Registration failed: {result}")
        
        st.markdown("---")
        st.caption("Demo: researcher/password123 | policymaker/password123 | worker1/password123")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.stop()

# ========== DASHBOARD ==========
st.success(f"✅ Welcome {st.session_state['username']}!")

with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['username']}")
    st.markdown(f"**Role:** {st.session_state['role'].upper()}")
    if st.session_state['worker_id']:
        st.markdown(f"**Worker ID:** {st.session_state['worker_id']}")
    st.markdown("---")
    
    # Navigation menu based on role
    if st.session_state['role'] == 'worker':
        page = st.radio("📋 Menu", ["🏠 My Dashboard", "📝 Enter My Data", "📊 My Precarity Score"])
    else:
        page = st.radio("📋 Menu", ["🏠 Dashboard", "📊 All Workers Analytics", "📁 Upload Data"])
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for key in ['logged_in', 'username', 'role', 'worker_id']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Load all data
df = pd.read_csv(WORKER_DATA)

# ========== WORKER VIEW ==========
if st.session_state['role'] == 'worker':
    
    if page == "🏠 My Dashboard":
        st.title("📊 My Dashboard")
        
        worker_df = df[df['worker_id'] == st.session_state['worker_id']]
        
        if len(worker_df) == 0:
            st.info("📝 No data found for you. Please go to 'Enter My Data' to add your information.")
            
            # Quick data entry
            with st.form("quick_form"):
                st.subheader("Quick Data Entry")
                col1, col2 = st.columns(2)
                with col1:
                    age = st.number_input("Age", 18, 80, 25)
                    city = st.selectbox("City", ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata"])
                    platform = st.selectbox("Platform", ["Zomato", "Swiggy", "Uber", "Ola"])
                with col2:
                    hours_per_day = st.slider("Hours/Day", 2, 16, 8)
                    days_per_week = st.slider("Days/Week", 1, 7, 6)
                    monthly_income = st.number_input("Monthly Income (₹)", 0, 100000, 15000)
                
                has_insurance = st.checkbox("Have Health Insurance?")
                has_loan = st.checkbox("Have Work Loan?")
                
                if st.form_submit_button("Save"):
                    data = {
                        'age': age, 'city': city, 'platform': platform,
                        'months_experience': 6, 'hours_per_day': hours_per_day,
                        'days_per_week': days_per_week, 'monthly_income': monthly_income,
                        'has_health_insurance': has_insurance, 'has_paid_leave': False,
                        'has_retirement': False, 'multiple_platforms': False,
                        'has_work_loan': has_loan
                    }
                    if add_worker_data(st.session_state['worker_id'], data):
                        st.success("✅ Data saved!")
                        st.rerun()
        else:
            st.dataframe(worker_df)
            
            # Calculate and show score
            worker_dict = worker_df.iloc[0].to_dict()
            score = calculate_precarity_score_for_worker(worker_dict)
            risk_level, advice = get_risk_level(score)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Your Precarity Score", f"{score}/100")
            with col2:
                st.metric("Risk Level", risk_level)
            
            st.info(f"💡 {advice}")
    
    elif page == "📝 Enter My Data":
        st.title("📝 Enter/Update My Data")
        
        worker_df = df[df['worker_id'] == st.session_state['worker_id']]
        existing = len(worker_df) > 0
        
        if existing:
            st.info("Update your information below")
            default_data = worker_df.iloc[0]
        else:
            st.info("Enter your information below")
        
        with st.form("data_form"):
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age", 18, 80, value=int(default_data['age']) if existing else 25)
                city = st.selectbox("City", ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Pune", "Hyderabad"], 
                                   index=0 if not existing else ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Pune", "Hyderabad"].index(default_data['city']) if default_data['city'] in ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Pune", "Hyderabad"] else 0)
                platform = st.selectbox("Platform", ["Zomato", "Swiggy", "Uber", "Ola", "Urban Company"])
            with col2:
                hours_per_day = st.slider("Hours per Day", 2, 16, int(default_data['hours_per_day']) if existing else 8)
                days_per_week = st.slider("Days per Week", 1, 7, int(default_data['days_per_week']) if existing else 6)
                monthly_income = st.number_input("Monthly Income (₹)", 0, 100000, int(default_data['monthly_income']) if existing else 15000)
            
            st.markdown("### Benefits")
            col3, col4 = st.columns(2)
            with col3:
                has_insurance = st.checkbox("Health Insurance", value=bool(default_data['has_health_insurance']) if existing else False)
                has_leave = st.checkbox("Paid Leave", value=bool(default_data['has_paid_leave']) if existing else False)
            with col4:
                has_retirement = st.checkbox("Retirement Benefits", value=bool(default_data['has_retirement']) if existing else False)
                multiple_platforms = st.checkbox("Work on Multiple Platforms", value=bool(default_data['multiple_platforms']) if existing else False)
            
            has_loan = st.checkbox("Have Work Loan (vehicle/equipment)", value=bool(default_data['has_work_loan']) if existing else False)
            
            if st.form_submit_button("Save Data"):
                data = {
                    'age': age, 'city': city, 'platform': platform,
                    'months_experience': 6,
                    'hours_per_day': hours_per_day,
                    'days_per_week': days_per_week,
                    'monthly_income': monthly_income,
                    'has_health_insurance': has_insurance,
                    'has_paid_leave': has_leave,
                    'has_retirement': has_retirement,
                    'multiple_platforms': multiple_platforms,
                    'has_work_loan': has_loan
                }
                
                if existing:
                    # Update by deleting old and adding new
                    updated_df = df[df['worker_id'] != st.session_state['worker_id']]
                    updated_df.to_csv(WORKER_DATA, index=False)
                    add_worker_data(st.session_state['worker_id'], data)
                else:
                    add_worker_data(st.session_state['worker_id'], data)
                
                st.success("✅ Data saved!")
                st.rerun()
    
    elif page == "📊 My Precarity Score":
        st.title("📊 My Precarity Analysis")
        
        worker_df = df[df['worker_id'] == st.session_state['worker_id']]
        
        if len(worker_df) == 0:
            st.warning("No data found. Please enter your data first.")
        else:
            worker_dict = worker_df.iloc[0].to_dict()
            score = calculate_precarity_score_for_worker(worker_dict)
            risk_level, advice = get_risk_level(score)
            
            # Display score gauge
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Your Precarity Score", f"{score}/100", 
                         delta="Lower is better" if score < 50 else "Needs attention")
            with col2:
                st.metric("Risk Level", risk_level)
            
            # Show score breakdown
            st.subheader("Score Breakdown")
            
            # Income score
            income = worker_dict.get('monthly_income', 15000)
            if income < 10000:
                income_score = 100
            elif income < 15000:
                income_score = 75
            elif income < 20000:
                income_score = 50
            elif income < 30000:
                income_score = 25
            else:
                income_score = 0
            st.progress(income_score/100, text=f"Income Level: {income_score}/100 (Lower income = higher risk)")
            
            # Hours score
            hours = worker_dict.get('hours_per_day', 8) * worker_dict.get('days_per_week', 6)
            if hours > 60:
                hours_score = 100
            elif hours > 50:
                hours_score = 75
            elif hours > 40:
                hours_score = 50
            elif hours > 30:
                hours_score = 25
            else:
                hours_score = 0
            st.progress(hours_score/100, text=f"Working Hours: {hours_score}/100 (More hours = higher risk)")
            
            # Benefits score
            benefits = sum([
                worker_dict.get('has_health_insurance', False),
                worker_dict.get('has_paid_leave', False),
                worker_dict.get('has_retirement', False)
            ])
            benefits_score = (3 - benefits) / 3 * 100
            st.progress(benefits_score/100, text=f"Benefits Gap: {benefits_score}/100 (Missing benefits = higher risk)")
            
            st.info(f"💡 {advice}")

# ========== RESEARCHER/ADMIN VIEW ==========
else:
    df = pd.read_csv(WORKER_DATA)
    
    if page == "🏠 Dashboard":
        st.title("📊 All Workers Dashboard")
        
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Workers", len(df))
        with col2:
            st.metric("Avg Monthly Income", f"₹{df['monthly_income'].mean():,.0f}")
        with col3:
            st.metric("Avg Hours/Week", f"{int((df['hours_per_day'] * df['days_per_week']).mean())}")
        with col4:
            st.metric("With Insurance", f"{df['has_health_insurance'].sum()}")
        
        # Calculate scores for all workers
        all_scores = []
        for idx, worker in df.iterrows():
            score = calculate_precarity_score_for_worker(worker.to_dict())
            all_scores.append(score)
        
        df['precarity_score'] = all_scores
        
        # Risk distribution
        risk_counts = df['precarity_score'].apply(lambda x: 'High Risk' if x > 60 else ('Medium Risk' if x > 30 else 'Low Risk')).value_counts()
        
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(risk_counts)
        with col2:
            st.dataframe(df[['worker_id', 'age', 'city', 'platform', 'monthly_income', 'precarity_score']])
        
        st.subheader("All Workers Data")
        st.dataframe(df)
    
    elif page == "📊 All Workers Analytics":
        st.title("📊 Analytics")
        
        # Calculate scores
        scores = []
        for idx, worker in df.iterrows():
            score = calculate_precarity_score_for_worker(worker.to_dict())
            scores.append(score)
        df['precarity_score'] = scores
        
        # Platform comparison
        st.subheader("Income by Platform")
        platform_stats = df.groupby('platform')['monthly_income'].mean().sort_values(ascending=False)
        st.bar_chart(platform_stats)
        
        # City comparison
        st.subheader("Average Precarity Score by City")
        city_scores = df.groupby('city')['precarity_score'].mean().sort_values()
        st.bar_chart(city_scores)
        
        # Risk distribution
        st.subheader("Risk Level Distribution")
        df['risk_level'] = df['precarity_score'].apply(lambda x: 'High' if x > 60 else ('Medium' if x > 30 else 'Low'))
        risk_dist = df['risk_level'].value_counts()
        st.bar_chart(risk_dist)
        
        # Download option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Full Report", csv, "precarity_report.csv", "text/csv")
    
    elif page == "📁 Upload Data":
        st.title("📁 Upload External Data")
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
        if uploaded_file:
            new_df = pd.read_csv(uploaded_file)
            st.write("Preview of uploaded data:")
            st.dataframe(new_df.head())
            
            if st.button("Merge with Existing Data"):
                # Check required columns
                required = ['worker_id', 'monthly_income', 'hours_per_day', 'days_per_week']
                missing = [c for c in required if c not in new_df.columns]
                if missing:
                    st.error(f"Missing columns: {missing}")
                else:
                    merged = pd.concat([df, new_df], ignore_index=True)
                    merged.to_csv(WORKER_DATA, index=False)
                    st.success(f"Added {len(new_df)} new records!")
                    st.rerun()