import streamlit as st
from streamlit_folium import st_folium
import sys
sys.path.append('scripts')
from map_builder import build_map, load_merged_data, get_top_barrios_str

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
    "en": "rank(% of homes on Airbnb) − rank(estrato)",
    "es": "percentil(% de viviendas en Airbnb) − percentil(estrato)",
}

RESULTS_HEADER = {"en": "Results for", "es": "Resultados para"}

RESULTS_TEMPLATE = {
    "en": {
        "medellin": """
**{top} top the index.** Both sit in Comuna 13 (San Javier), the city's lowest-estrato comuna and
home to the Comuna 13 Graffitour, one of Medellín's most-visited tourist draws. Five more San Javier
barrios and three from Villa Hermosa round out the rest of the top 10.

**El Poblado and Manila no longer dominate.** Under an earlier version of this index, their extreme
Airbnb saturation (one barrio topped 100% of its 2018-counted housing stock) overwhelmed the formula
and pushed them to the top despite their high estrato. Percentile-ranking both inputs fixed that: a
barrio's saturation can only rank as high as anyone else's, so high estrato now properly discounts it.
El Poblado and Manila still show real overtourism pressure — just not displacement risk, which is
the distinction this index is built to draw.

**San Javier's low absolute saturation numbers still carry the signal.** These barrios have thousands
of housing units, so even meaningful Airbnb activity is a small share of the total stock — but paired
with the lowest estrato in the dataset, that's still the combination this index flags as elevated risk.
""",
        "barranquilla": """
**{top} top the index.** Both are low-estrato barrios carrying a real, if modest, share of the city's
Airbnb activity. Metropolitana and Suroccidente contribute the rest of the top 10 (San Luis, 20 de
Julio, 7 de Abril, Los Girasoles, El Golfo, La Paz, Ciudad Modesto), all estrato 1.

**Riomar's wealthy core no longer tops the list, but its low-estrato pockets still show up.** San
Salvador and Corregimiento La Playa sit inside Riomar — Barranquilla's wealthiest localidad overall
— but are themselves estrato 1–2, and rank alongside the other low-income barrios rather than with
Riomar's high-estrato core (El Poblado, Altamira, Villa del Este), which shows real Airbnb saturation
but doesn't rank as high-risk. That's the index correctly discriminating within a locality, not just
between them.

**Unlike Medellín, no Barranquilla barrio ever reached the extreme saturation levels that broke the
earlier version of this index**, so the fix changes Barranquilla's ranking less dramatically than
Medellín's.
""",
    },
    "es": {
        "medellin": """
**{top} encabezan el índice.** Ambos están en la Comuna 13 (San Javier), la comuna de menor estrato
de la ciudad y sede del Graffitour de la Comuna 13, una de las atracciones turísticas más visitadas
de Medellín. Cinco barrios más de San Javier y tres de Villa Hermosa completan el resto del top 10.

**El Poblado y Manila ya no dominan.** En una versión anterior de este índice, su saturación extrema
de Airbnb (un barrio superó el 100% de su parque de vivienda contado en 2018) desbordaba la fórmula y
los llevaba al primer lugar a pesar de su estrato alto. Al usar percentiles en ambos insumos se corrigió
esto: la saturación de un barrio solo puede rankear tan alto como la de cualquier otro, así que un
estrato alto ahora lo compensa correctamente. El Poblado y Manila siguen mostrando una presión turística
real — solo que no riesgo de desplazamiento, que es justamente la distinción que este índice busca hacer.

**Los porcentajes bajos de saturación de San Javier siguen llevando la señal.** Estos barrios tienen
miles de viviendas, así que incluso una actividad significativa de Airbnb representa una fracción
pequeña del total — pero combinada con el estrato más bajo del conjunto de datos, sigue siendo la
combinación que este índice marca como de mayor riesgo.
""",
        "barranquilla": """
**{top} encabezan el índice.** Ambos son barrios de estrato bajo con una participación real, aunque
modesta, en la actividad de Airbnb de la ciudad. Metropolitana y Suroccidente aportan el resto del top
10 (San Luis, 20 de Julio, 7 de Abril, Los Girasoles, El Golfo, La Paz, Ciudad Modesto), todos estrato 1.

**El núcleo adinerado de Riomar ya no encabeza la lista, pero sus zonas de estrato bajo sí aparecen.**
San Salvador y Corregimiento La Playa están dentro de Riomar — la localidad más adinerada de
Barranquilla en general — pero son en sí mismos de estrato 1–2, y rankean junto a los demás barrios
de bajos ingresos en lugar de con el núcleo de estrato alto de Riomar (El Poblado, Altamira, Villa
del Este), que muestra saturación real de Airbnb pero no rankea como de alto riesgo. Esa es la
diferenciación correcta que hace el índice dentro de una misma localidad, no solo entre localidades.

**A diferencia de Medellín, ningún barrio de Barranquilla llegó nunca a los niveles extremos de
saturación que rompían la versión anterior de este índice**, así que la corrección cambia el
ranking de Barranquilla de forma menos drástica que el de Medellín.
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
top_barrios_str = get_top_barrios_str(city, n=2, lang=lang)
st.markdown(RESULTS_TEMPLATE[lang][city].format(top=top_barrios_str))

with st.expander(EXPANDER_LABEL[lang]):
    secondary_type = st.selectbox(
        SECONDARY_MAP_LABEL[lang],
        ["estrato", "housing_saturation", "density"],
        format_func=lambda x: SECONDARY_MAP_OPTIONS_LABELS[lang][x],
        key="secondary_map_type",
    )
    m2 = build_map(merged, city=city, map_type=secondary_type, lang=lang)
    st_folium(m2, width=1000, height=600, key="secondary_map", returned_objects=[])