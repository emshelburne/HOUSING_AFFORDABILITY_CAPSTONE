# streamlit_page: Cluster Explorer - Demos

import os
import pandas as pd
import streamlit as st

from utils.figures import plot_clusters_3d
from utils.load_data import load_vis_clusters

# ---------- Page Header ----------
st.header("Cluster Explorer: Demolitions")

# ---------- Intro / Method blurb ----------
st.markdown(
    """
This page explores patterns in **demolition permits** using an unsupervised ML pipeline:

- We applied **Agglomerative Clustering** on engineered features (including text features from permit descriptions).
- Text features were embedded via **TF–IDF** (Term Frequency-Inverse Document Frequency)  and then **SVD** (Singular Value Decomposition), a dimensionality reducer.
- The first two SVD components are shown as the **NLP dimensions** (NLP Dim. 1, NLP Dim. 2), giving a 2D map of semantic similarity.
- The vertical axis uses the **project value (log scale)** to highlight the spread in construction costs.

Use the 3D view to rotate/zoom and inspect clusters. Hover to see **Permit ID**, coordinates, and project value.
"""
)

# ---------- Data load ----------
DATA_PATH = r"C:\Users\emshe\Desktop\BRAINSTATION\CAPSTONE\GIT_REPO\DEMO\data\vis_clusters_demos.csv"


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
fig = plot_clusters_3d(emb, permit_type="demolitions")
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
st.subheader("Agglomerative Clustering Results — Demolition / Deconstruction Permits (4 Clusters)")
st.markdown("Below is a summary of the 4 clusters, their defining characteristics, and interpretations.")

st.markdown(
    """
##### Cluster 0 — Deconstruction & Recycling (Higher Value)
- **Size / Share:** 2,465 permits (43.1%)
- **Avg Project Value:** **$34,394**
- **Top Tokens:** deconstruction, demolition, recycle, low demolish, green, grade
- **Features:** Mix of single-detached and some multiple dwellings; emphasis on recycling and deconstruction.
- **Interpretation:** **Moderately higher-value demolitions** with sustainability and material recovery focus.

##### Cluster 1 — Standard Family House Demolitions
- **Size / Share:** 1,462 permits (25.6%)
- **Avg Project Value:** **$17,017**
- **Top Tokens:** family building, low demolish, recycling
- **Features:** Predominantly single-detached houses, some duplexes with suites.
- **Interpretation:** **Typical demolitions of small family homes**, low-value and straightforward.

##### Cluster 2 — Large Multi-Dwelling Demolitions
- **Size / Share:** 3 permits (0.1%)
- **Avg Project Value:** **$4,648,644**
- **Top Tokens:** demolition, new, build, basement, mixed, law
- **Features:** Multiple dwellings only; extremely high-value.
- **Interpretation:** **Rare, large-scale demolition projects**, e.g. apartments or mixed-use complexes.

##### Cluster 3 — Green Deconstruction
- **Size / Share:** 1,784 permits (31.2%)
- **Avg Project Value:** **$16,975**
- **Top Tokens:** mean, deconstruction, building mean, family building, low demolish, green
- **Features:** Detached houses and duplexes; heavy references to “econstruction,” recycling, and green compliance.
- **Interpretation:** **Eco-focused deconstruction projects**, standard single-house demolitions framed as green/eco-friendly.
"""
)
