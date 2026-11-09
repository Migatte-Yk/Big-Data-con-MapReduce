# Evidencias

Todo lo que hay en esta carpeta salió de la ejecución real del 8 de noviembre de 2026:

- Los `.txt` y `.log` son lo que mostró la consola o lo que escribieron los servicios de Hadoop. En los logs de los jobs se quitaron solo las líneas de aviso (`WARN`).
- Los `.png` son capturas de las páginas web de Hadoop.
- Los jobs se corrieron primero en modo local y después en YARN. Los archivos 01, 02, 03, 08 y los `*_lectura_hdfs.txt` se volvieron a generar en la corrida de YARN.

| Archivo | Qué muestra |
|---|---|
| 00_generacion_dataset.txt | Cómo se creó el dataset y qué errores se le metieron |
| 01_versiones.txt | Versiones de Java, Python, Hadoop y Git |
| 01_hdfs_namenode_format.log | Preparación inicial de HDFS |
| 02_daemon_*.log | Arranque de los cuatro servicios de Hadoop |
| 02_estado_cluster.txt | HDFS y YARN funcionando |
| 03_hdfs_carga_dataset.txt | Subida del dataset a HDFS |
| 04_intento_yarn_job1_fallido.log | Intento fallido en YARN por permisos de Windows |
| 05/06/07_Job*_local.log | Log de cada job, con sus contadores |
| 05/06/07_Job*_lectura_hdfs.txt | Resultado de cada job leído desde HDFS |
| 08_hdfs_arbol_final.txt | Carpetas y archivos finales en HDFS |
| 09_salida_consola_ejecucion.txt | Todo lo que mostró `ejecutar_mapreduce.sh` |
| 10_validacion_cruzada_pandas.txt | Comparación con pandas: todo coincide |
| 11 y 12 (.png) | Página web de HDFS: resumen y DataNode activo |
| 13, 14 y 15 (.png) | Explorador de HDFS con la entrada y los resultados |
| 16 (.png) | Página web de YARN con el nodo activo |
| 17 y 18 (.png) | El primer intento en YARN, fallido por permisos, y su mensaje de error |
| 05/06/07_Job*_yarn.log | Log de cada job en YARN (2 tareas map y 1 reduce) |
| 19_salida_consola_ejecucion_yarn.txt | Todo lo que mostró `ejecutar_mapreduce.sh yarn` |
| 20_validacion_cruzada_yarn.txt | Comparación con pandas de los resultados de YARN: todo coincide |
| 21 (.png) | YARN con los tres jobs en estado SUCCEEDED |
| 22 (.png) | Detalle del Job 1 terminado en YARN |
| 23 (.png) | Explorador de HDFS con las salidas de la ejecución en YARN |
| 24_intento_yarn_python_fallido/ | Segundo intento en YARN, fallido por el lanzador de Python |

## Capturas que faltan (las toma el estudiante)

Estas muestran la terminal o el editor, así que hay que tomarlas a mano. Primero encienda HDFS (ver `documentacion/configuracion.md`, paso 5). Luego abra Git Bash en la carpeta del proyecto, ejecute `source scripts/entorno_hadoop.sh` y capture la ventana después de cada paso:

| # | Qué hacer | Qué se debe ver |
|---|---|---|
| C1 | `java -version; python --version; hadoop version` | Las versiones |
| C2 | `cat /c/hadoop/etc/hadoop/core-site.xml /c/hadoop/etc/hadoop/hdfs-site.xml` | La configuración |
| C3 | `hdfs dfs -ls -R /user/bigdata/ventas` | Los archivos en HDFS |
| C4 | Abrir un Mapper y un Reducer de `src/` en VS Code | El código |
| C5 | `bash scripts/ejecutar_mapreduce.sh` | Cada job terminando con `completed successfully` |
| C6 | `hdfs dfs -cat /user/bigdata/ventas/salida/ingresos_producto/part-00000` | Un resultado leído desde HDFS |
| C7 | `python scripts/validar_resultados.py` | La comprobación con pandas |
| C8 | La carpeta del proyecto en el Explorador de archivos | La estructura final |

Haga C5 antes que C6: el resultado no existe hasta que corre el job.
