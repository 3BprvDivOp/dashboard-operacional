import geopandas as gpd
import pandas as pd

print("Carregando malha e municípios...")

malha = pd.read_excel("Malha.xlsx")
malha["MUNICÍPIO"] = malha["MUNICÍPIO"].str.upper().str.strip()

gdf = gpd.read_file("SP_Municipios_2024.shp")
gdf["NM_MUN"] = gdf["NM_MUN"].str.upper().str.strip()

gdf = gdf.merge(
    malha,
    left_on="NM_MUN",
    right_on="MUNICÍPIO",
    how="inner"
)

print("Dissolvendo por CIA...")

gdf_cia = gdf.dissolve(by="CIA").reset_index()

gdf_cia.to_file("malha_cia.geojson", driver="GeoJSON")

print("malha_cia.geojson criado com sucesso!")