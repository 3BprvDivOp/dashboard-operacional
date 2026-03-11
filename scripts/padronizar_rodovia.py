import pandas as pd
import re

df_coord = pd.read_excel("coordenadas.xlsx")

def padronizar_rodovia(valor):
    if pd.isna(valor):
        return None

    valor = str(valor).strip()

    # Extrai todos os números
    numeros = re.findall(r"\d+", valor)

    if len(numeros) == 1:
        # Ex: SP 461
        return f"000/{numeros[0].zfill(3)}"

    if len(numeros) >= 2:
        # Ex: SPA 074/255 ou SPI 274/310
        return f"{numeros[0].zfill(3)}/{numeros[1].zfill(3)}"

    return None

df_coord["ROD_PADRAO"] = df_coord["rodovia"].apply(padronizar_rodovia)

print(df_coord[["rodovia","ROD_PADRAO"]].head(30))
