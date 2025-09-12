
import streamlit as st
import pandas as pd
from utils.load_data import load_permits, load_econ

st.header("Neighbourhood Drill-Down")
permits_path = st.text_input("Permits file", "data/permits.parquet")
econ_path    = st.text_input("Economic metrics file", "data/cmhc_metrics.parquet")

try:
    permits = load_permits(permits_path)
    econ    = load_econ(econ_path)
except Exception as e:
    st.error(f"Problem loading data: {e}")
    st.stop()

nbhds = sorted(set(permits.get("nbhd", pd.Series(dtype=str)).dropna().unique()) | set(econ.get("nbhd", pd.Series(dtype=str)).dropna().unique()))
nbhd = st.selectbox("Select neighbourhood", nbhds if nbhds else [])

if nbhd:
    st.subheader(f"{nbhd}")
    # Example: cluster distribution over time (placeholder)
    if "cluster" in permits.columns:
        df = (permits[permits["nbhd"]==nbhd]
                .assign(year=lambda d: d["issue_date"].dt.year)
                .groupby(["year","cluster"]).size().reset_index(name="count"))
        st.caption("Cluster counts by year (placeholder)")
        st.bar_chart(df.pivot(index="year", columns="cluster", values="count").fillna(0))
    # Example: economic metric over time (placeholder)
    if "metric_name" in econ.columns:
        metric = st.selectbox("Economic metric", sorted(econ["metric_name"].unique()))
        series = econ[(econ["nbhd"]==nbhd) & (econ["metric_name"]==metric)].sort_values("date")
        st.line_chart(series.set_index("date")["value"])
else:
    st.info("Pick a neighbourhood to see details.")
