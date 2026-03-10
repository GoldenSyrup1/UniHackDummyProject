# model/gap_score.py
import h3
import geopandas as gpd
import pandas as pd

def get_hexes_for_region(lat, lng, radius_km=20, resolution=8):
    center = h3.latlng_to_cell(lat, lng, resolution)
    hexes = h3.grid_disk(center, k=int(radius_km / 1.5))
    return list(hexes)

def score_hex(hex_id, deprivation_df, accessibility_df):
    """Higher score = bigger gap (more need, less service)"""
    dep = deprivation_df.get(hex_id, {}).get("score", 0)
    acc = accessibility_df.get(hex_id, {}).get("score", 0)
    # Gap = high need, low access
    gap = dep * (1 - acc)
    return round(gap, 3)