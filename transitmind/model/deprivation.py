import h3
import pandas as pd
import geopandas as gpd
from collections import defaultdict

# Without real ABS data, we use a realistic synthetic model
# based on known patterns: outer suburbs = higher deprivation
def compute_deprivation_synthetic(hexes, city_lat, city_lng, resolution=8):
    """
    Proxy deprivation score using distance from CBD.
    Outer areas score higher (less resources, more car dependency).
    Replace with real ABS mesh block data when available.
    """
    import math
    scores = {}
    for hex_id in hexes:
        lat, lng = h3.cell_to_latlng(hex_id)
        # Distance from CBD in degrees (rough proxy)
        dist = math.sqrt((lat - city_lat)**2 + (lng - city_lng)**2)
        # Normalise: further = more deprived (simplified)
        score = min(dist / 0.5, 1.0)
        scores[hex_id] = round(score, 3)
    return scores

def compute_deprivation_from_abs(shapefile_path, hexes, resolution=8):
    """
    Real version: load ABS mesh block shapefile with SEIFA index.
    Download from: abs.gov.au/census/find-census-data/mapstats
    SEIFA IRSD: lower score = more disadvantaged
    """
    gdf = gpd.read_file(shapefile_path)
    gdf = gdf[["geometry", "IRSD_score"]].dropna()

    scores = {}
    for hex_id in hexes:
        lat, lng = h3.cell_to_latlng(hex_id)
        point = gpd.GeoSeries(
            [gpd.points_from_xy([lng], [lat])[0]], crs="EPSG:4326"
        )
        # Find which mesh block this hex centre falls in
        match = gdf[gdf.geometry.contains(point.iloc[0])]
        if not match.empty:
            irsd = match.iloc[0]["IRSD_score"]
            # Invert: low IRSD = high deprivation
            scores[hex_id] = round(1 - (irsd / 1200), 3)
        else:
            scores[hex_id] = 0.3  # default mid score

    return scores