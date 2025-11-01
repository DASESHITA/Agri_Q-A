import streamlit as st
import pandas as pd
import numpy as np
import re

# Page config with theme
st.set_page_config(
    page_title="Agri-Climate Q&A", 
    page_icon="🌾", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #556B2F;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background-color: #F8F9FA;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E8B57;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #2E8B57, #3CB371);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    .sample-question {
        background-color: #E8F5E8;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #3CB371;
        cursor: pointer;
    }
    .sample-question:hover {
        background-color: #D4EDDA;
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    .answer-section {
        background-color: #F0F8FF;
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #87CEEB;
        margin: 1rem 0;
    }
    .source-badge {
        background-color: #6C757D;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        display: inline-block;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    crop_df = pd.read_csv('crop_production.csv')
    rainfall_df = pd.read_csv('rainfall_data.csv')
    temp_df = pd.read_csv('temperature_data.csv')
    
    # Clean column names
    crop_df.columns = [col.lower().replace('_', ' ') for col in crop_df.columns]
    rainfall_df.columns = [col.lower().replace('_', ' ') for col in rainfall_df.columns]
    temp_df.columns = [col.lower().replace('_', ' ') for col in temp_df.columns]
    
    return crop_df, rainfall_df, temp_df

crop_df, rainfall_df, temp_df = load_data()

# Get all available states dynamically
all_states = sorted(list(set(crop_df['state'].unique()) | set(rainfall_df['state'].unique()) | set(temp_df['state'].unique())))
all_crops = sorted(crop_df['crop type'].unique())

# Question processing functions (same as before)
def extract_states(question):
    found_states = []
    for state in all_states:
        if state.lower() in question.lower():
            found_states.append(state)
    return found_states

def extract_crops(question):
    found_crops = []
    for crop in all_crops:
        if crop.lower() in question.lower():
            found_crops.append(crop)
    return found_crops

def extract_years(question):
    years = re.findall(r'\b(20\d{2})\b', question)
    return [int(year) for year in years] if years else []

def compare_rainfall(question):
    states = extract_states(question)
    years = extract_years(question)
    
    if not states:
        return "Please specify states to compare."
    
    result = "## 🌧️ Rainfall Comparison\n\n"
    for state in states:
        state_data = rainfall_df[rainfall_df['state'] == state]
        if years:
            state_data = state_data[state_data['year'].isin(years)]
        
        if not state_data.empty:
            avg_rainfall = state_data['rainfall mm'].mean()
            result += f"**{state}**: Average rainfall = {avg_rainfall:.2f} mm\n\n"
        else:
            result += f"**{state}**: No rainfall data available\n\n"
    
    result += f"*Source: {rainfall_df.shape[0]} records from India Meteorological Department*"
    return result

def analyze_crop_production(question):
    states = extract_states(question)
    crops = extract_crops(question)
    years = extract_years(question)
    
    if not states:
        return "Please specify states to analyze."
    
    result = "## 🌾 Crop Production Analysis\n\n"
    for state in states:
        state_data = crop_df[crop_df['state'] == state]
        if years:
            state_data = state_data[state_data['year'].isin(years)]
        
        if not state_data.empty:
            if crops:
                crop_data = state_data[state_data['crop type'].isin(crops)]
                result += f"**{state}** - Production for specified crops:\n"
                for crop in crops:
                    crop_prod = crop_data[crop_data['crop type'] == crop]['production volume']
                    if not crop_prod.empty:
                        avg_prod = crop_prod.mean()
                        result += f"  - {crop}: {avg_prod:.2f} tons\n"
            else:
                top_crops = state_data.groupby('crop type')['production volume'].mean().nlargest(3)
                result += f"**{state}** - Top 3 crops by production:\n"
                for crop, production in top_crops.items():
                    result += f"  - {crop}: {production:.2f} tons\n"
            result += "\n"
        else:
            result += f"**{state}**: No crop data available\n\n"
    
    result += f"*Source: {crop_df.shape[0]} records from Ministry of Agriculture*"
    return result

def analyze_temperature(question):
    states = extract_states(question)
    years = extract_years(question)
    
    if not states:
        return "Please specify states to analyze."
    
    result = "## 🌡️ Temperature Analysis\n\n"
    for state in states:
        state_data = temp_df[temp_df['state'] == state]
        if years:
            state_data = state_data[state_data['year'].isin(years)]
        
        if not state_data.empty:
            avg_temp = state_data['avg temperature'].mean()
            result += f"**{state}**: Average temperature = {avg_temp:.2f}°C\n\n"
        else:
            result += f"**{state}**: No temperature data available\n\n"
    
    result += f"*Source: {temp_df.shape[0]} records from India Meteorological Department*"
    return result

def complex_analysis(question):
    states = extract_states(question)
    crops = extract_crops(question)
    years = extract_years(question)
    
    if len(states) < 2:
        return "Please specify at least 2 states for comparison."
    
    result = "## 📊 Cross-Domain Analysis\n\n"
    
    # Rainfall comparison
    result += "### Rainfall Comparison\n"
    for state in states:
        rain_data = rainfall_df[rainfall_df['state'] == state]
        if years:
            rain_data = rain_data[rain_data['year'].isin(years)]
        if not rain_data.empty:
            avg_rain = rain_data['rainfall mm'].mean()
            result += f"- **{state}**: {avg_rain:.2f} mm\n"
    result += "\n"
    
    # Temperature comparison
    result += "### Temperature Comparison\n"
    for state in states:
        temp_data = temp_df[temp_df['state'] == state]
        if years:
            temp_data = temp_data[temp_data['year'].isin(years)]
        if not temp_data.empty:
            avg_temp = temp_data['avg temperature'].mean()
            result += f"- **{state}**: {avg_temp:.2f}°C\n"
    result += "\n"
    
    # Crop production
    if crops:
        result += "### Crop Production\n"
        for crop in crops:
            result += f"**{crop}**:\n"
            for state in states:
                crop_data = crop_df[(crop_df['state'] == state) & (crop_df['crop type'] == crop)]
                if years:
                    crop_data = crop_data[crop_data['year'].isin(years)]
                if not crop_data.empty:
                    avg_prod = crop_data['production volume'].mean()
                    result += f"  - {state}: {avg_prod:.2f} tons\n"
            result += "\n"
    
    result += "*Sources: Integrated data from Ministry of Agriculture & IMD*"
    return result

# Main app with enhanced UI
st.markdown('<div class="main-header">🌾 Agriculture & Climate Q&A System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Ask natural language questions about crops, rainfall, and temperature across Indian states</div>', unsafe_allow_html=True)

# Metrics in the sidebar
st.sidebar.markdown("### 📈 Data Overview")
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    st.markdown(f'<div class="metric-card"><h4>🌧️ Rainfall</h4><h3>{rainfall_df.shape[0]}</h3><small>Records</small></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><h4>🌾 Crops</h4><h3>{crop_df.shape[0]}</h3><small>Records</small></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><h4>🌡️ Temperature</h4><h3>{temp_df.shape[0]}</h3><small>Records</small></div>', unsafe_allow_html=True)

# Sample questions with better design
st.sidebar.markdown("### 💡 Try These Questions")
sample_questions = [
    "Compare rainfall in Karnataka and Tamil Nadu",
    "Show top crops in Maharashtra and Punjab", 
    "Analyze temperature in Uttar Pradesh and Bihar",
    "Compare everything for Karnataka and West Bengal with Rice and Wheat"
]

for i, q in enumerate(sample_questions):
    if st.sidebar.markdown(f'<div class="sample-question" onclick="this.style.backgroundColor=\'#D4EDDA\'">#{i+1}: {q}</div>', unsafe_allow_html=True):
        st.session_state.question = q

# Available data info
st.sidebar.markdown("### 📁 Available Data")
st.sidebar.markdown(f'<div class="card"><strong>States</strong><br>{", ".join(all_states)}</div>', unsafe_allow_html=True)
st.sidebar.markdown(f'<div class="card"><strong>Crops</strong><br>{", ".join(all_crops)}</div>', unsafe_allow_html=True)
st.sidebar.markdown(f'<div class="card"><strong>Years Available</strong><br>2015 - 2024</div>', unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🎯 Ask Your Question")
    question = st.text_area(
        "Enter your question here:",
        value=st.session_state.get('question', ''),
        placeholder="Examples:\n• Compare rainfall in Karnataka and Tamil Nadu\n• Show top crops in Maharashtra\n• Analyze temperature patterns in 2020-2022\n• Compare everything for Punjab and Gujarat with Wheat",
        height=100
    )

with col2:
    st.markdown("### 💡 Question Tips")
    st.markdown("""
    - Mention **state names** for location
    - Specify **years** for time period  
    - Include **crop names** for agriculture data
    - Use words like *compare, analyze, show*
    """)

# Process question
if question:
    st.markdown("---")
    st.markdown('<div class="answer-section">', unsafe_allow_html=True)
    st.subheader("🔍 Analysis Results")
    
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['compare', 'comparison']):
        if 'rainfall' in question_lower and 'temperature' in question_lower:
            answer = complex_analysis(question)
        elif 'rainfall' in question_lower:
            answer = compare_rainfall(question)
        elif 'temperature' in question_lower:
            answer = analyze_temperature(question)
        else:
            answer = complex_analysis(question)
    elif 'crop' in question_lower or 'production' in question_lower:
        answer = analyze_crop_production(question)
    elif 'temperature' in question_lower:
        answer = analyze_temperature(question)
    elif 'rainfall' in question_lower:
        answer = compare_rainfall(question)
    else:
        answer = complex_analysis(question)
    
    st.markdown(answer)
    st.markdown('</div>', unsafe_allow_html=True)

# Data preview with better design
with st.expander("📊 Explore Raw Data", expanded=False):
    tab1, tab2, tab3 = st.tabs(["🌾 Crop Data", "🌧️ Rainfall Data", "🌡️ Temperature Data"])
    
    with tab1:
        st.markdown(f'<span class="source-badge">Records: {crop_df.shape[0]}</span>', unsafe_allow_html=True)
        st.dataframe(crop_df.head(10), use_container_width=True)
    
    with tab2:
        st.markdown(f'<span class="source-badge">Records: {rainfall_df.shape[0]}</span>', unsafe_allow_html=True)
        st.dataframe(rainfall_df.head(10), use_container_width=True)
    
    with tab3:
        st.markdown(f'<span class="source-badge">Records: {temp_df.shape[0]}</span>', unsafe_allow_html=True)
        st.dataframe(temp_df.head(10), use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6C757D; margin-top: 2rem;">
    <p>🌱 <strong>Agriculture & Climate Q&A System</strong> | Powered by Streamlit | Data Sources: Ministry of Agriculture & India Meteorological Department</p>
</div>
""", unsafe_allow_html=True)