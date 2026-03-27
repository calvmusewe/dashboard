import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ------------------------------
# Page config
st.set_page_config(page_title="University Enrollment & Retention Dashboard", layout="wide")
st.title("🎓 University Enrollment & Retention Dashboard")
st.markdown("Analyze student enrollment trends, retention rates, and demographic composition across programs and years.")

# ------------------------------
# Generate synthetic data (replace with real dataset)
@st.cache_data
def load_data():
    np.random.seed(42)
    years = list(range(2018, 2025))  # 2018 to 2024
    programs = ["Business", "Engineering", "Arts & Sciences", "Education", "Health Sciences", "Computer Science"]
    levels = ["Undergraduate", "Graduate"]
    # Create base combinations
    data = []
    for year in years:
        for program in programs:
            for level in levels:
                enrollment = np.random.randint(100, 1000)
                retention_rate = np.random.uniform(0.70, 0.95)
                # Graduate programs often have higher retention
                if level == "Graduate":
                    retention_rate = min(retention_rate + 0.05, 0.98)
                # Some programs have better retention
                if program in ["Business", "Computer Science"]:
                    retention_rate = min(retention_rate + 0.03, 0.97)
                data.append({
                    "Academic_Year": year,
                    "Program": program,
                    "Student_Level": level,
                    "Enrollment": enrollment,
                    "Retention_Rate": retention_rate,
                    "Demographic": np.random.choice(["Domestic", "International"], p=[0.7, 0.3])
                })
    df = pd.DataFrame(data)
    # Add a synthetic demographic breakdown (just for pie chart)
    # We'll expand rows to simulate individual students for demographic counts
    # For simplicity, we'll create a separate DataFrame for demographics
    demo_data = []
    for _, row in df.iterrows():
        for _ in range(int(row["Enrollment"] / 10)):  # reduce rows for performance
            demo_data.append({
                "Academic_Year": row["Academic_Year"],
                "Program": row["Program"],
                "Student_Level": row["Student_Level"],
                "Demographic": np.random.choice(["Domestic", "International"], p=[0.7, 0.3])
            })
    demo_df = pd.DataFrame(demo_data)
    return df, demo_df

df, demo_df = load_data()

# ------------------------------
# Sidebar filters
st.sidebar.header("🔍 Filters")

# Program filter
programs = st.sidebar.multiselect(
    "Select Programs",
    options=df["Program"].unique(),
    default=df["Program"].unique()
)

# Academic year filter
years = st.sidebar.multiselect(
    "Select Academic Years",
    options=df["Academic_Year"].unique(),
    default=df["Academic_Year"].unique()
)

# Student level filter
levels = st.sidebar.multiselect(
    "Select Student Level",
    options=df["Student_Level"].unique(),
    default=df["Student_Level"].unique()
)

# Apply filters
filtered_df = df[
    (df["Program"].isin(programs)) &
    (df["Academic_Year"].isin(years)) &
    (df["Student_Level"].isin(levels))
]

filtered_demo = demo_df[
    (demo_df["Program"].isin(programs)) &
    (demo_df["Academic_Year"].isin(years)) &
    (demo_df["Student_Level"].isin(levels))
]

# ------------------------------
# Key Metrics
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    total_enrollment = filtered_df["Enrollment"].sum()
    st.metric("Total Enrollment", f"{total_enrollment:,}")
with col2:
    avg_retention = filtered_df["Retention_Rate"].mean() * 100
    st.metric("Average Retention Rate", f"{avg_retention:.1f}%")
with col3:
    num_programs = filtered_df["Program"].nunique()
    st.metric("Programs Included", num_programs)
st.markdown("---")

# ------------------------------
# Visualizations

# 1. Enrollment Trend Over Time
st.subheader("📈 Enrollment Over Time")
enrollment_trend = filtered_df.groupby(["Academic_Year", "Program"])["Enrollment"].sum().reset_index()
fig1 = px.line(enrollment_trend, x="Academic_Year", y="Enrollment", color="Program",
               title="Enrollment by Program Over Years", markers=True)
st.plotly_chart(fig1, use_container_width=True)

# 2. Retention Rate by Program and Level
st.subheader("📊 Retention Rate by Program and Student Level")
retention_heat = filtered_df.pivot_table(values="Retention_Rate", index="Program", columns="Student_Level", aggfunc="mean")
fig2 = px.imshow(retention_heat, text_auto=True, aspect="auto",
                 title="Average Retention Rate (as %)",
                 labels=dict(x="Student Level", y="Program", color="Retention Rate"))
fig2.update_coloraxes(colorscale="RdYlGn", colorbar_title="Retention Rate")
st.plotly_chart(fig2, use_container_width=True)

# 3. Enrollment by Student Level (Stacked Bar)
st.subheader("📊 Enrollment by Student Level")
enrollment_level = filtered_df.groupby(["Academic_Year", "Student_Level"])["Enrollment"].sum().reset_index()
fig3 = px.bar(enrollment_level, x="Academic_Year", y="Enrollment", color="Student_Level",
              title="Enrollment by Level", barmode="stack")
st.plotly_chart(fig3, use_container_width=True)

# 4. Demographic Breakdown (Pie Chart)
st.subheader("🌍 Demographic Composition")
demo_counts = filtered_demo["Demographic"].value_counts().reset_index()
demo_counts.columns = ["Demographic", "Count"]
fig4 = px.pie(demo_counts, values="Count", names="Demographic", title="Domestic vs. International Students")
st.plotly_chart(fig4, use_container_width=True)

# 5. Program Enrollment Distribution (Bar)
st.subheader("🏫 Current Year Enrollment by Program")
latest_year = filtered_df["Academic_Year"].max()
latest_data = filtered_df[filtered_df["Academic_Year"] == latest_year]
latest_data = latest_data.groupby("Program")["Enrollment"].sum().reset_index()
fig5 = px.bar(latest_data, x="Program", y="Enrollment", color="Program",
              title=f"Enrollment by Program ({latest_year})")
st.plotly_chart(fig5, use_container_width=True)

# 6. Data Table
st.subheader("📋 Detailed Data (Filtered)")
st.dataframe(filtered_df, use_container_width=True)

# 7. Download Button
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(filtered_df)
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name="university_enrollment_data.csv",
    mime="text/csv",
)

# Optional: Simple retention vs enrollment scatter
st.subheader("🔍 Relationship: Enrollment vs. Retention Rate")
fig6 = px.scatter(filtered_df, x="Enrollment", y="Retention_Rate", color="Program", size="Enrollment",
                  hover_data=["Academic_Year"], title="Enrollment vs. Retention Rate")
st.plotly_chart(fig6, use_container_width=True)