#!/usr/bin/env python3
"""Job 2 – Reducer: suma las unidades vendidas de cada categoría.

Entrada : <categoria>\\t<cantidad>   (ordenada por categoría tras shuffle & sort)
Salida  : <categoria>\\t<unidades_totales>

Mismo formato de entrada y salida: también actúa como Combiner.
"""
import sys
from io import TextIOWrapper


def main():
    entrada = TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace", newline="")
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    clave_actual, acumulado = None, 0
    for linea in entrada:
        linea = linea.rstrip("\r\n")
        if not linea:
            continue
        clave, _, valor = linea.partition("\t")
        try:
            cantidad = int(valor)
        except ValueError:
            sys.stderr.write("reporter:counter:Reducer,Valor no numerico,1\n")
            continue
        if clave != clave_actual:
            if clave_actual is not None:
                print(f"{clave_actual}\t{acumulado}")
            clave_actual, acumulado = clave, 0
        acumulado += cantidad
    if clave_actual is not None:
        print(f"{clave_actual}\t{acumulado}")


if __name__ == "__main__":
    main()
