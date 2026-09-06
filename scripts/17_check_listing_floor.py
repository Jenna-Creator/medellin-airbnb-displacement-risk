import pandas as pd

for city in ['medellin', 'barranquilla']:
    print(f"--- {city} ---")
    df = pd.read_csv(f'data/processed/{city}_displacement_index.csv')
    top = df.sort_values('displacement_risk_index', ascending=False).head(15)
    print(top[['listing_count', 'pct_homes_on_airbnb', 'displacement_risk_index']])
    print()