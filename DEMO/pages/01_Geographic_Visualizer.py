# streamlit_page: Geographic Development Visualizer

from utils.load_data import load_geojson, load_econ, load_permits
from utils.figures import map_boundaries, monthly_permits_over_rent_map
import json
import pandas as pd
import geopandas as gpd
import streamlit as st
from typing import Tuple
import numpy as np
import re

st.header("Geographic Visualizer")

# --- Intro text ---
st.markdown("""
This interactive visualizer combines **economic indicators** (rent levels or vacancy rates) 
with **building permit activity** across Vancouver neighborhoods.  
- Neighborhoods are shaded by the selected economic metric.  
- Colored points represent permits, sized by project value and categorized by cluster.  
Use the animation controls to explore how development and economic conditions have evolved over time.
""")

# Load data
geo_path = r"C:\Users\emshe\Desktop\BRAINSTATION\CAPSTONE\GIT_REPO\DEMO\data\nbhds.geojson"
geojson, gdf = load_geojson(geo_path)

econ_path = r"C:\Users\emshe\Desktop\BRAINSTATION\CAPSTONE\GIT_REPO\DEMO\data\econ.parquet"
econ_df = load_econ(econ_path)

demos_path = r"C:\Users\emshe\Desktop\BRAINSTATION\CAPSTONE\GIT_REPO\DEMO\data\demos.parquet"
demos_df = load_permits(demos_path)

renos_path = r"C:\Users\emshe\Desktop\BRAINSTATION\CAPSTONE\GIT_REPO\DEMO\data\renos.parquet"
renos_df = load_permits(renos_path)

builds_path = r"C:\Users\emshe\Desktop\BRAINSTATION\CAPSTONE\GIT_REPO\DEMO\data\builds.parquet"
builds_df = load_permits(builds_path)




# ---------------------- Controls ----------------------
st.subheader("Configure Visualization")

# Economic metric options (raw keys, pretty printed in UI)
METRIC_OPTIONS = [
    'avg_rent_studio', 'avg_rent_one_bedroom', 'avg_rent_two_bedroom',
    'avg_rent_three_bedroom_plus', 'avg_rent_total',
    'med_rent_studio', 'med_rent_one_bedroom', 'med_rent_two_bedroom',
    'med_rent_three_bedroom_plus', 'med_rent_total',
    'vacancy_rate_studio', 'vacancy_rate_one_bedroom', 'vacancy_rate_two_bedroom',
    'vacancy_rate_three_bedroom_plus', 'vacancy_rate_total'
]

def _pretty(s: str) -> str:
    return s.replace('_', ' ').title()

with st.form("viz_controls", clear_on_submit=False):
    col1, col2, col3 = st.columns([1, 2, 1.2], vertical_alignment="center")

    with col1:
        permit_choice = st.selectbox(
            "Permit Type",
            options=["Builds", "Demolitions", "Renovations"],
            index=0
        )

    with col2:
        metric_choice = st.selectbox(
            "Economic Metric",
            options=METRIC_OPTIONS,
            index=METRIC_OPTIONS.index("avg_rent_total"),
            format_func=_pretty
        )

    with col3:
        pace_choice = st.selectbox(
            "Animation Pace",
            options=["Slow", "Medium", "Fast"],
            index=0
        )

    submitted = st.form_submit_button("Update Visualization")

# Resolve selected permits df
permits_map = {
    "Builds": builds_df,
    "Demolitions": demos_df,
    "Renovations": renos_df,
}
sel_permits_df = permits_map[permit_choice]

# Convert pace to the function's expected lowercase
pace_arg = pace_choice.lower()

# When parameters are (re)selected and submitted, render the figure
if submitted:
    fig = monthly_permits_over_rent_map(
        econ_df,
        gdf,
        sel_permits_df,
        metric=metric_choice,
        animation_pace=pace_arg
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    # Initial/default render (optional: you can pre-render with defaults)
    fig = monthly_permits_over_rent_map(
        econ_df,
        gdf,
        builds_df,
        metric="avg_rent_total",
        animation_pace="slow"
    )
    st.plotly_chart(fig, use_container_width=True)


# --- Cluster guide ---
st.subheader("Cluster Guide")
st.markdown("""
**New Building Permits**  
- **B0** – Small Detached & Duplex Mix  
- **B1** – Large Multi-Dwelling Projects  
- **B2** – Mid-Value Family Housing  
- **B3** – Laneway Houses (Lower Value)  
- **B4** – Numbered Suites & Laneways  
- **B5** – Duplexes with Secondary Suites  
- **B6** – Detached with Suites  
- **B7** – Large Multi-Unit Midrise Projects  

**Renovation Permits**  
- **R0** – Multi-Unit Interior Renovations  
- **R1** – Single-Detached Home Renovations  
- **R2** – Higher-Value Renovations (Windows, Roofs, Exteriors)  
- **R3** – Secondary Suite Renovations  
- **R4** – Large-Scale Structural Repairs  
- **R5** – Multi-Unit Alterations  

**Demolition Permits**  
- **D0** – Deconstruction & Recycling (Higher Value)  
- **D1** – Standard Family House Demolitions  
- **D2** – Large Multi-Dwelling Demolitions  
- **D3** – Green Deconstruction  
""")