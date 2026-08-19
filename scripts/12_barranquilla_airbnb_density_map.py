import pandas as pd
import geopandas as gpd
import folium

barrios = gpd.read_file('data/geo/barranquilla_barrios.geojson')
index_df = pd.read_csv('data/processed/barranquilla_displacement_index.csv')

# index_df already has a 'localidad' column, and so does barrios --
# drop it from index_df before merging so they don't collide (same fix as script 05)
index_df = index_df.drop(columns=['localidad'])

# Merge barrios and index_df on 'barrio', how='left'
# (same pattern as script 05, but no zfill needed this time -- 'barrio' is
# already a clean matching string on both sides)
merged = barrios.merge(index_df, on='barrio', how='left')

m = folium.Map(location=[10.9685, -74.7813], zoom_start=12.5, zoom_snap=0.25, tiles='cartodbpositron')

folium.Choropleth(
    geo_data=merged,
    data=merged,
    columns=['barrio', 'log_density'],
    key_on='feature.properties.barrio',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Airbnb Listings per km² (log scale)',
    nan_fill_color='lightgray',
).add_to(m)

folium.GeoJson(
    merged,
    style_function=lambda x: {'fillOpacity': 0, 'weight': 0},
    tooltip=folium.GeoJsonTooltip(
        fields=['barrio', 'localidad', 'estrato_predominante', 'listing_count', 'displacement_risk_index'],
        aliases=['Barrio:', 'Localidad:', 'Estrato:', 'Airbnb Listings:', 'Risk Index:'],
        localize=True,
    ),
).add_to(m)

m.save('data/processed/barranquilla_airbnb_density_map.html')
print("Map saved! Open data/processed/barranquilla_airbnb_density_map.html in your browser.")