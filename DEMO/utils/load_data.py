import json
import pandas as pd
import geopandas as gpd
import streamlit as st
from typing import Tuple

# ---------- Permits ----------



@st.cache_data(show_spinner=False)
def get_permits(path: str) -> pd.DataFrame:
    df = load_permits(path)

    # Ensure expected columns exist and dtypes are friendly
    expected = [
        "permit_id",
        "issue_date",
        "project_description",
        "nbhd",
        "lon",
        "lat",
        "type",
        "cluster",
        "cluster_label",
        "project_value",
    ]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    # Parse dates if needed
    if not pd.api.types.is_datetime64_any_dtype(df["issue_date"]):
        df["issue_date"] = pd.to_datetime(df["issue_date"], errors="coerce")

    # Normalize/pretty project types for display
    # Map common short codes to human-friendly labels
    type_map = {
        "demo": "Demolition",
        "demolition": "Demolition",
        "reno": "Renovation",
        "renovation": "Renovation",
        "build": "Build",
        "new_build": "Build",
        "new": "Build",
    }
    df["type_pretty"] = (
        df["type"].astype(str).str.strip().str.lower().map(type_map).fillna(
            df["type"].astype(str).str.strip().str.title()
        )
    )

    return df

def load_corr_results(path: str) -> pd.DataFrame:
    """
    Load correlation results from CSV or Parquet file.

    Expected columns:
      - x, econ, lead, corr, pval, pval_adj, n, method
    """
    if path.endswith(".csv"):
        df = pd.read_csv(path)
    elif path.endswith(".parquet"):
        df = pd.read_parquet(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")

    # Basic sanity checks
    required = {"x", "econ", "lead", "corr", "pval_adj"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


@st.cache_data(show_spinner=False)
def load_vis_clusters(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


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
def load_geojson(path: str, id_col: str = "nbhd"):
    
    """
    Load a GeoJSON file and return (geojson_dict, geodataframe).
    """

    gdf = gpd.read_file(path)

    # Ensure CRS so downstream code doesn't error
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326", allow_override=True)

    # Keep a lean copy for the geojson (id + geometry) if possible
    if id_col in gdf.columns:
        gdf = gdf.copy()
        gdf[id_col] = gdf[id_col].astype(str)
        geojson_dict = json.loads(gdf[[id_col, "geometry"]].to_json())
    else:
        geojson_dict = json.loads(gdf.to_json())
    
    return geojson_dict, gdf

