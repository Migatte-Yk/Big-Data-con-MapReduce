# Análisis de ventas con Hadoop MapReduce (R2-A4-S15)

Práctica de **Big Data** de la Especialización en Analítica y Ciencia de Datos, Universidad de Cundinamarca.

Usé Hadoop para procesar un archivo CSV de ventas con tres jobs MapReduce escritos en Python. Los datos se guardan en HDFS y los jobs se lanzan con Hadoop Streaming.

| Job | El Mapper saca | El Reducer suma |
|---|---|---|
| 1. Ventas por categoría | categoría e importe | ingresos de cada categoría |
| 2. Cantidad por categoría | categoría y cantidad | unidades vendidas de cada categoría |
| 3. Ingresos por producto | producto e importe | ingresos de cada producto |

## Objetivos

- Poner en práctica MapReduce con un caso sencillo de ventas.
- Guardar la entrada y los resultados en HDFS.
- Limpiar datos con errores (vacíos, textos donde van números, comas decimales, filas incompletas).
- Dejar todo documentado para que se pueda repetir.

## Herramientas

| Herramienta | Versión |
|---|---|
| Windows 11 Pro | 10.0.26200 |
| Java (OpenJDK) | 17.0.19 |
| Apache Hadoop | 3.3.6 |
| winutils.exe y hadoop.dll | 3.3.6, del repositorio `cdarlint/winutils` (Apache no los publica para Windows) |
| Python | 3.14.4 (pandas y matplotlib solo para la verificación y los gráficos) |

## Carpetas

```
BigDataMapReduce/
├── data/dataset.csv          # 5 000 ventas de prueba (datos sintéticos)
├── src/                      # Mappers, Reducers y utilidades_csv.py (validación)
├── scripts/                  # ejecutar_mapreduce.sh y scripts de apoyo
├── resultados/               # salidas de los tres jobs descargadas de HDFS
├── evidencias/               # logs y capturas de la ejecución
├── documentacion/            # configuracion.md y ejecucion.md
└── informe/                  # informe en Markdown y PDF, con sus gráficos
```

## Requisitos

- Java 17 y Python 3.10 o superior.
- Hadoop 3.3.6 en `C:\hadoop`, con `winutils.exe` y `hadoop.dll` en `C:\hadoop\bin`.
- Git Bash.

Los pasos de instalación están en [documentacion/configuracion.md](documentacion/configuracion.md).

## Cómo ejecutarlo

```bash
source scripts/entorno_hadoop.sh
hdfs namenode -format -nonInteractive   # solo la primera vez
hdfs namenode &
hdfs datanode &
bash scripts/ejecutar_mapreduce.sh       # carga el CSV en HDFS y corre los 3 jobs
python scripts/validar_resultados.py     # compara con un cálculo en pandas
python scripts/generar_graficos.py
python informe/generar_pdf.py
```

Los jobs se corrieron de dos formas, y las dos dieron los mismos resultados:

- **Modo local:** `bash scripts/ejecutar_mapreduce.sh`. Todo corre en un solo proceso de Java.
- **YARN:** con los servicios (también `yarn resourcemanager` y `yarn nodemanager`) encendidos desde un Git Bash abierto **como administrador**, `bash scripts/ejecutar_mapreduce.sh yarn`. Cada job usó 2 tareas map en paralelo y 1 reduce.

Más detalle en [documentacion/ejecucion.md](documentacion/ejecucion.md).

## Resultados

De 5 001 líneas leídas (contando el encabezado), 4 878 ventas fueron válidas, 122 se descartaron y 32 se corrigieron.

| Categoría | Ingresos (COP) | % ingresos | Unidades | % unidades |
|---|---:|---:|---:|---:|
| Electrónica | 597 643 900 | 29,3 % | 2 316 | 17,4 % |
| Ropa | 468 758 600 | 23,0 % | 3 034 | 22,8 % |
| Deportes | 433 513 000 | 21,3 % | 1 345 | 10,1 % |
| Hogar | 343 288 900 | 16,8 % | 1 981 | 14,9 % |
| Libros | 113 946 400 | 5,6 % | 1 275 | 9,6 % |
| Alimentos | 82 327 900 | 4,0 % | 3 346 | 25,2 % |
| **Total** | **2 039 478 700** | 100 % | **13 297** | 100 % |

Los productos que más venden en dinero son la Bicicleta estática (350,6 millones) y el Monitor de 24 pulgadas (312,2 millones). Entre los dos suman el 32,5 % del total. La lista completa está en `resultados/ingresos_producto/part-00000`.

Para comprobar los resultados, `scripts/validar_resultados.py` hace las mismas cuentas con pandas. Las 36 cifras coinciden con las de Hadoop, tanto en modo local como en YARN.

## Datos

Proyecto académico. El dataset es sintético: lo generó `scripts/generar_dataset.py` y no contiene ventas reales ni datos personales.
