#!/usr/bin/env python3
"""Job 2 – Mapper: unidades vendidas por categoría.

Entrada : líneas del CSV de ventas (stdin).
Salida  : <categoria>\\t<cantidad>   (cantidad entera > 0)
"""
from utilidades_csv import configurar_es, registros


def main():
    for r in registros(configurar_es()):
        print(f"{r['categoria']}\t{r['cantidad']}")


if __name__ == "__main__":
    main()
