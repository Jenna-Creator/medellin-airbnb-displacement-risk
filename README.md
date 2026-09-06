# Airbnb Displacement Risk — Medellín & Barranquilla

A data pipeline that flags neighborhoods where short-term rental (Airbnb) growth is concentrated in historically low-income areas — a pattern often associated with tourism-driven displacement of long-term residents.

## Explore the maps

**Live app (recommended):** [medellin-airbnb-displacement-risk-8zpij5vbtjx4vffmfuhhpw.streamlit.app](https://medellin-airbnb-displacement-risk-8zpij5vbtjx4vffmfuhhpw.streamlit.app) — loads directly to the Displacement Risk Index map for whichever city you pick. A language toggle (English/Español) sits at the top. The other three map types — Airbnb Housing Saturation, Predominant Estrato, and Airbnb Density (a reference map, not used in the index) — are available in a collapsed expander below the results, so the index is what you see first.

**Run it locally instead:** `pip3 install -r requirements.txt`, then `streamlit run app.py` from the repo root.

**Static HTML links** (fallback, one map per link): click any link below to view a standalone version of each map via [raw.githack.com](https://raw.githack.com) (GitHub itself only shows HTML files as source code, not rendered).

**Displacement risk index (the main result):**
- [Medellín](https://raw.githack.com/Jenna-Creator/medellin-airbnb-displacement-risk/main/data/processed/medellin_choropleth.html)
- [Barranquilla](https://raw.githack.com/Jenna-Creator/medellin-airbnb-displacement-risk/main/data/processed/barranquilla_choropleth.html)

**Inputs to the index, mapped separately** — useful for seeing what goes into the composite score before looking at the combined result:
- [Medellín — Airbnb housing saturation (log scale)](https://raw.githack.com/Jenna-Creator/medellin-airbnb-displacement-risk/main/data/processed/medellin_housing_saturation_map.html)
- [Medellín — predominant estrato](https://raw.githack.com/Jenna-Creator/medellin-airbnb-displacement-risk/main/data/processed/medellin_estrato_map.html)
- [Barranquilla — Airbnb housing saturation (log scale)](https://raw.githack.com/Jenna-Creator/medellin-airbnb-displacement-risk/main/data/processed/barranquilla_housing_saturation_map.html)
- [Barranquilla — predominant estrato](https://raw.githack.com/Jenna-Creator/medellin-airbnb-displacement-risk/main/data/processed/barranquilla_estrato_map.html)

**Reference map, not used in the index** — the original land-area-based density metric, kept for comparison:
- [Medellín — Airbnb density (log scale)](https://raw.githack.com/Jenna-Creator/medellin-airbnb-displacement-risk/main/data/processed/medellin_airbnb_density_map.html)
- [Barranquilla — Airbnb density (log scale)](https://raw.githack.com/Jenna-Creator/medellin-airbnb-displacement-risk/main/data/processed/barranquilla_airbnb_density_map.html)

Every map (live app or static) includes an on-map title box explaining what you're looking at, and hover/click details with the underlying numbers per barrio — no need to leave the map to understand what a color or score means.

## Problem statement

Colombia's two largest cities, Medellín and Barranquilla, have both seen sharp growth in short-term rental listings over the past several years. A common concern raised about this growth — in Medellín especially, around neighborhoods like Comuna 13 (San Javier) — is that it drives up housing costs and displaces long-term residents once a historically low-income area becomes a tourist draw.

Raw listing counts alone don't distinguish between two very different stories: a wealthy neighborhood absorbing a large volume of tourists (an overtourism/saturation problem) versus a low-income neighborhood absorbing a smaller but fast-growing share of tourist rentals (a displacement-risk problem). This project builds a simple, transparent index designed to separate those two patterns.

## How the index was designed

Each barrio (neighborhood) gets scored on two things:

1. **Airbnb housing saturation** — active Airbnb listings as a percentage of the barrio's counted housing units, from DANE's 2018 census at the block (manzana) level, aggregated up to the barrio.
2. **Estrato** — Colombia's official socioeconomic stratification scale (1 = lowest income, 6 = highest), originally created for progressive utility billing and now used widely as a proxy for neighborhood income level.

The **Displacement Risk Index** is a difference of z-scores:

```
pct_homes_on_airbnb = 100 * listing_count / total_viviendas
displacement_risk_index = z(log(pct_homes_on_airbnb + 1)) − z(estrato)
```

This project originally normalized Airbnb activity by land area (listings per km²) instead of housing stock. A reviewer flagged that this implicitly assumes every barrio is equally populated, which isn't true — a barrio with a small footprint but a dense high-rise core has far more housing (and far more potential displacement) than an equally small, mostly-park barrio. Switching to a housing-unit denominator, using DANE's Marco Geoestadístico Nacional 2018 (see Source data below), corrects for that.

A few design choices, and why:

- **Log-transforming saturation** before scoring it, for the same reason the original density metric was log-transformed: a handful of barrios have Airbnb activity that dwarfs the rest, so a log transform keeps a few extreme outliers from swamping the whole distribution.
- **Z-scoring both variables** puts saturation and estrato (1–6) on the same scale before comparing them, since they'd otherwise be incomparable units.
- **Subtracting** the two z-scores captures *mismatch*, not raw volume. A high score means unusually high saturation paired with unusually low estrato — the specific combination associated with displacement pressure. A wealthy, high-saturation neighborhood and a poor, low-saturation one both score near zero; only the poor-and-high-saturation combination scores high.
- **A minimum housing-unit threshold**, applied before scoring: barrios with very few counted housing units produce statistically unstable saturation percentages, since a single listing can swing the ratio dramatically. Barrios below the threshold have their saturation value set to missing rather than included in the ranking. The threshold differs by city — 50 units for Medellín, 100 for Barranquilla — chosen by inspecting each city's own distribution for a natural gap between legitimately non-residential areas (Medellín's La Alpujarra, an administrative/government district; Barranquilla's Zona Franca and Industrial Norte, free-trade/industrial parks) and small-but-real residential barrios. This is a judgment call, not a statistically derived cutoff, and is applied in `04_build_index.py` and `07_barranquilla_build_index.py`.
- **A minimum listing-count threshold was considered but not applied.** A diagnostic check (`17_check_listing_floor.py`) confirmed no top-ranked barrio in either city was riding an implausibly small number of listings to a high score once the housing-unit threshold was in place, so a second floor wasn't necessary.

This is a relative screening tool, not a causal claim — a high score flags a neighborhood worth a closer look, not proof that displacement is happening there.

## Data pipeline

Raw data → clean/dedupe → spatial join → housing + estrato merge/index → interactive maps. Each stage is its own script under `scripts/`, meant to be run in order:

| Script | What it does |
|---|---|
| `01_clean_scrapes.py` | Loads all raw Apify JSON exports from `data/raw/`, extracts fields (coordinates, price, room type, reviews), deduplicates by listing ID, and routes each listing to Medellín or Barranquilla by latitude. Outputs `data/processed/listings_clean.csv`. |
| `02_spatial_join.py` | Point-in-polygon join of Medellín listings against `data/geo/medellin_barrios_all.geojson` (265 barrios across 16 comunas). Computes area in km² (reprojected to UTM 18N) and density. Outputs `data/processed/medellin_barrio_density.csv`. |
| `03_barranquilla_spatial_join.py` | Same join, run against `data/geo/barranquilla_barrios.geojson` (189 barrios across 5 localidades, blank/unclassified polygons filtered out). Outputs `data/processed/barranquilla_barrio_density.csv`. |
| `04_build_index.py` | Merges `data/raw/comuna_estrato.csv` and `data/raw/medellin_barrio_housing.csv` (DANE housing counts, see script 15) onto the Medellín density table, computes each barrio's Airbnb listings as a % of its counted housing units, excludes barrios below the 50-unit threshold as statistically unreliable, then computes the composite displacement risk index. Outputs `data/processed/medellin_displacement_index.csv`. |
| `05_choropleth.py` | Builds the interactive Folium/Leaflet map of Medellín's composite index (via `map_builder.py`). Outputs `data/processed/medellin_choropleth.html`. |
| `06_barranquilla_fetch_estrato.py` | Pages through Barranquilla's `ESTRATO_1994` ArcGIS FeatureServer (175K+ parcel-level records), then groups by barrio to find each one's predominant estrato. Outputs `data/raw/barranquilla_barrio_estrato.csv`. |
| `07_barranquilla_build_index.py` | Same housing-saturation index logic as script 04, applied to Barranquilla's density, estrato, and housing tables (joined on barrio name), using a 100-unit threshold to exclude its industrial/free-trade-zone barrios. Outputs `data/processed/barranquilla_displacement_index.csv`. |
| `08_barranquilla_choropleth.py` | Same as script 05, for Barranquilla's composite index. Outputs `data/processed/barranquilla_choropleth.html`. |
| `09_barranquilla_refetch_boundaries.py` | Replaces the original 91-barrio boundary file with a more complete 189-barrio layer from Barranquilla's current land-use plan (POT), fetched directly as GeoJSON. Outputs `data/geo/barranquilla_barrios.geojson`. |
| `10_medellin_airbnb_density_map.py` | Maps Medellín's Airbnb density alone (log scale, listings per km²) — the original land-area-based metric. Kept as a reference map only; no longer an input to the composite index. Outputs `data/processed/medellin_airbnb_density_map.html`. |
| `11_medellin_estrato_map.py` | Maps Medellín's predominant estrato alone. Outputs `data/processed/medellin_estrato_map.html`. |
| `12_barranquilla_airbnb_density_map.py` | Same as script 10, for Barranquilla. Outputs `data/processed/barranquilla_airbnb_density_map.html`. |
| `13_barranquilla_estrato_map.py` | Same as script 11, for Barranquilla. Outputs `data/processed/barranquilla_estrato_map.html`. |
| `14_fetch_dane_housing.py` | Downloads and filters DANE's national manzana (census block) GeoPackage to Medellín and Barranquilla only, keeping each block's housing unit count (`TVIVIENDA`) and reprojecting to a block centroid point (UTM 18N) for spatial joining. Outputs `data/raw/dane_housing_blocks.geojson`. |
| `15_aggregate_housing_to_barrios.py` | Spatially joins the DANE block centroids to each city's barrio boundaries and sums housing units per barrio. Outputs `data/raw/medellin_barrio_housing.csv` and `data/raw/barranquilla_barrio_housing.csv`. |
| `16_debug_poblado.py` | Diagnostic script, not part of the regular pipeline: checks how many DANE blocks matched Medellín's El Poblado barrio and its land area, to sanity-check its unusually high saturation figure. See Limitations. |
| `17_check_listing_floor.py` | Diagnostic script, not part of the regular pipeline: checks whether any top-ranked barrio's score is driven by an implausibly small listing count. Confirmed this wasn't an issue once the housing-unit threshold (scripts 04/07) was in place. |
| `18_medellin_housing_saturation_map.py` | Maps Medellín's Airbnb housing saturation alone (log scale) — one of the two inputs to the composite index. Outputs `data/processed/medellin_housing_saturation_map.html`. |
| `19_barranquilla_housing_saturation_map.py` | Same as script 18, for Barranquilla. Outputs `data/processed/barranquilla_housing_saturation_map.html`. |

`map_builder.py` is a shared module (not run directly) used by scripts 05, 08, 10–13, 18–19, plus `app.py`. It centralizes the actual map-building — the on-map title box, color scales, hover/click details — in one place, supports all four map types and both languages (English/Spanish), so every map only needs to be fixed or updated in one spot.

`app.py` is the Streamlit app deployed at the live link above. It loads directly to the Displacement Risk Index map, with a city selector and a language toggle above it; the other three map types live in a collapsed expander below the results.

`run_all.sh` reruns every script in `scripts/` in order, regenerating the full pipeline and all eight static maps in one command. Scripts 16 and 17 are diagnostic and will also run (harmlessly — they only print output) since they live in the same folder.

Source data:

- **Airbnb listings** — scraped via the Apify `tri_angle/airbnb-scraper` actor, run separately per comuna (Medellín) and localidad (Barranquilla) to stay within result limits.
- **Barrio/comuna boundaries** — official GeoJSON layers from Medellín's GeoMedellín catalog and Barranquilla's Secretaría Distrital de Planeación (via their public ArcGIS Feature Services).
- **Estrato (Medellín)** — Encuesta de Calidad de Vida (ECV), a household survey published per comuna by the Alcaldía de Medellín. No public dataset breaks estrato down below the comuna level, which is a limitation below.
- **Estrato (Barranquilla)** — `ESTRATO_1994`, a parcel-level stratification layer published by Barranquilla's Secretaría Distrital de Planeación (via ArcGIS Feature Service). Despite the "1994" name — a reference to Law 142 of 1994, which created Colombia's estrato system — the layer is actively maintained; edit timestamps show updates as recent as 2025. This is more granular than Medellín's comuna-level estrato: each barrio's predominant stratum is computed directly from its own parcels rather than inherited from a larger area.
- **Housing units (both cities)** — DANE's Marco Geoestadístico Nacional 2018 integrado con el Censo Nacional de Población y Vivienda (CNPV) 2018, at the manzana (census block) level. Downloaded as a national GeoPackage, filtered to Medellín and Barranquilla, and aggregated up to the barrio level (scripts 14–15). This is the most recent manzana-level housing count DANE has published — see Limitations for what that means for interpreting the results.

## Results

**Medellín — El Poblado and Manila top the index, a reversal from the original land-density version.** Under the original density metric, Comuna 13 (San Javier) topped the list because it's geographically compact, so a modest number of listings still produced high density per km². Measured against DANE's counted housing stock instead, the picture flips: El Poblado (the specific barrio, not the broader comuna of the same name) has roughly 435 Airbnb listings against 299 counted dwellings — 145% of its 2018-counted housing stock — and neighboring Manila isn't far behind at 67%. Both are estrato-6 barrios.

**Those very high figures likely combine a real finding with a data-vintage artifact.** A diagnostic check (`16_debug_poblado.py`) confirmed this isn't a spatial-join error: El Poblado's polygon is genuinely small (0.25 km²) and housing-sparse — about a quarter of the 34 DANE census blocks inside it have zero counted housing units, consistent with it being a dense commercial/nightlife core (the Parque Lleras area) rather than a residential neighborhood. The most likely explanation for a >100% figure is some combination of: (1) DANE's count is from the 2018 census, which predates Medellín's post-2020 digital nomad boom, so newer construction and short-term-rental conversions since then aren't captured in the denominator; and (2) a single physical dwelling can carry multiple separately-listed Airbnb rooms, inflating the numerator relative to the denominator. Both are genuine limitations of comparing a 2018 housing count against a live listings scrape — see Limitations.

**San Javier's barrios still show up, but lower down and for a different reason.** Their saturation percentages are small (under 2%) — not because Airbnb activity is minimal (San Javier No. 2 has 21 listings, for instance), but because these barrios have thousands of counted housing units, so even a real and growing tourist presence (the Comuna 13 Graffitour draws heavy foot traffic) doesn't yet register as a large share of the housing stock. They rank where they do mostly on the strength of their very low estrato (1), not high saturation.

**Barranquilla — Riomar's own barrios show real saturation, not just raw density.** El Poblado (Barranquilla's, unrelated to Medellín's), Altamira, and Villa del Este — all estrato 5, in Barranquilla's wealthiest localidad — carry roughly 7–13.5% of their housing stock as Airbnb listings. That's a real, if less extreme, echo of Medellín's El Poblado pattern.

**Norte - Centro Histórico rounds out the top of the list at lower estrato.** El Rosario, Colombia, Santa Ana, and Los Nogales (estrato 2–4) combine smaller saturation percentages (roughly 3–5%) with a lower income level to land close to Riomar's barrios on the composite score — the classic displacement-risk combination of modest-but-real tourism pressure on lower-income housing.

**Unlike Medellín, no barrio in Barranquilla exceeds 100% saturation**, so the census-vintage caveat matters less here — Barranquilla hasn't seen the same post-2020 tourism surge as Medellín.

## Limitations

- **Housing data vintage**: DANE's manzana-level housing counts are from the 2018 census (CNPV), the most recent count published at that granularity — no finer-grained update exists as of this writing. DANE's more recent housing "projections" are model-based estimates published only at the municipality level, not by barrio or manzana, so they can't be joined to this project's boundaries. Any construction or short-term-rental conversion after 2018 — including Medellín's post-2020 digital nomad boom — isn't reflected in the denominator, and is the leading explanation for El Poblado and Manila's saturation figures exceeding 100%.
- **Listing-vs-dwelling counting mismatch**: a single physical housing unit can host multiple separately-listed Airbnb rooms (e.g., private-room listings within one apartment), which would inflate the numerator relative to DANE's whole-dwelling count. This project can't distinguish this from genuine new STR-specific construction with the data on hand.
- **Minimum housing-unit threshold**: excluding barrios below 50 (Medellín) or 100 (Barranquilla) counted housing units is a judgment call, based on each city's own distribution, not a statistically derived cutoff. A different choice of cutoff would change which barrios appear in the ranking at the margins.
- **Centroid-based spatial join**: DANE housing counts were joined to barrios using each census block's centroid, not its full geometry. For most barrios this is unproblematic (dozens of blocks average out any edge effects), but a barrio whose boundary is small relative to the surrounding blocks could see a block counted on the wrong side of the line. Spot-checked for El Poblado (34 matched blocks, arithmetic confirmed correct) but not exhaustively verified for every barrio.
- **Estrato granularity**: estrato is only available at the comuna level for Medellín — no public barrio-level dataset exists. Every barrio within a comuna shares one estrato value, so real intra-comuna variation isn't captured.
- **Villa Hermosa's estrato** is an approximation — its source data reports "estrato 1+2" combined without breaking the two apart.
- **Point-in-time snapshot**: the Airbnb data reflects listings active at scrape time, not year-over-year growth, since Apify's search-based scraper doesn't expose new-listing history.
- **Spatial match rate**: a small share of geocoded listings fall outside the barrio boundary set (mostly rural corregimientos not covered here) and are dropped from the density calculation.
- **Scraper budget cap**: the Apify scrape was run separately per comuna/localidad (avoiding cross-neighborhood competition for one shared budget), but if any single comuna's true listing count exceeded that comuna's individual cap, its listings would still be undercounted relative to its real size. Worth spot-checking Apify's run logs for the highest-volume comunas (e.g., El Poblado) to confirm each run completed naturally rather than hitting its limit.
- **Estrato sample size (Barranquilla)**: some barrios have very few parcels in the estrato dataset, making their "predominant" value less statistically reliable than barrios with hundreds of parcels.
- **Comuna vs. barrio naming (Medellín)**: "El Poblado" is both a comuna (a large, popularly-known district) and the name of one small barrio inside it. The choropleth's barrio-level detail for "El Poblado" only reflects that one small polygon — the area people usually mean by "El Poblado" is spread across many separately-named barrios (Provenza, Manila, Castropol, El Tesoro, etc.), which is where most of that comuna's Airbnb listings actually show up.

## Repo structure

```
data/
  raw/          Raw Apify scrapes, comuna_estrato.csv, barranquilla_barrio_estrato.csv,
                dane_housing_blocks.geojson, medellin_barrio_housing.csv, barranquilla_barrio_housing.csv
  geo/          Barrio/localidad boundary GeoJSON files (Medellín + Barranquilla)
  processed/    Cleaned listings, density tables, displacement indices, and all eight maps
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
  14_fetch_dane_housing.py
  15_aggregate_housing_to_barrios.py
  16_debug_poblado.py                       Diagnostic, not part of the regular rebuild
  17_check_listing_floor.py                 Diagnostic, not part of the regular rebuild
  18_medellin_housing_saturation_map.py
  19_barranquilla_housing_saturation_map.py
  map_builder.py     Shared map-building + data-loading module (bilingual: EN/ES), used by scripts 05, 08, 10-13, 18-19, and app.py
app.py                Streamlit app: loads directly to the Displacement Risk Index map, with a language toggle and the other three map types tucked into a collapsed expander (deployed live, see link above)
requirements.txt       Python packages needed to run app.py or any script locally
packages.txt           System-level (apt) packages needed for geopandas on Streamlit Cloud
run_all.sh
```

## Tools

Python, pandas, geopandas, shapely, Folium, Streamlit (`streamlit` + `streamlit-folium`). Data sourced via Apify (Airbnb scraper), each city's official open-GIS ArcGIS Feature Services, and DANE's national census GeoPackage. Live app hosted on Streamlit Community Cloud.
