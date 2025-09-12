import streamlit as st
from utils.load_data import load_geojson
from utils.figures import map_boundaries

st.header("Neighbourhood Boundaries Test")

geo_path = r"C:\Users\emshe\Desktop\BRAINSTATION\CAPSTONE\GIT_REPO\DEMO\data\nbhds.geojson"
geojson = load_geojson(geo_path)

fig = map_boundaries(geojson, title="Vancouver Neighbourhoods")
st.plotly_chart(fig, use_container_width=True)
