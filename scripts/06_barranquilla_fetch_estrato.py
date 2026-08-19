import requests
import pandas as pd

BASE_URL = "https://services3.arcgis.com/oGYAc07w6wsvgUYr/arcgis/rest/services/ESTRATO_1994/FeatureServer/0/query"

all_records = []
offset = 0
batch_size = 2000

while True:
    params = {
        "where": "1=1",
        "outFields": "BARRIOS202,ESTRATO",
        "returnGeometry": "false",
        "resultRecordCount": batch_size,
        "resultOffset": offset,
        "orderByFields": "FID",
        "f": "json"
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    features = data["features"]

    if not features:
        break

    for feature in features:
        all_records.append(feature["attributes"])

    print(f"Fetched {len(all_records)} records so far...")
    offset += batch_size

    if not data.get("exceededTransferLimit", False):
        break

df = pd.DataFrame(all_records)
df.columns = ['barrio', 'estrato']
df['estrato'] = df['estrato'].astype(int)

# Group by 'barrio', and for each barrio find its most common 'estrato' value
summary = df.groupby('barrio')['estrato'].agg(lambda x: x.value_counts().index[0]).reset_index()

summary.columns = ['barrio', 'estrato_predominante']
summary.to_csv('data/raw/barranquilla_barrio_estrato.csv', index=False)
print(summary.sort_values('estrato_predominante').head(10))