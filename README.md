# La informalidad depende de cómo la midas

¿Cuántos trabajadores informales hay en Colombia? La respuesta cambia según la definición. Este repositorio calcula la informalidad laboral de 2025 con cinco definiciones sobre los mismos microdatos de la Gran Encuesta Integrada de Hogares (GEIH) del DANE, y mide a cuántas personas cambia de categoría esa elección.

Artículo: [nicolasforero.pages.dev/escritos/informalidad](https://nicolasforero.pages.dev/escritos/informalidad/)

## Validación primero

La medida oficial es una traducción literal a Python del código Stata que el DANE publica en el anexo de su boletín de ocupación informal (`referencias/`). Antes de comparar definiciones, el cálculo debe reproducir las cifras publicadas:

| Cifra (2025) | DANE | Este repositorio |
|---|---:|---:|
| Informalidad, total nacional, año | 55,7 % | 55,72 % |
| Informalidad, 13 ciudades y A.M., año | 42,2 % | 42,18 % |
| Informalidad, centros poblados y rural disperso, año | 83,5 % | 83,51 % |
| Informalidad, total nacional, oct-dic | 55,7 % | 55,68 % |
| Informalidad hombres, oct-dic | 58,1 % | 58,05 % |
| Informalidad mujeres, oct-dic | 52,4 % | 52,37 % |
| Cotizan a pensión, oct-dic | 43,08 % | 43,08 % |
| Aportan a salud (contributivo o especial), oct-dic | 46,50 % | 46,50 % |
| Ocupados, oct-dic (miles) | 24.397,3 | 24.397,3 |

Una prueba (`tests/`) falla si alguna de estas cifras se aleja de la publicada.

## Las cinco definiciones

| Definición | Es informal quien… | Tasa 2025 |
|---|---|---:|
| Oficial (DANE, 17.ª CIET) | asalariado sin salud y pensión pagadas con su empleador; independiente cuyo negocio no tiene registro mercantil al día ni contabilidad; trabajador sin remuneración | 55,7 % |
| Pensión | no cotiza a un fondo de pensiones ni está pensionado | 55,1 % |
| Salud | no aporta al régimen contributivo o especial | 53,3 % |
| Tamaño (criterio anterior del DANE, 15.ª CIET) | trabaja donde hay hasta 5 personas, salvo gobierno e independientes profesionales | 52,8 % |
| Sector informal | trabaja en una unidad económica no registrada y sin contabilidad | 45,4 % |

Con las cinco, el 36,8 % de los ocupados es informal siempre y el 36,8 % es formal siempre. El 26,4 % restante, unos 6,3 millones de personas, cambia según la definición.

## Cómo reproducirlo

1. Descargar los 12 meses de la [GEIH 2025](https://microdatos.dane.gov.co/index.php/catalog/853) (formato CSV). El portal del DANE pide registro y un captcha, así que la descarga es manual.
2. `python src/cargar.py RUTA` (carpeta con `Enero 2025/`, …, `Diciembre 2025/`).
3. `python src/analisis.py` → `resultados/informalidad_2025.json`.
4. `pytest`.

## Lo que este proyecto no hace

- **No publica microdatos.** Solo código y agregados. Los microdatos se consultan en el portal del DANE.
- **No reporta intervalos de confianza propios.** Los archivos públicos no traen los estratos y conglomerados del diseño muestral; para la precisión de la cifra oficial se remite a los errores relativos del DANE. Las diferencias entre definiciones se calculan sobre las mismas personas, así que no son ruido muestral entre encuestas.
- **El criterio de tamaño es una aproximación.** El DANE ya no lo publica para la GEIH marco 2018; aquí "independientes profesionales" son los cuenta propia con oficios de los grandes grupos 2 y 3 de la CIUO-08.
- **No dice cuál definición es la correcta.** Cada una responde una pregunta distinta (protección social, tamaño de la unidad productiva, registro); el punto es saber cuál se está usando.
- **No mide causas ni efectos de la informalidad.**

## Fuente y licencia

Datos: DANE, Gran Encuesta Integrada de Hogares (GEIH) 2025. Código de informalidad: DANE, anexo estadístico del boletín de ocupación informal, trimestre octubre-diciembre 2025. Cálculos propios. El código de este repositorio es MIT.
