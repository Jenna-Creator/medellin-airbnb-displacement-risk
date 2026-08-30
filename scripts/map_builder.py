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
        'legend_name': 'Displacement Risk Index',
        'title': 'Displacement Risk Index',
        'description': 'Combines Airbnb density and estrato into one score (z-score of density minus z-score of estrato). Red = high density + low estrato (higher risk). Blue = low density + high estrato (lower risk).',
    },
    'density': {
        'column': 'log_density',
        'fill_color': 'YlOrRd',
        'legend_name': 'Airbnb Listings per km² (log scale)',
        'title': 'Airbnb Density',
        'description': 'The other input to the Displacement Risk Index. Shown on a log scale so outlier neighborhoods do not flatten the rest of the map -- see the tooltip for actual listing counts.',
    },
    'estrato': {
        'column': 'estrato_predominante',
        'fill_color': 'Blues',
        'legend_name': 'Predominant Estrato',
        'title': 'Predominant Estrato',
        'description': 'One of two inputs to the Displacement Risk Index. Colombia\'s socioeconomic scale, from 1 (lowest income) to 6 (highest).',
    },
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
    return merged


def build_map(merged, city, map_type):
    city_cfg = CITY_CONFIG[city]
    type_cfg = MAP_TYPE_CONFIG[map_type]

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
    <b>{city.title()} — {type_cfg["title"]}</b><br>
    {type_cfg["description"]}
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
        legend_name=type_cfg['legend_name'],
        nan_fill_color='lightgray',
    ).add_to(m)

    folium.GeoJson(
        merged,
        style_function=lambda x: {'fillOpacity': 0, 'weight': 0},
        tooltip=folium.GeoJsonTooltip(
            fields=[city_cfg['name_field'], city_cfg['subregion_field'], 'estrato_predominante', 'listing_count', 'displacement_risk_index'],
            aliases=['Barrio:', f"{city_cfg['subregion_label']}:", 'Estrato:', 'Airbnb Listings:', 'Risk Index:'],
            localize=True,
        ),
        popup=folium.GeoJsonPopup(
            fields=[city_cfg['name_field'], city_cfg['subregion_field'], 'estrato_predominante', 'listing_count', 'density_per_km2', 'displacement_risk_index'],
            aliases=['Barrio:', f"{city_cfg['subregion_label']}:", 'Estrato:', 'Airbnb Listings:', 'Listings per km²:', 'Risk Index:'],
            localize=True,
        ),
    ).add_to(m)

    return m