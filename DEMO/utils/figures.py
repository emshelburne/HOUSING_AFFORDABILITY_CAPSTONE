import matplotlib.pyplot as plt
import seaborn as sns
from itertools import product

import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd
import geopandas as gpd
import streamlit as st
from typing import Tuple
import numpy as np
import re
import math 


'''
This file contains function definitions for generating visualizations for this streamlit app
'''


# Function to plot correlation bar chart

# --- helpers
def _titleize_no_underscores(s: str) -> str:
    """Replace underscores with spaces and Title Case."""
    return s.replace("_", " ").title()

def _pretty_x(x: str) -> str:
    """
    Examples:
      'nficf_build_c0'  -> 'Build C0'
      'nficf_demo_c12'  -> 'Demo C12'
      'nficf_reno_c3'   -> 'Reno C3'
    """
    if not isinstance(x, str):
        return str(x)
    s = x
    # drop 'nficf_' prefix (case-insensitive)
    s = re.sub(r"^nficf_", "", s, flags=re.IGNORECASE)
    # Force Build/Demo/Reno capitalization regardless of input case
    s = re.sub(r"\b(build|demo|reno)\b", lambda m: m.group(1).title(), s, flags=re.IGNORECASE)
    # Force cluster label to uppercase C#
    s = re.sub(r"\bc(\d+)\b", lambda m: f"C{m.group(1)}", s, flags=re.IGNORECASE)
    # Remove underscores
    s = s.replace("_", " ")
    return s

def _pretty_pair(x: str, econ: str, lead) -> str:
    lead = int(lead)
    lag_label = f"Lag: {lead} Year" + ("" if lead == 1 else "s")
    return f"{_pretty_x(x).title()} → {_titleize_no_underscores(econ)} ({lag_label})"

# --- main
def plot_corr_bars(
    df: pd.DataFrame,
    top_n: int = 40,
    title: str = "Suggestive Correlations",
    method: str | None = None,   # NEW: 'spearman' or 'kendall' (optional)
):
    d = df.copy()
    d = d.dropna(subset=["corr", "pval_adj"])

    # Build pretty pair label
    d["pair"] = d.apply(lambda r: _pretty_pair(r["x"], r["econ"], r["lead"]), axis=1)

    # Sort by absolute correlation and keep top N
    d = d.sort_values("corr", key=lambda s: s.abs(), ascending=False).head(top_n)

    # Preserve order on x-axis
    d["pair"] = pd.Categorical(d["pair"], categories=d["pair"], ordered=True)

    # Prepare customdata for hover
    d["_pair_for_hover"] = d["pair"]
    d["_pval_adj_for_hover"] = d["pval_adj"]

    # Map method to full name for title suffix
    method_map = {
        None: "",
        "spearman": " (Spearman's Rank Correlation Coefficient)",
        "kendall": " (Kendall's Rank Correlation Coefficient)",
    }
    title_suffix = method_map.get((method or "").lower(), "")
    full_title = f"{title}{title_suffix}"

    fig = px.bar(
        d,
        x="pair",
        y="corr",
        color="corr",
        color_continuous_scale="RdBu",
        title=full_title
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>" +
            "Correlation: %{y:.3f}<br>" +
            "Adjusted p-value: %{customdata[1]:.3f}<extra></extra>"
        ),
        customdata=d[["_pair_for_hover", "_pval_adj_for_hover"]].to_numpy()
    )

    # Style
    fig.update_layout(
        xaxis_title='',
        yaxis_title="Correlation",
        bargap=0.2,
        height=600,
        margin=dict(l=40, r=20, t=60, b=120),
        coloraxis_colorbar=dict(title="")   # <--- removes "corr" label
    )
    fig.update_xaxes(tickangle=45)

    # Zero line
    fig.add_hline(y=0, line_width=1, line_color="gray", opacity=0.6)

    d.drop(columns=["_pair_for_hover", "_pval_adj_for_hover"], inplace=True)

    return fig


# Define function to generate 3D scatter plot of clusters (pretty hover + Permit ID)

def plot_clusters_3d(emb, permit_type='builds'):
    """
    3D cluster viz with:
      - Numeric legend ordering for clusters
      - Discrete colors
      - Larger markers (affects legend symbol size, too)
      - Pretty hover with Permit ID
      - Log z-axis showing ONLY powers of 10 (no 2,3,4,... minor ticks)
    """
    emb = emb.copy()

    # Ensure cluster is string/categorical and sort numerically
    emb["cluster"] = emb["cluster"].astype(str)
    try:
        cat_order = [str(k) for k in sorted({int(x) for x in emb["cluster"]})]
    except ValueError:
        cat_order = sorted(emb["cluster"].unique(), key=lambda s: (len(s), s))
    emb["cluster"] = pd.Categorical(emb["cluster"], categories=cat_order, ordered=True)

    # Pretty labels
    labels = {col: col.replace("_", " ").title() for col in emb.columns}
    labels.update({
        "nlp_x": "NLP Dim. 1",
        "nlp_y": "NLP Dim. 2",
        "project_value": "Project Value",
        "cluster": "Cluster",
        "permit_id": "Permit ID",
    })

    # Build figure
    fig = px.scatter_3d(
        emb,
        x="nlp_x",
        y="nlp_y",
        z="project_value",
        color="cluster",
        hover_name="permit_id",
        hover_data={
            "project_value": ":,.0f",
            "nlp_x": ":.3f",
            "nlp_y": ":.3f",
            "cluster": True,
        },
        labels=labels,
        category_orders={"cluster": cat_order},
        title=f"3D Visualization of {permit_type.title()} Clustering",
        opacity=0.85,
        color_discrete_sequence=px.colors.qualitative.Prism,  # pick any qualitative palette you like
    )

    # Larger markers (also enlarges legend symbols for scatter3d)
    fig.update_traces(marker=dict(size=6))

    # ---- z-axis ticks: ONLY powers of 10 within data range ----
    z = emb["project_value"].to_numpy()
    z = z[np.isfinite(z)]
    z_pos = z[z > 0]  # log scale requires positive values

    zaxis_dict = dict(
        title=f'{labels["project_value"]} (log scale)',
        type="log",
    )

    if z_pos.size > 0:
        emin = int(np.floor(np.log10(np.min(z_pos))))
        emax = int(np.ceil(np.log10(np.max(z_pos))))
        tickvals = [10 ** i for i in range(emin, emax + 1)]
        ticktext = [f"10^{i}" for i in range(emin, emax + 1)]
        zaxis_dict.update({
            "tickvals": tickvals,
            "ticktext": ticktext,
            # Optional cosmetics:
            "ticks": "outside",
            "ticklen": 6,
            "tickwidth": 1,
        })
    # else: leave default ticks (e.g., if all values are non-positive or identical)

    fig.update_layout(
        scene=dict(
            xaxis_title=labels["nlp_x"],
            yaxis_title=labels["nlp_y"],
            zaxis=zaxis_dict,
        ),
        legend_title_text=labels["cluster"],
        legend=dict(itemsizing="constant"),
        hoverlabel=dict(namelength=-1),
    )

    return fig




# Function to get nbhd specific bar chart animation

# Compact value labels
def compact_no_currency(x: float) -> str:
    ax = abs(x)
    if ax >= 1_000_000_000:  return f"{x/1_000_000_000:.2f}B"
    if ax >= 1_000_000:      return f"{x/1_000_000:.2f}M"
    if ax >= 1_000:          return f"{x/1_000:.2f}K"
    return f"{x:,.0f}"

# For bar-top text (still CAD-prefixed)
def compact_cad(x: float) -> str:
    ax = abs(x)
    if ax >= 1_000_000_000:  return f"C${x/1_000_000_000:.2f}B"
    if ax >= 1_000_000:      return f"C${x/1_000_000:.2f}M"
    if ax >= 1_000:          return f"C${x/1_000:.2f}K"
    return f"C${x:,.0f}"

def animated_cluster_bars(
    permits_df: pd.DataFrame,
    neighborhood: str = "Vancouver",      # "Vancouver" = all neighborhoods
    permit_category: str = "builds",      # {"builds","renos","demos"}
    pace: str = "medium"                  # {"slow","medium","fast"}
):
    """
    Animated monthly column chart of permit counts by cluster (x = cluster label, y = count).
    """

    if permits_df.empty:
        raise ValueError("permits_df is empty.")

    # ---- inputs/pace
    cat_map = {"builds": ["build","new_build","new","builds"],
               "renos":  ["reno","renovation","renos"],
               "demos":  ["demo","demolition","demos"]}
    cat_key = permit_category.strip().lower()
    if cat_key not in cat_map:
        raise ValueError("permit_category must be one of {'builds','renos','demos'}.")
    
    pace = pace.strip().lower()
    pace_map = {"slow": 1500, "medium": 1000, "fast": 500}

    if pace not in pace_map:
        raise ValueError("pace must be one of {'slow','medium','fast'}.")

    # ---- FIXED label universes per category (ensures full x each frame)
    label_universe = {
        "builds": [f"B{i}" for i in range(8)],   # B0..B7
        "renos":  [f"R{i}" for i in range(6)],   # R0..R5
        "demos":  [f"D{i}" for i in range(4)],   # D0..D3
    }
    labels_all = label_universe[cat_key]
    prefix = labels_all[0][0]  # "B"|"R"|"D"

    df = permits_df.copy()
    required = {"issue_date","type","nbhd","project_value"}
    miss = required - set(df.columns)
    if miss:
        raise ValueError(f"permits_df is missing columns: {miss}")

    # Prefer labeled column; fall back to numeric cluster and map to prefix+num
    cluster_col = "cluster_label" if "cluster_label" in df.columns else \
                  ("cluster" if "cluster" in df.columns else None)
    if cluster_col is None:
        raise ValueError("permits_df must contain either 'cluster_label' or 'cluster'.")

    # Dates & filters
    df["issue_date"] = pd.to_datetime(df["issue_date"], errors="coerce")
    df = df.dropna(subset=["issue_date"])
    if neighborhood.lower() != "vancouver":
        df = df[df["nbhd"].astype(str).str.lower() == neighborhood.strip().lower()]

    df["type_norm"] = df["type"].astype(str).str.lower().str.strip()
    df = df[df["type_norm"].isin(cat_map[cat_key])]
    if df.empty:
        raise ValueError("No permits found for the given filters.")

    # Normalize cluster labels to match fixed universe (e.g., "b3 " -> "B3")
    if cluster_col == "cluster_label":
        df[cluster_col] = (
            df[cluster_col].astype(str).str.strip().str.upper()
        )
    else:
        # cluster is numeric or string number; cast to int if possible, then prefix
        nums = pd.to_numeric(df[cluster_col], errors="coerce").astype("Int64")
        df["__cluster_label"] = nums.map(lambda v: f"{prefix}{int(v)}" if pd.notna(v) else None)
        cluster_col = "__cluster_label"

    # Coerce anything not in universe to NaN so it won't pollute categories
    df.loc[~df[cluster_col].isin(labels_all), cluster_col] = None

    # ---- aggregate
    df["month"] = df["issue_date"].dt.to_period("M").dt.to_timestamp()
    df["project_value"] = pd.to_numeric(df["project_value"], errors="coerce").fillna(0.0)

    # ===== build a continuous monthly range so empty months still render =====
    first_month = df["month"].min()
    last_month  = df["month"].max()
    # use start-of-month frequency to get every month in the span
    all_months = pd.date_range(first_month, last_month, freq="MS").to_pydatetime().tolist()
    # ================================================================================
    
    agg = (df.dropna(subset=[cluster_col])
             .groupby(["month", cluster_col], dropna=False)
             .agg(count=("issue_date","size"),
                  sum_value=("project_value","sum"))
             .reset_index())

    # Build full month×fixed-label grid and fill missing with zeros
    full_grid = pd.DataFrame(
        [{"month": m, cluster_col: c} for m, c in product(all_months, labels_all)]
    )
    data_full = (full_grid.merge(agg, on=["month", cluster_col], how="left")
                           .fillna({"count": 0, "sum_value": 0.0}))

    # Lock categorical order to the fixed universe
    data_full[cluster_col] = pd.Categorical(data_full[cluster_col],
                                            categories=labels_all, ordered=True)

    # ---- precomputed labels (helpers live outside)
    data_full["sum_value_label"] = data_full["sum_value"].apply(compact_cad)
    data_full["sum_value_compact_nc"] = data_full["sum_value"].apply(compact_no_currency)
    data_full["month_str"] = pd.to_datetime(data_full["month"]).dt.strftime("%b %Y")

    # ---- figure


    # stable color map for clusters
    palette = (
        px.colors.qualitative.Dark24
        + px.colors.qualitative.Set3
        + px.colors.qualitative.Pastel  # plenty; we only need first len(labels_all)
    )
    color_map = {lab: palette[i % len(palette)] for i, lab in enumerate(labels_all)}

    fig = px.bar(
        data_full,
        x=cluster_col, y="count",
        # NOTE: do NOT pass color=cluster_col (that causes grouped skinny bars)
        animation_frame="month",
        category_orders={cluster_col: labels_all},
        labels={"count":"Permits", cluster_col:"Cluster", "month":"Month"},
        title=f"Monthly {permit_category.capitalize()} Permits by Cluster"
              + ("" if neighborhood.lower()=="vancouver" else f" — {neighborhood}"),
        text="sum_value_label",
        custom_data=["month_str","sum_value_compact_nc"]
    )

    # Apply per-point colors to the single trace in the base data
    if fig.data:
        x_vals = list(fig.data[0].x)
        fig.data[0].marker.update(color=[color_map.get(x, "#888") for x in x_vals])

    # And to each animation frame (the frame has a single trace too)
    for fr in (fig.frames or []):
        if fr.data:
            x_vals = list(fr.data[0].x)
            fr.data[0].marker = fr.data[0].marker or {}
            fr.data[0].marker.update(color=[color_map.get(x, "#888") for x in x_vals])

    hover_tmpl = (
        "<b>%{x}</b><br>"
        "Month: %{customdata[0]}<br>"
        "Permits: %{y}<br>"
        "Total Cost = %{customdata[1]}<extra></extra>"
    )
    fig.update_traces(textposition="outside", cliponaxis=False,
                      hovertemplate=hover_tmpl, showlegend=False)
    if fig.frames:
        for fr in fig.frames:
            for tr in fr.data:
                tr.hovertemplate = hover_tmpl
                tr.textposition = "outside"
                tr.cliponaxis = False
                tr.showlegend = False
    # fig = px.bar(
    #     data_full,
    #     x=cluster_col, y="count", color=cluster_col,
    #     animation_frame="month",
    #     category_orders={cluster_col: labels_all},  # fixed order
    #     labels={"count":"Permits", cluster_col:"Cluster", "month":"Month"},
    #     title=f"Monthly {permit_category.capitalize()} Permits by Cluster"
    #           + ("" if neighborhood.lower()=="vancouver" else f" — {neighborhood}"),
    #     text="sum_value_label",
    #     custom_data=["month_str","sum_value_compact_nc"]
    # )

    hover_tmpl = (
        "<b>%{x}</b><br>"
        "Month: %{customdata[0]}<br>"
        "Permits: %{y}<br>"
        "Total Cost = %{customdata[1]}<extra></extra>"
    )
    fig.update_traces(textposition="outside", cliponaxis=False,
                      hovertemplate=hover_tmpl, showlegend=False)
    if fig.frames:
        for fr in fig.frames:
            for tr in fr.data:
                tr.hovertemplate = hover_tmpl
                tr.textposition = "outside"
                tr.cliponaxis = False
                tr.showlegend = False

    # ---- slider labels: rename frames to 'Mon YYYY' and rebuild steps (like your map)
    name_map = {}
    for fr in fig.frames:
        orig = fr.name
        try:
            name_map[orig] = pd.to_datetime(orig).strftime("%b %Y")
        except Exception:
            name_map[orig] = str(orig)
    for fr in fig.frames:
        fr.name = name_map.get(fr.name, fr.name)

    if fig.layout.sliders:
        for slider in fig.layout.sliders:
            slider.currentvalue.prefix = "Month: "
            new_steps = []
            for step in slider.steps:
                args = step.args
                target = None
                if isinstance(args, (list, tuple)) and len(args) > 0:
                    a0 = args[0]
                    if isinstance(a0, (list, tuple)) and len(a0) > 0:
                        orig = a0[0]; target = [name_map.get(orig, orig)]
                    else:
                        orig = a0;    target = name_map.get(orig, orig)
                kwargs = args[1] if (isinstance(args, (list, tuple)) and len(args) > 1) else {"mode":"immediate"}
                step.args = (target, kwargs)
                step.label = name_map.get(step.label, step.label)
                new_steps.append(step)
            slider.steps = tuple(new_steps)

    # ---- Play/Pause buttons placed like your map
    frame_dur = pace_map[pace]
    trans_dur = int(0.6 * frame_dur)

    if not fig.layout.updatemenus:
        fig.update_layout(
            updatemenus=[{
                "type": "buttons",
                "showactive": True,
                "x": 0.02, "y": 0.02,
                "xanchor": "left", "yanchor": "bottom",
                "buttons": [
                    {
                        "label": "▶ Play",
                        "method": "animate",
                        "args": [None, {
                            "frame": {"duration": frame_dur, "redraw": True},
                            "transition": {"duration": trans_dur},
                            "fromcurrent": True
                        }]
                    },
                    {
                        "label": "⏸ Pause",
                        "method": "animate",
                        "args": [[None], {
                            "mode": "immediate",
                            "frame": {"duration": 0, "redraw": False},
                            "transition": {"duration": 0}
                        }]
                    }
                ]
            }]
        )

    else:
        for um in fig.layout.updatemenus:
            if um.buttons:
                for bt in um.buttons:
                    args = list(bt.args) if bt.args is not None else []
                    if len(args) >= 2 and isinstance(args[1], dict):
                        cfg = dict(args[1])
                        frame_cfg = dict(cfg.get("frame", {}))
                        frame_cfg.update({"duration": frame_dur, "redraw": True})
                        trans_cfg = dict(cfg.get("transition", {}))
                        trans_cfg.update({"duration": trans_dur})
                        cfg["frame"] = frame_cfg
                        cfg["transition"] = trans_cfg
                        args[1] = cfg
                        bt.args = tuple(args)

    # ---- layout/margins
    fig.update_layout(
        showlegend=False, bargap=0.15,
        xaxis_title="Cluster", yaxis_title="Permits",
        margin=dict(l=60, r=20, t=60, b=80),
        transition=dict(duration=frame_dur, easing="cubic-in-out"),
    )

    # Headroom for labels
    max_count = int(data_full["count"].max()) if len(data_full) else 1
    fig.update_yaxes(range=[0, max(1, max_count * 1.30)])

    subtitle = f"{permit_category.capitalize()} · " + ("All Vancouver" if neighborhood.lower()=="vancouver" else neighborhood)
    fig.add_annotation(xref="paper", yref="paper", x=0, y=1.08, showarrow=False,
                       text=subtitle, font=dict(size=12))

    return fig




# Define function to map feature prefix to color to enhance visualization interpretability

# Color mapping by prefix
prefix_colors = {
        "avg_rent": "tab:blue",
        "med_rent": "tab:green",
        "vacancy_rate": "tab:red",}

def color_for(col):

    """
    Define color mapping functin
    """
    
    for p, c in prefix_colors.items():
        if col.startswith(p):
            return c
    if col.endswith("_change"):
        return "gray"
    return "black"


# Define function to plot average economic metrics over time

def plot_economic_metrics_grid(df, nbhd = None):

    """
    Plot a grid of subplots for economic metrics over time, averaged across neighborhoods
    """

    # Filter by neighborhood if requested
    if nbhd is not None:
        subset = df[df["nbhd"] == nbhd].copy()
        if subset.empty:
            raise ValueError(f"No rows found for neighborhood: {nbhd!r}")
        title_prefix = f"Neighborhood: {nbhd.title()}"
    else:
        subset = df.copy()
        title_prefix = "All Neighborhoods"

    # Select metric columns: numeric, excluding identifiers and *_change
    exclude_cols = ["nbhd", "zone", "year"]
    metrics = [
        c for c in subset.columns
        if c not in exclude_cols
        and np.issubdtype(subset[c].dtype, np.number)
        and not c.endswith("_change")
    ]
    if not metrics:
        raise ValueError("No numeric metric columns found to plot.")

    # Aggregate by year
    yearly = subset.groupby("year", as_index=False)[metrics].mean().sort_values("year")

    # Grid setup
    n = len(metrics)
    ncols = 3
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(ncols * 4.5, nrows * 3),
        sharex=False
    )
    axes = np.array(axes).reshape(-1)
    
    years = yearly["year"].values

    # Plot
    for i, metric in enumerate(metrics):
        ax = axes[i]
        ax.plot(years, yearly[metric].values, marker="o", linewidth=1.5, color=color_for(metric))
        ax.set_title(metric.replace("_", " ").title(), fontsize=9)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_xlabel("Year")
        ax.set_xticks(years)
        ax.tick_params(axis="x", rotation=45)

    # Hide unused axes
    for j in range(len(metrics), len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(f"Economic Metrics Over Time — {title_prefix}", fontsize=12, y=0.995)
    fig.tight_layout(rect=[0, 0.0, 1, 0.97])

    return fig, axes





def map_boundaries(geojson: dict, title="Neighbourhood Boundaries"):

    """
    Draw neighbourhood boundaries from a GeoJSON.
    
    Parameters
    ----------
    geojson : dict
        Dictionary loaded from your nbhds.geojson
        (features should have 'properties.nbhd')
    title : str
        Plot title
    """

    # Extract neighbourhood names for dummy coloring
    nbhds = [feat["properties"]["nbhd"] for feat in geojson["features"]]
    df = {"nbhd": nbhds, "dummy": range(len(nbhds))}

    fig = px.choropleth_mapbox(
        data_frame=df,
        geojson=geojson,
        locations="nbhd",
        color="dummy",
        featureidkey="properties.nbhd",
        mapbox_style="carto-positron",
        center={"lat": 49.25, "lon": -123.1},
        zoom=10.5,
        opacity=0.6,
        title=title
    )
    fig.update_traces(marker_line_width=0.5, marker_line_color="black")
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

    return fig



# Define function to overlay economic choroplath and permits scatter plot




def monthly_permits_over_rent_map(
    econ_df: pd.DataFrame,     
    nbhds_gdf: gpd.GeoDataFrame,
    permits_df: pd.DataFrame, 
    metric: str = "avg_rent_total",
    color_scale: str = "RdYlGn_r",        # green=low, red=high
    animation_pace: str = "fast"          # 'fast' | 'medium' | 'slow'
):
    """
    Generate one animated map combining:
      - Choropleth polygons colored by a yearly economic metric 
      - Scatter points for permits per month (colored by cluster_label)
        with a palette chosen by permit 'type' (build/demo/reno)
    """
    # --- Copy to avoid altering originals
    econ = econ_df.copy()
    nb = nbhds_gdf.copy()
    per = permits_df.copy()

    # Ensure datetime
    per["issue_date"] = pd.to_datetime(per["issue_date"])

    # Restrict permits to <= 2024 (to match econ coverage)
    per = per[per["issue_date"].dt.year <= 2024].copy()

    # Ensure polygons in correct coordinate system
    if nb.crs is None:
        raise ValueError("nbhds_gdf has no CRS. Set nb.crs (e.g., EPSG:3857) before calling.")
    nb = nb.to_crs("EPSG:4326")

    # Determine single permit type (this visualizer only animates one type at a time)
    types_present = per["type"].dropna().unique().tolist() if "type" in per.columns else []
    permit_type = types_present[0] if types_present else "build"
    
    # All months present in permits
    months = per["issue_date"].dt.to_period("M").sort_values().unique()
    # Add a pretty Month label (e.g., "Jan 2021")
    months_df = pd.DataFrame({
        "frame": [str(m) for m in months],
        "year": [m.year for m in months],
        "Month": [m.to_timestamp().strftime("%b %Y") for m in months],
    })

    # Cross-join months and neighborhoods so polygons render every month
    base = months_df.assign(key=1).merge(nb[["nbhd"]].assign(key=1), on="key").drop(columns="key")

    # Bring in rent metric by nbhd and year, repeated for all months of that year
    if metric not in econ.columns:
        raise ValueError(f"Metric '{metric}' not found in econ_df.")
    econ_small = econ[["nbhd", "year", metric]].rename(columns={metric: "value"})
    poly_df = base.merge(econ_small, on=["nbhd", "year"], how="left")

    # Prepare polygons GeoJSON 
    nb_geojson = json.loads(nb[["nbhd", "geometry"]].to_json())

    # Global color range
    vmin = float(poly_df["value"].quantile(0.02))
    vmax = float(poly_df["value"].quantile(0.98))
    if not np.isfinite(vmin) or not np.isfinite(vmax) or vmin == vmax:
        vmin, vmax = 0.0, 1.0

    # Map center
    minx, miny, maxx, maxy = nb.total_bounds
    map_center = {"lat": (miny + maxy)/2, "lon": (minx + maxx)/2}

    # --- NEW: flip color scale for vacancy rates ---
    if isinstance(metric, str) and metric.lower().startswith("vacancy_rate"):
        color_scale = "RdYlGn"  # low = green (good), high = red (bad)
    # ----------------------------------------------

    # Build polygons figure (animated by month)
    metric_title = metric.replace('_',' ').title()
    fig_poly = px.choropleth_map(
        poly_df.sort_values(["frame", "nbhd"]),
        geojson=nb_geojson,
        locations="nbhd",
        featureidkey="properties.nbhd",
        color="value",
        animation_frame="frame",
        color_continuous_scale=color_scale,  
        range_color=[vmin, vmax],
        height=750,
        title=f"{metric_title} by Neighborhood (shaded) + {permit_type.title()} Permits (points)",
        # pass Month through to hover via custom data
        custom_data=["Month"]
    )
    fig_poly.update_layout(
        map_style="carto-positron",
        map_center=map_center,
        map_zoom=10,
        margin=dict(r=0, t=60, l=0, b=0),
        coloraxis_colorbar=dict(title=metric_title)
    )
    # Pretty polygon hover (base traces)
    poly_hover_tmpl = (
        "<b>%{location}</b><br>"
        "Month: %{customdata[0]}<br>"
        + metric_title + ": %{z:.2f}<extra></extra>"
    )
    fig_poly.update_traces(
        marker_line_width=0.6,
        marker_line_color="black",
        marker_opacity=0.6,   # <-- NEW: make polygons translucent
        hovertemplate=poly_hover_tmpl
    )

    # Monthly frame key
    per["frame"] = per["issue_date"].dt.to_period("M").astype(str)
    # Pretty month for points hover
    per["Month"] = per["issue_date"].dt.strftime("%b %Y")

    # Size by project value (with soft clipping to keep dots reasonable)
    q99 = per["project_value"].quantile(0.99) if "project_value" in per.columns else None
    if q99 and np.isfinite(q99):
        per["project_value_vis"] = per["project_value"].clip(upper=float(q99))
    else:
        per["project_value_vis"] = per.get("project_value", 1.0)

    # Create pretty label for project value in hover (does not affect size)
    if "project_value" in per.columns:
        per["Project Value"] = per["project_value"]

    # Color by cluster_label with palette chosen by permit type
    if "cluster_label" in per.columns:
        color_col = "cluster_label"
    elif "cluster" in per.columns:
        per["cluster_label"] = per["cluster"].astype(str)
        color_col = "cluster_label"
    else:
        per["cluster_label"] = "Unknown"
        color_col = "cluster_label"

    labels_all = sorted(
        per[color_col].dropna().unique().tolist(),
        key=lambda s: int(re.search(r"\d+", str(s)).group()) if re.search(r"\d+", str(s)) else 1_000_000
    )
    per[color_col] = pd.Categorical(per[color_col], categories=labels_all, ordered=True)

    palette = px.colors.qualitative.Dark24
    color_map = {lab: palette[i % len(palette)] for i, lab in enumerate(labels_all)}

    # Recompute labels_all in case we want a fixed label space (kept as in your code)
    labels_all = sorted(
        per[color_col].dropna().unique().tolist(),
        key=lambda s: int(re.search(r"\d+", str(s)).group()) if re.search(r"\d+", str(s)) else 1_000_000
    )
    prefix = (labels_all[0][0] if labels_all and isinstance(labels_all[0], str) and labels_all[0] else "B")
    if permit_type.lower().startswith("build"):
        labels_all = [f"B{i}" for i in range(8)]
    else:
        nums = [int(re.search(r"\d+", s).group()) for s in labels_all if re.search(r"\d+", str(s))]
        max_idx = max(nums) if nums else 0
        labels_all = [f"{prefix}{i}" for i in range(max_idx + 1)]
    per[color_col] = pd.Categorical(per[color_col], categories=labels_all, ordered=True)

    palette = px.colors.qualitative.Dark24
    color_map = {lab: palette[i % len(palette)] for i, lab in enumerate(labels_all)}

    # Build permit scatter plot figure (pretty hover labels)
    if "nbhd" in per.columns:
        hover_name_val = per["nbhd"]
    else:
        hover_name_val = None

    per["Cluster"] = per[color_col].astype(str)
    if "permit_id" in per.columns:
        per["Permit ID"] = per["permit_id"]

    fig_pts = px.scatter_map(
        per.sort_values(["frame", color_col]),
        lat="lat",
        lon="lon",
        size="project_value_vis",
        size_max=22,
        color=color_col,
        color_discrete_map=color_map,
        category_orders={color_col: labels_all},
        animation_frame="frame",
        hover_name=hover_name_val,
        hover_data={
            "Month": True,
            "Permit ID": True,
            "Project Value": (":.0f" if "project_value" in per.columns else False),
            "Cluster": True,
            "permit_id": False,
            "cluster_label": False,
            "frame": False,
            "project_value_vis": False,
            "lat": False,
            "lon": False,
        },
    )

    # Hide legend for ALL dynamic traces, including those inside frames
    fig_pts.update_traces(showlegend=False)
    for fr in fig_pts.frames:
        for tr in fr.data:
            tr.showlegend = False

    # ---- Compose final figure BEFORE adding a custom legend ----
    fig = fig_poly
    for tr in fig_pts.data:
        tr.showlegend = False
        fig.add_trace(tr)

    frames_poly = {fr.name: fr for fr in fig.frames}
    for fr in fig_pts.frames:
        for tr in fr.data:
            tr.showlegend = False
        if fr.name in frames_poly:
            frames_poly[fr.name].data += fr.data
        else:
            fig.frames += (fr,)
    # ----------------------------------------------------------------

    # Force polygon hovertemplate onto ALL frames (prevents Month-only issue)
    for tr in fig.data:
        if getattr(tr, "type", "").startswith("choropleth"):
            tr.hovertemplate = poly_hover_tmpl
    for fr in fig.frames:
        for tr in fr.data:
            if getattr(tr, "type", "").startswith("choropleth"):
                tr.hovertemplate = poly_hover_tmpl

    # --- Disable built-in legend entirely (prevents dropping) ---
    fig.update_layout(showlegend=False)

    # --- Custom static legend via shapes + annotations (paper coords) ---
    legend_x = 0.01
    legend_y = 0.98
    swatch_w = 0.018
    swatch_h = 0.022
    gap_y    = 0.006
    text_dx  = 0.024
    pad = 0.008

    total_h = len(labels_all) * (swatch_h + gap_y) - gap_y
    y0_bg = legend_y - total_h - pad
    y1_bg = legend_y + pad
    x0_bg = legend_x - pad
    x1_bg = legend_x + swatch_w

    fig.add_shape(
        type="rect", xref="paper", yref="paper",
        x0=x0_bg, y0=y0_bg, x1=x1_bg, y1=y1_bg,
        line=dict(color="rgba(0,0,0,0)"),
        fillcolor="rgba(255,255,255,0.65)",
        layer="above"
    )

    cur_y = legend_y
    for lab in labels_all:
        fig.add_shape(
            type="rect", xref="paper", yref="paper",
            x0=legend_x, y0=cur_y - swatch_h, x1=legend_x + swatch_w, y1=cur_y,
            line=dict(color="rgba(0,0,0,0.4)", width=0.5),
            fillcolor=color_map.get(lab, "#999999"),
            layer="above"
        )
        fig.add_annotation(
            xref="paper", yref="paper",
            x=legend_x + text_dx, y=cur_y - swatch_h/2,
            text=str(lab),
            showarrow=False,
            xanchor="left", yanchor="middle",
            font=dict(size=12, color="black"),
            bgcolor="rgba(0,0,0,0)"
        )
        cur_y -= (swatch_h + gap_y)

    # --- Animation pace control (fixed for graph_objs) ---
    _pace = (animation_pace or "fast").lower()
    _dur_map = {
        "fast":   (300, 150),   # (frame_duration, transition_duration)
        "medium": (700, 300),
        "slow":   (1200, 500),
    }
    frame_dur, trans_dur = _dur_map.get(_pace, _dur_map["fast"])

    # Update play/pause button durations (updatemenus/buttons).
    # If no updatemenus exist, add a Play ▶ and Pause ⏸ set (matches your bar chart UI).
    if not fig.layout.updatemenus:
        fig.update_layout(
            updatemenus=[{
                "type": "buttons",
                "showactive": True,
                "x": 0.02, "y": 0.02, "xanchor": "left", "yanchor": "bottom",
                "buttons": [
                    {
                        "label": "▶ Play",
                        "method": "animate",
                        "args": [None, {
                            "frame": {"duration": frame_dur, "redraw": True},
                            "transition": {"duration": trans_dur},
                            "fromcurrent": True
                        }]
                    },
                    {
                        "label": "⏸ Pause",
                        "method": "animate",
                        "args": [[None], {
                            "mode": "immediate",
                            "frame": {"duration": 0, "redraw": False},
                            "transition": {"duration": 0}
                        }]
                    }
                ]
            }]
        )
    else:
        for um in fig.layout.updatemenus:
            if um.buttons:
                for bt in um.buttons:
                    args = list(bt.args) if bt.args is not None else []
                    if len(args) >= 2 and isinstance(args[1], dict):
                        cfg = dict(args[1])  # copy
                        frame_cfg = dict(cfg.get("frame", {}))
                        frame_cfg.update({"duration": frame_dur, "redraw": True})
                        trans_cfg = dict(cfg.get("transition", {}))
                        trans_cfg.update({"duration": trans_dur})
                        cfg["frame"] = frame_cfg
                        cfg["transition"] = trans_cfg
                        args[1] = cfg
                        bt.args = tuple(args)

    # Update slider transition duration
    if fig.layout.sliders:
        for sl in fig.layout.sliders:
            sl.update(transition=dict(duration=trans_dur))

    # =======================
    # PRETTY SLIDER LABELS
    # =======================
    # Map original frame names (like 'YYYY-MM') -> 'Mon YYYY'
    name_map = dict(zip(months_df["frame"].tolist(), months_df["Month"].tolist()))

    # 1) Rename frames
    for fr in fig.frames:
        fr.name = name_map.get(fr.name, fr.name)

    # 2) Rebuild slider steps to use renamed frame names and show nice labels
    if fig.layout.sliders:
        for slider in fig.layout.sliders:
            slider.currentvalue.prefix = "Month: "
            new_steps = []
            for step in slider.steps:
                args = step.args
                target = None
                if isinstance(args, (list, tuple)) and len(args) > 0:
                    a0 = args[0]
                    if isinstance(a0, (list, tuple)) and len(a0) > 0:
                        orig = a0[0]
                        target = [name_map.get(orig, orig)]
                    else:
                        orig = a0
                        target = name_map.get(orig, orig)
                # Preserve animation kwargs if present
                kwargs = args[1] if (isinstance(args, (list, tuple)) and len(args) > 1) else {"mode": "immediate"}
                # Rebuild as a NEW tuple
                step.args = (target, kwargs)
                step.label = name_map.get(step.label, step.label)
                new_steps.append(step)
            slider.steps = tuple(new_steps)

    return fig


