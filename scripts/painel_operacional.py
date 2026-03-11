import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# =====================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================

st.set_page_config(layout="wide")
st.title("PAINEL OPERACIONAL - INTELIGÊNCIA")

# =====================================
# CARREGAR EVENTOS PROCESSADOS
# =====================================

@st.cache_data
def carregar_eventos():
    return pd.read_parquet("eventos_processados.parquet")

eventos = carregar_eventos()

# =====================================
# FILTROS
# =====================================

st.sidebar.header("FILTROS")

data_min = eventos["Data"].min()
data_max = eventos["Data"].max()

data_inicio, data_fim = st.sidebar.date_input(
    "Período:",
    [data_min, data_max]
)

cia_sel = st.sidebar.multiselect(
    "CIA",
    sorted(eventos["Cia"].dropna().unique())
)

pelotao_sel = st.sidebar.multiselect(
    "Pelotão",
    sorted(eventos["Pelotao"].dropna().unique())
)

natureza_sel = st.sidebar.multiselect(
    "Natureza",
    sorted(eventos["Natureza"].dropna().unique())
)

df_filtrado = eventos.copy()

if data_inicio and data_fim:
    df_filtrado = df_filtrado[
        (df_filtrado["Data"] >= pd.to_datetime(data_inicio)) &
        (df_filtrado["Data"] <= pd.to_datetime(data_fim))
    ]

if cia_sel:
    df_filtrado = df_filtrado[df_filtrado["Cia"].isin(cia_sel)]

if pelotao_sel:
    df_filtrado = df_filtrado[df_filtrado["Pelotao"].isin(pelotao_sel)]

if natureza_sel:
    df_filtrado = df_filtrado[df_filtrado["Natureza"].isin(natureza_sel)]

# =====================================
# KPIs
# =====================================

col1, col2, col3 = st.columns(3)

col1.metric("Eventos", len(df_filtrado))
col2.metric("Municípios", df_filtrado["Municipio"].nunique())
col3.metric("CIAs", df_filtrado["Cia"].nunique())

# =====================================
# CARREGAR MALHA (ÁREAS DAS CIAs)
# =====================================

@st.cache_data
def carregar_malha():

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

    gdf_cia = gdf.dissolve(by="CIA").reset_index()

    return gdf, gdf_cia

gdf_municipios, gdf_cia = carregar_malha()

# =====================================
# MAPA
# =====================================

mapa = folium.Map(
    location=[-21.5, -48.5],
    zoom_start=7
)

cores_cia = {
    1: "#A9CCE3",
    2: "#F9E79F",
    3: "#ABEBC6",
    4: "#D7BDE2"
}

# Municípios (contorno leve)
folium.GeoJson(
    gdf_municipios,
    style_function=lambda x: {
        "fillOpacity": 0,
        "color": "#888888",
        "weight": 0.5
    }
).add_to(mapa)

# CIAs coloridas
folium.GeoJson(
    gdf_cia,
    style_function=lambda x: {
        "fillColor": cores_cia.get(x["properties"]["CIA"], "gray"),
        "fillOpacity": 0.25,
        "color": "black",
        "weight": 4
    }
).add_to(mapa)

# Pontos
marker_cluster = MarkerCluster().add_to(mapa)

for _, row in df_filtrado.iterrows():
    if pd.notnull(row["LATITUDE"]) and pd.notnull(row["LONGITUDE"]):
        folium.Marker(
            location=[row["LATITUDE"], row["LONGITUDE"]],
            popup=f"""
            <b>Município:</b> {row['Municipio']}<br>
            <b>CIA:</b> {row['Cia']}<br>
            <b>Pelotão:</b> {row['Pelotao']}<br>
            <b>Natureza:</b> {row['Natureza']}<br>
            <b>Data:</b> {row['Data'].strftime('%d/%m/%Y')}<br>
            <b>Rodovia:</b> {row['Malha Viaria']}<br>
            <b>KM:</b> {row['km']}
            """
        ).add_to(marker_cluster)

st_folium(mapa, width=1400, height=750)