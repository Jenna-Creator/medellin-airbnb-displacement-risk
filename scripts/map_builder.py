import folium
import pandas as pd
import geopandas as gpd

CITY_CONFIG = {
    'medellin': {
        'center': [6.2442, -75.5812],
        'key_field': 'codigo',
        'name_field': 'nombre_barrio',
        'subregion_field': 'comuna',
        'subregion_label': 'Comuna',
    },
    'barranquilla': {
        'center': [10.985, -74.807],
        'key_field': 'barrio',
        'name_field': 'barrio',
        'subregion_field': 'localidad',
        'subregion_label': 'Localidad',
    },
}

MAP_TYPE_CONFIG = {
    'composite': {
        'column': 'displacement_risk_index',
        'fill_color': 'RdYlBu_r',
        'en': {
            'legend_name': 'Displacement Risk Index',
            'title': 'Displacement Risk Index',
            'description': 'Combines Airbnb housing saturation and estrato into one score (z-score of saturation minus z-score of estrato). Red = high saturation + low estrato (higher risk). Blue = low saturation + high estrato (lower risk).',
        },
        'es': {
            'legend_name': 'Índice de Riesgo de Desplazamiento',
            'title': 'Índice de Riesgo de Desplazamiento',
            'description': 'Combina la saturación de vivienda por Airbnb y el estrato en un solo puntaje (z-score de saturación menos z-score de estrato). Rojo = alta saturación + estrato bajo (mayor riesgo). Azul = baja saturación + estrato alto (menor riesgo).',
        },
    },
    'housing_saturation': {
        'column': 'log_pct_homes',
        'fill_color': 'YlOrRd',
        'en': {
            'legend_name': '% of Housing Units Listed on Airbnb (log scale)',
            'title': 'Airbnb Housing Saturation',
            'description': 'One of two inputs to the Displacement Risk Index. The share of a barrio\'s counted housing stock (DANE 2018 census) listed on Airbnb, shown on a log scale -- see the tooltip for the actual percentage. Barrios with too few counted housing units are excluded as statistically unreliable.',
        },
        'es': {
            'legend_name': '% de Viviendas Listadas en Airbnb (escala logarítmica)',
            'title': 'Saturación de Vivienda por Airbnb',
            'description': 'Uno de los dos insumos del Índice de Riesgo de Desplazamiento. La proporción del parque de vivienda contado en un barrio (censo DANE 2018) que está listada en Airbnb, mostrada en escala logarítmica -- vea el recuadro para el porcentaje real. Los barrios con muy pocas viviendas contadas se excluyen por poca confiabilidad estadística.',
        },
    },
    'density': {
        'column': 'log_density',
        'fill_color': 'Purples',
        'en': {
            'legend_name': 'Airbnb Listings per km² (log scale)',
            'title': 'Airbnb Density (reference)',
            'description': 'Not used in the index. Shown for reference: raw listing concentration per unit of land area, which assumes every neighborhood is equally populated -- the assumption the housing saturation map corrects for.',
        },
        'es': {
            'legend_name': 'Alojamientos de Airbnb por km² (escala logarítmica)',
            'title': 'Densidad de Airbnb (referencia)',
            'description': 'No se usa en el índice. Se muestra como referencia: la concentración bruta de alojamientos por unidad de área, que asume que cada barrio tiene la misma densidad poblacional -- el supuesto que corrige el mapa de saturación de vivienda.',
        },
    },
    'estrato': {
        'column': 'estrato_predominante',
        'fill_color': 'Blues',
        'en': {
            'legend_name': 'Predominant Estrato',
            'title': 'Predominant Estrato',
            'description': 'One of two inputs to the Displacement Risk Index. Colombia\'s socioeconomic scale, from 1 (lowest income) to 6 (highest).',
        },
        'es': {
            'legend_name': 'Estrato Predominante',
            'title': 'Estrato Predominante',
            'description': 'Uno de los dos insumos del Índice de Riesgo de Desplazamiento. La escala socioeconómica de Colombia, de 1 (ingreso más bajo) a 6 (más alto).',
        },
    },
}

DETAIL_ALIASES = {
    'en': ['Barrio:', 'Estrato:', 'Airbnb Listings:', 'Total Housing Units:', '% Homes on Airbnb:', 'Saturation Rank:', 'Risk Index:'],
    'es': ['Barrio:', 'Estrato:', 'Alojamientos de Airbnb:', 'Total de Viviendas:', '% de Viviendas en Airbnb:', 'Ranking de Saturación:', 'Índice de Riesgo:'],
}


def load_merged_data(city):
    if city == 'medellin':
        barrios = gpd.read_file('data/geo/medellin_barrios_all.geojson')
        index_df = pd.read_csv('data/processed/medellin_displacement_index.csv')
        barrios['codigo'] = barrios['codigo'].astype(str).str.zfill(4)
        index_df['codigo'] = index_df['codigo'].astype(str).str.zfill(4)
        index_df = index_df.drop(columns=['nombre_barrio', 'comuna'])
        merged = barrios.merge(index_df, on='codigo', how='left')
    else:
        barrios = gpd.read_file('data/geo/barranquilla_barrios.geojson')
        index_df = pd.read_csv('data/processed/barranquilla_displacement_index.csv')
        index_df = index_df.drop(columns=['localidad'])
        merged = barrios.merge(index_df, on='barrio', how='left')

    merged['saturation_rank'] = merged['pct_homes_on_airbnb'].rank(pct=True, ascending=True)

    return merged


def build_map(merged, city, map_type, lang='en'):
    city_cfg = CITY_CONFIG[city]
    type_cfg = MAP_TYPE_CONFIG[map_type]
    text = type_cfg[lang]

    m = folium.Map(location=city_cfg['center'], zoom_start=12.5, zoom_snap=0.25, tiles='OpenStreetMap')

    minx, miny, maxx, maxy = merged.total_bounds
    fit_bounds_js = f'''
<script>
document.addEventListener("DOMContentLoaded", function() {{
    {m.get_name()}.fitBounds([[{miny}, {minx}], [{maxy}, {maxx}]], {{animate: false}});
}});
</script>
'''
    m.get_root().html.add_child(folium.Element(fit_bounds_js))

    title_html = f'''
    <div style="position: fixed; top: 10px; left: 50px; width: 220px; z-index: 9999;
                background-color: white; color: black; padding: 8px; border: 2px solid grey;
                border-radius: 5px; font-size: 12px;">
    <b>{city.title()} — {text["title"]}</b><br>
    {text["description"]}
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    folium.Choropleth(
        geo_data=merged,
        data=merged,
        columns=[city_cfg['key_field'], type_cfg['column']],
        key_on=f"feature.properties.{city_cfg['key_field']}",
        fill_color=type_cfg['fill_color'],
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=text['legend_name'],
        nan_fill_color='lightgray',
    ).add_to(m)

    merged['pct_homes_on_airbnb'] = merged['pct_homes_on_airbnb'].round(1)

    if lang == 'es':
        merged['saturation_rank_label'] = merged['saturation_rank'].apply(
            lambda p: f"{max(1, round(100 * (1 - p)))}% superior" if pd.notna(p) else "N/A"
        )
    else:
        merged['saturation_rank_label'] = merged['saturation_rank'].apply(
            lambda p: f"Top {max(1, round(100 * (1 - p)))}%" if pd.notna(p) else "N/A"
        )

    detail_fields = [city_cfg['name_field'], city_cfg['subregion_field'], 'estrato_predominante',
                      'listing_count', 'total_viviendas', 'pct_homes_on_airbnb',
                      'saturation_rank_label', 'displacement_risk_index']
    detail_aliases = [DETAIL_ALIASES[lang][0], f"{city_cfg['subregion_label']}:"] + DETAIL_ALIASES[lang][1:]
    detail_style = "font-family: arial; font-size: 13px; background-color: white; color: #333; padding: 8px;"

    folium.GeoJson(
        merged,
        style_function=lambda x: {'fillOpacity': 0, 'weight': 0},
        tooltip=folium.GeoJsonTooltip(
            fields=detail_fields,
            aliases=detail_aliases,
            style=detail_style,
            localize=True,
        ),
        popup=folium.GeoJsonPopup(
            fields=detail_fields,
            aliases=detail_aliases,
            style=detail_style,
            localize=True,
        ),
    ).add_to(m)

    return m


def get_top_barrios_str(city, n=2, lang='en'):
    """Returns the top n barrios by displacement_risk_index, formatted as a
    natural-language list ("A and B" / "A y B"), read live from the CSV so
    this can never drift out of sync with the actual data."""
    df = pd.read_csv(f'data/processed/{city}_displacement_index.csv')
    name_field = 'nombre_barrio' if city == 'medellin' else 'barrio'
    top_names = df.sort_values('displacement_risk_index', ascending=False).head(n)[name_field].tolist()
    conjunction = 'and' if lang == 'en' else 'y'
    if len(top_names) == 1:
        return top_names[0]
    return f"{', '.join(top_names[:-1])} {conjunction} {top_names[-1]}"