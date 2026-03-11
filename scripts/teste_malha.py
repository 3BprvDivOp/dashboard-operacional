import geopandas as gpd
import pandas as pd

# Ler malha oficial
gdf = gpd.read_file("SP_Municipios_2024.shp")

# Ler planilha
df = pd.read_excel("municipios_selecionados.xlsx")

# Corrigir caractere
df["name_muni"] = df["name_muni"].str.replace("`", "'", regex=False)

# Padronizar nomes
df["name_muni"] = df["name_muni"].str.upper().str.strip()
gdf["NM_MUN"] = gdf["NM_MUN"].str.upper().str.strip()

# Filtrar municípios da CIA
gdf_filtrado = gdf[gdf["NM_MUN"].isin(df["name_muni"])]

# Exportar GeoJSON
gdf_filtrado.to_file("CIA1_Municipios.geojson", driver="GeoJSON")

print("Arquivo CIA1_Municipios.geojson criado com sucesso!")
