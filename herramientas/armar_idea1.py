"""Espera a que salgan las imágenes de Idea 1 y monta los dos vídeos solo.

Existe para no quedarme mirando la cola: las 22 imágenes (11 verticales y 11
apaisadas) van al final, y cuando terminen esto arma los dos formatos, los deja
en `sitio/descargas/` y escribe un informe con la sincronía medida.

Audita antes de montar: si alguna imagen falta, no monta ese formato y lo dice.
Mejor no entregar que entregar un vídeo con un hueco.
"""
import glob
import json
import os
import shutil
import sys
import time

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
PROY = os.path.dirname(S)
FUENTE = "/Users/maity/comfy/output/reels"
REGISTRO = os.path.join(PROY, "idea1.log")

FORMATOS = [("idea1", (1080, 1920), "vertical"),
            ("idea1h", (1920, 1080), "horizontal")]


def di(m):
    with open(REGISTRO, "a", buffering=1) as f:
        f.write("%s  %s\n" % (time.strftime("%H:%M"), m))
    print(" ", m, flush=True)


def listas(prefijo, n=11):
    """Ordenadas de más NUEVA a más vieja.

    Antes tomaba la primera —la _00001_— y eso está bien para no perder una
    lámina buena, pero mal cuando se acaba de regenerar todo: se montaba la
    versión vieja. Regenerar significa querer la nueva; si hay que rescatar una
    antigua, se copia a mano sobre f%02d.png antes de montar.
    """
    return [sorted(glob.glob("%s/%s-%02d_*.png" % (FUENTE, prefijo, i)),
                   reverse=True)
            for i in range(1, n + 1)]


def esperar(prefijo, n=11, tope=7200, cada=45, desde=None):
    """desde: solo cuentan las láminas generadas DESPUÉS de este instante.

    Sin esto la espera terminaba al momento: al regenerar, las versiones viejas
    siguen en disco y `listas()` las encuentra, así que parecía que ya estaba
    todo hecho y se montaba con las antiguas.
    """
    t0 = time.time()
    while time.time() - t0 < tope:
        hechas = sum(1 for g in listas(prefijo, n)
                     if g and (desde is None or os.path.getmtime(g[0]) >= desde))
        if hechas >= n:
            return True
        time.sleep(cada)
    return False


def armar(prefijo, formato, etiqueta):
    from montar_audio import montar
    from idea1 import laminas, ACENTO, AUDIO

    faltan = [i for i, g in enumerate(listas(prefijo), 1) if not g]
    if faltan:
        di("%s: faltan las láminas %s — no monto" % (etiqueta, faltan))
        return None

    d = os.path.join(PROY, "out", "idea1-" + etiqueta)
    os.makedirs(d, exist_ok=True)
    for i, g in enumerate(listas(prefijo), 1):
        shutil.copy(g[0], os.path.join(d, "f%02d.png" % i))

    salida = os.path.join(PROY, "sitio", "descargas",
                          "idea1-%s.mp4" % etiqueta)
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    r = montar(laminas(), AUDIO, d, salida, acento=ACENTO, formato=formato)
    di("%s listo · %s · %.2f MB · desfase %.2f s"
       % (etiqueta, r["formato"], r["mb"], r["desfase_s"]))
    return r


if __name__ == "__main__":
    # se pasa por argumento el instante a partir del cual cuentan las láminas
    DESDE = float(sys.argv[1]) if len(sys.argv) > 1 else None
    di("esperando las imágenes de Idea 1")
    res = {}
    for prefijo, formato, etiqueta in FORMATOS:
        if not esperar(prefijo, desde=DESDE):
            di("%s: se agotó la espera" % etiqueta)
            continue
        try:
            res[etiqueta] = armar(prefijo, formato, etiqueta)
        except Exception as e:
            di("%s: ERROR %s" % (etiqueta, str(e)[:200]))
    with open(os.path.join(PROY, "idea1.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    di("terminado")
