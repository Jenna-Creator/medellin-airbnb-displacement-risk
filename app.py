import streamlit as st
from streamlit_folium import st_folium
import sys
sys.path.append('scripts')
from map_builder import build_map, load_merged_data

st.set_page_config(page_title="Airbnb Displacement Risk", layout="wide")
st.title("Airbnb Displacement Risk, by City")

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

st.sidebar.markdown("""
---
**Three maps per city:**

- **Predominant Estrato** — each neighborhood's "estrato" or income level (1–6), no Airbnb data involved.
- **Airbnb Density** — the raw concentration of Airbnb listings, on a log scale.
- **Displacement Risk Index** — the combined score: high Airbnb density *and* low estrato (income level) together.

Estrato and Airbnb Density are the two ingredients; the Risk Index is what you get when you combine them.
""")

CITY_DISPLAY_NAMES = {"medellin": "Medellín", "barranquilla": "Barranquilla"}

RESULTS_TEXT = {
    "medellin": """
**Comuna 13 (San Javier) tops the index.** The highest-risk barrios — San Javier No. 2,
San Javier No. 1, Los Alcázares, La Pradera, Veinte de Julio — sit in the city's
lowest-estrato comuna, also home to the Comuna 13 Graffitour, one of Medellín's
most-visited tourist draws.

**El Poblado is the opposite pattern.** It holds roughly a third of the city's Airbnb
listings, but scores *low* on the index, since it's also uniformly high-estrato. That
reads as overtourism/saturation in an already-wealthy area, not displacement pressure
on low-income residents.
""",
    "barranquilla": """
**Norte Centro Histórico and Suroccidente top the index.** San Luis, El Rosario, San
Francisco, Ciudad Modesto, and La Paz — all low-estrato barrios — carry a
disproportionate share of Airbnb listings relative to their income level.

**Riomar mirrors El Poblado's pattern.** It's Barranquilla's wealthiest, most
Airbnb-saturated localidad, but doesn't dominate the risk index since it's also
uniformly high-estrato — density without displacement pressure.
""",
}

merged = load_merged_data(city)
m = build_map(merged, city=city, map_type=map_type)

st.markdown("#### Background")

st.markdown(" Many cities in Latin America (and all over the world) have seen sharp growth in short-term rental "
    "listings over the past several years. A common concern raised about this growth, "
    "in Medellín especially, is that it drives up housing costs and displaces long-term "
    "residents once a historically low-income area becomes a tourist draw. <br><br>"
    "Raw listing counts alone don't distinguish between two very different stories: "
    "a wealthy neighborhood absorbing a large volume of tourists (an overtourism/saturation problem)"
    " versus a low-income neighborhood absorbing a smaller but fast-growing share of tourist rentals"
    " (a displacement-risk problem). This project builds a simple, transparent index designed to "
    "separate those two patterns.", unsafe_allow_html=True)

st.markdown("#### How the index works")
st.markdown(
    "Each barrio is scored on two things: **Airbnb listing density** (active "
    "listings per km²) and **estrato**, Colombia's 1–6 socioeconomic scale. "
    "The Displacement Risk Index is a difference of z-scores:"
)
st.code("z(log(density)) − z(estrato)", language=None)
st.markdown("A high score means unusually high rental density paired with unusually "
    "low estrato — the specific combination associated with displacement "
    "pressure. This is a relative screening tool, not a causal claim.<br><br>"
    "Use the filters on the left to toggle between the different cities "
    "available as well as the three maps: two inputs to the index and the composite Displacement Risk "
    "Index.", unsafe_allow_html=True)

st_folium(m, width=1000, height=600)

st.markdown(f"#### Results for {CITY_DISPLAY_NAMES[city]}")
st.markdown(RESULTS_TEXT[city])