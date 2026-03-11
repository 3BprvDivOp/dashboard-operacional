import geopandas as gpd

# Ler malha original
gdf = gpd.read_file("dados/malha_cia.geojson")

# Garantir que CIA é numérico
gdf["CIA"] = gdf["CIA"].astype(int)

# Dissolver por CIA (🔥 AQUI ESTÁ O SEGREDO)
gdf_cia = gdf.dissolve(by="CIA")

# Resetar índice
gdf_cia = gdf_cia.reset_index()

# Salvar nova malha
gdf_cia.to_file("dados/malha_cia_unificada.geojson", driver="GeoJSON")

print("Malha unificada criada com sucesso!")