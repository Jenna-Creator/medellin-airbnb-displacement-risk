import geopandas as gpd

blocks = gpd.read_file('data/raw/dane_housing_blocks.geojson')

CITY_FILES = {
    'medellin': 'data/geo/medellin_barrios_all.geojson',
    'barranquilla': 'data/geo/barranquilla_barrios.geojson',
}

for city, barrio_path in CITY_FILES.items():
    city_blocks = blocks[blocks['city'] == city]
    barrios = gpd.read_file(barrio_path)

    if city == 'medellin':
        barrios['codigo'] = barrios['codigo'].astype(str).str.zfill(4)
        key_field = 'codigo'
    else:
        key_field = 'barrio'

    joined = gpd.sjoin(city_blocks, barrios, how='left', predicate='within')

    # Group by key_field and sum the 'TVIVIENDA' column
    # same groupby().sum() pattern as script 03's density groupby, just summing
    # a housing-count column instead of counting rows
    housing = joined.groupby(key_field)['TVIVIENDA'].sum().reset_index()
    housing.columns = [key_field, 'total_viviendas']

    output_path = f'data/raw/{city}_barrio_housing.csv'
    housing.to_csv(output_path, index=False)
    print(f"{city}: saved {len(housing)} barrios")
    print(housing.sort_values('total_viviendas', ascending=False).head())