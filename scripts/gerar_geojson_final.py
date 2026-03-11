import geopandas as gpd
import pandas as pd

# Ler GeoJSON base do estado
gdf = gpd.read_file("SP_Municipios.geojson")

# Ler planilha Malha
malha = pd.read_excel("Malha.xlsx")

# Padronizar nomes (IMPORTANTE)
gdf["NM_MUN"] = gdf["NM_MUN"].str.upper().str.strip()
malha["MUNICÍPIO"] = malha["MUNICÍPIO"].str.upper().str.strip()

# Fazer merge
gdf_final = gdf.merge(
    malha[["MUNICÍPIO", "CIA", "PELOTÃO"]],
    left_on="NM_MUN",
    right_on="MUNICÍPIO",
    how="inner"
)

# Salvar GeoJSON final
gdf_final.to_file("MALHA_COMPLETA.geojson", driver="GeoJSON")

print("GeoJSON final criado com sucesso!")
