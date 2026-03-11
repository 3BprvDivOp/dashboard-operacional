import geopandas as gpd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

caminho_entrada = os.path.join(BASE_DIR, "dados", "malha_cia.geojson")
caminho_saida = os.path.join(BASE_DIR, "dados", "malha_cia_dissolvida.geojson")

# Ler GeoJSON original
gdf = gpd.read_file(caminho_entrada)

# Dissolver por CIA
gdf_dissolvido = gdf.dissolve(by="CIA")

# Resetar índice
gdf_dissolvido = gdf_dissolvido.reset_index()

# Salvar novo GeoJSON
gdf_dissolvido.to_file(caminho_saida, driver="GeoJSON")

print("Malha dissolvida criada com sucesso!")