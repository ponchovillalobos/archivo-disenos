"""Texto que avanza palabra a palabra, sincronizado con el audio real.

Es el motor de ritmo que nos faltaba. Medido en Viralito: el subtítulo genera
**150-210 cambios visuales por minuto**, contra unos 40 de todos los efectos
juntos. El ritmo de un vídeo que engancha no lo llevan los cortes — lo lleva
el texto.

Nosotros teníamos las marcas por palabra y mostrábamos párrafos quietos. Con
eso, la única cosa que se movía en pantalla era un zoom del 5 %.

Cómo funciona:

  · Las palabras del bloque se agrupan en **líneas de hasta cuatro**, cortando
    también donde hay una pausa de más de 0,6 s. Cuatro es el tope porque por
    encima el ojo deja de leer de un vistazo y empieza a barrer.
El hueco entre palabras va en PÍXELES, no en `em`: `gap` se calcula contra el
tamaño de fuente del CONTENEDOR, que era el de por defecto —16 px—, así que
0,22em daban 3 píxeles y las palabras salían pegadas: «Elmiedoyla».

  · Para cada línea se renderiza **un PNG por palabra activa**: la ya dicha va
    a plena opacidad, la activa en color de acento y un punto mayor, y las que
    faltan atenuadas. Así el espectador ve venir la frase.
  · Cada PNG se cachea por su contenido, así que una línea repetida no se
    vuelve a renderizar.

Se renderiza con Chromium igual que el resto, para no perder los ejes de las
fuentes variables ni el kerning.
"""
import hashlib
import json
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
import reel2 as r2                              # noqa: E402
from bloques import pausa_oculta                # noqa: E402

MAX_PALABRAS = 4        # por encima, el ojo barre en vez de leer de un vistazo
MAX_CARACTERES = 15     # cuatro palabras largas en español NO caben donde caben
                        # cuatro cortas: «sensación, exacta. Corazón acelerado,»
                        # se partía en tres líneas. El tope real es el ancho.
MAX_HUECO = 0.6         # una pausa mayor rompe línea aunque quepan más palabras
CACHE = os.path.join(S, "cache-texto")


def lineas(palabras, max_palabras=MAX_PALABRAS, max_hueco=MAX_HUECO,
           max_caracteres=MAX_CARACTERES):
    fuera, act = [], []
    for i, w in enumerate(palabras):
        largo = sum(len(x["palabra"]) for x in act) + len(act) + len(w["palabra"])
        if act and largo > max_caracteres:
            fuera.append(act)
            act = []
        act.append(w)
        hueco = (palabras[i + 1]["inicio"] - w["fin"]) if i + 1 < len(palabras) else 99
        # una línea nunca cruza el final de una frase: se leía «prende No estás»,
        # que junta el remate de una idea con el arranque de la siguiente
        fin_frase = w["palabra"].rstrip("»\"").endswith((".", "?", "!", "…"))
        # y tampoco cruza una pausa que el transcriptor escondió DENTRO de la
        # palabra siguiente: ahí hay frontera de idea aunque falte el punto
        oculta = (i + 1 < len(palabras)
                  and pausa_oculta(palabras, i + 1) > 0)
        if fin_frase or oculta or len(act) >= max_palabras or hueco >= max_hueco:
            fuera.append(act)
            act = []
    if act:
        fuera.append(act)
    return fuera


def _html(linea, activa, acento, W, H, tam, y_rel):
    trozos = []
    for j, w in enumerate(linea):
        p = w["palabra"]
        if j < activa:
            cls = "dicha"
        elif j == activa:
            cls = "viva"
        else:
            cls = "pend"
        trozos.append('<span class="%s">%s</span>' % (cls, p))
    cuerpo = " ".join(trozos)
    return f"""<!doctype html><meta charset="utf-8"><style>
@font-face{{font-family:F;src:url(data:font/ttf;base64,{r2.TIT})format("truetype");
  font-weight:100 900;font-display:block}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;background:transparent;overflow:hidden}}
.caja{{position:absolute;left:0;{y_rel};width:{W}px;padding:0 {int(W*0.06)}px;
  font-size:{tam}px;
  display:flex;flex-wrap:nowrap;white-space:nowrap;
  gap:{int(tam*0.30)}px;
  justify-content:center;align-items:baseline}}
span{{font-family:F,Georgia,serif;font-weight:900;font-size:{tam}px;line-height:1.06;
  display:inline-block;transform-origin:center bottom;
  font-variation-settings:"opsz" 144,"SOFT" 0,"WONK" 1;letter-spacing:-.018em;
  text-shadow:0 2px 14px rgba(0,0,0,.78),0 1px 4px rgba(0,0,0,.7)}}
.dicha{{color:#ffffff}}
/* El realce va por TRANSFORM, nunca por font-size. Cambiando el tamaño,
   la línea entera se re-centraba y daba un tirón lateral de ~18 px cada
   0,3 s; y con flex-wrap una palabra podía saltar de fila entre dos
   fotogramas. transform no provoca reflujo: la línea no se mueve. */
.viva{{color:{acento};transform:scale(1.06)}}
.pend{{color:rgba(255,255,255,.42)}}
</style><div class="caja">{cuerpo}</div>"""


def capas_de_bloque(palabras, acento, W, H, tam=None, abajo=True):
    """Devuelve [(inicio, fin, ruta_png)] cubriendo todo el bloque."""
    os.makedirs(CACHE, exist_ok=True)
    # 0,082 se quedaba corto; 0,105 desbordaba: con 21 caracteres a 113 px,
    # 19 de 31 líneas se salían del ancho útil y flex-wrap las partía en dos.
    # 0,088 con 15 caracteres entra siempre en una sola fila.
    tam = tam or int(min(W, H) * 0.088)
    y_rel = ("bottom:%dpx" % int(H * 0.14)) if abajo else ("top:%dpx" % int(H * 0.16))
    fuera = []
    todas = lineas(palabras)
    for i_ln, ln in enumerate(todas):
        sig = todas[i_ln + 1][0]["inicio"] if i_ln + 1 < len(todas) else None
        for j, w in enumerate(ln):
            html = _html(ln, j, acento, W, H, tam, y_rel)
            clave = hashlib.sha1(html.encode()).hexdigest()[:16]
            png = os.path.join(CACHE, clave + ".png")
            if not os.path.exists(png):
                r2.capa_texto(html, png)
            ini = w["inicio"]
            if j + 1 < len(ln):
                fin = ln[j + 1]["inicio"]
            else:
                # Hasta que arranque la línea SIGUIENTE, no 0,28 s después.
                # `lineas()` corta justo donde hay un hueco de 0,6 s o más, así
                # que con 0,28 el texto se evaporaba: 11 huecos, hasta 0,76 s
                # cada uno, 3,5 s de pantalla desnuda — y siempre en la frontera
                # de idea, que es donde más se mira.
                fin = sig if sig is not None else w["fin"] + 0.9
            fuera.append((round(ini, 3), round(fin, 3), png))
    return fuera


def indice(capas, fps=30):
    """Convierte la lista en un buscador por fotograma: cuál toca en cada uno."""
    tabla = {}
    for ini, fin, png in capas:
        for f in range(int(ini * fps), int(fin * fps) + 1):
            tabla[f] = png
    return tabla
