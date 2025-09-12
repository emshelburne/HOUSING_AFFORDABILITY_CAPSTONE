import json
import pandas as pd
import streamlit as st
from typing import Tuple

# ---------- Permits ----------

@st.cache_data
def load_permits(path: str) -> pd.DataFrame:
    """
    Loads permits from Parquet/CSV.
    Works with either the full per-type files (builds/demos/renos)
    or the lean combined 'permits_all.parquet'.

    Normalizes:
      - issue_date -> datetime64[ns]
      - adds 'year' convenience column
    """

    df = pd.read_parquet(path) if path.lower().endswith(".parquet") else pd.read_csv(path)
    if "issue_date" in df.columns:
        df["issue_date"] = pd.to_datetime(df["issue_date"], errors="coerce")
        df["year"] = df["issue_date"].dt.year

    return df


# ---------- Economic metrics ----------

@st.cache_data
def load_econ(path: str) -> pd.DataFrame:
    """
    Loads the economic metrics dataframe (wide format as saved).
    Expected columns:
      - nbhd
      - year
      - metric columns (e.g. avg_rent_studio, vacancy_rate_total, etc.)
    """
    df = pd.read_parquet(path) if path.lower().endswith(".parquet") else pd.read_csv(path)

    # Ensure year is numeric
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    return df


# ---------- GeoJSON ----------

@st.cache_data
def load_geojson(path: str) -> dict:
    """
    Loads a GeoJSON file. If your GeoDataFrame column was 'nbhd',
    the feature key will be 'properties.nbhd' (use this in Plotly).
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
