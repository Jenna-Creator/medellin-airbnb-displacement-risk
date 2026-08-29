# Airbnb Displacement Risk — Medellín & Barranquilla

A data pipeline that flags neighborhoods where short-term rental (Airbnb) growth is concentrated in historically low-income areas — a pattern often associated with tourism-driven displacement of long-term residents.

## Explore the maps

**Option 1 — Streamlit app (recommended):** run `streamlit run app.py` from the repo root for an interactive dropdown that lets you switch between both cities and all three map types (Displacement Risk Index, Airbnb Density, Predominant Estrato) in one page. Requires `pip3 install streamlit streamlit-folium` first (in addition to the packages below).

**Option 2 — static HTML links:** click any link below to view a standalone version of each map via [raw.githack.com](https://raw.githack.com) (GitHub itself only shows HTML files as source code, not rendered).

**Displacement risk index (the main result):**
- [Medellín](https://raw.githack.com/Jenna-Creator/medellin-airbnb-displacement-risk/main/data/processed/medellin_choropleth.html)
- [Barranquilla](https://raw.githack.com/Jenna-Creator/medellin-airbnb-displacement-risk/main/data/processed/barranquilla_choropleth.html)

**Inputs to the index, mapped separately** — useful for seeing what goes into the composite score before looking at the combined result:
- [Medellín — Airbnb density (log scale)](https://raw.githack.com/Jenna-Creator/medellin-airbnb-displacement-risk/main/data/processed/medellin_airbnb_density_map.html)
- [Medellín — predominant estrato](https://raw.githack.com/Jenna-Creator/medellin-airbnb-displacement-risk/main/data/processed/medellin_estrato_map.html)
- [Barranquilla — Airbnb density (log scale)](https://raw.githack.com/Jenna-Creator/medellin-airbnb-displacement-risk/main/data/processed/barranquilla_airbnb_density_map.html)
- [Barranquilla — predominant estrato](https://raw.githack.com/Jenna-Creator/medellin-airbnb-displacement-risk/main/data/processed/barranquilla_estrato_map.html)

Every map (Streamlit or static) includes an on-map title box explaining what you're looking at, hover tooltips with the underlying numbers per barrio, and click popups with additional detail — no need to leave the map to understand what a color or score means.

## Problem statement

Colombia's two largest coastal-adjacent cities, Medellín and Barranquilla, have both seen sharp growth in short-term rental listings over the past several years. A common concern raised about this growth — in Medellín especially, around neighborhoods like Comuna 13 (San Javier) — is that it drives up housing costs and displaces long-term residents once a historically low-income area becomes a tourist draw.

Raw listing counts alone don't distinguish between two very different stories: a wealthy neighborhood absorbing a large volume of tourists (an overtourism/saturation problem) versus a low-income neighborhood absorbing a smaller but fast-growing share of tourist rentals (a displacement-risk problem). This project builds a simple, transparent index designed to separate those two patterns.

## How the index was designed

Each barrio (neighborhood) gets scored on two things:

1. **Airbnb listing density** — active listings per km², from a citywide Apify scrape.
2. **Estrato** — Colombia's official socioeconomic stratification scale (1 = lowest income, 6 = highest), originally created for progressive utility billing and now used widely as a proxy for neighborhood income level.

The **Displacement Risk Index** is a difference of z-scores:

```
displacement_risk_index = z(log(density_per_km2 + 1)) − z(estrato)
```

A few design choices, and why:

- **Log-transforming density** before scoring it. Raw density is heavily skewed — a handful of barrios have 1,000+ listings/km² while most have single digits or zero — so a log transform keeps a few extreme outliers from swamping the whole distribution.
- **Z-scoring both variables** puts density (roughly 0–1,700+) and estrato (1–6) on the same scale before comparing them, since they'd otherwise be incomparable units.
- **Subtracting** the two z-scores captures *mismatch*, not raw volume. A high score means unusually high rental density paired with unusually low estrato — the specific combination associated with displacement pressure. A wealthy, high-density neighborhood (like El Poblado) and a poor, low-density one both score near zero; only the poor-and-high-density combination scores high.

This is a relative screening tool, not a causal claim — a high score flags a neighborhood worth a closer look, not proof that displacement is happening there.

## Data pipeline

Raw data → clean/dedupe → spatial join → estrato merge/index → interactive maps. Each stage is its own script under `scripts/`, meant to be run in order:

| Script | What it does |
|---|---|
| `01_clean_scrapes.py` | Loads all raw Apify JSON exports from `data/raw/`, extracts fields (coordinates, price, room type, reviews), deduplicates by listing ID, and routes each listing to Medellín or Barranquilla by latitude. Outputs `data/processed/listings_clean.csv`. |
| `02_spatial_join.py` | Point-in-polygon join of Medellín listings against `data/geo/medellin_barrios_all.geojson` (265 barrios across 16 comunas). Computes area in km² (reprojected to UTM 18N) and density. Outputs `data/processed/medellin_barrio_density.csv`. |
| `03_barranquilla_spatial_join.py` | Same join, run against `data/geo/barranquilla_barrios.geojson` (189 barrios across 5 localidades, blank/unclassified polygons filtered out). Outputs `data/processed/barranquilla_barrio_density.csv`. |
| `04_build_index.py` | Merges `data/raw/comuna_estrato.csv` onto the Medellín density table by comuna, then computes the composite displacement risk index. Outputs `data/processed/medellin_displacement_index.csv`. |
| `05_choropleth.py` | Builds the interactive Folium/Leaflet map of Medellín's composite index (via `map_builder.py`). Outputs `data/processed/medellin_choropleth.html`. |
| `06_barranquilla_fetch_estrato.py` | Pages through Barranquilla's `ESTRATO_1994` ArcGIS FeatureServer (175K+ parcel-level records), then groups by barrio to find each one's predominant estrato. Outputs `data/raw/barranquilla_barrio_estrato.csv`. |
| `07_barranquilla_build_index.py` | Same composite-index logic as script 04, applied to Barranquilla's density and estrato tables, joined on barrio name. Outputs `data/processed/barranquilla_displacement_index.csv`. |
| `08_barranquilla_choropleth.py` | Same as script 05, for Barranquilla's composite index. Outputs `data/processed/barranquilla_choropleth.html`. |
| `09_barranquilla_refetch_boundaries.py` | Replaces the original 91-barrio boundary file with a more complete 189-barrio layer from Barranquilla's current land-use plan (POT), fetched directly as GeoJSON. Outputs `data/geo/barranquilla_barrios.geojson`. |
| `10_medellin_airbnb_density_map.py` | Maps Medellín's Airbnb density alone (log scale), one of the two inputs to the composite index, so readers can see it before the combined result. Outputs `data/processed/medellin_airbnb_density_map.html`. |
| `11_medellin_estrato_map.py` | Maps Medellín's predominant estrato alone. Outputs `data/processed/medellin_estrato_map.html`. |
| `12_barranquilla_airbnb_density_map.py` | Same as script 10, for Barranquilla. Outputs `data/processed/barranquilla_airbnb_density_map.html`. |
| `13_barranquilla_estrato_map.py` | Same as script 11, for Barranquilla. Outputs `data/processed/barranquilla_estrato_map.html`. |

`map_builder.py` is a shared module (not run directly) used by scripts 05, 08, and 10–13, plus `app.py`. It centralizes the actual map-building — the on-map title box, color scales, hover tooltips, and click popups — in one place, so all six maps (static or in the Streamlit app) render consistently and only need to be fixed or updated in one spot.

`app.py` is the Streamlit app described above.

`run_all.sh` reruns every script in `scripts/` in order (`01` through `13`), regenerating the full pipeline and all six static maps in one command.

Source data:

- **Airbnb listings** — scraped via the Apify `tri_angle/airbnb-scraper` actor, run separately per comuna (Medellín) and localidad (Barranquilla) to stay within result limits.
- **Barrio/comuna boundaries** — official GeoJSON layers from Medellín's GeoMedellín catalog and Barranquilla's Secretaría Distrital de Planeación (via their public ArcGIS Feature Services).
- **Estrato (Medellín)** — Encuesta de Calidad de Vida (ECV), a household survey published per comuna by the Alcaldía de Medellín. No public dataset breaks estrato down below the comuna level, which is a limitation below.
- **Estrato (Barranquilla)** — `ESTRATO_1994`, a parcel-level stratification layer published by Barranquilla's Secretaría Distrital de Planeación (via ArcGIS Feature Service). Despite the "1994" name — a reference to Law 142 of 1994, which created Colombia's estrato system — the layer is actively maintained; edit timestamps show updates as recent as 2025. This is more granular than Medellín's comuna-level estrato: each barrio's predominant stratum is computed directly from its own parcels rather than inherited from a larger area.

## Results

**Medellín — Comuna 13 (San Javier) tops the index.** The five highest-risk barrios are San Javier No. 2, San Javier No. 1, Los Alcázares, La Pradera, and Veinte de Julio — all in Comuna 13, the lowest-estrato comuna in the dataset (estrato 1) and home to the Comuna 13 Graffitour, now one of the city's most-visited tourist attractions. This lines up with widely reported concerns about tourism-driven gentrification specifically in Comuna 13.

Other barrios flagging as elevated-risk: San Miguel (Villa Hermosa), El Nogal-Los Almendros and Rosales (Belén), and Barrio Caicedo (Buenos Aires) — all mid-to-low estrato comunas absorbing a small but meaningful share of the city's tourist rentals.

**El Poblado is the opposite pattern.** It holds by far the most listings in absolute terms — roughly a third of the city's total — but scores *low* on the index, because it's also uniformly high-estrato (5–6). Its Airbnb boom is concentrated in an already-wealthy area, which reads as overtourism/saturation rather than displacement of low-income residents. Comuna 13's smaller, faster-growing presence in the city's poorest comuna is the more direct displacement signal.

**Barranquilla — Norte Centro Histórico and Suroccidente top the index.** The highest-risk barrios are San Luis (estrato 1), El Rosario and San Francisco (estrato 2, Norte Centro Histórico), and Ciudad Modesto and La Paz (estrato 1, Suroccidente) — all low-estrato barrios absorbing a disproportionate share of Airbnb listings relative to their income level.

This mirrors Medellín's pattern in an interesting way: Riomar, Barranquilla's wealthiest and most Airbnb-saturated localidad (Villa del Este, El Poblado, Altos del Limón), holds the most listings in raw density terms but doesn't dominate the risk index, because it's also uniformly high-estrato — the same overtourism-vs-displacement contrast El Poblado shows in Medellín. The displacement signal instead shows up in lower-estrato, lower-density barrios where Airbnb's presence is smaller in absolute terms but large relative to the neighborhood's income level.

## Limitations

- **Estrato granularity**: estrato is only available at the comuna level for Medellín — no public barrio-level dataset exists. Every barrio within a comuna shares one estrato value, so real intra-comuna variation isn't captured.
- **Villa Hermosa's estrato** is an approximation — its source data reports "estrato 1+2" combined without breaking the two apart.
- **Point-in-time snapshot**: the Airbnb data reflects listings active at scrape time, not year-over-year growth, since Apify's search-based scraper doesn't expose new-listing history.
- **Spatial match rate**: a small share of geocoded listings fall outside the barrio boundary set (mostly rural corregimientos not covered here) and are dropped from the density calculation.
- **Scraper budget cap**: the Apify scrape was run separately per comuna/localidad (avoiding cross-neighborhood competition for one shared budget), but if any single comuna's true listing count exceeded that comuna's individual cap, its listings would still be undercounted relative to its real size. Worth spot-checking Apify's run logs for the highest-volume comunas (e.g., El Poblado) to confirm each run completed naturally rather than hitting its limit.
- **Estrato sample size (Barranquilla)**: some barrios have very few parcels in the estrato dataset, making their "predominant" value less statistically reliable than barrios with hundreds of parcels.
- **Comuna vs. barrio naming (Medellín)**: "El Poblado" is both a comuna (a large, popularly-known district) and the name of one small barrio inside it. The choropleth's barrio-level tooltip for "El Poblado" only reflects that one small polygon — the area people usually mean by "El Poblado" is spread across many separately-named barrios (Provenza, Manila, Castropol, El Tesoro, etc.), which is where most of that comuna's Airbnb listings actually show up.

## Repo structure

```
data/
  raw/          Raw Apify scrapes, comuna_estrato.csv (Medellín), barranquilla_barrio_estrato.csv
  geo/          Barrio/localidad boundary GeoJSON files (Medellín + Barranquilla)
  processed/    Cleaned listings, density tables, displacement indices, and all six maps
scripts/
  01_clean_scrapes.py
  02_spatial_join.py
  03_barranquilla_spatial_join.py
  04_build_index.py
  05_choropleth.py
  06_barranquilla_fetch_estrato.py
  07_barranquilla_build_index.py
  08_barranquilla_choropleth.py
  09_barranquilla_refetch_boundaries.py
  10_medellin_airbnb_density_map.py
  11_medellin_estrato_map.py
  12_barranquilla_airbnb_density_map.py
  13_barranquilla_estrato_map.py
  map_builder.py     Shared map-building + data-loading module used by scripts 05, 08, 10-13, and app.py
app.py                Streamlit app with a dropdown to explore all six maps in one page
run_all.sh
```

## Tools

Python, pandas, geopandas, shapely, Folium, Streamlit (`streamlit` + `streamlit-folium`). Data sourced via Apify (Airbnb scraper) and each city's official open-GIS ArcGIS Feature Services.
