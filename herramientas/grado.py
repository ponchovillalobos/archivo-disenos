"""Grado de color posterior, por si el modelo no obedece la paleta.

No es un filtro de Instagram: es un grado de dos tonos como el de cine. Las
sombras van hacia un color y las luces hacia otro, respetando la luminancia
original. Por eso la imagen conserva su textura y su contraste; solo cambia
de mundo cromático.

La fuerza va baja a propósito (0,35). Por encima de ~0,5 se ve teñido y falso.
"""
from PIL import Image
import numpy as np

# (sombra, luz) por paleta — dos colores, no uno
DUOS = {
 "teal-naranja": ((14, 46, 54), (255, 186, 112)),
 "indigo-ambar": ((22, 26, 66), (255, 196, 110)),
 "magenta-cian": ((12, 44, 60), (255, 120, 200)),
 "oliva":        ((26, 32, 16), (206, 220, 130)),
 "sepia":        ((38, 26, 14), (255, 214, 160)),
 "rojo-carbon":  ((28, 10, 12), (255, 150, 140)),
 "purpura":      ((32, 18, 60), (214, 176, 255)),
 "azul-hielo":   ((18, 32, 52), (222, 244, 255)),
 "dorado-selva": ((14, 34, 20), (255, 216, 120)),
 "esmeralda":    ((8, 40, 34), (150, 240, 205)),
 "cobre":        ((26, 26, 30), (255, 176, 116)),
 "lavanda":      ((36, 32, 56), (232, 216, 250)),
 "vino":         ((36, 12, 16), (255, 172, 120)),
 "menta":        ((18, 30, 30), (176, 245, 224)),
 "mostaza":      ((16, 30, 48), (255, 210, 90)),
 "ladrillo":     ((34, 18, 14), (255, 168, 118)),
}


def graduar(origen, destino, paleta, fuerza=0.35):
    if paleta not in DUOS:
        raise KeyError("paleta desconocida: %s" % paleta)
    som, luz = (np.array(c, float) for c in DUOS[paleta])
    a = np.asarray(Image.open(origen).convert("RGB"), float)
    # luminancia Rec.709: es la que respeta cómo percibimos el brillo
    L = (a @ [0.2126, 0.7152, 0.0722])[..., None] / 255
    objetivo = som + (luz - som) * L          # mapa de dos tonos
    sal = a * (1 - fuerza) + objetivo * fuerza
    Image.fromarray(np.clip(sal, 0, 255).astype("uint8")).save(destino)
    return destino


def medir(ruta):
    """Devuelve (saturación media 0-255, tono dominante en grados)."""
    import colorsys
    a = np.asarray(Image.open(ruta).convert("RGB"), float) / 255
    sat = ((a.max(axis=2) - a.min(axis=2)) * 255).mean()
    hs = [colorsys.rgb_to_hsv(*p)[0] * 360
          for row in a[::17, ::17] for p in row
          if colorsys.rgb_to_hsv(*p)[1] > .15 and colorsys.rgb_to_hsv(*p)[2] > .1]
    return sat, (int(np.median(hs)) if hs else -1)
