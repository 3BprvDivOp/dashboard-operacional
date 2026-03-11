import os
import json
import pandas as pd
import numpy as np

# =========================================
# CONFIGURAÇÃO DE CAMINHO BASE
# =========================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

caminho_entrada = os.path.join(BASE_DIR, "eventos_processados.json")
caminho_saida = os.path.join(BASE_DIR, "dados", "eventos_mapa_light.json")

# =========================================
# CARREGAR JSON PROCESSADO
# =========================================

print("Carregando eventos processados...")

with open(caminho_entrada, "r", encoding="utf-8") as f:
    dados = json.load(f)

df = pd.DataFrame(dados)

print("Colunas encontradas no dataset:")
print(df.columns)

# =========================================
# COLUNAS UTILIZADAS NO MAPA
# =========================================

colunas_mapa = [
    "LATITUDE",
    "LONGITUDE",
    "Cia",
    "Pelotao",
    "Natureza",
    "Ano",
    "Data",
    "ROD_FINAL"
]

# manter apenas colunas existentes
colunas_existentes = [c for c in colunas_mapa if c in df.columns]

df_mapa = df[colunas_existentes].copy()

# =========================================
# REMOVER REGISTROS SEM COORDENADA
# =========================================

df_mapa = df_mapa[
    df_mapa["LATITUDE"].notna() &
    df_mapa["LONGITUDE"].notna()
]

# =========================================
# CONVERTER DATAS PARA STRING
# =========================================

if "Data" in df_mapa.columns:
    df_mapa["Data"] = df_mapa["Data"].astype(str)

# =========================================
# SUBSTITUIR NaN POR None (JSON VÁLIDO)
# =========================================

df_mapa = df_mapa.replace({np.nan: None})

# =========================================
# SALVAR JSON FINAL LEVE
# =========================================

print("Gerando JSON leve para o mapa...")

with open(caminho_saida, "w", encoding="utf-8") as f:
    json.dump(
        df_mapa.to_dict(orient="records"),
        f,
        ensure_ascii=False
    )

print("JSON do mapa criado com sucesso!")
print("Total registros no mapa:", len(df_mapa))