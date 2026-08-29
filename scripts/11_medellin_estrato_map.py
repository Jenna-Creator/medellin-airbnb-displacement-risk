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
import sys
sys.path.append('scripts')
from map_builder import build_map

m = build_map(merged, city='medellin', map_type='estrato')
m.save('data/processed/medellin_estrato_map.html')
print("Map saved! Open data/processed/medellin_estrato_map.html in your browser.")