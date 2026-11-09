#!/usr/bin/env python3
"""Job 3 – Reducer: suma los ingresos de cada producto.

Entrada : <producto_id>|<producto>\\t<importe>   (ordenada por clave)
Salida  : <producto_id>|<producto>\\t<ingresos_totales>

Mismo formato de entrada y salida: también actúa como Combiner.
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
