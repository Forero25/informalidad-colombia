import json, os, sys
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from informalidad_dane import ei_dane
from definiciones import todas

BASE = dict(DIRECTORIO="1", SECUENCIA_P=1, ORDEN=1, HOGAR=1, MES=1, CLASE=1, AREA=11, DPTO="11", FEX_C18=1.0,
            P6430=np.nan, P6450=np.nan, P6920=np.nan, P6930=np.nan, P6940=np.nan, P3045S1=np.nan, P3046=np.nan,
            P3065=np.nan, P3066=np.nan, P3067=np.nan, P3067S1=np.nan, P3067S2=np.nan, P6775=np.nan, P3068=np.nan,
            P3069=np.nan, P6765=np.nan, RAMA2D_R4="47", OFICIO_C8="5221", P3271=1, P6040=30, P6100=np.nan, P6110=np.nan)


def filas(*cambios):
    return pd.DataFrame([{**BASE, **c} for c in cambios])


def ei(*cambios):
    return list(ei_dane(filas(*cambios))[0])


def test_asalariado_formal_solo_con_salud_y_pension_del_empleador():
    salud = dict(P6100=1, P6110=1)
    pension = dict(P6920=1, P6930=1, P6940=3)
    assert ei({"P6430": 1, **salud, **pension}) == [1]
    assert ei({"P6430": 1, **salud}) == [0]                       # sin pensión: informal
    assert ei({"P6430": 1, **pension, "P6100": 3}) == [0]          # subsidiado: informal
    assert ei({"P6430": 1, "P6100": 1, "P6110": 3, **pension}) == [0]  # se paga toda la salud él mismo


def test_gobierno_y_familiares():
    assert ei({"P6430": 2}) == [1]
    assert ei({"P6430": 6}) == [0]
    assert ei({"P6430": 4, "RAMA2D_R4": "84"}) == [1]


def test_cuenta_propia_con_negocio_registrado_y_renovado():
    neg = dict(P6430=4, P6765=7, P3067=1, P3067S1=1)
    assert ei({**neg, "P3067S2": 2025}) == [1]
    assert ei({**neg, "P3067S2": 2024}) == [1]   # año anterior todavía cuenta
    assert ei({**neg, "P3067S2": 2023}) == [0]


def test_faltante_es_mayor_que_todo_como_en_stata():
    # patrón sin negocio, sin registro, contabilidad "no sabe" y tamaño faltante: Stata lo vuelve formal
    assert ei({"P6430": 5, "P6765": 1, "P3065": 2, "P3066": 9, "P3069": np.nan}) == [1]
    assert ei({"P6430": 5, "P6765": 1, "P3065": 2, "P3066": 9, "P3069": 2}) == [0]


def test_definiciones_alternativas():
    d = filas({"P6430": 3, "P6920": 2, "P6100": 3, "P3069": 1},     # empleada doméstica sin aportes
              {"P6430": 4, "P6920": 1, "P6100": 1, "P6110": 3, "P3069": 1, "OFICIO_C8": "2611"})  # abogado independiente que cotiza
    t = todas(d)
    assert list(t.loc[0]) == [True, True, True, True, False]   # fuera del sector informal: es un hogar
    assert t.loc[1, "pension"] == False and t.loc[1, "salud"] == False and t.loc[1, "tamano"] == False


def test_resultados_reproducen_las_cifras_del_dane():
    r = json.load(open(os.path.join(os.path.dirname(__file__), "..", "resultados", "informalidad_2025.json")))
    for clave, v in r["validacion"].items():
        tolerancia = 0.05 if "miles" not in clave else 0.5
        assert abs(round(v["propio"], 2 if "q4" in clave and "oficial" not in clave else 1) - v["dane"]) <= tolerancia, clave
