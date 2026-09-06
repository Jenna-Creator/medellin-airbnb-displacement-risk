from map_builder import build_map, load_merged_data

merged = load_merged_data('medellin')
m = build_map(merged, city='medellin', map_type='estrato')
m.save('data/processed/medellin_estrato_map.html')
print("Map saved! Open data/processed/medellin_estrato_map.html in your browser.")