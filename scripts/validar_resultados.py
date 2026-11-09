#!/usr/bin/env python3
"""Verificación cruzada de los resultados de Hadoop (NO es parte del procesamiento).

Recalcula los tres agregados con pandas, sin reutilizar el código de los Mappers,
y los compara con los archivos part-00000 descargados de HDFS en resultados/.
Si alguna cifra difiere, el script termina con código 1.

Uso:  python scripts/validar_resultados.py
"""
import sys
from decimal import Decimal
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding="utf-8")


def numero(s):
    s = str(s).strip()
    if s in ("", "nan"):
        return None
    if "," in s and "." not in s:
        s = s.replace(",", ".")
    try:
        return Decimal(s)
    except Exception:
        return None


def calcular():
    df = pd.read_csv(RAIZ / "data" / "dataset.csv", dtype=str, keep_default_na=False,
                     encoding="utf-8")
    # Filas truncadas: pandas las rellena con "" en las últimas columnas
    df = df[df["metodo_pago"].str.strip() != ""]
    df = df[df["categoria"].str.strip() != ""]
    df = df[(df["producto_id"].str.strip() != "") | (df["producto"].str.strip() != "")]
    df["cant"] = df["cantidad"].map(numero)
    df = df[df["cant"].map(lambda c: c is not None and c == c.to_integral_value() and c > 0)]
    df["precio"] = df["precio_unitario"].map(numero)
    df = df[df["precio"].map(lambda p: p is not None and p > 0)]
    df["tot"] = df["total_venta"].map(numero)
    df["importe"] = [t if (t is not None and t > 0) else c * p
                     for t, c, p in zip(df["tot"], df["cant"], df["precio"])]
    df["clave_prod"] = df["producto_id"] + "|" + df["producto"]
    return {
        "ventas_categoria": df.groupby("categoria")["importe"].apply(lambda s: sum(s, Decimal(0))),
        "cantidad_categoria": df.groupby("categoria")["cant"].apply(lambda s: sum(s, Decimal(0))),
        "ingresos_producto": df.groupby("clave_prod")["importe"].apply(lambda s: sum(s, Decimal(0))),
    }, len(df)


def leer_hadoop(nombre):
    salida = {}
    for linea in (RAIZ / "resultados" / nombre / "part-00000").read_text(encoding="utf-8").splitlines():
        k, v = linea.split("\t")
        salida[k] = Decimal(v)
    return salida


def main():
    esperado, validos = calcular()
    print(f"Registros válidos según pandas: {validos}")
    errores = 0
    for nombre, serie in esperado.items():
        hadoop = leer_hadoop(nombre)
        iguales = set(hadoop) == set(serie.index) and all(hadoop[k] == serie[k] for k in serie.index)
        print(f"{nombre:20s} claves={len(hadoop):3d}  coincide={'SÍ' if iguales else 'NO'}")
        if not iguales:
            errores += 1
            for k in sorted(set(hadoop) | set(serie.index)):
                print("   ", k, hadoop.get(k), serie.get(k))
    print("RESULTADO:", "todas las salidas de Hadoop coinciden" if errores == 0 else f"{errores} discrepancias")
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
