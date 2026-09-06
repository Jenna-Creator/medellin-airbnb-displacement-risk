import geopandas as gpd

path = 'data/raw/dane_manzanas.gpkg'
blocks = gpd.read_file(
    path,
    layer='MGN_ANM_MANZANA (Geopackage)',
    where="DPTO_CCDGO IN ('05','08') AND MPIO_CCDGO='001'"
)

# Keep only the columns we actually need: 'DPTO_CCDGO', 'TVIVIENDA', and 'geometry'
# same subsetting pattern you've used before, e.g. df[['col1', 'col2']]
blocks = blocks[['DPTO_CCDGO','TVIVIENDA','geometry']]

# tag each block with which city it belongs to, based on its department code
blocks['city'] = blocks['DPTO_CCDGO'].map({'05': 'medellin', '08': 'barranquilla'})

# reproject to a flat, meters-based CRS before computing centroids (same UTM zone
# scripts 02/03 already use for area calculations), then reproject back to
# lat/lon so it matches the barrio boundary files for the spatial join later
blocks = blocks.to_crs(epsg=32618)
blocks['geometry'] = blocks.geometry.centroid
blocks = blocks.to_crs(epsg=4326)


blocks.to_file('data/raw/dane_housing_blocks.geojson', driver='GeoJSON')
print(blocks['city'].value_counts())
print(f"Saved {len(blocks)} block centroids with housing counts.")