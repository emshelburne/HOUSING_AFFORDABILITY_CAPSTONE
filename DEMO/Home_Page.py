# streamlit_app: Home Page

import streamlit as st

st.set_page_config(page_title="Vancouver Development Explorer", layout="wide")
st.title("Vancouver Development Explorer")
st.markdown(
    """
Use the tabs in the sidebar to explore:
- **Map**: neighbourhood choropleth of economic metrics with optional permit overlay.
- **Neighbourhood**: drill-down charts for a selected area.
- **Clusters**: 3D cluster explorer & summary stats.
"""
)
