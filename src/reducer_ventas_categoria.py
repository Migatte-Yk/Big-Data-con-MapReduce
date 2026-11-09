#!/usr/bin/env python3
"""Job 1 – Reducer: suma los importes de cada categoría.

Hadoop ordena la salida de los Mappers por clave (fase shuffle & sort), de modo
que todas las líneas de una misma categoría llegan consecutivas. El Reducer
acumula mientras la clave no cambie y emite el total al detectar una clave nueva.

Entrada : <categoria>\\t<importe>   (ordenada por categoría)
Salida  : <categoria>\\t<ingresos_totales>

La salida tiene el mismo formato que la entrada, por eso este script también
se usa como Combiner (sumas parciales en el lado del Map).
"""
import sys
from decimal import Decimal, InvalidOperation
from io import TextIOWrapper


def main():
    entrada = TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace", newline="")
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    clave_actual, acumulado = None, Decimal("0")
    for linea in entrada:
        linea = linea.rstrip("\r\n")
        if not linea:
            continue
        clave, _, valor = linea.partition("\t")
        try:
            importe = Decimal(valor)
        except InvalidOperation:
            sys.stderr.write("reporter:counter:Reducer,Valor no numerico,1\n")
            continue
        if clave != clave_actual:
            if clave_actual is not None:
                print(f"{clave_actual}\t{acumulado:.2f}")
            clave_actual, acumulado = clave, Decimal("0")
        acumulado += importe
    if clave_actual is not None:
        print(f"{clave_actual}\t{acumulado:.2f}")


if __name__ == "__main__":
    main()
