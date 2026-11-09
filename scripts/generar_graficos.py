#!/usr/bin/env python3
"""Genera las figuras del informe a partir de las salidas REALES de Hadoop
(resultados/*/part-00000 descargados de HDFS). No recalcula nada.

Uso:  python scripts/generar_graficos.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

RAIZ = Path(__file__).resolve().parent.parent
FIG = RAIZ / "informe" / "figuras"
FIG.mkdir(parents=True, exist_ok=True)

SERIE = "#2a78d6"          # una sola serie -> un solo tono, sin leyenda
TEXTO, TEXTO2, REJILLA, FONDO = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.edgecolor": REJILLA, "axes.labelcolor": TEXTO2,
                     "xtick.color": TEXTO2, "ytick.color": TEXTO})


def leer(nombre):
    pares = []
    for linea in (RAIZ / "resultados" / nombre / "part-00000").read_text(encoding="utf-8").splitlines():
        k, v = linea.split("\t")
        pares.append((k, float(v)))
    return pares


def barras(pares, titulo, eje_x, archivo, formato, etiqueta, alto=3.6):
    pares = sorted(pares, key=lambda p: p[1])          # mayor arriba
    etiquetas = [p[0] for p in pares]
    valores = [p[1] for p in pares]
    fig, ax = plt.subplots(figsize=(7.2, alto), dpi=200, facecolor=FONDO)
    ax.set_facecolor(FONDO)
    ax.barh(etiquetas, valores, color=SERIE, height=0.62, edgecolor=FONDO, linewidth=2)
    ax.xaxis.set_major_formatter(FuncFormatter(formato))
    ax.grid(axis="x", color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel(eje_x)
    ax.set_title(titulo, loc="left", color=TEXTO, fontsize=11.5, fontweight="bold")
    tope = max(valores)
    ax.set_xlim(0, tope * 1.17)
    for y, v in enumerate(valores):
        ax.text(v + tope * 0.01, y, etiqueta(v), va="center", fontsize=8.5, color=TEXTO2)
    fig.tight_layout()
    fig.savefig(FIG / archivo, facecolor=FONDO)
    plt.close(fig)
    print("Figura:", FIG / archivo)


millones = lambda v, _=None: f"{v / 1e6:,.0f}"
barras(leer("ventas_categoria"), "Ingresos totales por categoría (Job 1)",
       "Millones de COP", "fig01_ingresos_categoria.png", millones,
       lambda v: f"{v / 1e6:,.1f} M")
barras(leer("cantidad_categoria"), "Unidades vendidas por categoría (Job 2)",
       "Unidades", "fig02_unidades_categoria.png", lambda v, _=None: f"{v:,.0f}",
       lambda v: f"{v:,.0f}")
productos = sorted(leer("ingresos_producto"), key=lambda p: p[1], reverse=True)[:10]
productos = [(k.split("|", 1)[1], v) for k, v in productos]
barras(productos, "Diez productos con mayores ingresos (Job 3)",
       "Millones de COP", "fig03_top10_productos.png", millones,
       lambda v: f"{v / 1e6:,.1f} M", alto=4.4)
