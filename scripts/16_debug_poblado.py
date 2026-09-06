import geopandas as gpd

barrios = gpd.read_file('data/geo/medellin_barrios_all.geojson')
poblado = barrios[barrios['nombre_barrio'] == 'El Poblado']
print(poblado[['nombre_barrio', 'comuna']])
print(f"Area: {poblado.to_crs(epsg=32618).geometry.area.values[0] / 1e6:.3f} km2")

blocks = gpd.read_file('data/raw/dane_housing_blocks.geojson')
medellin_blocks = blocks[blocks['city'] == 'medellin']
matched = gpd.sjoin(medellin_blocks, poblado, how='inner', predicate='within')
print(f"{len(matched)} DANE blocks matched to El Poblado")
print(matched['TVIVIENDA'].tolist())