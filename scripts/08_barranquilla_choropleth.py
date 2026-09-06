from map_builder import build_map, load_merged_data

merged = load_merged_data('barranquilla')
m = build_map(merged, city='barranquilla', map_type='composite')
m.save('data/processed/barranquilla_choropleth.html')
print("Map saved! Open data/processed/barranquilla_choropleth.html in your browser.")