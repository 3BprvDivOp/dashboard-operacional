import geopandas as gpd
import pandas as pd
import folium

# ===============================
# 1️⃣ LER SHAPEFILE DO IBGE
# ===============================

gdf = gpd.read_file("SP_Municipios_2024.shp")

# ===============================
# 2️⃣ LER PLANILHA MALHA
# ===============================

malha = pd.read_excel("Malha.xlsx")

# Padronizar nomes
gdf["NM_MUN"] = gdf["NM_MUN"].str.upper().str.strip()
malha["MUNICÍPIO"] = malha["MUNICÍPIO"].str.upper().str.strip()

malha["CIA"] = malha["CIA"].astype(int)

# ===============================
# 3️⃣ FAZER MERGE
# ===============================

gdf = gdf.merge(
    malha[["MUNICÍPIO", "CIA", "PELOTÃO"]],
    left_on="NM_MUN",
    right_on="MUNICÍPIO",
    how="inner"
)

# ===============================
# 4️⃣ CRIAR POLÍGONO ÚNICO POR CIA
# ===============================

gdf_cia = gdf.dissolve(by="CIA")
gdf_cia = gdf_cia.reset_index()

# ===============================
# 5️⃣ CRIAR MAPA BASE
# ===============================

mapa = folium.Map(
    location=[-21.5, -48.5],
    zoom_start=7,
    tiles="OpenStreetMap"
)

# ===============================
# 6️⃣ CORES DAS CIAs (SUAVES)
# ===============================

cores_cia = {
    1: "#A9CCE3",  # Azul claro suave
    2: "#F9E79F",  # Amarelo pastel
    3: "#ABEBC6",  # Verde claro
    4: "#D7BDE2"   # Roxo pastel
}

# ===============================
# 7️⃣ CAMADA 1 – MUNICÍPIOS
# ===============================

folium.GeoJson(
    gdf,
    name="Municípios",
    style_function=lambda x: {
        "fillOpacity": 0,          # 👈 sem preenchimento
        "color": "#888888",
        "weight": 0.5
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["NM_MUN", "CIA", "PELOTÃO"],
        aliases=["Município:", "CIA:", "Pelotão:"]
    )
).add_to(mapa)

# ===============================
# 8️⃣ CAMADA 2 – CONTORNO DAS CIAs
# ===============================

folium.GeoJson(
    gdf_cia,
    name="Limite das CIAs",
    style_function=lambda x: {
        "fillColor": cores_cia.get(x["properties"]["CIA"], "gray"),
        "fillOpacity": 0.25,
        "color": "black",
        "weight": 4
    }
).add_to(mapa)

# ===============================
# 9️⃣ SALVAR MAPA
# ===============================

mapa.save("MAPA_OPERACIONAL_4CIAS.html")

print("Mapa operacional das 4 CIAs criado com sucesso!")
