import requests, zipfile, io, os
import gtfs_kit as gk

GTFS_FEEDS = {
    "Sydney": "https://api.transport.nsw.gov.au/v1/gtfs/schedule/buses/1",
    "Melbourne": "https://data.ptv.vic.gov.au/downloads/gtfs.zip",
    "Brisbane": "https://gtfsrt.api.translink.com.au/GTFS/SEQ_GTFS.zip",
}


def fetch_gtfs(city="Sydney", api_key=None):
    """Download and parse GTFS feed, return stops as GeoDataFrame"""
    url = GTFS_FEEDS[city]
    headers = {"Authorization": f"apikey {api_key}"} if api_key else {}

    print(f"Downloading GTFS for {city}...")
    r = requests.get(url, headers=headers, timeout=30)

    feed = gk.read_feed(io.BytesIO(r.content), dist_units="km")
    stops = feed.stops[["stop_id", "stop_lat", "stop_lon", "stop_name"]].dropna()
    return stops


def load_local_gtfs(path="data/gtfs.zip"):
    """Fallback: load from a locally downloaded zip"""
    feed = gk.read_feed(path, dist_units="km")
    stops = feed.stops[["stop_id", "stop_lat", "stop_lon", "stop_name"]].dropna()
    return stops