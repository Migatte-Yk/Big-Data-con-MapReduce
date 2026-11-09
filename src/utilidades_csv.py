"""Funciones comunes de lectura y validación usadas por los tres Mappers.

Hadoop Streaming entrega al Mapper cada línea del split de entrada por la
entrada estándar (stdin). Este módulo convierte una línea CSV en un registro
validado, o informa el motivo por el que se descarta.

Reglas de calidad:
  * Encabezado (primera columna = "id_venta")      -> se omite.
  * Número de columnas distinto de 10               -> descartado.
  * Categoría o producto vacíos                     -> descartado.
  * Cantidad no entera o <= 0                       -> descartado.
  * Precio no numérico o <= 0                       -> descartado.
  * Precio con coma decimal ("45900,50")            -> se normaliza.
  * total_venta vacío o inválido                    -> se recalcula cantidad × precio.

Cada descarte se reporta a Hadoop como contador con la sintaxis de Streaming
"reporter:counter:<grupo>,<contador>,<incremento>" escrita en stderr; así los
totales aparecen en el log del job sin ensuciar la salida.
"""
import csv
import io
import sys
from decimal import Decimal, InvalidOperation

COLUMNAS = ["id_venta", "fecha", "region", "categoria", "producto_id", "producto",
            "cantidad", "precio_unitario", "total_venta", "metodo_pago"]
GRUPO_CONTADORES = "Calidad de datos"


def configurar_es():
    """stdin/stdout en UTF-8 y saltos de línea '\\n' (evita '\\r\\n' en Windows)."""
    entrada = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace", newline="")
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    return entrada


def contador(nombre, incremento=1):
    sys.stderr.write(f"reporter:counter:{GRUPO_CONTADORES},{nombre},{incremento}\n")


def a_decimal(texto):
    """Convierte '1234.50', '1234,50', '1.234,50' o '1,234.50' a Decimal; None si no es número."""
    t = (texto or "").strip().replace(" ", "").replace("$", "")
    if not t:
        return None
    if "," in t and "." in t:
        # El separador que aparece al final es el decimal
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".", "").replace(",", ".")
        else:
            t = t.replace(",", "")
    elif "," in t:
        t = t.replace(",", ".")
    try:
        valor = Decimal(t)
    except InvalidOperation:
        return None
    return valor if valor.is_finite() else None


def parsear_linea(linea):
    """Devuelve (registro, None) si la línea es válida o (None, motivo) si no lo es."""
    linea = linea.lstrip("﻿").rstrip("\r\n")
    if not linea.strip():
        return None, "Linea vacia"
    try:
        campos = next(csv.reader([linea]))
    except (csv.Error, StopIteration):
        return None, "CSV mal formado"
    if campos and campos[0].strip() == "id_venta":
        return None, "Encabezado omitido"
    if len(campos) != len(COLUMNAS):
        return None, "Columnas incompletas"
    r = dict(zip(COLUMNAS, (c.strip() for c in campos)))

    if not r["categoria"]:
        return None, "Categoria vacia"
    if not r["producto_id"] and not r["producto"]:
        return None, "Producto vacio"

    cantidad = a_decimal(r["cantidad"])
    if cantidad is None or cantidad != cantidad.to_integral_value():
        return None, "Cantidad no numerica"
    if cantidad <= 0:
        return None, "Cantidad no positiva"

    precio = a_decimal(r["precio_unitario"])
    if precio is None or precio <= 0:
        return None, "Precio invalido"
    if "," in r["precio_unitario"]:
        contador("Precio con coma normalizado")

    total = a_decimal(r["total_venta"])
    if total is None or total <= 0:
        total = cantidad * precio
        contador("Total recalculado")

    r["cantidad"] = int(cantidad)
    r["precio_unitario"] = precio
    r["importe"] = total.quantize(Decimal("0.01"))
    return r, None


def registros(entrada):
    """Itera sobre los registros válidos de la entrada y cuenta los descartes."""
    for linea in entrada:
        registro, motivo = parsear_linea(linea)
        if registro is None:
            contador(motivo)
            continue
        contador("Registros validos")
        yield registro
