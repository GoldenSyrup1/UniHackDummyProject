# app.py
import streamlit as st
import pydeck as pdk
import pandas as pd
from model.gap_score import score_hex, get_hexes_for_region
from llm.brief_gen import generate_brief
import random
st.set_page_config(page_title="TransitMind", layout="wide")
st.title("🚌 TransitMind — Transit Equity Explorer")

city = st.selectbox("Select city", ["Sydney", "Melbourne", "Brisbane"])
city_coords = {"Sydney": (-33.86, 151.20), "Melbourne": (-37.81, 144.96), "Brisbane": (-27.47, 153.02)}
lat, lng = city_coords[city]

# Generate hex grid
hexes = get_hexes_for_region(lat, lng, radius_km=25)

# --- placeholder scores until real data is wired in ---

rows = [{"hex": h, "gap_score": random.uniform(0, 1)} for h in hexes]
df = pd.DataFrame(rows)

# Pydeck H3 hex layer
layer = pdk.Layer(
    "H3HexagonLayer",
    df,
    pickable=True,
    stroked=True,
    filled=True,
    extruded=True,
    get_hexagon="hex",
    get_fill_color="[255 * gap_score, 255 * (1 - gap_score), 50, 180]",
    get_elevation="gap_score * 500",
)

view = pdk.ViewState(latitude=lat, longitude=lng, zoom=10, pitch=40)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view,
                          tooltip={"text": "Gap Score: {gap_score}"}))

# Click a zone → generate brief
st.subheader("📋 Policy Brief Generator")
if st.button("Generate brief for worst zone"):
    worst = df.loc[df["gap_score"].idxmax()]
    brief = generate_brief(worst["hex"], worst["gap_score"],
                           {"elderly_pct": 22, "no_car_pct": 31, "median_income": 640})
    st.info(brief)