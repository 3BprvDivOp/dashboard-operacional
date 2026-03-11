import os
import json
import pandas as pd
import re
import glob

# =========================================
# CONFIGURAÇÃO BASE
# =========================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pasta_eventos = os.path.join(BASE_DIR, "base_eventos_consolidada")
caminho_coord = os.path.join(BASE_DIR, "dados", "coordenadas.xlsx")
caminho_saida = os.path.join(BASE_DIR, "dados", "eventos_processados_atualizado.json")

# =========================================
# 1️⃣ CARREGAR TODOS OS EXCEL AUTOMATICAMENTE
# =========================================

arquivos = glob.glob(os.path.join(pasta_eventos, "*.xlsx"))

lista_dfs = []

for arq in arquivos:
    if "~$" not in arq:  # ignora arquivos temporários do Excel
        print("Carregando:", os.path.basename(arq))
        df_temp = pd.read_excel(arq)
        lista_dfs.append(df_temp)

df_eventos = pd.concat(lista_dfs, ignore_index=True)

print("Total eventos carregados:", len(df_eventos))

# =========================================
# 2️⃣ CARREGAR COORDENADAS
# =========================================

df_coord = pd.read_excel(caminho_coord)

df_coord["km"] = pd.to_numeric(df_coord["km"], errors="coerce").round(0)

# Padronizar rodovia
def padronizar_rodovia(valor):
    if pd.isna(valor):
        return None

    valor = str(valor).strip()
    numeros = re.findall(r"\d+", valor)

    if len(numeros) == 1:
        return f"000/{numeros[0].zfill(3)}"

    if len(numeros) >= 2:
        return f"{numeros[0].zfill(3)}/{numeros[1].zfill(3)}"

    return None

df_coord["ROD_PADRAO"] = df_coord["rodovia"].apply(padronizar_rodovia)

# 🔥 Remove duplicidade real antes do merge
df_coord = df_coord.drop_duplicates(subset=["ROD_PADRAO", "km"])

# =========================================
# 3️⃣ PREPARAR EVENTOS
# =========================================

df_eventos["km"] = pd.to_numeric(df_eventos["km"], errors="coerce").round(0)
df_eventos["ROD_FINAL"] = df_eventos["Malha Viaria"].astype(str)

# =========================================
# 4️⃣ MERGE
# =========================================

df_merged = df_eventos.merge(
    df_coord,
    left_on=["ROD_FINAL", "km"],
    right_on=["ROD_PADRAO", "km"],
    how="left"
)

print("Total após merge:", len(df_merged))
print("Com coordenada:", df_merged["x"].notna().sum())

# =========================================
# 5️⃣ CLASSIFICAÇÃO VÍTIMAS
# =========================================

cols_leve = [
    "NumVitimaLeveCrianca",
    "NumVitimaLeveAdolescente",
    "NumVitimaLeveAdulto"
]

cols_grave = [
    "NumVitimaGraveCrianca",
    "NumVitimaGraveAdolescente",
    "NumVitimaGraveAdulto"
]

cols_fatal = [
    "NumVitimaFataisCrianca",
    "NumVitimaFataisAdolescente",
    "NumVitimaFataisAdulto"
]

for col in cols_leve + cols_grave + cols_fatal:
    df_merged[col] = pd.to_numeric(df_merged[col], errors="coerce").fillna(0)

df_merged["TOTAL_LEVE"] = df_merged[cols_leve].sum(axis=1)
df_merged["TOTAL_GRAVE"] = df_merged[cols_grave].sum(axis=1)
df_merged["TOTAL_FATAL"] = df_merged[cols_fatal].sum(axis=1)

df_merged["TEM_LEVE"] = df_merged["TOTAL_LEVE"] > 0
df_merged["TEM_GRAVE"] = df_merged["TOTAL_GRAVE"] > 0
df_merged["TEM_FATAL"] = df_merged["TOTAL_FATAL"] > 0

# =========================================
# 6️⃣ DATAS E ANO
# =========================================

df_merged["Data"] = pd.to_datetime(df_merged["Data"], errors="coerce", dayfirst=True)
df_merged["ANO"] = df_merged["Data"].dt.year

# =========================================
# 7️⃣ AJUSTAR COORDENADAS
# =========================================

df_merged["LATITUDE"] = df_merged["y"]
df_merged["LONGITUDE"] = df_merged["x"]

# =========================================
# 8️⃣ CONVERTER QUALQUER DATETIME ESCONDIDO
# =========================================

df_merged = df_merged.where(pd.notnull(df_merged), None)

df_merged = df_merged.applymap(
    lambda x: str(x) if isinstance(x, (pd.Timestamp,)) else x
)

# =========================================
# LIMPAR NULOS
# =========================================

df_merged = df_merged.where(pd.notnull(df_merged), None)

# =========================================
# SALVAR JSON (VERSÃO DEFINITIVA)
# =========================================

with open(caminho_saida, "w", encoding="utf-8") as f:
    json.dump(
        df_merged.to_dict(orient="records"),
        f,
        ensure_ascii=False,
        default=str
    )

print("JSON salvo com sucesso!")
print("Eventos sem coordenada:", df_merged["LATITUDE"].isna().sum())