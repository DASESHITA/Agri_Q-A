import streamlit as st
import pandas as pd
import numpy as np
import re

st.set_page_config(page_title="Agri-Climate Q&A", page_icon="🌾", layout="wide")
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
all_states = sorted(list(set(crop_df['state'].unique()) | set(rainfall_df['state'].unique()) | set(temp_df['state'].unique())))
all_crops = sorted(crop_df['crop type'].unique())
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

# Main app
st.title("🌾 Agriculture & Climate Q&A System")
st.markdown("Ask natural language questions about crops, rainfall, and temperature across Indian states")
st.sidebar.header("💡 Sample Questions")
sample_questions = [
    "Compare rainfall in Karnataka and Tamil Nadu",
    "Show top crops in Maharashtra and Punjab", 
    "Analyze temperature in Uttar Pradesh and Bihar",
    "Compare everything for Karnataka and West Bengal with Rice and Wheat"
]

for i, q in enumerate(sample_questions):
    if st.sidebar.button(f"#{i+1}: {q}"):
        st.session_state.question = q

st.sidebar.header("📁 Available Data")
st.sidebar.write(f"**States**: {', '.join(all_states)}")
st.sidebar.write(f"**Crops**: {', '.join(all_crops)}")
st.sidebar.write(f"**Years**: 2015-2024")

question = st.text_input(
    "Ask your question:",
    value=st.session_state.get('question', ''),
    placeholder="e.g., Compare rainfall in Karnataka and Tamil Nadu for 2020-2022"
)

# Process question
if question:
    st.markdown("---")
    st.subheader("🔍 Answer")
    
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

# Data preview
with st.expander("📊 View Raw Data"):
    tab1, tab2, tab3 = st.tabs(["Crop Data", "Rainfall Data", "Temperature Data"])
    
    with tab1:
        st.write(f"Crop Records: {crop_df.shape[0]}")
        st.dataframe(crop_df.head(10))
    with tab2:
        st.write(f"Rainfall Records: {rainfall_df.shape[0]}")
        st.dataframe(rainfall_df.head(10))
    with tab3:
        st.write(f"Temperature Records: {temp_df.shape[0]}")
        st.dataframe(temp_df.head(10))

