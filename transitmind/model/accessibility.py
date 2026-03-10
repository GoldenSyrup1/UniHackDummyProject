import h3
import pandas as pd
from collections import defaultdict

def compute_accessibility(stops_df, hexes, resolution=8):
    """
    For each hex, count how many transit stops fall within it and neighbours.
    Returns dict: {hex_id: accessibility_score (0-1)}
    """
    # Assign each stop to a hex
    stop_counts = defaultdict(int)
    for _, row in stops_df.iterrows():
        hex_id = h3.latlng_to_cell(row["stop_lat"], row["stop_lon"], resolution)
        stop_counts[hex_id] += 1

    # Score each hex using itself + immediate neighbours (smoothing)
    raw_scores = {}
    for hex_id in hexes:
        neighbours = h3.grid_disk(hex_id, k=1)
        total_stops = sum(stop_counts.get(n, 0) for n in neighbours)
        raw_scores[hex_id] = total_stops

    # Normalise to 0-1
    max_stops = max(raw_scores.values()) if raw_scores else 1
    return {
        hex_id: round(count / max_stops, 3)
        for hex_id, count in raw_scores.items()
    }