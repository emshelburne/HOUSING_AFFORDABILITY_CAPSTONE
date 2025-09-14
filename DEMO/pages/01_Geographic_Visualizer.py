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
This interactive visualizer combines **rental economic indicators** (rent levels or vacancy rates) 
with **building permit activity** across Vancouver neighborhoods.  
- Neighborhoods are shaded by the selected economic metric.  
- Colored points represent permits, sized by financial project value and categorized by cluster.  
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

# --- Page state ---
if "geo_confirmed" not in st.session_state:
    st.session_state.geo_confirmed = False
if "geo_params" not in st.session_state:
    st.session_state.geo_params = {}
if "geo_anim_token" not in st.session_state:
    st.session_state.geo_anim_token = None  # used to force a fresh plot key

# --- UI controls in a form (no rendering until submitted) ---
with st.form("viz_controls", clear_on_submit=False):
    col1, col2, col3 = st.columns([1, 2, 1.2], vertical_alignment="center")

    with col1:
        permit_choice = st.selectbox(
            "Permit Type",
            options=["Builds", "Demolitions", "Renovations"],
            index=0,
            key="geo_permit_choice"
        )

    with col2:
        metric_choice = st.selectbox(
            "Economic Metric",
            options=METRIC_OPTIONS,
            index=METRIC_OPTIONS.index("avg_rent_total"),
            format_func=_pretty,
            key="geo_metric_choice"
        )

    with col3:
        pace_choice = st.selectbox(
            "Animation Pace",
            options=["Slow", "Medium", "Fast"],
            index=0,
            key="geo_pace_choice"
        )

    submitted = st.form_submit_button("Confirm selections")

# Map permit type to the dataframe
permits_map = {
    "Builds": builds_df,
    "Demolitions": demos_df,
    "Renovations": renos_df,
}

# --- Handle confirmation ---
if submitted:
    st.session_state.geo_confirmed = True
    st.session_state.geo_params = {
        "permit_choice": st.session_state.geo_permit_choice,
        "metric_choice": st.session_state.geo_metric_choice,
        "pace_choice": st.session_state.geo_pace_choice.lower(),
    }
    # new token forces Plotly to fully restart animation when we render
    import time
    st.session_state.geo_anim_token = f"{time.time():.6f}"

# --- Action buttons (only visible once confirmed) ---
btn_cols = st.columns([1, 1, 6])
with btn_cols[0]:
    restart = st.button("↺ Restart animation", disabled=not st.session_state.geo_confirmed)
with btn_cols[1]:
    clear = st.button("🧹 Clear selections", disabled=not st.session_state.geo_confirmed)

if restart:
    # Make a new token to reset the Plotly element key (hard restart of animation)
    import time
    st.session_state.geo_anim_token = f"{time.time():.6f}"

if clear:
    st.session_state.geo_confirmed = False
    st.session_state.geo_params = {}
    st.session_state.geo_anim_token = None

# --- Rendering slot ---
chart_slot = st.empty()

if st.session_state.geo_confirmed and st.session_state.geo_params:
    # Resolve selected DF + args
    sel_df = permits_map[st.session_state.geo_params["permit_choice"]]
    metric_arg = st.session_state.geo_params["metric_choice"]
    pace_arg = st.session_state.geo_params["pace_choice"]

    # Build figure only after confirmation / restart
    with st.spinner("Rendering animation…"):
        fig = monthly_permits_over_rent_map(
            econ_df,
            gdf,
            sel_df,
            metric=metric_arg,
            animation_pace=pace_arg
        )
    # Use a changing key to hard-reset animation when restart is clicked
    plot_key = f"geo_anim_{st.session_state.geo_anim_token}"
    chart_slot.plotly_chart(fig, use_container_width=True, key=plot_key)
else:
    st.info("Pick your options above and click **Confirm selections** to render the animation.")


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