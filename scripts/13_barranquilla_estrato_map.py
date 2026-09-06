from map_builder import build_map, load_merged_data

merged = load_merged_data('barranquilla')
m = build_map(merged, city='barranquilla', map_type='estrato')
m.save('data/processed/barranquilla_estrato_map.html')
print("Map saved! Open data/processed/barranquilla_estrato_map.html in your browser.")