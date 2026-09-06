import pandas as pd
import numpy as np

density = pd.read_csv('data/processed/medellin_barrio_density.csv')
estrato = pd.read_csv('data/raw/comuna_estrato.csv')
housing = pd.read_csv('data/raw/medellin_barrio_housing.csv')

density['codigo'] = density['codigo'].astype(str).str.zfill(4)
housing['codigo'] = housing['codigo'].astype(str).str.zfill(4)

df = density.merge(estrato, on='comuna', how='left')
df = df.merge(housing, on='codigo', how='left')

df['log_density'] = np.log1p(df['density_per_km2'])

df['pct_homes_on_airbnb'] = (df['listing_count'] / df['total_viviendas']) * 100
df['pct_homes_on_airbnb'] = df['pct_homes_on_airbnb'].replace([np.inf, -np.inf], np.nan)

# barrios with very few counted housing units produce statistically unstable
# ratios -- a single listing can swing the percentage wildly. Treat those as
# missing data rather than letting a tiny denominator produce a misleading number.
MIN_VIVIENDAS = 50
df.loc[df['total_viviendas'] < MIN_VIVIENDAS, 'pct_homes_on_airbnb'] = np.nan

df['log_pct_homes'] = np.log1p(df['pct_homes_on_airbnb'])
df['z_penetration'] = (df['log_pct_homes'] - df['log_pct_homes'].mean()) / df['log_pct_homes'].std()
df['z_estrato'] = (df['estrato_predominante'] - df['estrato_predominante'].mean()) / df['estrato_predominante'].std()
df['displacement_risk_index'] = df['z_penetration'] - df['z_estrato']

df = df.sort_values('displacement_risk_index', ascending=False)
df.to_csv('data/processed/medellin_displacement_index.csv', index=False)
print(df[['nombre_barrio', 'comuna', 'pct_homes_on_airbnb', 'estrato_predominante', 'displacement_risk_index']].head(10))