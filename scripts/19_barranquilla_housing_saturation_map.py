from map_builder import build_map, load_merged_data

merged = load_merged_data('barranquilla')
m = build_map(merged, city='barranquilla', map_type='housing_saturation')
m.save('data/processed/barranquilla_housing_saturation_map.html')
print("Saved data/processed/barranquilla_housing_saturation_map.html")