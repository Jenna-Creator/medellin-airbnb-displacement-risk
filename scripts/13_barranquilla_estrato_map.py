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

import sys
sys.path.append('scripts')
from map_builder import build_map

m = build_map(merged, city='barranquilla', map_type='estrato')
m.save('data/processed/barranquilla_estrato_map.html')
print("Map saved! Open data/processed/barranquilla_estrato_map.html in your browser.")