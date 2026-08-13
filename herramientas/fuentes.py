"""Catálogo de fuentes, con sus ejes variables y para qué sirve cada una.

Hasta ahora el compositor cargaba dos fuentes a pelo (`reel2.py:43`) y toda la
serie se veía igual. Con una sola familia de display no hay forma de que un
carrusel de historia y uno de comunicación tengan voz distinta.

Cada entrada declara **sus ejes reales**, leídos del archivo, no supuestos. Eso
importa porque un eje variable no es decoración: `opsz` cambia el DIBUJO de la
letra según el tamaño al que se compone —en un titular de 144 px la letra
adelgaza los remates y abre el ojo; a 14 px los engorda para que sobrevivan—.
Usar `opsz` como efecto de animación y no como tipografía es el error más común
con fuentes variables.

Las 15 nuevas vienen de Google Fonts (OFL), vía el repositorio del propio
usuario. La licencia está en `fuentes/OFL.txt`.
"""
import base64
import os
from functools import lru_cache

S = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(os.path.dirname(S), "fuentes")

# familia: (archivo, papel, ejes, nota de uso)
CATALOGO = {
    # --- display: titulares ---
    "Fraunces": ("Fraunces.ttf", "display",
                 {"opsz": (9, 144), "wght": (100, 900), "SOFT": (0, 100), "WONK": (0, 1)},
                 "La de la casa. WONK 1 activa las formas raras; SOFT redondea."),
    "Playfair": ("PlayfairDisplay-var.ttf", "display", {"wght": (400, 900)},
                 "Didone de contraste extremo. Elegante y frío; pide tamaño grande."),
    "PlayfairIt": ("PlayfairDisplay-italic-var.ttf", "display", {"wght": (400, 900)},
                   "La cursiva de Playfair, para destacar una palabra dentro del titular."),
    "Cinzel": ("Cinzel-var.ttf", "display", {"wght": (400, 900)},
               "Capitales inscripcionales romanas. Solo versales: no tiene minúsculas "
               "de verdad. Para la serie histórica."),
    "DMSerif": ("DMSerifDisplay-Regular.ttf", "display", {},
                "Estática, contraste alto, muy compacta. Titulares cortos."),

    # --- texto: cuerpo largo ---
    "Newsreader": ("Newsreader.ttf", "texto", {"wght": (200, 800), "opsz": (6, 72)},
                   "La de la casa para cuerpo. Tiene opsz: úsalo."),
    "Cormorant": ("CormorantGaramond-var.ttf", "texto", {"wght": (300, 700)},
                  "Garalda muy fina. Preciosa en grande, ilegible en pequeño."),
    "Lora": ("Lora-var.ttf", "texto", {"wght": (400, 700)},
             "Serif robusta con gota caligráfica. Aguanta tamaños pequeños."),
    "OldStandard": ("OldStandardTT-Regular.ttf", "texto", {},
                    "Aire de imprenta decimonónica. Para citas y documentos."),
    "IMFell": ("IMFellEnglish-Regular.ttf", "texto", {},
               "Tipos de metal del XVII, con sus imperfecciones. Muy marcada."),

    # --- palo seco: interfaz, antetítulos, pies ---
    "InterTight": ("InterTight-var.ttf", "palo", {"wght": (100, 900)},
                   "Grotesca neutra y estrecha. Antetítulos y pies."),
    "LibreFranklin": ("LibreFranklin-var.ttf", "palo", {"wght": (100, 900)},
                      "Grotesca americana con más carácter que Inter."),
    "Recursive": ("Recursive.ttf", "palo",
                  {"MONO": (0, 1), "CASL": (0, 1), "wght": (300, 1000),
                   "slnt": (-15, 0), "CRSV": (0, 1)},
                  "Cinco ejes. CASL 1 la vuelve informal; MONO 1, monoespaciada."),
    "Anybody": ("Anybody.ttf", "palo", {"wdth": (50, 150), "wght": (100, 900)},
                "Tiene ANCHURA variable, que casi ninguna tiene. Para encajar "
                "un titular en un ancho exacto sin deformarlo."),

    # --- cifras ---
    "JetBrains": ("JetBrainsMono-var.ttf", "cifras", {"wght": (100, 800)},
                  "Monoespaciada: las cifras se alinean en columna. Para datos."),

    # --- otras escrituras ---
    "Shippori": ("ShipporiMincho-Regular.ttf", "japonés", {},
                 "Mincho japonesa. Para la serie de samuráis, si hace falta kanji."),
}

# Combinaciones probadas. Una voz = una pareja display + texto + palo.
VOCES = {
    "fuente-primaria": ("Fraunces", "Newsreader", "Recursive"),
    "historia":        ("Cinzel", "Cormorant", "InterTight"),
    "editorial":       ("Playfair", "Lora", "LibreFranklin"),
    "documento":       ("DMSerif", "OldStandard", "InterTight"),
    "imprenta":        ("IMFell", "OldStandard", "LibreFranklin"),
}


def ruta(familia):
    a = CATALOGO[familia][0]
    p = os.path.join(DIR, a)
    if not os.path.exists(p):
        raise FileNotFoundError("falta la fuente %s en %s" % (a, DIR))
    return p


@lru_cache(maxsize=32)
def b64(familia):
    with open(ruta(familia), "rb") as f:
        return base64.b64encode(f.read()).decode()


def cara(familia, alias=None):
    """Bloque @font-face listo para incrustar. Incrustado, no enlazado: en
    file:// el navegador bloquea las fuentes externas y compone con la de
    respaldo sin avisar."""
    ejes = CATALOGO[familia][2]
    pesos = ejes.get("wght", (400, 400))
    return ("@font-face{font-family:%s;src:url(data:font/ttf;base64,%s)"
            "format(\"truetype\");font-weight:%d %d;font-display:block}"
            % (alias or familia, b64(familia), pesos[0], pesos[1]))


def voz(nombre="fuente-primaria"):
    """Devuelve (css, {papel: familia}) para una voz completa."""
    d, t, p = VOCES[nombre]
    css = cara(d, "D") + cara(t, "T") + cara(p, "P")
    return css, {"display": d, "texto": t, "palo": p}


def ejes_css(familia, **valores):
    """`font-variation-settings` solo con los ejes que la fuente TIENE.

    Pedir un eje inexistente no da error: el navegador lo ignora en silencio y
    uno se queda pensando que la fuente no responde."""
    tiene = CATALOGO[familia][2]
    usados = [(k, v) for k, v in valores.items() if k in tiene]
    if not usados:
        return ""
    return "font-variation-settings:" + ",".join(
        '"%s" %g' % (k, v) for k, v in usados) + ";"


if __name__ == "__main__":
    print("  familia        papel     ejes")
    for n, (a, papel, ejes, nota) in CATALOGO.items():
        existe = "" if os.path.exists(os.path.join(DIR, a)) else "  ! FALTA"
        print("   %-14s %-9s %s%s" % (n, papel, ", ".join(ejes) or "estática", existe))
    print("\n  voces:")
    for n, (d, t, p) in VOCES.items():
        print("   %-18s %s + %s + %s" % (n, d, t, p))
