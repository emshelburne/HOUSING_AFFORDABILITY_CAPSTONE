# streamlit_app: Home Page


# Uncomment below for tests

# Boot diagnostic
# import os, sys, logging
# os.environ.setdefault("GEOPANDAS_IO_ENGINE", "pyogrio")
# os.environ.setdefault("PYTHONUNBUFFERED", "1")  # flush prints to logs
# logging.basicConfig(level=logging.INFO)
# print("Boot: reached top of Home_Page.py", file=sys.stderr, flush=True)


import streamlit as st

# must be the very first Streamlit command
st.set_page_config(
    page_title="Vancouver Housing Permits & Rental Market Explorer",
    layout="wide",
    initial_sidebar_state="expanded"  # optional
)



st.title("Vancouver Housing Permits & Rental Market Explorer")

st.markdown("""
This interactive app explores how patterns in building, demolition, and renovation permits relate to Vancouver’s rental housing market. 
The project was inspired in part by the **Broadway Plan**—a major (and controversial) city initiative to redevelop the Broadway corridor 
with high-density housing, raising important questions about affordability and neighborhood change.

---

### Project Overview
We collected permit data from the City of Vancouver and economic indicators (rents, vacancy rates) from CMHC. 
Using four clustering algorithms—**K-Means, Gaussian Mixture, HDBSCAN, and Agglomerative**—we found that 
**Agglomerative Clustering** best captured meaningful patterns across permit descriptions. 
To measure how development intensity varies across space and time, we introduced the **NFiCF metric** 
(Neighborhood Fraction in Cluster Frequency). We then tested for correlations between cluster intensity 
and renter-focused metrics such as average and median rents and vacancy rates.

- All monetary values are CPI-adjusted to **2024 CAD**.  
- All correlation results should be viewed as **exploratory**—suggestive but not causal.  

---

### App Features
- **Geographic Visualizer**: Animated maps overlaying monthly permit activity on neighborhoods 
  colored by rent or vacancy metrics.  
- **Neighborhood Spotlight**: Select a neighborhood to see animated cluster breakdowns alongside 
  trends in local rents and vacancy.  
- **Cluster Visualizers**: Explore the defining features and interpretations of clusters for 
  **Builds, Renovations, and Demolitions**.  
- **Correlation Summary**: Review our key findings linking development clusters to rental outcomes, 
  with expandable explanations and bar-chart visualizations.  
- **Permit Lookup Tool**: Search and inspect details of specific permits, with sensitive information anonymized.  
""")
