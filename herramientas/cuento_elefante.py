"""Prueba de consistencia de personaje: un cuento sin texto en seis imágenes.

SDXL **no tiene consistencia de personaje nativa**. Hay tres formas de
conseguirla y solo una está a nuestro alcance sin descargar modelos:

  · **IPAdapter** — condiciona por imagen de referencia. No instalado.
  · **ControlNet** — los nodos están, los modelos no (2-3 GB por modelo).
  · **Semilla fija + ficha de personaje repetida** — es lo que se usa aquí.

## La estrategia, y por qué debería funcionar

La arquitectura de seis campos que ya usa el sistema se presta a esto mejor que
un prompt corrido. Se congela lo que define al personaje y solo se mueve el
resto:

    CONSTANTE (idéntico en las seis, palabra por palabra)
      semilla ....... 101010
      personaje ..... la ficha, en el campo `ropa`
      tratamiento ... la misma paleta
      aire y luz .... el mismo mundo

    VARIABLE
      escena ........ qué pasa
      encuadre ...... desde dónde se ve

**Los anclajes son lo que de verdad sostiene al personaje.** Un «elefante viejo»
sale distinto cada vez; un elefante con **un colmillo izquierdo roto**, una
**muesca en la oreja derecha** y una **manta roja tejida** tiene tres rasgos
concretos a los que el modelo se agarra. El color de la manta es el ancla más
fuerte: SDXL conserva mucho mejor un objeto de color que una proporción.

## El cuento

Seis tiempos, sin una palabra. Un elefante viejo encuentra un brote, lo protege,
y el árbol le sobrevive. Se cuenta con la escala: el brote empieza siendo un
punto y termina siendo lo más grande del cuadro.
"""
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
from lote import flujo                              # noqa: E402

# ── LO QUE NO CAMBIA ────────────────────────────────────────────────────────
# Palabra por palabra en las seis. Cada rasgo es concreto y visual: nada de
# «majestuoso» o «sabio», que el modelo no sabe dibujar.
PERSONAJE = (
    "the same single old African elephant in every image: one broken left tusk "
    "snapped short, a deep V-shaped notch in the right ear, heavily wrinkled "
    "grey skin with a pale scar across the left shoulder, and a faded red woven "
    "blanket draped over its back"
)

PALETA = "dorado-selva"
AIRE = "warm dry air with fine dust catching the light"
LUZ = "low golden sunlight raking across the plain, long soft shadows"

# ── LO QUE CAMBIA ───────────────────────────────────────────────────────────
# (escena, objeto, encuadre)
TIEMPOS = [
 ("an old elephant standing alone in a vast dry savanna at dawn, cracked earth "
  "stretching to the horizon, nothing else in sight",
  "cracked dry earth",
  "extreme wide shot, the elephant small and centred, enormous sky above"),

 ("an old elephant lowering its head toward a single tiny green shoot pushing "
  "through the cracked earth, the only green in the whole frame",
  "one small green shoot",
  "wide shot from ground level, the shoot in the near foreground, the elephant "
  "behind it"),

 ("an old elephant standing over a tiny green shoot while heavy rain falls, its "
  "body shielding the small plant from the storm",
  "rain and a sheltered shoot",
  "medium wide shot from the side, the elephant filling the upper frame, the "
  "shoot dry beneath"),

 ("an old elephant resting beside a young sapling as tall as its knee, the "
  "earth around them turned green",
  "a young sapling",
  "wide shot, elephant lying down on the left, sapling on the right"),

 ("a very old elephant standing beneath a grown acacia tree that now towers "
  "over it, wide canopy casting shade across the plain",
  "a grown acacia tree",
  "extreme wide shot, the tree dominating the frame, the elephant small in its "
  "shade"),

 ("a great acacia tree alone on the plain at sunset, deep shade beneath it, a "
  "trail of elephant footprints leading away toward the horizon, no animal in "
  "sight",
  "elephant footprints leading away",
  "extreme wide shot, the tree centred, footprints running out of frame"),
]

# El negativo suma lo que rompe la continuidad de un personaje.
EXTRA_NEG = ("(two elephants:1.6), (herd:1.5), (multiple animals:1.5), "
             "(baby elephant:1.4), (both tusks intact:1.4), (people:1.4), "
             "(rider:1.4), (village:1.3), (fence:1.3), (text:1.4)")


def generar(ancho=832, alto=1216, prefijo="elef", calidad=False):
    """832×1216 — múltiplo de 64 y algo más apaisado que el reel, que le va
    mejor a un paisaje con un animal dentro."""
    import lote
    base = lote.CALIDAD if calidad else lote.RAPIDO
    rutas = []
    for i, (escena, objeto, encuadre) in enumerate(TIEMPOS, 1):
        neg = lote.NEG + ", " + EXTRA_NEG
        veto = lote.PALETAS[PALETA][2]
        neg += "".join(", (%s:1.3)" % c for c in veto.split(", "))
        rutas.append(flujo(
            "%s-%d" % (prefijo, i),
            "epic cinematic film still of " + escena,
            objeto, encuadre, AIRE, LUZ,
            ancho=ancho, alto=alto,
            ropa=PERSONAJE,          # ← la ficha de personaje, congelada
            paleta=PALETA,
            negativo=neg, base=base))
    return rutas


if __name__ == "__main__":
    for r in generar():
        print("  ", os.path.basename(r))
