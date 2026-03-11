import pandas as pd
import os

# =====================================
# CONFIGURAÇÃO
# =====================================

PASTA_BOPM = r"C:\Users\ZAFANI\Desktop\AUTOMAÇÃO\INTELIGENCIA_OPERACIONAL\base_eventos_consolidada"

print("Carregando arquivos BOPM...")

arquivos = [f for f in os.listdir(PASTA_BOPM) if f.endswith(".xlsx")]

if not arquivos:
    print("Nenhum arquivo BOPM encontrado.")
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
# PADRONIZAÇÃO DE COLUNAS
# =====================================

# Converter todas as colunas que contenham "data" no nome
for col in eventos.columns:
    if "data" in col.lower():
        eventos[col] = pd.to_datetime(eventos[col], errors="coerce")

# Garantir que a coluna principal de data exista
if "Data" in eventos.columns:
    eventos["Ano"] = eventos["Data"].dt.year
else:
    print("Coluna 'Data' não encontrada!")        

# Padronizar município
if "Municipio" in eventos.columns:
    eventos["Municipio"] = (
        eventos["Municipio"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

# Padronizar rodovia
if "Malha Viaria" in eventos.columns:
    eventos["ROD_FINAL"] = (
        eventos["Malha Viaria"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

# Garantir km numérico
if "km" in eventos.columns:
    eventos["km"] = pd.to_numeric(eventos["km"], errors="coerce")

print("Carregando coordenadas...")

# =====================================
# COORDENADAS
# =====================================

coordenadas = pd.read_excel("coordenadas.xlsx")

coordenadas["ROD_FINAL"] = (
    coordenadas["rodovia"]
    .astype(str)
    .str.upper()
    .str.replace("SP ", "", regex=False)
    .str.replace("SPA ", "", regex=False)
    .str.replace("SPI ", "", regex=False)
    .str.replace("SPD ", "", regex=False)
    .str.strip()
)

coordenadas["km"] = pd.to_numeric(coordenadas["km"], errors="coerce")

print("Criando índice por rodovia...")

coord_dict = {
    rod: grupo.sort_values("km")
    for rod, grupo in coordenadas.groupby("ROD_FINAL")
}

# =====================================
# FUNÇÃO KM MAIS PRÓXIMO
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

eventos[["LATITUDE", "LONGITUDE"]] = eventos.apply(
    encontrar_coordenada,
    axis=1
)

# =====================================
# LIMPEZA FINAL (evita erro no parquet)
# =====================================

for col in eventos.select_dtypes(include=["object"]).columns:
    eventos[col] = eventos[col].astype(str)

print("Salvando arquivo otimizado...")

eventos.to_json(
    "eventos_processados.json",
    orient="records",
    date_format="iso"
)

print("Arquivo eventos_processados.json criado com sucesso!")
