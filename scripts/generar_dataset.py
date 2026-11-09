#!/usr/bin/env python3
"""Genera el dataset SINTÉTICO de ventas usado en la práctica (data/dataset.csv).

Los datos NO provienen de una empresa real: se generan con una semilla fija
(random.seed(2026)) para que cualquier persona obtenga exactamente el mismo
archivo. De forma deliberada se insertan registros defectuosos (≈3 %) para
probar el manejo de errores de los Mappers:
  - categoría o producto vacíos,
  - cantidades no numéricas, cero o negativas,
  - precios con coma decimal ("45900,50") o con texto,
  - total_venta vacío (el Mapper debe recalcularlo),
  - nombres de producto con comas (campo entrecomillado en el CSV),
  - filas truncadas (menos columnas).

Uso:  python scripts/generar_dataset.py
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEMILLA = 2026
N_REGISTROS = 5000
SALIDA = Path(__file__).resolve().parent.parent / "data" / "dataset.csv"

# (producto_id, nombre, precio_base_COP)
CATALOGO = {
    "Electrónica": [
        ("ELE-001", "Audífonos inalámbricos", 189900),
        ("ELE-002", "Teclado mecánico", 249900),
        ("ELE-003", "Mouse óptico", 59900),
        ("ELE-004", "Monitor 24 pulgadas", 689900),
        ("ELE-005", "Cargador USB-C, 65W", 119900),
    ],
    "Hogar": [
        ("HOG-001", "Juego de sábanas", 129900),
        ("HOG-002", "Lámpara de escritorio", 89900),
        ("HOG-003", "Set de ollas", 319900),
        ("HOG-004", "Cafetera de goteo", 159900),
    ],
    "Ropa": [
        ("ROP-001", "Camiseta algodón", 49900),
        ("ROP-002", "Jean clásico", 139900),
        ("ROP-003", "Chaqueta impermeable", 229900),
        ("ROP-004", "Tenis urbanos", 199900),
    ],
    "Deportes": [
        ("DEP-001", "Balón de fútbol", 79900),
        ("DEP-002", "Mancuernas, par 5 kg", 109900),
        ("DEP-003", "Bicicleta estática", 899900),
        ("DEP-004", "Esterilla de yoga", 69900),
    ],
    "Alimentos": [
        ("ALI-001", "Café de origen 500 g", 32900),
        ("ALI-002", "Chocolate de mesa", 12900),
        ("ALI-003", "Panela orgánica", 6900),
        ("ALI-004", "Aceite de oliva 1 L", 45900),
    ],
    "Libros": [
        ("LIB-001", "Novela latinoamericana", 59900),
        ("LIB-002", "Manual de Python", 119900),
        ("LIB-003", "Atlas de Colombia", 89900),
    ],
}
# Peso relativo de cada categoría en el volumen de transacciones
PESO_CATEGORIA = {"Electrónica": 18, "Hogar": 15, "Ropa": 22, "Deportes": 10,
                  "Alimentos": 25, "Libros": 10}
REGIONES = ["Bogotá", "Fusagasugá", "Girardot", "Soacha", "Zipaquirá", "Facatativá"]
METODOS = ["Tarjeta", "Efectivo", "Transferencia", "PSE"]
COLUMNAS = ["id_venta", "fecha", "region", "categoria", "producto_id", "producto",
            "cantidad", "precio_unitario", "total_venta", "metodo_pago"]


def fila_valida(i, rnd):
    categoria = rnd.choices(list(PESO_CATEGORIA), weights=PESO_CATEGORIA.values())[0]
    pid, nombre, base = rnd.choice(CATALOGO[categoria])
    cantidad = rnd.choices([1, 2, 3, 4, 5, 6, 8, 10], weights=[40, 22, 12, 8, 6, 5, 4, 3])[0]
    # variación de precio ±10 % (promociones), redondeado a 100 COP
    precio = round(base * rnd.uniform(0.90, 1.10) / 100) * 100
    fecha = date(2025, 1, 1) + timedelta(days=rnd.randrange(365))
    return [f"V{i:05d}", fecha.isoformat(), rnd.choice(REGIONES), categoria, pid, nombre,
            str(cantidad), f"{precio:.2f}", f"{cantidad * precio:.2f}", rnd.choice(METODOS)]


def ensuciar(fila, rnd):
    """Introduce un único defecto controlado en la fila."""
    tipo = rnd.choice(["cat_vacia", "prod_vacio", "cant_texto", "cant_neg", "cant_cero",
                       "precio_coma", "precio_texto", "total_vacio", "truncada"])
    if tipo == "cat_vacia":
        fila[3] = ""
    elif tipo == "prod_vacio":
        fila[4] = fila[5] = ""
    elif tipo == "cant_texto":
        fila[6] = rnd.choice(["dos", "N/A", "", "?"])
    elif tipo == "cant_neg":
        fila[6] = "-" + fila[6]
    elif tipo == "cant_cero":
        fila[6] = "0"
    elif tipo == "precio_coma":      # formato latino: válido, el Mapper debe normalizarlo
        fila[7] = fila[7].replace(".", ",")
        fila[8] = ""
    elif tipo == "precio_texto":
        fila[7] = "sin precio"
        fila[8] = ""
    elif tipo == "total_vacio":      # válido: el Mapper recalcula cantidad × precio
        fila[8] = ""
    elif tipo == "truncada":
        fila = fila[:5]
    return fila, tipo


def main():
    rnd = random.Random(SEMILLA)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    defectos = {}
    with open(SALIDA, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLUMNAS)
        for i in range(1, N_REGISTROS + 1):
            fila = fila_valida(i, rnd)
            if rnd.random() < 0.03:
                fila, tipo = ensuciar(fila, rnd)
                defectos[tipo] = defectos.get(tipo, 0) + 1
            w.writerow(fila)
    print(f"Dataset sintético escrito en {SALIDA} ({N_REGISTROS} registros + encabezado)")
    print("Defectos insertados:", dict(sorted(defectos.items())))


if __name__ == "__main__":
    main()
