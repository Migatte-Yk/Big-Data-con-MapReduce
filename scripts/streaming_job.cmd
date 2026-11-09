@echo off
rem ---------------------------------------------------------------------------
rem Lanza UN job de Hadoop Streaming (Windows).
rem Uso: streaming_job.cmd <nombre_job> <sufijo> <ruta_src> <entrada_hdfs> <salida_hdfs> [local|yarn] [ruta_python]
rem   sufijo = ventas_categoria | cantidad_categoria | ingresos_producto
rem   modo   = local (LocalJobRunner, por defecto) | yarn (requiere terminal de administrador)
rem
rem Se necesita este .cmd porque hadoop.cmd separa los argumentos por "," y "=";
rem aqui los valores con esos caracteres van entre comillas.
rem ---------------------------------------------------------------------------
setlocal
set JOB=%~1
set SUF=%~2
set SRC=%~3
set IN=%~4
set OUT=%~5
set MODO=%~6
if "%MODO%"=="" set MODO=local
rem Ruta completa del interprete de Python (en YARN, "python" puede apuntar al
rem lanzador de Windows, que dentro del contenedor no encuentra instalaciones)
set PY=%~7
if "%PY%"=="" set PY=python
set STREAMING=%HADOOP_HOME%\share\hadoop\tools\lib\hadoop-streaming-3.3.6.jar

if /I "%MODO%"=="yarn" goto yarn

rem ---- Modo local: motor MapReduce de Hadoop en un solo JVM, E/S en HDFS ----
rem Los scripts se invocan por ruta absoluta (LocalJobRunner no puede crear los
rem enlaces simbolicos de -files sin privilegios de administrador en Windows).
call "%HADOOP_HOME%\bin\hadoop.cmd" jar "%STREAMING%" ^
  -D "mapreduce.framework.name=local" ^
  -D "mapreduce.job.name=%JOB%" ^
  -D "mapreduce.job.reduces=1" ^
  -cmdenv "PYTHONIOENCODING=utf-8" ^
  -mapper "%PY% %SRC%/mapper_%SUF%.py" ^
  -combiner "%PY% %SRC%/reducer_%SUF%.py" ^
  -reducer "%PY% %SRC%/reducer_%SUF%.py" ^
  -input "%IN%" ^
  -output "%OUT%"
exit /b %ERRORLEVEL%

:yarn
rem ---- Modo YARN: contenedores gestionados por ResourceManager/NodeManager ----
call "%HADOOP_HOME%\bin\hadoop.cmd" jar "%STREAMING%" ^
  -D "mapreduce.framework.name=yarn" ^
  -D "mapreduce.job.name=%JOB%" ^
  -D "mapreduce.job.reduces=1" ^
  -files "file:///%SRC%/mapper_%SUF%.py,file:///%SRC%/reducer_%SUF%.py,file:///%SRC%/utilidades_csv.py" ^
  -cmdenv "PYTHONIOENCODING=utf-8" ^
  -mapper "%PY% mapper_%SUF%.py" ^
  -combiner "%PY% reducer_%SUF%.py" ^
  -reducer "%PY% reducer_%SUF%.py" ^
  -input "%IN%" ^
  -output "%OUT%"
exit /b %ERRORLEVEL%
