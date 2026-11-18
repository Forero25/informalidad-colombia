"""Calcula las cinco definiciones, las valida contra las cifras publicadas por el DANE y guarda solo agregados.

Uso: python src/analisis.py  (lee data/ocupados_2025.pkl y escribe resultados/informalidad_2025.json)
"""
import json, os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from definiciones import todas

TRECE = [5, 8, 11, 13, 17, 23, 50, 52, 54, 66, 68, 73, 76]
RAMAS = [(1, 3, "Agro"), (5, 9, "Minas"), (10, 33, "Industria"), (35, 39, "Servicios públicos"),
         (41, 43, "Construcción"), (45, 47, "Comercio"), (49, 53, "Transporte"), (55, 56, "Alojamiento y comida"),
         (58, 63, "Información y comunicaciones"), (64, 68, "Financieras e inmobiliarias"),
         (69, 82, "Profesionales y administrativas"), (84, 84, "Administración pública"), (85, 85, "Educación"),
         (86, 88, "Salud"), (90, 96, "Artes y otros servicios"), (97, 98, "Hogares empleadores"),
         (99, 99, "Extraterritoriales")]
POSICION = {1: "Asalariado privado", 2: "Gobierno", 3: "Empleo doméstico", 4: "Cuenta propia", 5: "Patrón",
            6: "Familiar sin remuneración", 7: "Jornalero", 8: "Sin remuneración otros hogares"}
# Cifras publicadas por el DANE (boletín y anexo de ocupación informal, oct-dic 2025)
DANE = {"oficial_anual": 55.7, "oficial_13c": 42.2, "oficial_rural": 83.5, "oficial_q4": 55.7,
        "oficial_q4_h": 58.1, "oficial_q4_m": 52.4, "cotiza_pension_q4": 43.08, "aporta_salud_q4": 46.50,
        "ocupados_q4_miles": 24397.3}


def main():
    d = pd.read_pickle("data/ocupados_2025.pkl")
    D = todas(d)
    w = d["FEX_C18"]
    todos = pd.Series(True, index=d.index)

    def tasa(s, m=todos):
        return float(100 * w[s & m].sum() / w[m].sum())

    q4, c13, rural = d.MES.isin([10, 11, 12]), d.AREA.isin(TRECE), d.CLASE == 2
    propio = {"oficial_anual": tasa(D.oficial), "oficial_13c": tasa(D.oficial, c13), "oficial_rural": tasa(D.oficial, rural),
              "oficial_q4": tasa(D.oficial, q4), "oficial_q4_h": tasa(D.oficial, q4 & (d.P3271 == 1)),
              "oficial_q4_m": tasa(D.oficial, q4 & (d.P3271 == 2)),
              "cotiza_pension_q4": tasa(d.P6920 == 1, q4),
              "aporta_salud_q4": tasa(d.P6100.isin([1, 2]) & d.P6110.isin([1, 2, 3, 4]), q4),
              "ocupados_q4_miles": float(w[q4].sum() / 3 / 1000)}
    out = {"fuente": "DANE, GEIH 2025 (microdatos, catálogo 853). Cálculos propios.",
           "validacion": {k: {"propio": propio[k], "dane": DANE[k]} for k in DANE},
           "ocupados_prom_miles": float(w.sum() / 12 / 1000), "n_registros": int(len(d)),
           "nacional": {k: tasa(D[k]) for k in D}}
    r2 = pd.to_numeric(d.RAMA2D_R4, errors="coerce")
    rama = pd.Series("Sin dato", index=d.index)
    for a, b, n in RAMAS:
        rama[(r2 >= a) & (r2 <= b)] = n
    cortes = {"sexo": d.P3271.map({1: "Hombres", 2: "Mujeres"}),
              "edad": pd.cut(d.P6040, [14, 24, 34, 44, 54, 64, 200],
                             labels=["15-24", "25-34", "35-44", "45-54", "55-64", "65+"]).astype(str),
              "dominio": pd.Series(np.where(c13, "13 ciudades y A.M.", np.where(rural, "Rural y centros poblados", "Otras cabeceras")), index=d.index),
              "rama": rama, "posicion": d.P6430.map(POSICION), "dpto": d.DPTO}
    for c, s in cortes.items():
        out[c] = {str(v): {"ocupados_miles": float(w[s == v].sum() / 12 / 1000), **{k: tasa(D[k], s == v) for k in D}}
                  for v in sorted(s.dropna().unique())}
    k = D.sum(axis=1)
    out["al_menos_una"], out["todas"] = tasa(D.any(axis=1)), tasa(D.all(axis=1))
    out["n_definiciones"] = {int(i): float(100 * w[k == i].sum() / w.sum()) for i in range(6)}
    out["en_disputa_millones"] = float(w[(k > 0) & (k < 5)].sum() / 12 / 1e6)
    out["desacuerdo_con_oficial"] = {b: {"formal_oficial_informal_otra_millones": float(w[~D.oficial & D[b]].sum() / 12 / 1e6),
                                         "informal_oficial_formal_otra_millones": float(w[D.oficial & ~D[b]].sum() / 12 / 1e6),
                                         "pct_ocupados": float(100 * w[D.oficial != D[b]].sum() / w.sum())}
                                     for b in D if b != "oficial"}
    out["mensual"] = {int(m): {k2: tasa(D[k2], d.MES == m) for k2 in D} for m in range(1, 13)}
    dom = d.P6430 == 3
    jov = (d.P6040 <= 24) & D.oficial & ~D.tamano
    x = D.oficial & ~D.pension
    out["detalles"] = {"pct_mujeres_empleo_domestico": float(100 * w[dom & (d.P3271 == 2)].sum() / w[dom].sum()),
                       "jovenes_inf_oficial_formal_tamano_pct_en_empresas_de_6_o_mas": float(100 * w[jov & (d.P3069 >= 4)].sum() / w[jov].sum()),
                       "inf_oficial_que_cotizan_pct_cuenta_propia": float(100 * w[x & (d.P6430 == 4)].sum() / w[x].sum())}
    # celdas pequeñas: se marcan para no publicar tasas con pocos registros
    out["registros_por_dpto"] = {str(v): int((d.DPTO == v).sum()) for v in sorted(d.DPTO.unique())}
    os.makedirs("resultados", exist_ok=True)
    json.dump(out, open("resultados/informalidad_2025.json", "w"), ensure_ascii=False, indent=1)
    for k2, v in out["validacion"].items():
        print(f"{k2:20s} propio {v['propio']:9.2f}  DANE {v['dane']:9.2f}")


if __name__ == "__main__":
    main()
