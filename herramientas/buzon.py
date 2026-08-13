"""Buzón de audios: vigila `audio/ENTRADA` y transcribe todo lo que caiga ahí.

La idea es que el usuario arrastre un audio y se olvide. Cuando avise, la
transcripción ya está hecha y solo queda la parte que sí requiere criterio:
escribir las escenas.

Deliberadamente **solo transcribe**. No genera imágenes ni monta vídeo por su
cuenta: convertir cada bloque en una escena es trabajo de redacción, y un
prompt automático saca ilustraciones planas. Eso se hace a mano, después.

Qué hace con cada archivo:
  ENTRADA/charla.mp3
    → transcripciones/charla.json   (con marcas por palabra)
    → transcripciones/charla.txt    (el texto a secas, para leerlo)
    → procesados/charla.mp3         (el original, movido, para no repetirlo)

Espera a que el archivo deje de crecer antes de tocarlo: si se copia uno grande
desde el Finder, la transcripción arrancaría sobre medio archivo.
"""
import json
import os
import sys
import time

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
PROY = os.path.dirname(S)
ENTRADA = os.path.join(PROY, "audio", "ENTRADA")
TRANS = os.path.join(PROY, "audio", "transcripciones")
HECHOS = os.path.join(PROY, "audio", "procesados")
REGISTRO = os.path.join(PROY, "audio", "buzon.log")

EXT = {".mp3", ".m4a", ".wav", ".aiff", ".aif", ".flac", ".mp4",
       ".mov", ".m4v", ".ogg", ".opus", ".wma", ".aac"}


def _di(m):
    linea = "%s  %s" % (time.strftime("%H:%M"), m)
    with open(REGISTRO, "a", buffering=1) as f:
        f.write(linea + "\n")
    print(" ", linea, flush=True)


def _estable(ruta, esperas=3, pausa=2):
    """True cuando el archivo deja de crecer: el Finder copia poco a poco."""
    ant = -1
    for _ in range(esperas):
        try:
            act = os.path.getsize(ruta)
        except OSError:
            return False
        if act == ant and act > 0:
            return True
        ant = act
        time.sleep(pausa)
    return os.path.getsize(ruta) == ant


def nuevos():
    if not os.path.isdir(ENTRADA):
        return []
    return [os.path.join(ENTRADA, n) for n in sorted(os.listdir(ENTRADA))
            if not n.startswith(".") and os.path.splitext(n)[1].lower() in EXT]


def procesar(ruta):
    from transcribir import transcribir
    base = os.path.splitext(os.path.basename(ruta))[0]
    t0 = time.time()
    d = transcribir(ruta)

    with open(os.path.join(TRANS, base + ".json"), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    with open(os.path.join(TRANS, base + ".txt"), "w", encoding="utf-8") as f:
        f.write(d["texto"] + "\n")

    destino = os.path.join(HECHOS, os.path.basename(ruta))
    if os.path.exists(destino):                     # no pisar un homónimo
        destino = os.path.join(HECHOS, "%s-%s%s" % (
            base, time.strftime("%H%M%S"), os.path.splitext(ruta)[1]))
    os.replace(ruta, destino)

    m, s = divmod(int(d["duracion"]), 60)
    _di("%s · %d:%02d · %d palabras · transcrito en %.0f s"
        % (base, m, s, len(d["palabras"]), time.time() - t0))
    return d


def vigilar(cada=10):
    for c in (ENTRADA, TRANS, HECHOS):
        os.makedirs(c, exist_ok=True)
    _di("buzón en marcha, vigilando audio/ENTRADA")
    while True:
        for r in nuevos():
            if not _estable(r):
                continue
            try:
                procesar(r)
            except Exception as e:
                _di("ERROR con %s: %s" % (os.path.basename(r), e))
                # se queda en ENTRADA para poder mirarlo, pero no se reintenta
                # en bucle: se marca con un punto delante
                try:
                    os.replace(r, os.path.join(
                        ENTRADA, "." + os.path.basename(r)))
                except OSError:
                    pass
        time.sleep(cada)


if __name__ == "__main__":
    if not sys.executable.startswith("/Users/maity/asr/.venv"):
        os.execv("/Users/maity/asr/.venv/bin/python",
                 ["/Users/maity/asr/.venv/bin/python", __file__] + sys.argv[1:])
    if "--una-vez" in sys.argv:
        for r in nuevos():
            procesar(r)
    else:
        vigilar()
