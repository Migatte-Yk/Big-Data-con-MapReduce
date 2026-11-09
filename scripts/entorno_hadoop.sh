#!/usr/bin/env bash
# Variables de entorno de la sesión (Git Bash en Windows). No modifica el sistema:
# solo afectan a la terminal actual.  Uso:  source scripts/entorno_hadoop.sh
export HADOOP_HOME='C:\hadoop'
export HADOOP_CONF_DIR='C:\hadoop\etc\hadoop'
export JAVA_HOME='C:\PROGRA~1\MIE74D~1\JDK-17~1.10-'
export PYTHONIOENCODING=utf-8
# Evita que Git Bash convierta rutas HDFS como /user/... en rutas de Windows
export MSYS_NO_PATHCONV=1
export PATH="/c/hadoop/bin:/c/hadoop/sbin:$PATH"
# En Git Bash los .cmd se invocan con extensión; se crean alias cortos.
hadoop() { hadoop.cmd "$@"; }
hdfs()   { hdfs.cmd "$@"; }
yarn()   { yarn.cmd "$@"; }
mapred() { mapred.cmd "$@"; }
export -f hadoop hdfs yarn mapred
