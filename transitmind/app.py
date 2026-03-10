import streamlit as st
import pydeck as pdk
import pandas as pd
import os
from dotenv import load_dotenv

from model.gap_score import get_hexes_for_region, score_hex
from model.accessibility import compute_accessibility
from model.deprivation import compute_deprivation_synthetic
from simulation.route_sim import simulate_new_route
from llm.brief_gen import generate_brief

load_dotenv()

st.set_page_config(page_title="TransitMind", layout="wide")
st.title("🚌 TransitMind — Transit Equity Explorer")

CITIES = {
    "Sydney": (-33.86, 151.20),
    "Melbourne": (-37.81, 144.96),
    "Brisbane": (-27.47, 153.02),
}

city = st.selectbox("Select city", list(CITIES.keys()))
lat, lng = CITIES[city]

@st.cache_data
def load_scores(city, lat, lng):
    hexes = get_hexes_for_region(lat, lng, radius_km=25)
    dep = compute_deprivation_synthetic(hexes, lat, lng)

    # Try real GTFS, fall back to empty (no stops = low accessibility everywhere)
    try:
        from data.fetch_gtfs import load_local_gtfs
        stops = load_local_gtfs("data/gtfs.zip")
        acc = compute_accessibility(stops, hexes)
    except Exception:
        acc = {h: 0.1 for h in hexes}  # fallback: assume low access

    rows = []
    for h in hexes:
        gap = score_hex(h, {h: {"score": dep[h]}}, {h: {"score": acc[h]}})
        rows.append({"hex": h, "gap_score": gap, "deprivation": dep[h], "accessibility": acc[h]})

    return pd.DataFrame(rows)

df = load_scores(city, lat, lng)

# --- Map ---
col1, col2 = st.columns([3, 1])

with col1:
    layer = pdk.Layer(
        "H3HexagonLayer",
        df,
        pickable=True,
        stroked=True,
        filled=True,
        extruded=True,
        get_hexagon="hex",
        get_fill_color="[255 * gap_score, 255 * (1 - gap_score), 50, 180]",
        get_elevation="gap_score * 800",
    )
    view = pdk.ViewState(latitude=lat, longitude=lng, zoom=10, pitch=45)
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip={"text": "Gap: {gap_score}\nDeprivation: {deprivation}\nAccessibility: {accessibility}"}
    ))

with col2:
    st.metric("Hexes analysed", len(df))
    st.metric("High-gap zones (>0.7)", int((df["gap_score"] > 0.7).sum()))
    st.metric("Avg gap score", round(df["gap_score"].mean(), 2))

    st.subheader("📋 Policy Brief")
    if st.button("Generate for worst zone"):
        worst = df.loc[df["gap_score"].idxmax()]
        with st.spinner("Generating..."):
            brief = generate_brief(
                worst["hex"], worst["gap_score"],
                {"elderly_pct": 22, "no_car_pct": 31, "median_income": 640}
            )
        st.info(brief)

# --- Route Simulation ---
st.subheader("🛣 Simulate a New Route")
st.caption("Enter start and end coordinates to see how a new route reduces the gap")

c1, c2, c3, c4 = st.columns(4)
start_lat = c1.number_input("Start Lat", value=lat - 0.1)
start_lng = c2.number_input("Start Lng", value=lng - 0.1)
end_lat = c3.number_input("End Lat", value=lat + 0.1)
end_lng = c4.number_input("End Lng", value=lng + 0.1)

if st.button("Run Simulation"):
    hexes = df["hex"].tolist()
    dep = dict(zip(df["hex"], df["deprivation"]))
    new_gaps = simulate_new_route(start_lat, start_lng, end_lat, end_lng, hexes, dep)
    df["simulated_gap"] = df["hex"].map(new_gaps)
    df["improvement"] = df["gap_score"] - df["simulated_gap"]

    avg_improvement = df["improvement"].mean()
    st.success(f"Average gap score reduced by {avg_improvement:.3f} across all zones")

    sim_layer = pdk.Layer(
        "H3HexagonLayer",
        df,
        pickable=True,
        filled=True,
        extruded=True,
        get_hexagon="hex",
        get_fill_color="[255 * simulated_gap, 255 * (1 - simulated_gap), 50, 180]",
        get_elevation="simulated_gap * 800",
    )
    st.pydeck_chart(pdk.Deck(
        layers=[sim_layer],
        initial_view_state=view,
        tooltip={"text": "New gap: {simulated_gap}\nImprovement: {improvement}"}
    ))