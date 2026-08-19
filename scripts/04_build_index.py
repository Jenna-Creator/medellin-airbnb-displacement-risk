import pandas as pd
import numpy as np

density = pd.read_csv('data/processed/medellin_barrio_density.csv')
estrato = pd.read_csv('data/raw/comuna_estrato.csv')

# Merge density and estrato on 'comuna' (how='left', since every barrio should find a match)
df = density.merge(estrato, on='comuna', how='left')

# Create a log-transformed density column
df['log_density'] = np.log1p(df['density_per_km2'])

# Z-score log_density and estrato_predominante
df['z_density'] = (df['log_density'] - df['log_density'].mean()) / df['log_density'].std()
df['z_estrato'] = (df['estrato_predominante'] - df['estrato_predominante'].mean()) / df['estrato_predominante'].std()

# Compute the composite index
df['displacement_risk_index'] = df['z_density'] - df['z_estrato']

df = df.sort_values('displacement_risk_index', ascending=False)
df.to_csv('data/processed/medellin_displacement_index.csv', index=False)
print(df[['nombre_barrio', 'comuna', 'density_per_km2', 'estrato_predominante', 'displacement_risk_index']].head(10))