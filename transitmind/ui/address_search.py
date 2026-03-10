from geopy.geocoders import Nominatim
import h3

def suburb_to_hex(suburb, city, resolution=8):
    geolocator = Nominatim(user_agent="transitmind")
    location = geolocator.geocode(f"{suburb}, {city}, Australia")
    if not location:
        return None, None, None
    lat, lng = location.latitude, location.longitude
    hex_id = h3.latlng_to_cell(lat, lng, resolution)
    return hex_id, lat, lng

def get_score_for_suburb(suburb, city, df):
    hex_id, lat, lng = suburb_to_hex(suburb, city)
    if not hex_id:
        return None
    match = df[df["hex"] == hex_id]
    if match.empty:
        return None
    row = match.iloc[0]
    return {
        "hex": hex_id,
        "lat": lat,
        "lng": lng,
        "gap_score": row["gap_score"],
        "deprivation": row["deprivation"],
        "accessibility": row["accessibility"]
    }