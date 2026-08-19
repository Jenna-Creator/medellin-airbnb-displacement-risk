import pandas as pd
import geopandas as gpd
import folium

# Load the barrio geometry and the displacement index data
barrios = gpd.read_file('data/geo/medellin_barrios_all.geojson')
index_df = pd.read_csv('data/processed/medellin_displacement_index.csv')

barrios['codigo'] = barrios['codigo'].astype(str).str.zfill(4)
index_df['codigo'] = index_df['codigo'].astype(str).str.zfill(4)

merged = barrios.merge(index_df, on='codigo', how='left')
index_df = index_df.drop(columns=['nombre_barrio', 'comuna'])

# Merge density and estrato on 'comuna' (how='left', since every barrio should find a match)
merged = barrios.merge(index_df, on='codigo', how='left')

# Base map, centered roughly on Medellín
m = folium.Map(location=[6.2442, -75.5812], zoom_start=12, tiles='cartodbpositron')

# Layer 1: the colored choropleth itself
folium.Choropleth(
    geo_data=merged,
    data=merged,
    columns=['codigo', 'displacement_risk_index'],
    key_on='feature.properties.codigo',
    fill_color='RdYlBu_r',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Displacement Risk Index',
    nan_fill_color='lightgray',
).add_to(m)

# Layer 2: an invisible layer on top, just for hover tooltips
folium.GeoJson(
    merged,
    style_function=lambda x: {'fillOpacity': 0, 'weight': 0},
    tooltip=folium.GeoJsonTooltip(
        fields=['nombre_barrio', 'comuna', 'displacement_risk_index'],
        aliases=['Barrio:', 'Comuna:', 'Risk Index:'],
        localize=True,
    ),
).add_to(m)

m.save('data/processed/medellin_choropleth.html')
print("Map saved! Open data/processed/medellin_choropleth.html in your browser.")