# streamlit_page: Neighborhood Spotlight

import streamlit as st
import pandas as pd
from utils.load_data import resolve_sources, load_permits, load_econ
from utils.figures import compact_no_currency, compact_cad, animated_cluster_bars, plot_economic_metrics_grid

import matplotlib.pyplot as plt
import seaborn as sns
from itertools import product

import plotly.express as px
import plotly.graph_objects as go
import json
import geopandas as gpd
from typing import Tuple
import numpy as np
import re
import math


src = resolve_sources()

# Load data
econ_df     = load_econ(src["ECON"])
permits_all = load_permits(src['PERMITS'])



# --- Header ---
st.header("Neighborhood Spotlight")

# --- Intro text ---
st.markdown("""
Explore development activity and renter economics for a particular neighborhood (or all of Vancouver).

**What you’ll see here:**
- An **animated bar chart** of monthly permit counts by **cluster** (B0, B1, …), with the **total project cost** shown above each bar. You can scope to a specific **neighborhood** or to **Vancouver** (all neighborhoods), pick a **development type** (Builds / Renovations / Demolitions), and adjust the **animation pace**.
- A visual summary of economic metrics over time with line graphs.
""")

# =============== Controls ===============
st.subheader("Configure Neighborhood Spotlight")

NBHD_SET = {
    'Downtown Eastside/Strathcona', 'Kerrisdale', 'Hastings/Sunrise/Grandview/Woodlands',
    'Collingwood', 'Sunset', 'Kitsilano/Point Grey South', 'Point Grey', 'Renfrew',
    'Downtown Central', 'Kitsilano/Point Grey North', 'Downtown North', 'Marpole South',
    'Marpole Remainder', 'South Cambie', 'West End/Stanley Park South', 'South False Creek',
    'Cedar Cottage', 'English Bay', 'Fraser View/Killarny', 'Riley Park',
    'West End/Stanley Park North', 'Mount Pleasant', 'North False Creek',
    'Westside/Kerrisdale Remainder', 'South Granville'
}
NBHD_OPTIONS = ["Vancouver"] + sorted(NBHD_SET)

DEV_FRIENDLY_TO_ARG = {"Builds": "builds", "Renovations": "renos", "Demolitions": "demos"}
PACE_OPTIONS = ["Fast", "Medium", "Slow"]

# --- Session state setup ---
if "nbhd_confirmed" not in st.session_state:
    st.session_state.nbhd_confirmed = False
if "nbhd_params" not in st.session_state:
    st.session_state.nbhd_params = {}
if "nbhd_anim_token" not in st.session_state:
    st.session_state.nbhd_anim_token = None

# --- User form ---
with st.form("nbhd_controls", clear_on_submit=False):
    c1, c2, c3 = st.columns([1.2, 1, 1])

    with c1:
        sel_nbhd = st.selectbox("Neighborhood", NBHD_OPTIONS,
                                index=NBHD_OPTIONS.index("Vancouver"),
                                key="nbhd_choice")
    with c2:
        sel_dev_friendly = st.selectbox("Development Type",
                                        list(DEV_FRIENDLY_TO_ARG.keys()),
                                        index=0,
                                        key="nbhd_dev_choice")
    with c3:
        sel_pace = st.selectbox("Animation Pace", PACE_OPTIONS, index=0,
                                key="nbhd_pace_choice")

    submitted = st.form_submit_button("Confirm selections")

if submitted:
    st.session_state.nbhd_confirmed = True
    st.session_state.nbhd_params = {
        "neighborhood": st.session_state.nbhd_choice,
        "permit_category": DEV_FRIENDLY_TO_ARG[st.session_state.nbhd_dev_choice],
        "pace": st.session_state.nbhd_pace_choice,  # we'll .lower() at callsite
    }
    import time
    st.session_state.nbhd_anim_token = f"{time.time():.6f}"

# --- Restart / Clear buttons ---
btn_cols = st.columns([1, 1, 6])
with btn_cols[0]:
    restart = st.button("↺ Restart animation", disabled=not st.session_state.nbhd_confirmed)
with btn_cols[1]:
    clear = st.button("🧹 Clear selections", disabled=not st.session_state.nbhd_confirmed)

if restart:
    import time
    st.session_state.nbhd_anim_token = f"{time.time():.6f}"

# ---- Placeholders (so we can clear them on reset) ----
chart_slot = st.empty()   # Plotly animation
guide_slot = st.empty()   # Cluster guide text
econ_slot  = st.empty()   # Matplotlib econ grid

if clear:
    st.session_state.nbhd_confirmed = False
    st.session_state.nbhd_params = {}
    st.session_state.nbhd_anim_token = None
    # Clear rendered sections explicitly
    chart_slot.empty()
    guide_slot.empty()
    econ_slot.empty()


# --- Render in the desired order: Animation -> Cluster Guide -> Econ Grid ---
if st.session_state.nbhd_confirmed and st.session_state.nbhd_params:
    params = st.session_state.nbhd_params

    # 1) Animation
    with st.spinner("Rendering animation…"):
        try:
            fig = animated_cluster_bars(
                permits_df=permits_all,
                neighborhood=params["neighborhood"],
                permit_category=params["permit_category"],
                pace=params["pace"].lower(),   # ensure lower-case for function
            )
            plot_key = f"nbhd_anim_{st.session_state.nbhd_anim_token}"
            chart_slot.plotly_chart(fig, use_container_width=True, key=plot_key)
        except ValueError as ve:
            chart_slot.warning(str(ve))
        except Exception as e:
            chart_slot.exception(e)

    # 2) Cluster Guide (right after the animation)
    with guide_slot.container():
        st.subheader("Cluster Guide")
        st.markdown("""
**New Building Permits**  
- **B0** – Small Detached & Duplex Mix  
- **B1** – Large Multi-Dwelling High-rise Projects  
- **B2** – Mid-Value Family Housing  
- **B3** – Laneway Houses (Lower Value)  
- **B4** – Numbered Suites & Laneways  
- **B5** – Duplexes with Secondary Suites  
- **B6** – Detached with Suites  
- **B7** – Large Multi-Unit Mid-rise Projects  

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

    # 3) Economic Metrics Grid (Matplotlib)
    selected_nbhd = params["neighborhood"]
    nbhd_arg = None if str(selected_nbhd).strip().lower() == "vancouver" else selected_nbhd

    if econ_df is not None:
        with st.spinner("Rendering economic metrics…"):
            try:
                fig_mpl, _axes = plot_economic_metrics_grid(econ_df, nbhd=nbhd_arg)
                econ_slot.empty()  # clear any previous plot
                econ_slot.pyplot(fig_mpl, clear_figure=True)   # no key here
            except ValueError as ve:
                econ_slot.warning(str(ve))
            except Exception as e:  
                econ_slot.exception(e)
else:
    st.info("Pick your options above and click **Confirm selections** to render the animation.")



