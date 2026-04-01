import pandas as pd
import os

print("Carregando eventos processados...")

# ===============================
# CARREGAR JSON PROCESSADO
# ===============================

df = pd.read_json("eventos_processados.json")

print("Colunas encontradas no dataset:")
print(df.columns)

# ===============================
# COLUNAS NECESSÁRIAS PARA O MAPA
# ===============================

colunas_mapa = [

    "LATITUDE",
    "LONGITUDE",

    "Natureza",
    "TipoAcidente",

    "Data",

    "Cia",
    "Pelotao",

    "ROD_FINAL",
    "km",

    "TOTAL_FATAL",
    "TOTAL_GRAVE",
    "TOTAL_LEVE",

    "TEM_FATAL",
    "TEM_GRAVE",
    "TEM_LEVE",

    "ANO"

]

# Manter apenas colunas existentes
colunas_existentes = [c for c in colunas_mapa if c in df.columns]

df_mapa = df[colunas_existentes].copy()

# ===============================
# REMOVER EVENTOS SEM COORDENADA
# ===============================

df_mapa = df_mapa.dropna(subset=["LATITUDE", "LONGITUDE"])

# ===============================
# CONVERTER DATA PARA STRING
# ===============================

if "Data" in df_mapa.columns:
    df_mapa["Data"] = df_mapa["Data"].astype(str)

# ===============================
# GARANTIR PASTA dados/
# ===============================

if not os.path.exists("dados"):
    os.makedirs("dados")

# ===============================
# SALVAR JSON DO MAPA
# ===============================

print("Gerando dados/eventos_mapa_light.json...")

df_mapa.to_json(
    "dados/eventos_mapa_light.json",
    orient="records",
    force_ascii=False
)

print("JSON do mapa gerado com sucesso!")
print("Total de eventos no mapa:", len(df_mapa))