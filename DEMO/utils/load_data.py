import json
import pandas as pd
import geopandas as gpd
import streamlit as st
from typing import Tuple
from pathlib import Path
from urllib.parse import urlparse
import os


'''
This file contains functions to load data for this streamlit app
'''

# ---- secrets helper ----
def _sget(section: str, key: str, default=None):
    try:
        return st.secrets[section][key]
    except Exception:
        return default

# ---- find the top-most repo root (prefer folder with .git) ----
def _repo_root() -> Path:
    here = Path(__file__).resolve().parent
    git_root = None
    marker_root = None
    for base in [here, *here.parents]:
        if (base / ".git").exists():
            git_root = base        # keep walking to get the TOP-most .git
        markers = ("pages", ".streamlit", "requirements.txt", "pyproject.toml", "setup.cfg")
        if any((base / m).exists() for m in markers):
            marker_root = base
    return git_root or marker_root or here.parents[-1]

# ---- find a named directory by walking UPWARD ----
def _find_upward_dir(name: str) -> Path | None:
    here = Path(__file__).resolve().parent
    for base in [here, *here.parents]:
        d = base / name
        if d.is_dir():
            return d.resolve()
    return None

# ---- main data-dir resolver (prefers APP_DATA) ----
def _data_dir() -> Path:
    override = os.environ.get("DATA_DIR") or _sget("paths", "DATA_DIR")  # e.g. "APP_DATA"
    if override:
        p = Path(override)
        if p.is_absolute():
            return p
        # If relative, first try to find that folder upward (handles APP_DATA at repo root)
        found = _find_upward_dir(override)
        if found:
            return found
        # Else anchor to TOP-most repo root
        return (_repo_root() / override).resolve()

    # No override: search upward for common data dirs (case-sensitive first)
    for name in ("APP_DATA", "app_data", "DATA", "data", "DEMO/data"):
        found = _find_upward_dir(name)
        if found:
            return found

    # Last resort: REPO_ROOT/APP_DATA (may not exist)
    return (_repo_root() / "APP_DATA").resolve()

def _pick_existing(data_dir: Path, preferred: str, alts: list[str] | None = None) -> Path:
    """Return the first existing file among preferred + alts.
       If name has no extension, also try .csv and .parquet variants."""
    candidates = []
    if preferred:
        candidates.append(preferred)
        base = Path(preferred).name
        if "." not in base:  # no extension given
            candidates += [preferred + ".csv", preferred + ".parquet"]
    for name in (alts or []):
        candidates.append(name)
        base = Path(name).name
        if "." not in base:
            candidates += [name + ".csv", name + ".parquet"]

    for name in candidates:
        p = data_dir / name
        if p.exists():
            return p
    raise FileNotFoundError(f"None of these exist under {data_dir}:\n  " + "\n  ".join(candidates))

def resolve_sources():
    if _sget("remote", "USE_REMOTE", False):
        # allow remote for every file we use
        return {
            "GEOJSON": _sget("remote", "GEOJSON_URL"),
            "ECON":    _sget("remote", "ECON_URL"),
            "DEMOS":   _sget("remote", "DEMOS_URL"),
            "RENOS":   _sget("remote", "RENOS_URL"),
            "BUILDS":  _sget("remote", "BUILDS_URL"),
            "PERMITS": _sget("remote", "PERMITS_URL"),
            "KENDALL": _sget("remote", "KENDALL_URL"),
            "SPEARMAN":_sget("remote", "SPEARMAN_URL"),
            "VIS_CLUSTERS_BUILDS": _sget("remote", "VIS_CLUSTERS_BUILDS_URL"),
            "VIS_CLUSTERS_DEMOS":  _sget("remote", "VIS_CLUSTERS_DEMOS_URL"),
            "VIS_CLUSTERS_RENOS":  _sget("remote", "VIS_CLUSTERS_RENOS_URL"),
            "DATA_LINKS": _sget("remote", "DATA_LINKS_URL"),
        }

    d = _data_dir()
    # filenames can be overridden in secrets -> [files]
    files = {
        "GEOJSON": _sget("files","GEOJSON","nbhds.geojson"),
        "ECON":    _sget("files","ECON","econ.parquet"),
        "DEMOS":   _sget("files","DEMOS","demos.parquet"),
        "RENOS":   _sget("files","RENOS","renos.parquet"),
        "BUILDS":  _sget("files","BUILDS","builds.parquet"),
        "PERMITS": _sget("files","PERMITS","permits.parquet"),
        "KENDALL": _sget("files","KENDALL","kendall.csv"),
        "SPEARMAN":_sget("files","SPEARMAN","spearman.csv"),
        "VIS_CLUSTERS_BUILDS": _sget("files","VIS_CLUSTERS_BUILDS","vis_clusters_builds.csv"),
        "VIS_CLUSTERS_DEMOS":  _sget("files","VIS_CLUSTERS_DEMOS","vis_clusters_demos.csv"),
        "VIS_CLUSTERS_RENOS":  _sget("files","VIS_CLUSTERS_RENOS","vis_clusters_renos.csv"),
        "DATA_LINKS": _sget("files","DATA_LINKS","data_links.md"),
    }

    return {
        "GEOJSON": _pick_existing(d, files["GEOJSON"], alts=["neighbourhoods.geojson","nbhds.json"]),
        "ECON":    _pick_existing(d, files["ECON"],    alts=["econ.csv"]),
        "DEMOS":   _pick_existing(d, files["DEMOS"],   alts=["demos.csv"]),
        "RENOS":   _pick_existing(d, files["RENOS"],   alts=["renos.csv"]),
        "BUILDS":  _pick_existing(d, files["BUILDS"],  alts=["builds.csv"]),
        "PERMITS": _pick_existing(d, files["PERMITS"], alts=["permits_all.parquet","all_permits.parquet","permits.csv"]),
        "KENDALL": _pick_existing(d, files["KENDALL"], alts=[]),
        "SPEARMAN":_pick_existing(d, files["SPEARMAN"],alts=[]),
        "VIS_CLUSTERS_BUILDS": _pick_existing(d, files["VIS_CLUSTERS_BUILDS"], alts=[]),
        "VIS_CLUSTERS_DEMOS":  _pick_existing(d, files["VIS_CLUSTERS_DEMOS"],  alts=[]),
        "VIS_CLUSTERS_RENOS":  _pick_existing(d, files["VIS_CLUSTERS_RENOS"],  alts=[]),
        "DATA_LINKS": _pick_existing(d, files["DATA_LINKS"], alts=["data_links.txt","data_links.csv"]),
    }




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
    path = str(path)  
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
    path = str(path)
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
    path = str(path)
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

