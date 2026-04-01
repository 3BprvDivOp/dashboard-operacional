import pandas as pd
import os

# =====================================
# CONFIGURAÇÃO
# =====================================

PASTA_BOPM = r"C:\Users\ZAFANI\Desktop\AUTOMAÇÃO\INTELIGENCIA_OPERACIONAL\base_eventos_consolidada"

print("Carregando arquivos BOPM...")

arquivos = [
    f for f in os.listdir(PASTA_BOPM)
    if f.endswith(".xlsx") and not f.startswith("~$")
]

if not arquivos:
    print("Nenhum arquivo encontrado.")
    exit()

lista_df = []

for arquivo in arquivos:
    caminho = os.path.join(PASTA_BOPM, arquivo)
    print(f"Lendo {arquivo}...")
    df = pd.read_excel(caminho)
    lista_df.append(df)

eventos = pd.concat(lista_df, ignore_index=True)

print("Padronizando dados...")

# =====================================
# DATAS
# =====================================

for col in eventos.columns:
    if "data" in col.lower():
        eventos[col] = pd.to_datetime(eventos[col], errors="coerce", dayfirst=True)

if "Data" in eventos.columns:
    eventos["ANO"] = eventos["Data"].dt.year

# =====================================
# PADRONIZAÇÃO RODOVIA
# =====================================

import re

def padronizar_rodovia(valor):
    if pd.isna(valor):
        return None

    valor = str(valor)

    numeros = re.findall(r"\d+", valor)

    if len(numeros) == 1:
        return f"000/{numeros[0].zfill(3)}"

    if len(numeros) >= 2:
        return f"{numeros[0].zfill(3)}/{numeros[1].zfill(3)}"

    return None

eventos["ROD_FINAL"] = eventos["Malha Viaria"].apply(padronizar_rodovia)

# km numérico
if "km" in eventos.columns:
    eventos["km"] = pd.to_numeric(eventos["km"], errors="coerce")

# =====================================
# CALCULAR VÍTIMAS
# =====================================

print("Calculando vítimas...")

def garantir_coluna(df, nome):

    if nome not in df.columns:
        df[nome] = 0

    return pd.to_numeric(df[nome], errors="coerce").fillna(0)


leve_cols = [
    "NumVitimaLeveCrianca",
    "NumVitimaLeveAdolescente",
    "NumVitimaLeveAdulto"
]

grave_cols = [
    "NumVitimaGraveCrianca",
    "NumVitimaGraveAdolescente",
    "NumVitimaGraveAdulto"
]

fatal_cols = [
    "NumVitimaFataisCrianca",
    "NumVitimaFataisAdolescente",
    "NumVitimaFataisAdulto"
]

for col in leve_cols:
    eventos[col] = garantir_coluna(eventos, col)

for col in grave_cols:
    eventos[col] = garantir_coluna(eventos, col)

for col in fatal_cols:
    eventos[col] = garantir_coluna(eventos, col)


eventos["TOTAL_LEVE"] = eventos[leve_cols].sum(axis=1)
eventos["TOTAL_GRAVE"] = eventos[grave_cols].sum(axis=1)
eventos["TOTAL_FATAL"] = eventos[fatal_cols].sum(axis=1)

# =====================================
# FLAGS USADAS PELO MAPA
# =====================================

eventos["TEM_LEVE"] = eventos["TOTAL_LEVE"] > 0
eventos["TEM_GRAVE"] = eventos["TOTAL_GRAVE"] > 0
eventos["TEM_FATAL"] = eventos["TOTAL_FATAL"] > 0


# =====================================
# CARREGAR COORDENADAS
# =====================================

print("Carregando coordenadas...")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
caminho_coord = os.path.join(BASE_DIR, "dados", "coordenadas.xlsx")

coordenadas = pd.read_excel(caminho_coord)

# PADRONIZAÇÃO DAS RODOVIAS DAS COORDENADAS (MESMA REGRA DOS EVENTOS)
coordenadas["ROD_FINAL"] = coordenadas["rodovia"].apply(padronizar_rodovia)

coordenadas["km"] = pd.to_numeric(coordenadas["km"], errors="coerce")

coord_dict = {
    rod: grupo.sort_values("km")
    for rod, grupo in coordenadas.groupby("ROD_FINAL")
}


# =====================================
# FUNÇÃO PARA ENCONTRAR KM MAIS PRÓXIMO
# =====================================

def encontrar_coordenada(row):

    rod = row["ROD_FINAL"]
    km_evento = row["km"]

    if rod not in coord_dict or pd.isna(km_evento):
        return pd.Series([None, None])

    base = coord_dict[rod]

    idx = (base["km"] - km_evento).abs().idxmin()
    linha = base.loc[idx]

    return pd.Series([linha["y"], linha["x"]])


print("Calculando coordenadas...")

print("Total coordenadas carregadas:", len(coordenadas))

eventos[["LATITUDE", "LONGITUDE"]] = eventos.apply(
    encontrar_coordenada,
    axis=1
)

print("Eventos totais:", len(eventos))
print("Eventos com coordenada:", eventos["LATITUDE"].notna().sum())

# =====================================
# LIMPEZA FINAL
# =====================================

for col in eventos.select_dtypes(include=["object"]).columns:
    eventos[col] = eventos[col].astype(str)


# =====================================
# SALVAR JSON FINAL
# =====================================

print("Salvando eventos_processados.json...")

eventos.to_json(
    "eventos_processados.json",
    orient="records",
    force_ascii=False
)

print("Processamento finalizado com sucesso.")