#!/usr/bin/env bash
# =============================================================================
# Ejecuta los tres jobs MapReduce (Hadoop Streaming + Python) sobre HDFS.
#
# Requisitos previos (ver documentacion/ejecucion.md):
#   - HDFS iniciado (hdfs namenode / hdfs datanode).
#   - Para modo yarn: ResourceManager y NodeManager iniciados desde una
#     terminal de ADMINISTRADOR (Windows exige privilegio de enlaces simbólicos).
#
# Uso (Git Bash, desde la raíz del proyecto):
#   bash scripts/ejecutar_mapreduce.sh            # modo local (LocalJobRunner) + HDFS
#   bash scripts/ejecutar_mapreduce.sh yarn       # modo YARN
# =============================================================================
set -u
MODO="${1:-local}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ"
source scripts/entorno_hadoop.sh

EV="evidencias"
HDFS_BASE=/user/bigdata/ventas
ENTRADA=$HDFS_BASE/entrada/dataset.csv
SRC_WIN="$(cygpath -m "$RAIZ/src")"
mkdir -p "$EV" resultados
# Ruta completa de python.exe (sin espacios): en YARN, "python" puede resolver al
# lanzador de Windows, que dentro del contenedor no encuentra instalaciones.
PY_WIN="$(cygpath -m "$(python -c 'import sys; print(sys.executable)')")"

paso() { echo; echo "=================== $* ==================="; }

paso "1. Versiones de las herramientas"
{
  echo '$ java -version';   java -version 2>&1
  echo '$ python --version'; python --version 2>&1
  echo '$ hadoop version';  hadoop version 2>&1
  echo '$ git --version';   git --version 2>&1
  echo "HADOOP_HOME=$HADOOP_HOME"; echo "JAVA_HOME=$JAVA_HOME"; echo "HADOOP_CONF_DIR=$HADOOP_CONF_DIR"
} | tee "$EV/01_versiones.txt"

paso "2. Estado del clúster"
{
  echo '$ hdfs dfsadmin -report'; hdfs dfsadmin -report 2>&1 | grep -E "Live datanodes|Name:|Configured Capacity|DFS Remaining|DFS Used:"
  echo '$ yarn node -list -all';  yarn node -list -all 2>&1 | grep -v WARN
} | tee "$EV/02_estado_cluster.txt"

paso "3. Carga del dataset en HDFS"
{
  echo "\$ hdfs dfs -mkdir -p $HDFS_BASE/entrada"; hdfs dfs -mkdir -p $HDFS_BASE/entrada
  echo "\$ hdfs dfs -put -f data/dataset.csv $HDFS_BASE/entrada/"; hdfs dfs -put -f data/dataset.csv $HDFS_BASE/entrada/
  echo "\$ hdfs dfs -ls -R $HDFS_BASE"; hdfs dfs -ls -R $HDFS_BASE/entrada
  echo "\$ hdfs dfs -cat $ENTRADA | head -4"; hdfs dfs -cat $ENTRADA 2>/dev/null | head -4
  echo "\$ hdfs fsck $ENTRADA -files -blocks"; hdfs fsck $ENTRADA -files -blocks 2>&1 | grep -E "bytes|blk_|Status"
} | tee "$EV/03_hdfs_carga_dataset.txt"

declare -A NOMBRES=( [ventas_categoria]="Job1_ventas_por_categoria"
                     [cantidad_categoria]="Job2_cantidad_por_categoria"
                     [ingresos_producto]="Job3_ingresos_por_producto" )
N=5
FALLOS=0
for SUF in ventas_categoria cantidad_categoria ingresos_producto; do
  JOB=${NOMBRES[$SUF]}
  SALIDA=$HDFS_BASE/salida/$SUF
  LOG="$EV/0${N}_${JOB}_${MODO}.log"
  paso "$N. $JOB (modo $MODO)"
  hdfs dfs -rm -r -f -skipTrash "$SALIDA" > /dev/null 2>&1
  INICIO=$(date +%s)
  {
    echo "\$ hadoop jar hadoop-streaming-3.3.6.jar -D mapreduce.framework.name=$MODO -D mapreduce.job.name=$JOB"
    echo "    -mapper mapper_$SUF.py -combiner reducer_$SUF.py -reducer reducer_$SUF.py"
    echo "    -input $ENTRADA -output $SALIDA"
    cmd /c "scripts\\streaming_job.cmd" "$JOB" "$SUF" "$SRC_WIN" "$ENTRADA" "$SALIDA" "$MODO" "$PY_WIN" 2>&1
  } | grep -av -E "^\s+at |WARN" > "$LOG"
  ESTADO=${PIPESTATUS[0]}
  echo "Duración (s): $(( $(date +%s) - INICIO ))" >> "$LOG"
  grep -aE "completed successfully|failed|Map input records|Map output records|Combine output|Reduce output records|Calidad de datos|Registros validos|Columnas|Categoria|Producto vacio|Cantidad|Precio|Total recalculado|Encabezado|Duración" "$LOG" | tail -25

  echo "--- Lectura del resultado desde HDFS"
  {
    echo "\$ hdfs dfs -ls $SALIDA"; hdfs dfs -ls "$SALIDA"
    echo "\$ hdfs dfs -cat $SALIDA/part-00000"; hdfs dfs -cat "$SALIDA/part-00000"
  } 2>&1 | tee "$EV/0${N}_${JOB}_lectura_hdfs.txt"

  # Solo se reemplaza la copia local si el job terminó bien
  if grep -aq "completed successfully" "$LOG"; then
    rm -rf "resultados/$SUF" && mkdir -p "resultados/$SUF"
    hdfs dfs -get "$SALIDA/part-00000" "$SALIDA/_SUCCESS" "resultados/$SUF/" 2>/dev/null
    [ -s "resultados/$SUF/part-00000" ] || { echo "!! No se pudo descargar $SALIDA"; FALLOS=$((FALLOS+1)); }
  else
    echo "!! $JOB falló: se conserva la copia anterior de resultados/$SUF"; FALLOS=$((FALLOS+1))
  fi
  N=$((N+1))
done

paso "8. Árbol de salidas en HDFS"
hdfs dfs -ls -R $HDFS_BASE 2>&1 | tee "$EV/08_hdfs_arbol_final.txt"

[ $FALLOS -eq 0 ] && echo "Ejecución finalizada correctamente." || echo "Ejecución con $FALLOS fallos."
exit $FALLOS
