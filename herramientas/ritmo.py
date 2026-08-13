"""Encuentra el pulso real de un audio hablado, para cortar encima.

El problema de los cortes rápidos es que si caen donde sea, marean. Si caen
donde el hablante acentúa, no se notan como cortes: se leen como énfasis. Ese
es todo el truco de la edición que engancha sin cansar.

Aquí no hay música con compás, así que el pulso hay que sacarlo del habla:

  1. **Envolvente de energía** — la voz sube en cada sílaba tónica. Los picos
     de esa curva son los acentos.
  2. **Rejilla** — se mide la separación mediana entre acentos y se construye
     una rejilla regular con ese paso. Cortar EN la rejilla es lo que hace que
     el montaje se sienta homogéneo en vez de nervioso.
  3. **Encaje** — cada corte se lleva al punto de rejilla más cercano que
     además coincida con el arranque de una palabra. Así el corte cae en el
     acento y en la palabra a la vez.

La diferencia con la edición viral al uso: allí los cortes se colocan en los
silencios largos (Viralito usa huecos > 0,4 s). Eso funciona con vídeo de una
persona hablando, donde el corte disimula un salto de imagen. Aquí las imágenes
son fijas, así que el corte no tapa nada: tiene que APORTAR, y aporta cuando
refuerza el acento.
"""
import os
import subprocess
import sys

import numpy as np

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
import imageio_ffmpeg                                  # noqa: E402

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SR = 8000          # basta y sobra para la envolvente; 16 kHz no aporta nada aquí
VENTANA = 0.02     # 20 ms


def onda(audio):
    """Lee el audio como mono a 8 kHz, sin depender de librerías de audio."""
    p = subprocess.run(
        [FFMPEG, "-v", "quiet", "-i", audio, "-f", "s16le", "-ac", "1",
         "-ar", str(SR), "-"], capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype="<i2").astype(np.float32) / 32768


def envolvente(x, ventana=VENTANA):
    n = int(SR * ventana)
    m = len(x) // n
    e = np.abs(x[:m * n]).reshape(m, n).max(axis=1)
    # suavizado corto: quita el temblor sin borrar los ataques
    k = np.hanning(5)
    k /= k.sum()
    return np.convolve(e, k, mode="same"), ventana


def acentos(env, paso, umbral=0.42, separacion=0.16):
    """Picos de la envolvente: las sílabas tónicas.

    `separacion` evita contar dos veces el mismo golpe de voz. 0,16 s sale de
    que nadie articula dos tónicas más rápido que eso.
    """
    if env.max() <= 0:
        return []
    e = env / env.max()
    minimo = int(separacion / paso)
    picos, ultimo = [], -minimo
    for i in range(1, len(e) - 1):
        if e[i] >= umbral and e[i] >= e[i - 1] and e[i] > e[i + 1]:
            if i - ultimo >= minimo:
                picos.append(round(i * paso, 3))
                ultimo = i
    return picos


def rejilla(picos, duracion, minimo=0.28, maximo=0.95):
    """Paso regular del discurso, y la rejilla que genera.

    Se toma la MEDIANA de las separaciones, no la media: una pausa larga en
    medio del audio desplaza la media y deja la rejilla fuera de sitio.
    """
    if len(picos) < 3:
        return maximo, []
    d = np.diff(picos)
    d = d[(d >= minimo) & (d <= maximo)]
    paso = float(np.median(d)) if len(d) else 0.5
    n = int(duracion / paso) + 1
    return round(paso, 3), [round(picos[0] + i * paso, 3) for i in range(n)]


def encajar(t, rej, palabras, tolerancia=0.18):
    """Lleva un instante al punto de rejilla más cercano que además sea el
    arranque de una palabra. Si no hay ninguno cerca, devuelve la rejilla sola;
    y si tampoco, el instante original."""
    cand = [g for g in rej if abs(g - t) <= tolerancia]
    if not cand:
        return t
    inicios = [w["inicio"] for w in palabras]
    con_palabra = [g for g in cand
                   if any(abs(g - i) <= tolerancia / 2 for i in inicios)]
    lista = con_palabra or cand
    return min(lista, key=lambda g: abs(g - t))


def analizar(audio, palabras=()):
    x = onda(audio)
    env, paso = envolvente(x)
    dur = len(x) / SR
    pic = acentos(env, paso)
    p, rej = rejilla(pic, dur)
    fuerza = env / max(1e-9, env.max())
    return {"duracion": round(dur, 2), "acentos": pic, "paso": p,
            "rejilla": rej, "pulsos_por_min": round(60 / p, 1) if p else 0,
            "energia": fuerza, "paso_energia": paso}


def energia_en(an, t):
    i = int(t / an["paso_energia"])
    e = an["energia"]
    return float(e[i]) if 0 <= i < len(e) else 0.0
