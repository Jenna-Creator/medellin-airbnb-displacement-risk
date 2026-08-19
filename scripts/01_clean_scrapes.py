import json
import glob
import re
import pandas as pd

def extract_fields(record):
    coords = record.get('coordinates') or {}
    lat = coords.get('latitude')
    lon = coords.get('longitude')

    price = record.get('price') or {}
    breakdown = price.get('breakDown') or {}
    base_price = breakdown.get('basePrice') or {}
    price_text = base_price.get('description')
    if price_text:
        match = re.search(r'x \$([\d,.]+)', price_text)
        nightly_usd = float(match.group(1).replace(',', '')) if match else None
    else:
        nightly_usd = None

    rating = record.get('rating') or {}

    if lat is not None and lat < 8:
        city = 'Medellin'
    elif lat is not None and lat >= 8:
        city = 'Barranquilla'
    else:
        city = 'Unknown'

    return {
        "id": record['id'],
        "lat": lat,
        "lon": lon,
        "room_type": record['roomType'],
        "property_type": record['propertyType'],
        "reviews_count": rating.get('reviewsCount', 0),
        "nightly_usd": nightly_usd,
        "city": city,
    }

def load_file(filepath):
    with open(filepath) as f:
        records = json.load(f)
    return [extract_fields(r) for r in records]

# --- main script ---
all_listings = []
unknown_locations = set()
for filepath in glob.glob('data/raw/*.json'):
    all_listings.extend(load_file(filepath))

print("total records read:", len(all_listings))

by_id = {}
for listing in all_listings:
    by_id[listing['id']] = listing

df = pd.DataFrame(list(by_id.values()))
df = df.dropna(subset=['lat', 'lon'])
df.to_csv('data/processed/listings_clean.csv', index=False)

print("unique after dedupe:", len(df))
print(df['city'].value_counts())
print("\nsample unrecognized locations:")
for loc in list(unknown_locations)[:20]:
    print(" ", loc)