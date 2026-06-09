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

    # Section 1: Raw Monthly Trend (Slices first 100 rows as per original code)
    st.subheader("📈 Monthly Temperature Trend")
    if (
        "Year" in data.columns
        and "Month" in data.columns
        and "Anomaly" in data.columns
    ):
        plot_data = data.head(100)

        fig = px.line(
            plot_data,
            x=plot_data.index,
            y="Anomaly",
            title="Monthly Temperature Anomaly (First 100 Records Sample)",
            labels={"Anomaly": "Temperature Anomaly (°C)", "index": "Record"},
            template="plotly_white",
        )

        fig.add_trace(
            go.Scatter(
                x=plot_data.index,
                y=plot_data["Rolling_Mean"],
                mode="lines",
                name=f"{window_size}-Mo Rolling Mean",
                line=dict(color="red", width=2),
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    # Section 2: NEW Diagrams for Mean Temperature Values
    st.subheader("📊 Mean Temperature Values & Trends")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        if "Rolling_Mean" in data.columns and "Year" in data.columns:
            # Diagram 1: Full dataset rolling mean trend line
            fig_rolling = px.line(
                data,
                x="Year",
                y="Rolling_Mean",
                title=f"Full Dataset: {window_size}-Month Rolling Mean Trend",
                labels={
                    "Rolling_Mean": "Mean Anomaly (°C)",
                    "Year": "Timeline",
                },
                template="plotly_white",
                color_discrete_sequence=["#E74C3C"],
            )
            st.plotly_chart(fig_rolling, use_container_width=True)

    with col_chart2:
        if "Year" in data.columns and "Anomaly" in data.columns:
            # Calculate the overall mean temperature values grouped by year
            yearly_mean = data.groupby("Year")["Anomaly"].mean().reset_index()

            # Diagram 2: Annual average temperature anomaly bar chart
            fig_yearly = px.bar(
                yearly_mean,
                x="Year",
                y="Anomaly",
                title="Average Annual Temperature Anomaly",
                labels={"Anomaly": "Mean Anomaly (°C)", "Year": "Year"},
                template="plotly_white",
                color="Anomaly",
                color_continuous_scale=px.colors.sequential.Reds,
            )
            st.plotly_chart(fig_yearly, use_container_width=True)

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