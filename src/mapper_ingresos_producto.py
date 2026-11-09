#!/usr/bin/env python3
"""Job 3 – Mapper: ingresos por producto.

Entrada : líneas del CSV de ventas (stdin).
Salida  : <producto_id>|<producto>\\t<importe>

La clave combina identificador y nombre para que el resultado sea legible y,
a la vez, único aunque dos productos compartan nombre. Se usa '|' (y no ',')
porque algunos nombres contienen comas.
"""
from utilidades_csv import configurar_es, registros


def main():
    for r in registros(configurar_es()):
        clave = f"{r['producto_id'] or 'SIN-ID'}|{r['producto'] or 'Sin nombre'}"
        print(f"{clave}\t{r['importe']}")


if __name__ == "__main__":
    main()
