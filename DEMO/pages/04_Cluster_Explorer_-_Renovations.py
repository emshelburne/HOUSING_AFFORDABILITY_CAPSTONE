# streamlit_page: Cluster Explorer - renos

import os
import pandas as pd
import streamlit as st

from utils.figures import plot_clusters_3d
from utils.load_data import load_vis_clusters, resolve_sources


# ---------- Data load ----------
src = resolve_sources()
emb = load_vis_clusters(src["VIS_CLUSTERS_RENOS"])


# ---------- Page Header ----------
st.header("Cluster Explorer: Renovations")

# ---------- Intro / Method blurb ----------
st.markdown(
    """
This page explores patterns in **renovation permits** using an unsupervised ML pipeline:

- We applied **Agglomerative Clustering** on engineered features (including text features from permit descriptions).
- Text features were embedded via **TF–IDF** (Term Frequency-Inverse Document Frequency)  and then **SVD** (Singular Value Decomposition), a dimensionality reducer.
- The first two SVD components are shown as the **NLP dimensions** (NLP Dim. 1, NLP Dim. 2), giving a 2D map of semantic similarity.
- The vertical axis uses the **project value (log scale)** to highlight the spread in construction costs.

Use the 3D view to rotate/zoom and inspect clusters. Hover to see **Permit ID**, coordinates, and project value.
"""
)



# Minimal schema check (soft)
required_cols = {"nlp_x", "nlp_y", "project_value", "cluster", "permit_id"}
missing = required_cols - set(map(str, emb.columns))
if missing:
    st.warning(
        "Some expected columns are missing: "
        + ", ".join(sorted(missing))
        + ". The plot may not render correctly."
    )

# ---------- Optional display controls ----------
with st.sidebar:
    st.subheader("Display Options")
    marker_size = st.slider("Marker size", min_value=3, max_value=10, value=6, step=1)
    opacity = st.slider("Point opacity", min_value=0.4, max_value=1.0, value=0.85, step=0.05)

# ---------- 3D Visualization ----------
fig = plot_clusters_3d(emb, permit_type="renovations")
# If you want marker size/opactiy from sidebar to apply without touching utils:
fig.update_traces(marker=dict(size=marker_size), opacity=opacity)

# Make the frame larger
fig.update_layout(
    width=1000,   # pixels
    height=800,  # pixels
)


st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Tip: drag to rotate; scroll or pinch to zoom; hover for Permit ID and details. "
)



# ---------- Cluster Summary ----------
st.markdown("---")
st.subheader("Agglomerative Clustering Results — Renovation Permits")
st.markdown("Below is a summary of the 6 clusters, their defining characteristics, and interpretations.")

st.markdown(
    """
##### Cluster 0 — Multi-Unit Interior Renovations
- **Size / Share:** 3,652 permits (46.4%)
- **Avg Project Value:** **$68,301**
- **Top Tokens:** floor, unit, building, multiple, kitchen, wall
- **Features:** Predominantly multiple dwellings; lots of interior improvements (floors, kitchens, bathrooms).
- **Interpretation:** **Routine low-cost renovations** in multi-unit residential buildings.

##### Cluster 1 — Single-Detached Home Renovations
- **Size / Share:** 2,340 permits (29.7%)
- **Avg Project Value:** **$54,300**
- **Top Tokens:** new, family, floor, remove, building, interior, door
- **Features:** Mostly single-detached houses; focus on general interior/exterior remodeling.
- **Interpretation:** **Mainstream single-family home renovations**, low- to mid-value.

##### Cluster 2 — Higher-Value Renovations (Windows, Roofs, Exteriors)
- **Size / Share:** 402 permits (5.1%)
- **Avg Project Value:** **$481,548**
- **Top Tokens:** new, building, floor, interior, window, door, repair, upgrade
- **Features:** Detached and multiple dwellings; scope includes exteriors, windows, and major repairs.
- **Interpretation:** **High-value renovation projects**, more comprehensive in scope.

##### Cluster 3 — Secondary Suite Renovations
- **Size / Share:** 949 permits (12.1%)
- **Avg Project Value:** **$59,653**
- **Top Tokens:** suite, secondary, secondary suite, family, access, law
- **Features:** Almost all projects involve adding or upgrading secondary suites.
- **Interpretation:** **Suite-focused renovations**, moderate value.

##### Cluster 4 — Large-Scale Structural Repairs
- **Size / Share:** 38 permits (0.5%)
- **Avg Project Value:** **$2,478,865**
- **Top Tokens:** new, building, roof, replace, repair, multiple, tree
- **Features:** Mix of multiple dwellings; significant structural scope (roof, repairs).
- **Interpretation:** **Rare but very large renovation projects**, extremely high values.

##### Cluster 5 — Multi-Unit Alterations
- **Size / Share:** 494 permits (6.3%)
- **Avg Project Value:** **$60,883**
- **Top Tokens:** multiple, building, unit, alteration, improvement
- **Features:** Almost entirely multiple dwellings; direct alterations and improvements.
- **Interpretation:** **Multi-unit building alterations**, mid-value renovation projects.
"""
)


