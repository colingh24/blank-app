import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Temperature Data Viewer", page_icon="🌍", layout="wide"
)

st.title("🌍 Berkeley Earth Temperature Data")
st.write("Global monthly land temperature data from Berkeley Earth")

# Load data from URL
url = "https://storage.googleapis.com/berkeley-earth-temperature-hr/global/Land_TAVG_monthly.txt"


@st.cache_data
def load_data():
    df = pd.read_csv(url, sep=r"\s+", skiprows=1, comment="%")
    return df


try:
    data = load_data()

    # --- Sidebar Configuration for Rolling Mean ---
    st.sidebar.header("Visualization Settings")
    window_size = st.sidebar.slider(
        "Rolling Mean Window (Months)",
        min_value=1,
        max_value=120,
        value=12,  # Default to 12-month (1 year) rolling average
        step=1,
    )

    # Calculate rolling mean on the entire dataset
    if "Anomaly" in data.columns:
        data["Rolling_Mean"] = (
            data["Anomaly"].rolling(window=window_size, min_periods=1).mean()
        )

    st.subheader("📊 Data Table")
    st.dataframe(data.head(50), use_container_width=True)

    st.subheader("📈 Temperature Trend")
    if (
        "Year" in data.columns
        and "Month" in data.columns
        and "Anomaly" in data.columns
    ):
        # Using a subset for the plot as per your original code (head 100)
        # Note: You can change data.head(100) to 'data' if you want to see the whole history
        plot_data = data.head(100)

        # Base line chart for raw Anomaly data
        fig = px.line(
            plot_data,
            x=plot_data.index,
            y="Anomaly",
            title=f"Temperature Anomaly Over Time ({window_size}-Month Rolling Mean)",
            labels={"Anomaly": "Temperature Anomaly (°C)", "index": "Record"},
            template="plotly_white",
        )

        # Add the Rolling Mean line on top
        fig.add_trace(
            go.Scatter(
                x=plot_data.index,
                y=plot_data["Rolling_Mean"],
                mode="lines",
                name=f"{window_size}-Mo Rolling Mean",
                line=dict(color="red", width=2.5),
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Dataset Info")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(data))
    with col2:
        st.metric("Columns", len(data.columns))
    with col3:
        if "Anomaly" in data.columns:
            st.metric("Avg Anomaly", f"{data['Anomaly'].mean():.2f}°C")

except Exception as e:
    st.error(f"Error loading data: {e}")