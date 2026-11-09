"""Convierte informe_tecnico.md en Informe_Tecnico_MapReduce.pdf.

Requisitos: Python 3, `pip install markdown` y Microsoft Edge (se usa su modo headless).
Uso (desde la raíz del proyecto):  python informe/generar_pdf.py
"""
import re
import sys
from pathlib import Path

import markdown

AQUI = Path(__file__).resolve().parent
MD = AQUI / "informe_tecnico.md"
HTML = AQUI / "_informe_temp.html"
PDF = AQUI / "Informe_Tecnico_MapReduce.pdf"
EDGE = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]

CSS = """
/* Formato APA 7 (trabajo de estudiante): Times New Roman 12, doble espacio,
   sangría de 1,27 cm, alineación a la izquierda, márgenes de 2,54 cm. */
body { font-family: 'Times New Roman', Times, serif; font-size: 12pt; line-height: 2; color: #000; }
p { margin: 0; text-align: left; text-indent: 1.27cm; }
h2 { font-size: 12pt; font-weight: bold; text-align: center; margin: 1em 0 0; page-break-after: avoid; }
h3 { font-size: 12pt; font-weight: bold; text-align: left; margin: 1em 0 0; page-break-after: avoid; }
ul, ol { margin: 0; } li p { text-indent: 0; }
.portada { text-align: center; padding-top: 3cm; }
.portada p { text-align: center; text-indent: 0; }
.titulo-apa { font-weight: bold; }
.resumen p:first-child { text-indent: 0; }
.salto { page-break-after: always; }
table { border-collapse: collapse; width: 100%; font-size: 10pt; margin: 0.2em 0 0.3em; line-height: 1.25; }
th { border-top: 1.5px solid #000; border-bottom: 1px solid #000; padding: 4px 6px; text-align: left; }
td { padding: 3px 6px; vertical-align: top; } tbody tr:last-child td { border-bottom: 1.5px solid #000; }
tr { page-break-inside: avoid; }
.tabla-num, .fig-num { font-weight: bold; margin: 1em 0 0; text-indent: 0; page-break-after: avoid; }
.tabla-tit, .fig-tit { font-style: italic; margin: 0 0 0.3em; text-indent: 0; page-break-after: avoid; }
.nota { font-size: 11pt; line-height: 1.5; text-indent: 0; margin-bottom: 0.6em; }
pre { background: #f5f5f5; border: 1px solid #ccc; padding: 6px 8px; font-size: 8.8pt; line-height: 1.3;
      white-space: pre-wrap; word-break: break-word; page-break-inside: avoid; margin: 0.4em 0; }
code { font-family: Consolas, 'Courier New', monospace; font-size: 9.5pt; }
img { max-width: 100%; max-height: 14cm; display: block; margin: 0.4em auto 0.2em; border: 1px solid #ccc; }
p:has(> img) { margin: 0; text-indent: 0; }
.figura { page-break-inside: avoid; }
.referencias p { padding-left: 1.27cm; text-indent: -1.27cm; overflow-wrap: anywhere; }
a { color: inherit; text-decoration: none; }
p:not(.referencias p) > a.url { white-space: nowrap; }
"""

# URL que aparece como texto (fuera de <code>/<pre> y de atributos) y no es localhost
URL_TEXTO = re.compile(r'(?<![="\'/>\w])(https?://(?!localhost)[^\s<>"()]+[^\s<>"().,;:])')


def enlazar_urls(html):
    """Convierte las URL en enlaces reales del PDF, para que no se corten al hacer clic."""
    partes = re.split(r'(<pre.*?</pre>|<code>.*?</code>)', html, flags=re.S)
    return "".join(p if p.startswith(("<pre", "<code>")) else
                   URL_TEXTO.sub(r'<a class="url" href="\1">\1</a>', p) for p in partes)


def main():
    cuerpo = markdown.markdown(MD.read_text(encoding="utf-8"),
                               extensions=["tables", "fenced_code", "md_in_html"])
    cuerpo = enlazar_urls(cuerpo)
    HTML.write_text(f"<!doctype html><html lang='es'><head><meta charset='utf-8'>"
                    f"<title>Informe Técnico MapReduce</title><style>{CSS}</style></head>"
                    f"<body>{cuerpo}</body></html>", encoding="utf-8")
    edge = next((e for e in EDGE if Path(e).exists()), None)
    if not edge:
        sys.exit("No se encontró Microsoft Edge")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge", headless=True)
        pg = b.new_page()
        pg.goto(HTML.as_uri())
        pg.wait_for_load_state("networkidle")
        pg.pdf(path=str(PDF), format="Letter", print_background=True,
               margin={"top": "2.54cm", "bottom": "2.54cm", "left": "2.54cm", "right": "2.54cm"},
               display_header_footer=True, footer_template="<span></span>",
               # APA 7: número de página en el encabezado, alineado a la derecha
               header_template="<div style='width:100%;text-align:right;font-size:11pt;"
                               "font-family:Times New Roman;padding:0.6cm 2.54cm 0 0'>"
                               "<span class='pageNumber'></span></div>")
        b.close()
    HTML.unlink()
    print("PDF generado:", PDF)


if __name__ == "__main__":
    main()
