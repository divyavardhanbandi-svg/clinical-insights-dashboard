"""
Clinical Insights Dashboard
----------------------------
A simple, self-contained Streamlit dashboard for exploring clinical /
hospital operations data: patient volumes, length of stay, readmission
rates, costs, and satisfaction — sliced by department, diagnosis,
age group, and time period.

Run:
    streamlit run app.py

Data:
    Expects a CSV named `sample_data.csv` in the same folder
    (generate it first with `python data_generator.py`), or upload
    your own CSV with the same column structure via the sidebar.
"""

import os
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Clinical Insights Dashboard",
    page_icon="🏥",
    layout="wide",
)

REQUIRED_COLUMNS = [
    "patient_id", "age", "gender", "department", "diagnosis",
    "admit_date", "discharge_date", "length_of_stay_days",
    "readmitted_30d", "insurance_type", "satisfaction_score",
    "treatment_cost_usd",
]


# ---------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------
@st.cache_data
def load_data(path_or_buffer) -> pd.DataFrame:
    df = pd.read_csv(path_or_buffer)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["admit_date"] = pd.to_datetime(df["admit_date"])
    df["discharge_date"] = pd.to_datetime(df["discharge_date"])

    bins = [0, 18, 35, 50, 65, 120]
    labels = ["0-18", "19-35", "36-50", "51-65", "65+"]
    df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels, right=True)

    return df


def get_dataframe() -> pd.DataFrame | None:
    st.sidebar.header("Data Source")
    uploaded = st.sidebar.file_uploader("Upload clinical CSV (optional)", type=["csv"])

    if uploaded is not None:
        return load_data(uploaded)

    default_path = os.path.join(os.path.dirname(__file__), "sample_data.csv")
    if os.path.exists(default_path):
        return load_data(default_path)

    st.warning(
        "No data found. Upload a CSV in the sidebar, or run "
        "`python data_generator.py` to create a sample dataset."
    )
    return None


# ---------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------
def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    min_date, max_date = df["admit_date"].min(), df["admit_date"].max()
    date_range = st.sidebar.date_input(
        "Admit date range", value=(min_date, max_date),
        min_value=min_date, max_value=max_date,
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        df = df[(df["admit_date"] >= start) & (df["admit_date"] <= end)]

    departments = st.sidebar.multiselect(
        "Department", sorted(df["department"].unique()),
        default=sorted(df["department"].unique()),
    )
    df = df[df["department"].isin(departments)]

    age_groups = st.sidebar.multiselect(
        "Age group", sorted(df["age_group"].dropna().unique().tolist()),
        default=sorted(df["age_group"].dropna().unique().tolist()),
    )
    df = df[df["age_group"].isin(age_groups)]

    insurance = st.sidebar.multiselect(
        "Insurance type", sorted(df["insurance_type"].unique()),
        default=sorted(df["insurance_type"].unique()),
    )
    df = df[df["insurance_type"].isin(insurance)]

    return df


# ---------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------
def render_kpis(df: pd.DataFrame):
    total_patients = len(df)
    avg_los = df["length_of_stay_days"].mean() if total_patients else 0
    readmit_rate = df["readmitted_30d"].mean() * 100 if total_patients else 0
    avg_satisfaction = df["satisfaction_score"].mean() if total_patients else 0
    total_cost = df["treatment_cost_usd"].sum() if total_patients else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Patients", f"{total_patients:,}")
    c2.metric("Avg Length of Stay", f"{avg_los:.1f} days")
    c3.metric("30-Day Readmission Rate", f"{readmit_rate:.1f}%")
    c4.metric("Avg Satisfaction", f"{avg_satisfaction:.1f} / 5")
    c5.metric("Total Treatment Cost", f"${total_cost:,.0f}")


# ---------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------
def render_charts(df: pd.DataFrame):
    left, right = st.columns(2)

    with left:
        st.subheader("Patient Volume by Department")
        vol = df["department"].value_counts().reset_index()
        vol.columns = ["department", "patients"]
        fig = px.bar(vol, x="department", y="patients", color="department")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Top Diagnoses")
        diag = df["diagnosis"].value_counts().head(8).reset_index()
        diag.columns = ["diagnosis", "cases"]
        fig = px.bar(diag, x="cases", y="diagnosis", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    left2, right2 = st.columns(2)

    with left2:
        st.subheader("Admissions Over Time")
        trend = (
            df.set_index("admit_date")
            .resample("W")
            .size()
            .reset_index(name="admissions")
        )
        fig = px.line(trend, x="admit_date", y="admissions", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    with right2:
        st.subheader("Readmission Rate by Department")
        readmit = df.groupby("department")["readmitted_30d"].mean().reset_index()
        readmit["readmitted_30d"] *= 100
        fig = px.bar(readmit, x="department", y="readmitted_30d",
                     labels={"readmitted_30d": "Readmission Rate (%)"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Length of Stay Distribution")
    fig = px.histogram(df, x="length_of_stay_days", nbins=20,
                        color="department", barmode="overlay", opacity=0.6)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Treatment Cost vs Length of Stay")
    fig = px.scatter(
        df, x="length_of_stay_days", y="treatment_cost_usd",
        color="department", hover_data=["diagnosis", "age_group"],
        trendline="ols" if _has_statsmodels() else None,
    )
    st.plotly_chart(fig, use_container_width=True)


def _has_statsmodels() -> bool:
    try:
        import statsmodels  # noqa: F401
        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main():
    st.title("🏥 Clinical Insights Dashboard")
    st.caption(
        "Explore patient volumes, length of stay, readmissions, cost, "
        "and satisfaction. Built on synthetic data — no real patient "
        "information is used."
    )

    df = get_dataframe()
    if df is None:
        return

    filtered = apply_filters(df)

    if filtered.empty:
        st.info("No records match the selected filters.")
        return

    render_kpis(filtered)
    st.divider()
    render_charts(filtered)

    with st.expander("View raw data"):
        st.dataframe(filtered, use_container_width=True)


if __name__ == "__main__":
    main()
