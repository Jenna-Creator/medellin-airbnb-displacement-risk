import streamlit as st
from streamlit_folium import st_folium
import sys
sys.path.append('scripts')
from map_builder import build_map, load_merged_data

@st.cache_data
def get_merged_data(city):
    return load_merged_data(city)

st.set_page_config(page_title="Airbnb Displacement Risk", layout="wide")

lang = st.selectbox("Language / Idioma", ["en", "es"], format_func=lambda x: {"en": "English", "es": "Español"}[x])

TITLE = {
    "en": "Airbnb Displacement Risk, by City",
    "es": "Riesgo de Desplazamiento por Airbnb, por Ciudad",
}
st.title(TITLE[lang])

CITY_DISPLAY_NAMES = {"medellin": "Medellín", "barranquilla": "Barranquilla"}
CITY_LABEL = {"en": "City", "es": "Ciudad"}

city = st.selectbox(
    CITY_LABEL[lang],
    ["medellin", "barranquilla"],
    format_func=lambda x: CITY_DISPLAY_NAMES[x],
)

SETUP_TEXT = {
    "en": "Airbnb listings can cluster in a wealthy neighborhood without putting anyone's housing at risk "
          "(overtourism), or cluster in a lower-income neighborhood in a way that does (displacement risk). This index is built "
          "to tell those two situations apart.",
    "es": "Los alojamientos de Airbnb pueden concentrarse en un barrio de altos ingresos sin poner en "
          "riesgo la vivienda de nadie (sobreturismo), o concentrarse en un barrio de bajos ingresos de "
          "una manera que sí lo hace (riesgo de desplazamiento). Este índice está diseñado para distinguir entre esas dos situaciones.",
}

FORMULA_TEXT = {
    "en": "z(log(% of homes on Airbnb)) − z(estrato)",
    "es": "z(log(% de viviendas en Airbnb)) − z(estrato)",
}

RESULTS_HEADER = {"en": "Results for", "es": "Resultados para"}

RESULTS_TEXT = {
    "en": {
        "medellin": """
**El Poblado and Manila top the index.** Both are high-estrato barrios where Airbnb listings now
account for an unusually large — in El Poblado's case, implausibly large — share of the
neighborhood's 2018-counted housing stock. Hover over the map for exact figures.

**Take those very high figures with a grain of salt.** They likely reflect real, extreme tourism
pressure combined with a known limitation of this method: the 2018 census predates Medellín's
post-2020 digital nomad boom (see the README for the full discussion).

**San Javier's barrios also show up, lower down and for a different reason.** Their saturation
percentages are small — not because there's no Airbnb activity, but because these barrios have
thousands of housing units, so even a real, growing tourist presence (the Comuna 13 Graffitour draws
heavy foot traffic) doesn't yet register as a large share of the housing stock. They rank where they
do mostly on the strength of their very low estrato.
""",
        "barranquilla": """
**Riomar's own barrios top the index.** El Poblado, Altamira, and Villa
del Este — all estrato 5, in Barranquilla's wealthiest localidad — carry a meaningful share of their
housing stock as Airbnb listings (hover over the map for exact figures). That's a genuine, if less
extreme, echo of Medellín's El Poblado pattern: a high-income area absorbing real tourism pressure.

**Norte - Centro Histórico rounds out the top of the list at lower estrato.** El Rosario, Colombia,
Santa Ana, and Los Nogales combine smaller saturation percentages with a lower income level to land
close to Riomar's barrios on the composite score — the classic displacement-risk combination of
modest-but-real tourism pressure on lower-income housing.

**Unlike Medellín, no barrio here approaches implausible saturation levels**, so the census-vintage
caveat matters less for Barranquilla's results.
""",
    },
    "es": {
        "medellin": """
**El Poblado y Manila encabezan el índice.** Ambos son barrios de estrato alto donde los alojamientos
de Airbnb representan ahora una proporción inusualmente grande —en el caso de El Poblado,
implausiblemente grande— del parque de vivienda contado en 2018. Pase el cursor sobre el mapa para
ver las cifras exactas.

**Tome esas cifras tan altas con cautela.** Probablemente reflejan una presión turística real y
extrema, combinada con una limitación conocida de este método: el censo de 2018 es anterior al auge
de nómadas digitales que vivió Medellín después de 2020 (vea el README para la discusión completa).

**Los barrios de San Javier también aparecen, más abajo y por una razón distinta.** Sus porcentajes
de saturación son pequeños —no porque no haya actividad de Airbnb, sino porque estos barrios tienen
miles de viviendas, así que incluso una presencia turística real y creciente (el Graffitour de la
Comuna 13 atrae mucho tráfico peatonal) todavía no representa una proporción grande del parque de
vivienda. Su posición en el ranking se debe principalmente a su estrato muy bajo.
""",
        "barranquilla": """
**Los barrios de Riomar encabezan el índice.** El Poblado, Altamira y Villa del Este —todos de
estrato 5, en la localidad más adinerada de Barranquilla— tienen una proporción significativa de su
parque de vivienda listada en Airbnb (pase el cursor sobre el mapa para ver las cifras exactas). Es
un eco genuino, aunque menos extremo, del patrón de El Poblado en Medellín: una zona de altos
ingresos que absorbe una presión turística real.

**Norte - Centro Histórico completa la parte alta de la lista con estrato más bajo.** El Rosario,
Colombia, Santa Ana y Los Nogales combinan porcentajes de saturación más pequeños con un nivel de
ingreso más bajo, quedando cerca de los barrios de Riomar en el puntaje compuesto —la combinación
clásica de riesgo de desplazamiento: presión turística modesta pero real sobre vivienda de bajos
ingresos.

**A diferencia de Medellín, ningún barrio aquí se acerca a niveles de saturación implausibles**, así
que la advertencia sobre la antigüedad del censo importa menos para los resultados de Barranquilla.
""",
    },
}

EXPANDER_LABEL = {
    "en": "See the individual inputs, and a reference density map",
    "es": "Ver los insumos individuales y un mapa de referencia de densidad",
}

SECONDARY_MAP_LABEL = {"en": "Map", "es": "Mapa"}

SECONDARY_MAP_OPTIONS_LABELS = {
    "en": {
        "housing_saturation": "Airbnb Housing Saturation",
        "density": "Airbnb Density (reference, not used in the index)",
        "estrato": "Predominant Estrato",
    },
    "es": {
        "housing_saturation": "Saturación de Vivienda por Airbnb",
        "density": "Densidad de Airbnb (referencia, no usada en el índice)",
        "estrato": "Estrato Predominante",
    },
}

merged = get_merged_data(city)

st.markdown(SETUP_TEXT[lang])
st.code(FORMULA_TEXT[lang], language=None)

m = build_map(merged, city=city, map_type="composite", lang=lang)
st_folium(m, width=1000, height=600, returned_objects=[])

st.markdown(f"#### {RESULTS_HEADER[lang]} {CITY_DISPLAY_NAMES[city]}")
st.markdown(RESULTS_TEXT[lang][city])

with st.expander(EXPANDER_LABEL[lang]):
    secondary_type = st.selectbox(
        SECONDARY_MAP_LABEL[lang],
        ["estrato", "housing_saturation", "density"],
        format_func=lambda x: SECONDARY_MAP_OPTIONS_LABELS[lang][x],
        key="secondary_map_type",
    )
    m2 = build_map(merged, city=city, map_type=secondary_type, lang=lang)
    st_folium(m2, width=1000, height=600, key="secondary_map", returned_objects=[])