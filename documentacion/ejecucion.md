# Cómo se ejecutó

Todos los comandos se escriben en **Git Bash**, desde la carpeta del proyecto, después de correr `source scripts/entorno_hadoop.sh`.

## 1. Crear el dataset

```bash
python scripts/generar_dataset.py
```

El script siempre produce el mismo archivo: 5 000 ventas inventadas más el encabezado. A 154 de ellas se les metieron errores a propósito para probar la limpieza (`evidencias/00_generacion_dataset.txt`).

## 2. Subir el dataset a HDFS

```bash
hdfs dfs -mkdir -p /user/bigdata/ventas/entrada
hdfs dfs -put -f data/dataset.csv /user/bigdata/ventas/entrada/
hdfs dfs -ls -R /user/bigdata/ventas
hdfs fsck /user/bigdata/ventas/entrada/dataset.csv -files -blocks
```

El archivo quedó guardado en HDFS sin errores: 463 189 bytes en un solo bloque (`evidencias/03_hdfs_carga_dataset.txt`).

## 3. Correr los jobs

```bash
bash scripts/ejecutar_mapreduce.sh          # modo local
bash scripts/ejecutar_mapreduce.sh yarn     # modo YARN (servicios encendidos como administrador)
```

Para cada job, el script borra el resultado anterior, lanza el job, guarda el log en `evidencias/` y copia el resultado de HDFS a `resultados/`.

El script le pasa a Hadoop la ruta completa de `python.exe`, porque dentro de los contenedores de YARN el comando `python` abre el lanzador de Windows y falla.

Por dentro, el Job 1 en modo local se lanza así (sintaxis de `cmd`):

```bat
hadoop jar %HADOOP_HOME%\share\hadoop\tools\lib\hadoop-streaming-3.3.6.jar ^
  -D "mapreduce.framework.name=local" ^
  -D "mapreduce.job.name=Job1_ventas_por_categoria" ^
  -D "mapreduce.job.reduces=1" ^
  -cmdenv "PYTHONIOENCODING=utf-8" ^
  -mapper   "<python.exe> C:/Users/Migatte/Desktop/Posgrado/BigDataMapReduce/src/mapper_ventas_categoria.py" ^
  -combiner "<python.exe> C:/Users/Migatte/Desktop/Posgrado/BigDataMapReduce/src/reducer_ventas_categoria.py" ^
  -reducer  "<python.exe> C:/Users/Migatte/Desktop/Posgrado/BigDataMapReduce/src/reducer_ventas_categoria.py" ^
  -input  /user/bigdata/ventas/entrada/dataset.csv ^
  -output /user/bigdata/ventas/salida/ventas_categoria
```

En modo YARN cambia `mapreduce.framework.name=yarn`, y los scripts se envían con `-files` para que Hadoop los copie a cada contenedor.

## 4. Ver los resultados en HDFS

```bash
hdfs dfs -ls  /user/bigdata/ventas/salida/ventas_categoria
hdfs dfs -cat /user/bigdata/ventas/salida/ventas_categoria/part-00000
```

## 5. Revisar y graficar

```bash
python scripts/validar_resultados.py   # repite las cuentas con pandas y compara
python scripts/generar_graficos.py     # crea los gráficos en informe/figuras/
```

## 6. Lo que pasó el 8 de noviembre de 2026

Los jobs se corrieron dos veces y las dos terminaron bien con los mismos resultados:

| Job | Modo | Identificador | Tareas map / reduce | Duración |
|---|---|---|---:|---:|
| 1. Ventas por categoría | Local | job_local347978619_0001 | 1 / 1 | ≈ 6 s |
| 2. Cantidad por categoría | Local | job_local1797907852_0001 | 1 / 1 | ≈ 6 s |
| 3. Ingresos por producto | Local | job_local1206865355_0001 | 1 / 1 | ≈ 6 s |
| 1. Ventas por categoría | YARN | application_1794196757153_0004 | 2 / 1 | 33 s |
| 2. Cantidad por categoría | YARN | application_1794196757153_0005 | 2 / 1 | 32 s |
| 3. Ingresos por producto | YARN | application_1794196757153_0006 | 2 / 1 | 36 s |

En todos los casos se leyeron 5 001 líneas y 4 878 ventas fueron válidas. YARN tarda más porque tiene que lanzar contenedores; con un archivo tan pequeño eso pesa más que el procesamiento.

Hadoop contó así los registros con problemas, con los mismos números en todos los jobs:

- 17 filas incompletas.
- 18 sin categoría y 19 sin producto.
- 17 con cantidad que no es número y 32 con cantidad cero o negativa.
- 19 con precio inválido.
- 15 precios con coma decimal, que se corrigieron.
- 32 totales vacíos, que se recalcularon.

Antes de que YARN funcionara hubo dos intentos fallidos, que también quedaron guardados:

1. Sin permisos de administrador, YARN no pudo crear los contenedores (`evidencias/04_intento_yarn_job1_fallido.log` y `evidencias/18_ui_yarn_diagnostico_symlink.png`).
2. Con permisos, el comando `python` abrió el lanzador de Windows dentro del contenedor y no encontró Python (`evidencias/24_intento_yarn_python_fallido/`). Se arregló usando la ruta completa de `python.exe`.

## 7. Apagar los servicios

Basta con cerrar las terminales donde corren los servicios, o terminar los procesos `java.exe` de Hadoop desde el Administrador de tareas.
