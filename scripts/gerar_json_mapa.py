import os
import json
import pandas as pd
import numpy as np

print("Carregando eventos processados...")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

caminho_entrada = os.path.join(BASE_DIR, "eventos_processados.json")
caminho_saida = os.path.join(BASE_DIR, "dados", "eventos_mapa_light.json")

# ==============================
# CARREGAR DADOS
# ==============================

with open(caminho_entrada, "r", encoding="utf-8") as f:
    dados = json.load(f)

df = pd.DataFrame(dados)

print("Colunas encontradas no dataset:")
print(df.columns)

# ==============================
# CRIAR CAMPOS NECESSÁRIOS
# ==============================

# Padronizar nome do campo ANO
if "Ano" in df.columns:
    df["ANO"] = df["Ano"]

# Campos de vítimas (caso não existam)
df["TOTAL_FATAL"] = df.get("TOTAL_FATAL", 0)
df["TOTAL_GRAVE"] = df.get("TOTAL_GRAVE", 0)
df["TOTAL_LEVE"] = df.get("TOTAL_LEVE", 0)

df["TEM_FATAL"] = df["TOTAL_FATAL"] > 0
df["TEM_GRAVE"] = df["TOTAL_GRAVE"] > 0
df["TEM_LEVE"] = df["TOTAL_LEVE"] > 0

# ==============================
# COLUNAS PARA O MAPA
# ==============================

colunas_mapa = [
    "LATITUDE",
    "LONGITUDE",
    "Cia",
    "Pelotao",
    "Natureza",
    "ANO",
    "Data",
    "TEM_FATAL",
    "TEM_GRAVE",
    "TEM_LEVE",
    "TOTAL_FATAL",
    "TOTAL_GRAVE",
    "TOTAL_LEVE"
]

df_mapa = df[colunas_mapa].copy()

# ==============================
# REMOVER SEM COORDENADAS
# ==============================

df_mapa = df_mapa[
    df_mapa["LATITUDE"].notna() &
    df_mapa["LONGITUDE"].notna()
]

# ==============================
# CONVERTER DATA
# ==============================

df_mapa["Data"] = df_mapa["Data"].astype(str)

# ==============================
# SUBSTITUIR NaN
# ==============================

df_mapa = df_mapa.replace({np.nan: None})

# ==============================
# SALVAR JSON
# ==============================

with open(caminho_saida, "w", encoding="utf-8") as f:
    json.dump(
        df_mapa.to_dict(orient="records"),
        f,
        ensure_ascii=False
    )

print("JSON do mapa criado com sucesso!")
print("Total registros no mapa:", len(df_mapa))