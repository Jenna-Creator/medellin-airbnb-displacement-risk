import geopandas as gpd
import pandas as pd
import unicodedata
import re

def normalize(name):
    name = str(name).strip().upper()
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('utf-8')
    name = re.sub(r'[^A-Z0-9 ]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

barrios = gpd.read_file('data/geo/barranquilla_barrios.geojson')
estrato = pd.read_csv('data/raw/barranquilla_barrio_estrato.csv')

boundary_names = set(barrios['barrio'])
estrato_names = set(estrato['barrio'])

missing = boundary_names - estrato_names
print(f"{len(missing)} boundary barrios have no exact-match estrato row:\n")

# normalized lookup on the estrato side, to spot likely typo-twins
norm_to_estrato = {}
for name in estrato_names:
    norm_to_estrato.setdefault(normalize(name), []).append(name)

for name in sorted(missing):
    candidates = norm_to_estrato.get(normalize(name), [])
    if candidates:
        print(f"  {name!r:35} -> likely match in estrato data: {candidates}")
    else:
        print(f"  {name!r:35} -> NO close match found at all")