import h3
import math
from model.accessibility import compute_accessibility
from model.gap_score import score_hex

def simulate_new_route(start_lat, start_lng, end_lat, end_lng,
                       hexes, deprivation_scores, resolution=8,
                       stops_per_km=3):
    """
    Simulate adding a bus route between two points.
    Adds virtual stops along the route and recomputes accessibility + gap scores.
    Returns: dict of {hex_id: new_gap_score}, total_impact (sum of gap reduction)
    """
    # Generate stops along the route
    n_stops = max(2, int(_haversine(start_lat, start_lng, end_lat, end_lng) * stops_per_km))
    virtual_stops = []
    for i in range(n_stops):
        t = i / (n_stops - 1)
        lat = start_lat + t * (end_lat - start_lat)
        lng = start_lng + t * (end_lng - start_lng)
        virtual_stops.append({"stop_lat": lat, "stop_lon": lng})

    import pandas as pd
    virtual_df = pd.DataFrame(virtual_stops)

    # Recompute accessibility with new stops added
    new_accessibility = compute_accessibility(virtual_df, hexes, resolution)

    # Recompute gap scores
    new_gaps = {}
    for hex_id in hexes:
        dep = deprivation_scores.get(hex_id, 0)
        acc = new_accessibility.get(hex_id, 0)
        new_gaps[hex_id] = round(dep * (1 - acc), 3)

    return new_gaps

def _haversine(lat1, lng1, lat2, lng2):
    """Distance in km between two points"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))