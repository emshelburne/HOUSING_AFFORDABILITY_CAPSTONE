
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.load_data import load_permits

st.header("Clusters")
permits_path = st.text_input("Permits file", "data/permits.parquet")

try:
    permits = load_permits(permits_path)
except Exception as e:
    st.error(f"Problem loading data: {e}")
    st.stop()

# Expect columns like: 'embed_x','embed_y','embed_z','cluster' (replace with your embeddings)
embed_cols = [c for c in ["embed_x","embed_y","embed_z"] if c in permits.columns]
if len(embed_cols)==3 and "cluster" in permits.columns:
    fig = px.scatter_3d(permits.sample(min(5000, len(permits))), x=embed_cols[0], y=embed_cols[1], z=embed_cols[2],
                        color="cluster", hover_data=["nbhd","project_value"] if "project_value" in permits.columns else ["nbhd"])
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Add embedding columns (embed_x, embed_y, embed_z) and 'cluster' to your permits data to see the 3D view.")

# Simple cluster summary table
if "cluster" in permits.columns:
    if "project_value" in permits.columns:
        summary = permits.groupby("cluster").agg(n=("cluster","size"), median_value=("project_value","median")).reset_index().sort_values("n", ascending=False)
    else:
        summary = permits.groupby("cluster").size().reset_index(name="n").sort_values("n", ascending=False)
    st.dataframe(summary, use_container_width=True)
