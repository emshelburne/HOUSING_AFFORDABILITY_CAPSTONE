# streamlit_page: Cluster Explorer - Builds

import os
import pandas as pd
import streamlit as st

from utils.figures import plot_clusters_3d
from utils.load_data import load_vis_clusters

# ---------- Page Header ----------
st.header("Cluster Explorer: Builds")

# ---------- Intro / Method blurb ----------
st.markdown(
    """
This page explores patterns in **new building permits** using an unsupervised ML pipeline:

- We applied **Agglomerative Clustering** on engineered features (including text features from permit descriptions).
- Text features were embedded via **TF–IDF** (Term Frequency-Inverse Document Frequency)  and then **SVD** (Singular Value Decomposition), a dimensionality reducer.
- The first two SVD components are shown as the **NLP dimensions** (NLP Dim. 1, NLP Dim. 2), giving a 2D map of semantic similarity.
- The vertical axis uses the **project value (log scale)** to highlight the spread in construction costs.

Use the 3D view to rotate/zoom and inspect clusters. Hover to see **Permit ID**, coordinates, and project value.
"""
)

# ---------- Data load ----------
DATA_PATH = r"C:\Users\emshe\Desktop\BRAINSTATION\CAPSTONE\GIT_REPO\DEMO\data\vis_clusters_builds.csv"


if not os.path.exists(DATA_PATH):
    st.error(f"Data file not found:\n`{DATA_PATH}`")
    st.stop()

emb = load_vis_clusters(DATA_PATH)

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
fig = plot_clusters_3d(emb, permit_type="builds")
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
    "Z-axis ticks show **only** powers of 10."
)

# ---------- Cluster Summary ----------
st.markdown("---")
st.subheader("Agglomerative Clustering Results — New Building Permits")
st.markdown("Below is a summary of the 8 clusters, their defining characteristics, and interpretations.")

st.markdown(
    """
##### Cluster 0 — Small Detached & Duplex Mix
- **Size / Share:** 1,924 permits (20.3%)
- **Avg Project Value:** **$657,475**
- **Top Tokens:** house, face, park, expose, sprinklered, garage
- **Features:** Mix of single-detached homes and duplexes, with some laneway houses.
- **Interpretation:** **Moderate-value detached/duplex housing**, often with fire-safety and exterior features.

##### Cluster 1 — Large Multi-Dwelling Projects
- **Size / Share:** 47 permits (0.5%)
- **Avg Project Value:** **$107,774,490**
- **Top Tokens:** unit, park, build, suite, floor, parking
- **Features:** Almost entirely multiple dwellings, very high value.
- **Interpretation:** **Major residential complexes** (condos/high-rises), extreme outliers in value.

##### Cluster 2 — Mid-Value Family Housing
- **Size / Share:** 1,690 permits (17.9%)
- **Avg Project Value:** **$1,627,255**
- **Top Tokens:** unit, park, family, garage, cellar
- **Features:** Mix of single-detached and multiple dwellings, with family-oriented tokens.
- **Interpretation:** **Mid- to high-value detached or small multi-unit family housing.**

##### Cluster 3 — Laneway Houses (Lower Value)
- **Size / Share:** 1,814 permits (19.2%)
- **Avg Project Value:** **$239,726**
- **Top Tokens:** house, laneway, laneway house, law, construct
- **Features:** Nearly all laneway houses, very low project values.
- **Interpretation:** **Small-scale laneway construction**, low cost per project.

##### Cluster 4 — Numbered Suites & Laneways
- **Size / Share:** 1,078 permits (11.4%)
- **Avg Project Value:** **$244,457**
- **Top Tokens:** number, suite, build, house, principal, laneway
- **Features:** Laneway and small detached projects with heavy suite/number references.
- **Interpretation:** **Small dwellings with suites or laneway connections**, low-mid value.

##### Cluster 5 — Duplexes with Secondary Suites
- **Size / Share:** 1,468 permits (15.5%)
- **Avg Project Value:** **$886,224**
- **Top Tokens:** suite, number, build, post, floor, basement
- **Features:** High prevalence of duplexes and detached houses with secondary suites.
- **Interpretation:** **Moderate-value duplex housing** with many suites and basement units.

##### Cluster 6 — Detached with Suites
- **Size / Share:** 1,213 permits (12.8%)
- **Avg Project Value:** **$942,246**
- **Top Tokens:** locate, suite, unit, secondary, basement, address
- **Features:** Detached homes with a high share of secondary suites.
- **Interpretation:** **Detached housing stock with basement/secondary suites**, solid mid-value.

##### Cluster 7 — Large Multi-Unit Midrise Projects
- **Size / Share:** 228 permits (2.4%)
- **Avg Project Value:** **$27,716,589**
- **Top Tokens:** unit, park, build, floor, parking, garage
- **Features:** Predominantly multiple dwellings, high project value.
- **Interpretation:** **Large multi-unit midrise developments**, substantial project costs.
"""
)
