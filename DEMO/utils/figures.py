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









# Define function to plot building permit project value over time

def plot_avg_project_value_over_time(df, nbhd=None, freq="Y"):
    
    """
    Plot average project_value over time, optionally filtered by neighborhood
    """

    data = df.copy()

    # Filter neighborhood if requested
    if nbhd is not None:
        nbhd = nbhd.title()
        data = data[data["nbhd"] == nbhd]
        if data.empty:
            raise ValueError(f"No records found for neighborhood: {nbhd}")
        title_prefix = nbhd.title()
    else:
        title_prefix = "All Neighborhoods"

    # Extract period for grouping (month or year)
    if freq == "M":
        data["period"] = data["issue_date"].dt.to_period("M").dt.to_timestamp()
        freq_label = "Month"
    elif freq == "Y":
        data["period"] = data["issue_date"].dt.to_period("Y").dt.to_timestamp()
        freq_label = "Year"
    else:
        raise ValueError("freq must be either 'M' (monthly) or 'Y' (yearly)")

    # Exclude 2025 as there is insufficient data
    data = data[data["period"].dt.year != 2025]

    # Aggregate average project value by chosen frequency
    grouped = (
        data.groupby("period", as_index=False)["project_value"]
        .mean()
        .sort_values("period")
    )

    # Interactive line chart
    fig = px.line(
        grouped,
        x="period",
        y="project_value",
        markers=True,
        title=f"Average Project Value Over Time ({freq_label}) — {title_prefix}",
        labels={"period": freq_label, "project_value": "Average Project Value"},
    )

    fig.update_traces(line=dict(width=2))
    fig.update_layout(
        hovermode="x unified",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
    )

    return fig

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
    # - Use hover_name for Neighborhood (if present)
    # - Use "Month", "Permit ID", "Project Value", and "Cluster"
    if "nbhd" in per.columns:
        hover_name_val = per["nbhd"]
    else:
        hover_name_val = None

    # Provide pretty columns for hover text only
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
            # hide unprettified/internal columns
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
    x1_bg = legend_x + swatch_w  # keep as you had it

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

    # Update play button durations (updatemenus/buttons)
    if fig.layout.updatemenus:
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

    return fig



