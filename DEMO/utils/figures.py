
import plotly.express as px

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
