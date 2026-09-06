from map_builder import build_map, load_merged_data

merged = load_merged_data('medellin')
m = build_map(merged, city='medellin', map_type='housing_saturation')
m.save('data/processed/medellin_housing_saturation_map.html')
print("Saved data/processed/medellin_housing_saturation_map.html")