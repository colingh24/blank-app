import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Temperature Data Viewer", page_icon="🌍", layout="wide")

st.title("🌍 Berkeley Earth Temperature Data")
st.write("Global monthly land temperature data from Berkeley Earth")

# Load data from URL
url = "https://storage.googleapis.com/berkeley-earth-temperature-hr/global/Land_TAVG_monthly.txt"

@st.cache_data
def load_data():
    df = pd.read_csv(url, sep=r'\s+', skiprows=1, comment='%')
    return df

try:
    data = load_data()
    
    st.subheader("📊 Data Table")
    st.dataframe(data.head(50), use_container_width=True)
    
    st.subheader("📈 Temperature Trend")
    if 'Year' in data.columns and 'Month' in data.columns and 'Anomaly' in data.columns:
        fig = px.line(
            data.head(100),
            x=data.index,
            y="Anomaly",
            title="Temperature Anomaly Over Time",
            labels={"Anomaly": "Temperature Anomaly (°C)", "index": "Record"},
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 Dataset Info")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(data))
    with col2:
        st.metric("Columns", len(data.columns))
    with col3:
        if 'Anomaly' in data.columns:
            st.metric("Avg Anomaly", f"{data['Anomaly'].mean():.2f}°C")
    
except Exception as e:
    st.error(f"Error loading data: {e}")
