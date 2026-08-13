"""Mide si una imagen transmite lo que se buscaba, con números.

Nació de un encargo concreto: «las imágenes deben ser alegres, no tétricas —
crecimiento, alegría, misterio, impactante, divertido». Eso es subjetivo, pero
tiene huellas objetivas que se pueden medir:

  · **luminosidad media** — lo tétrico vive por debajo de 70 sobre 255
  · **proporción de sombra** — cuántos píxeles casi negros hay; por encima del
    40 % la imagen se lee como oscura aunque tenga un foco brillante
  · **saturación** — el gris apagado transmite desánimo; por debajo de 25 la
    imagen se siente lavada
  · **calidez del tono** — el ámbar y el dorado (tonos 20-60°) se leen como
    acogedores; el azul-cian (180-240°) como frío y distante

No dice si una imagen es «bonita». Dice si es oscura, apagada o fría, que es
lo que hay que corregir cuando el resultado sale de terror sin quererlo.
"""
import colorsys

import numpy as np
from PIL import Image


def medir(ruta, muestreo=13):
    a = np.asarray(Image.open(ruta).convert("RGB"), float) / 255
    lum = a @ [0.2126, 0.7152, 0.0722]
    sat_mapa = a.max(axis=2) - a.min(axis=2)

    hs, calidos, frios = [], 0, 0
    for fila in a[::muestreo, ::muestreo]:
        for px in fila:
            h, s, v = colorsys.rgb_to_hsv(*px)
            if s > 0.15 and v > 0.1:
                g = h * 360
                hs.append(g)
                if 15 <= g <= 65:
                    calidos += 1
                elif 175 <= g <= 250:
                    frios += 1
    n = max(1, len(hs))
    return {
        "luz": round(lum.mean() * 255, 1),
        "sombra": round(float((lum < 0.12).mean()) * 100, 1),
        "saturacion": round(sat_mapa.mean() * 255, 1),
        "tono": int(np.median(hs)) if hs else -1,
        "calidez": round(calidos / n * 100),
        "frialdad": round(frios / n * 100),
    }


def juzgar(m):
    """Traduce los números a lo que hay que arreglar."""
    fallos = []
    if m["luz"] < 70:
        fallos.append("oscura (luz %.0f, mínimo 70)" % m["luz"])
    if m["sombra"] > 40:
        fallos.append("demasiada sombra (%.0f %%, máximo 40)" % m["sombra"])
    if m["saturacion"] < 25:
        fallos.append("apagada (sat %.0f, mínimo 25)" % m["saturacion"])
    if m["frialdad"] > m["calidez"] + 25:
        fallos.append("fría (%d %% frío contra %d %% cálido)"
                      % (m["frialdad"], m["calidez"]))
    return fallos


def hoja(rutas, titulo=""):
    print("  %slámina   luz  sombra  sat  tono  cálido  frío   veredicto" % titulo)
    malas = []
    for i, r in enumerate(rutas, 1):
        m = medir(r)
        f = juzgar(m)
        print("   %2d      %5.1f  %5.1f%%  %4.1f  %4d°  %4d%%  %4d%%   %s"
              % (i, m["luz"], m["sombra"], m["saturacion"], m["tono"],
                 m["calidez"], m["frialdad"], "; ".join(f) if f else "bien"))
        if f:
            malas.append((i, f))
    print("  %d de %d cumplen" % (len(rutas) - len(malas), len(rutas)))
    return malas
