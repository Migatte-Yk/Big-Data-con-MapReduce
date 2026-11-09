#!/usr/bin/env python3
"""Job 1 – Mapper: ventas (ingresos) por categoría.

Entrada : líneas del CSV de ventas (stdin).
Salida  : <categoria>\\t<importe>   (un par clave-valor por venta válida)

El importe es total_venta, o cantidad × precio_unitario si total_venta falta.
"""
from utilidades_csv import configurar_es, registros


def main():
    for r in registros(configurar_es()):
        print(f"{r['categoria']}\t{r['importe']}")


if __name__ == "__main__":
    main()
