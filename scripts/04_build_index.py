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

# z-scoring equalizes standard deviation, not range -- pct_homes_on_airbnb stays
# fat-tailed even after a log transform (one barrio at 145% vs a bounded 1-6
# estrato scale), so a z-score lets a single extreme saturation value dominate
# the index regardless of estrato. Percentile ranks are bounded to [0, 1] for
# both variables no matter how skewed the underlying values are, so an outlier
# can only push its own rank to the top -- not to an arbitrarily large number
# that swamps estrato's side of the subtraction.
df['saturation_rank'] = df['pct_homes_on_airbnb'].rank(pct=True, ascending=True)
df['estrato_rank'] = df['estrato_predominante'].rank(pct=True, ascending=True)
df['displacement_risk_index'] = df['saturation_rank'] - df['estrato_rank']

df = df.sort_values('displacement_risk_index', ascending=False)
df.to_csv('data/processed/medellin_displacement_index.csv', index=False)
print(df[['nombre_barrio', 'comuna', 'pct_homes_on_airbnb', 'estrato_predominante', 'displacement_risk_index']].head(10))