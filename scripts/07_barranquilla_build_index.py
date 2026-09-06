import pandas as pd
import numpy as np

density = pd.read_csv('data/processed/barranquilla_barrio_density.csv')
estrato = pd.read_csv('data/raw/barranquilla_barrio_estrato.csv')
housing = pd.read_csv('data/raw/barranquilla_barrio_housing.csv')

df = density.merge(estrato, on='barrio', how='left')
df = df.merge(housing, on='barrio', how='left')

df['log_density'] = np.log1p(df['density_per_km2'])

df['pct_homes_on_airbnb'] = (df['listing_count'] / df['total_viviendas']) * 100
df['pct_homes_on_airbnb'] = df['pct_homes_on_airbnb'].replace([np.inf, -np.inf], np.nan)

# barrios with very little counted housing stock (industrial parks, free-trade
# zones) produce unstable ratios -- treat those as missing rather than real signal
MIN_VIVIENDAS = 100
df.loc[df['total_viviendas'] < MIN_VIVIENDAS, 'pct_homes_on_airbnb'] = np.nan

# log1p-transform pct_homes_on_airbnb into 'log_pct_homes'
df['log_pct_homes'] = np.log1p(df['pct_homes_on_airbnb'])
# z-score log_pct_homes into 'z_penetration' (same pattern as z_estrato below)
df['z_penetration'] = (df['log_pct_homes'] - df['log_pct_homes'].mean()) / df['log_pct_homes'].std()
df['z_estrato'] = (df['estrato_predominante'] - df['estrato_predominante'].mean()) / df['estrato_predominante'].std()

df['displacement_risk_index'] = df['z_penetration'] - df['z_estrato']

df = df.sort_values('displacement_risk_index', ascending=False)
df.to_csv('data/processed/barranquilla_displacement_index.csv', index=False)
print(df[['barrio', 'localidad', 'pct_homes_on_airbnb', 'estrato_predominante', 'displacement_risk_index']].head(10))