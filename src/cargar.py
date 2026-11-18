"""Lee los CSV mensuales de la GEIH 2025 (DANE, catálogo 853) y une Ocupados con Características generales.

Uso: python src/cargar.py RUTA_GEIH  (carpeta con subcarpetas "Enero 2025", ..., cada una con CSV/)
Los microdatos no se versionan: el resultado queda en data/ocupados_2025.pkl, que git ignora.
"""
import glob, os, sys
import pandas as pd

LLAVE = ["DIRECTORIO", "SECUENCIA_P", "ORDEN", "HOGAR"]
OCUPADOS = LLAVE + ["MES", "CLASE", "AREA", "DPTO", "FEX_C18", "P6430", "P6450", "P6920", "P6930", "P6940",
                    "P3045S1", "P3046", "P3065", "P3066", "P3067", "P3067S1", "P3067S2", "P6775", "P3068",
                    "P3069", "P6765", "RAMA2D_R4", "OFICIO_C8"]
PERSONAS = LLAVE + ["P3271", "P6040", "P6100", "P6110"]
TEXTO = {"DIRECTORIO", "DPTO", "RAMA2D_R4", "OFICIO_C8"}


def leer(carpeta, prefijo, columnas):
    archivo = [f for f in os.listdir(os.path.join(carpeta, "CSV")) if f.startswith(prefijo)][0]
    return pd.read_csv(os.path.join(carpeta, "CSV", archivo), sep=";", usecols=lambda c: c in columnas,
                       dtype=str, encoding="latin1", low_memory=False)


def cargar(raiz):
    meses = []
    for carpeta in sorted(glob.glob(os.path.join(raiz, "* 2025"))):
        o = leer(carpeta, "Ocupados", OCUPADOS)
        p = leer(carpeta, "Caracter", PERSONAS)
        meses.append(o.merge(p, on=LLAVE, how="left", validate="1:1"))
    if len(meses) != 12:
        raise SystemExit(f"Se esperaban 12 meses y hay {len(meses)}")
    df = pd.concat(meses, ignore_index=True)
    for c in df.columns:
        if c not in TEXTO:
            df[c] = pd.to_numeric(df[c].str.replace(",", "."), errors="coerce")
    return df


if __name__ == "__main__":
    df = cargar(sys.argv[1])
    os.makedirs("data", exist_ok=True)
    df.to_pickle("data/ocupados_2025.pkl")
    print(df.shape)
