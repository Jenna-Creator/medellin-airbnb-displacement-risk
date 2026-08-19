import pandas as pd
import numpy as np

density = pd.read_csv('data/processed/barranquilla_barrio_density.csv')
estrato = pd.read_csv('data/raw/barranquilla_barrio_estrato.csv')

# Merge density and estrato on 'barrio', how='left' (same pattern as script 04)
df = df = density.merge(estrato, on='barrio', how='left')

# Log-transform density_per_km2, then z-score both log_density and estrato_predominante
# same three lines as script 04
df['log_density'] = np.log1p(df['density_per_km2'])
df['z_density'] = (df['log_density'] - df['log_density'].mean()) / df['log_density'].std()
df['z_estrato'] = (df['estrato_predominante'] - df['estrato_predominante'].mean()) / df['estrato_predominante'].std()

# Composite index = z_density minus z_estrato
df['displacement_risk_index'] = df['z_density'] - df['z_estrato']

df = df.sort_values('displacement_risk_index', ascending=False)
df.to_csv('data/processed/barranquilla_displacement_index.csv', index=False)
print(df[['barrio', 'localidad', 'density_per_km2', 'estrato_predominante', 'displacement_risk_index']].head(10))