import requests
import json

BASE_URL = "https://services3.arcgis.com/oGYAc07w6wsvgUYr/arcgis/rest/services/Mapa_Capas_POT_WFL1/FeatureServer/202/query"

params = {
    "where": "1=1",
    "outFields": "NOMBRE,LOCALIDAD,AREA_HAS",
    "f": "geojson"
}
response = requests.get(BASE_URL, params=params)
data = response.json()

# rename fields to match what scripts 03/07/08 already expect
for feature in data["features"]:
    props = feature["properties"]
    props["barrio"] = props.pop("NOMBRE")
    props["localidad"] = props.pop("LOCALIDAD")
    props["area_has"] = props.pop("AREA_HAS")

with open("data/geo/barranquilla_barrios.geojson", "w") as f:
    json.dump(data, f)

print(f"Saved {len(data['features'])} barrio polygons.")