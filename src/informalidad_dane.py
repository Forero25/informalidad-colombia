"""Traducción literal del código Stata del DANE (anexo GEIHEISS oct-dic 2025, pestaña Código_STATA).
Semántica de Stata: un valor faltante es mayor que cualquier número, así que `x >= k` es verdadero si x falta."""
import numpy as np
import pandas as pd

def ge(s,k):  # Stata: missing >= k es verdadero
    return s.fillna(np.inf)>=k

def ei_dane(d, anio=2025):
    """Devuelve (EI, FORMAL, SALUD, PENSION) como en el código del DANE. EI=0 es ocupado informal."""
    P=lambda c:d[c]
    pos=P("P6430"); anios=anio-1
    of2=pd.to_numeric(d["OFICIO_C8"].astype(str).str[:2],errors="coerce")
    rama=d["RAMA2D_R4"].astype(str)
    gob=rama.isin(["84","99"])
    F=pd.Series(np.nan,index=d.index)
    def rep(cond,v): F.loc[cond.fillna(False)]=v
    rep(pos==6,0); rep(gob,1); rep(pos==8,0)
    # asalariados
    a=pos.isin([1,7]); noreg=P("P3045S1").isin([2,9])
    rep(pos==2,1)
    rep(a&(P("P3045S1")==1),1)
    rep(a&noreg&(P("P3046")==1),1)
    rep(a&noreg&(P("P3046")==2),0)
    rep(a&noreg&(P("P3046")==9)&ge(P("P3069"),4),1)
    rep(a&noreg&(P("P3046")==9)&(P("P3069")<=3),0)
    # independientes sin negocio
    i45=pos.isin([4,5]); sn=P("P6765").isin([1,2,3,4,5,6,8]); nr=P("P3065").isin([2,9])
    rep(i45&sn&(P("P3065")==1),1)
    rep(i45&sn&nr&(P("P3066")==1),1)
    rep(i45&sn&nr&(P("P3066")==2),0)
    rep((pos==5)&sn&nr&(P("P3066")==9)&ge(P("P3069"),4),1)
    rep((pos==5)&sn&nr&(P("P3066")==9)&(P("P3069")<=3),0)
    rep((pos==4)&sn&nr&(P("P3066")==9)&ge(of2,0)&(of2<=20),1)
    rep((pos==4)&sn&nr&(P("P3066")==9)&ge(of2,21),0)
    # con negocio, con registro
    cn=P("P6765")==7; r1=P("P3067")==1; ren=P("P3067S1")
    rep(i45&cn&r1&(ren==1)&ge(P("P3067S2"),anios),1)
    rep(i45&cn&r1&(ren==1)&(P("P3067S2")<anios),0)
    rep(i45&cn&r1&(ren==2)&(P("P6775")==1),1)
    rep(i45&cn&r1&(ren==2)&(P("P6775")==3)&ge(of2,0)&(of2<=20),1)
    rep(i45&cn&r1&(ren==2)&(P("P6775")==3)&ge(of2,21),0)
    rep(i45&cn&r1&(ren==2)&(P("P6775")==2),0)
    rep((pos==4)&cn&r1&(ren==2)&(P("P6775")==9)&ge(of2,0)&(of2<=20),1)
    rep((pos==4)&cn&r1&(ren==2)&(P("P6775")==9)&ge(of2,21),0)
    rep((pos==5)&cn&r1&(ren==2)&(P("P6775")==9)&ge(P("P3069"),4),1)
    rep((pos==5)&cn&r1&(ren==2)&(P("P6775")==9)&(P("P3069")<=3),0)
    # con negocio, sin registro
    r2=P("P3067")==2
    rep(i45&cn&r2&(P("P6775")==1)&(P("P3068")==1),1)
    rep(i45&cn&r2&(P("P6775")==1)&(P("P3068")==2),0)
    rep(i45&cn&r2&(P("P6775")==3)&ge(of2,0)&(of2<=20),1)
    rep(i45&cn&r2&(P("P6775")==3)&ge(of2,21),0)
    rep(i45&cn&r2&(P("P6775")==1)&P("P3068").isin([9,3]),0)
    rep(i45&cn&r2&(P("P6775")==2),0)
    rep((pos==5)&cn&r2&(P("P6775")==9)&ge(P("P3069"),4),1)
    rep((pos==5)&cn&r2&(P("P6775")==9)&(P("P3069")<=3),0)
    rep((pos==4)&cn&r2&(P("P6775")==9)&ge(of2,0)&(of2<=20),1)
    rep((pos==4)&cn&r2&(P("P6775")==9)&ge(of2,21),0)
    # salud y pensión
    a2=pos.isin([1,3,7])
    salud=a2&P("P6100").isin([1,2])&P("P6110").isin([1,2,4])
    salud|=a2&(P("P6100")==9)&(P("P6450")==2)
    salud|=a2&(P("P6110")==9)&(P("P6450")==2)
    pension=a2&(P("P6920")==3)
    pension|=a2&(P("P6920")==1)&P("P6930").isin([1,2,3])&P("P6940").isin([1,3])
    EI=pd.Series(0.0,index=d.index)
    EI[pos==2]=1
    EI[i45]=F[i45]          # puede quedar faltante, como en Stata
    EI[pos.isin([1,2,3,7])&salud&pension]=1
    EI[pos.isin([1,2,3,4,5,7])&gob]=1
    return EI, F, salud, pension
