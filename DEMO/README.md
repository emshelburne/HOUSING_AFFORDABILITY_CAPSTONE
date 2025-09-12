
# Vancouver Development Explorer (Streamlit Skeleton)

This is a minimal scaffold to help you start your Streamlit app quickly.

## Quickstart
```bash
# 1) Create & activate a virtual env (conda or venv)
pip install -r requirements.txt

# 2) Run the app
streamlit run app.py
```

## Project layout
```
app.py                     # Home page + top-level navigation
pages/
  01_Map.py                # Choropleth + permit overlay
  02_Neighbourhood.py      # Drill-down charts for selected neighbourhood
  03_Clusters.py           # 3D cluster explorer
utils/
  load_data.py             # data loading + caching
  figures.py               # plotly figure helpers
components/                # reusable UI bits (optional)
data/                      # put your parquet/csv/geojson here
```
Replace the placeholder loaders with your actual datasets/columns.
