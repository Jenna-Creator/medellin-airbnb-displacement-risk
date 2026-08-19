import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load barrio boundaries, forcing codigo to stay a string (avoids losing leading zeros)
raw = json.load(open('data/geo/medellin_barrios_all.geojson'))
for feature in raw['features']:
    feature['properties']['codigo'] = str(feature['properties']['codigo']).zfill(4)
barrios = gpd.GeoDataFrame.from_features(raw['features'], crs="EPSG:4326")

# Load your cleaned listings and keep only Medellín ones for now
listings = pd.read_csv('data/processed/listings_clean.csv')
listings = listings[listings['city'] == 'Medellin']

# Turn each listing's (lon, lat) into a shapely Point, then build a GeoDataFrame
geometry = [Point(xy) for xy in zip(listings['lon'], listings['lat'])]
points_gdf = gpd.GeoDataFrame(listings, geometry=geometry, crs="EPSG:4326")

# Spatial join — for each listing point, find which barrio polygon contains it
joined = gpd.sjoin(points_gdf, barrios, how='left', predicate='within')

# Count how many listings landed in each barrio
counts = joined.groupby('codigo').size().reset_index(name='listing_count')

# Merge those counts back onto the barrios GeoDataFrame, filling barrios with no listings to 0
barrios = barrios.merge(counts, on='codigo', how='left')
barrios['listing_count'] = barrios['listing_count'].fillna(0)

# Reproject to UTM 18N just to calculate area in km²
barrios_utm = barrios.to_crs(epsg=32618)
barrios['area_km2'] = barrios_utm.geometry.area / 1_000_000

# Compute density_per_km2 = listing_count / area_km2
barrios['density_per_km2'] = barrios['listing_count'] / barrios['area_km2']

barrios.drop(columns='geometry').to_csv('data/processed/medellin_barrio_density.csv', index=False)
print(barrios[['nombre_barrio', 'listing_count', 'area_km2', 'density_per_km2']].sort_values('density_per_km2', ascending=False).head(10))