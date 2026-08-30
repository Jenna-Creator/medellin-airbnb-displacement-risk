import streamlit as st
from streamlit_folium import st_folium
import sys
sys.path.append('scripts')
from map_builder import build_map, load_merged_data

st.set_page_config(page_title="Airbnb Displacement Risk", layout="wide")
st.title("Airbnb Displacement Risk by City")

city = st.sidebar.selectbox("City", ["medellin", "barranquilla"], format_func=lambda x: x.title())
map_type = st.sidebar.selectbox(
    "Map",
    ["estrato", "density", "composite"],
    format_func=lambda x: {
        "composite": "Displacement Risk Index",
        "density": "Airbnb Density",
        "estrato": "Predominant Estrato",
    }[x],
)

merged = load_merged_data(city)
m = build_map(merged, city=city, map_type=map_type)

st_folium(m, width=1000, height=600)