"""Cinco formas de decir quién es informal. Cada función devuelve una serie booleana (True = informal)."""
import pandas as pd
from informalidad_dane import ei_dane


def gobierno(d):
    return d["RAMA2D_R4"].astype(str).isin(["84", "99"])


def oficial(d):
    """Medida oficial del DANE (17.ª CIET de la OIT), traducida de su código Stata."""
    ei, *_ = ei_dane(d)
    return ei == 0


def pension(d):
    """No cotiza a un fondo de pensiones ni está pensionado (P6920)."""
    return ~d["P6920"].isin([1, 3])


def salud(d):
    """No aporta al régimen contributivo o especial de salud (beneficiarios y subsidiados cuentan como informales)."""
    return ~(d["P6100"].isin([1, 2]) & d["P6110"].isin([1, 2, 3, 4]))


def tamano(d):
    """Criterio anterior del DANE (15.ª CIET): trabaja donde hay hasta 5 personas (P3069 <= 3).
    Excluye gobierno y, como aproximación a los "independientes profesionales", a los cuenta propia
    con oficios de los grandes grupos 2 y 3 de la CIUO-08."""
    profesional = d["OFICIO_C8"].astype(str).str[0].isin(["2", "3"])
    return (d["P3069"] <= 3) & (d["P6430"] != 2) & ~gobierno(d) & ~((d["P6430"] == 4) & profesional)


def sector(d):
    """Trabaja en una unidad económica del sector informal (paso 1 del código del DANE).
    Los hogares que contratan servicio doméstico no hacen parte de ese sector."""
    _, formal_unidad, *_ = ei_dane(d)
    return formal_unidad == 0


DEFINICIONES = {"oficial": oficial, "pension": pension, "salud": salud, "tamano": tamano, "sector": sector}


def todas(d):
    return pd.DataFrame({k: f(d) for k, f in DEFINICIONES.items()})
