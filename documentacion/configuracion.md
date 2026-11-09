# Configuración del entorno

Aquí está lo que se hizo para dejar Hadoop funcionando en el equipo `DESKTOP-69SJHMN` (Windows 11 Pro) el 8 de noviembre de 2026.

## 1. Lo que había al empezar

| Herramienta | Estado |
|---|---|
| Java | OpenJDK 17.0.19, instalado en `C:\Program Files\Microsoft\jdk-17.0.19.10-hotspot\` |
| Python | 3.14.4 |
| Git | 2.53.0 |
| Hadoop | No estaba instalado |
| WSL y Docker | No estaban instalados |
| Dataset de ventas | No había ninguno de actividades anteriores |

## 2. Instalar Hadoop 3.3.6

Se descargó la versión oficial y se comprobó que el archivo estuviera completo con su código SHA-512:

```bash
curl -O https://archive.apache.org/dist/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
curl -O https://archive.apache.org/dist/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz.sha512
sha512sum hadoop-3.3.6.tar.gz
tar -xzf hadoop-3.3.6.tar.gz -C /c/ && mv /c/hadoop-3.3.6 /c/hadoop
```

Al descomprimir salen tres avisos sobre archivos `.so`, que son de Linux. En Windows no importan.

Para Windows, Hadoop necesita además `winutils.exe` y `hadoop.dll`. Apache no los publica, así que se tomaron del repositorio <https://github.com/cdarlint/winutils> (carpeta `hadoop-3.3.6/bin`) y se copiaron a `C:\hadoop\bin`. Sus códigos SHA-256 son:

- winutils.exe: `496a591eb1e67df2a620f710d529ba6ddfe1c19149e6647cc4e320bb0efd8553`
- hadoop.dll: `d7ab36a68518748cef142be2da5069b4c763c2cd764c1d2e6ac48c7200405be3`

## 3. Archivos de configuración

Están en `C:\hadoop\etc\hadoop`. Antes de cambiar cada archivo se guardó una copia con extensión `.original`. Las versiones usadas también están en `documentacion/config_hadoop/`.

| Archivo | Qué se configuró |
|---|---|
| core-site.xml | HDFS en `hdfs://localhost:9000` |
| hdfs-site.xml | Una sola copia de cada bloque (hay un solo DataNode) y carpetas de datos en `C:/hadoop/data` |
| mapred-site.xml | MapReduce sobre YARN y opciones para que funcione con Java 17 |
| yarn-site.xml | Servicio de shuffle de MapReduce y 4096 MB de memoria para el nodo |
| hadoop-env.cmd | `JAVA_HOME` y opciones para Java 17 |

Hubo que hacer tres ajustes especiales:

- **`JAVA_HOME` sin espacios.** Los scripts de Hadoop en Windows fallan con la carpeta `Program Files`, así que se usó su nombre corto: `C:\PROGRA~1\MIE74D~1\JDK-17~1.10-`.
- **Opciones `--add-opens`.** Hadoop 3.3 usa partes internas de Java que Java 17 bloquea por defecto, y estas opciones las desbloquean.
- **Límite de disco.** Se subió para que YARN no marque el nodo como lleno.

## 4. Variables de entorno

No se cambió ninguna variable del sistema. El archivo `scripts/entorno_hadoop.sh` las define solo para la terminal abierta:

```bash
export HADOOP_HOME='C:\hadoop'
export HADOOP_CONF_DIR='C:\hadoop\etc\hadoop'
export JAVA_HOME='C:\PROGRA~1\MIE74D~1\JDK-17~1.10-'
export PYTHONIOENCODING=utf-8
export MSYS_NO_PATHCONV=1      # evita que Git Bash cambie las rutas de HDFS
export PATH="/c/hadoop/bin:/c/hadoop/sbin:$PATH"
```

## 5. Encender los servicios

```bash
source scripts/entorno_hadoop.sh
hdfs namenode -format -nonInteractive -force   # solo la primera vez
hdfs namenode     > /c/hadoop/logs/namenode.log 2>&1 &
hdfs datanode     > /c/hadoop/logs/datanode.log 2>&1 &
yarn resourcemanager > /c/hadoop/logs/resourcemanager.log 2>&1 &
yarn nodemanager     > /c/hadoop/logs/nodemanager.log 2>&1 &
```

Para comprobar que todo arrancó:

- `hdfs dfsadmin -report` debe mostrar `Live datanodes (1)`.
- `yarn node -list -all` debe mostrar un nodo en `RUNNING`.

También se puede revisar en el navegador: HDFS en <http://localhost:9870> y YARN en <http://localhost:8088>.

## 6. Problemas y cómo se resolvieron

| Error | Por qué pasa | Qué se hizo |
|---|---|---|
| `... is not a valid DFS filename` | Git Bash cambia las rutas que empiezan por `/` | `MSYS_NO_PATHCONV=1` |
| `No FileSystem for scheme "C"` | Hadoop confunde `C:` con un protocolo | Escribir las rutas como `file:///C:/...` |
| `Found 3 unexpected arguments` | `hadoop.cmd` corta los argumentos en las comas y los `=` | El script `streaming_job.cmd` los pone entre comillas |
| `PdhAddCounter ... failed` | Windows en español nombra distinto sus contadores de red | Ninguna: es un aviso y el nodo sigue funcionando |
| `CreateSymbolicLink error (1314)` | YARN necesita crear accesos directos especiales (enlaces simbólicos) y Windows solo lo permite a un administrador | Encender los servicios desde Git Bash abierto como administrador |
| `subprocess failed with code 1` en YARN y `No runtimes are installed` en el log del contenedor | Dentro del contenedor, `python` abre el lanzador de Python de Windows, que no encuentra instalaciones | Pasar la ruta completa de `python.exe` (lo hace `ejecutar_mapreduce.sh`) |

### Cómo usar YARN

Así se corrió en esta práctica (opción 1). Hay dos opciones:

1. Abrir Git Bash **como administrador**, encender los cuatro servicios y correr `bash scripts/ejecutar_mapreduce.sh yarn`.
2. Darle a la cuenta el permiso *Crear vínculos simbólicos* (`secpol.msc` → Directivas locales → Asignación de derechos de usuario) y volver a iniciar sesión.
