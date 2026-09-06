from map_builder import build_map, load_merged_data

merged = load_merged_data('medellin')
m = build_map(merged, city='medellin', map_type='composite')
m.save('data/processed/medellin_choropleth.html')
print("Map saved! Open data/processed/medellin_choropleth.html in your browser.")