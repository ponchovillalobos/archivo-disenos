"""Monta varios temas a la vez.

HILOS, no procesos: el trabajo pesado lo hacen Chromium y ffmpeg como
subprocesos externos, así que el GIL no estorba y evitamos el problema de
`spawn` en macOS (los hijos intentan reimportar el módulo principal por ruta).

Tope 3: con 4 competiría con ComfyUI por los 4 núcleos de rendimiento, y cada
Chromium se come ~400 MB con el swap ya justo.
"""
import os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
from montar_serie import serie

_lock = threading.Lock()


def correr(guiones, hilos=3):
    ok, fallos = [], []
    t0 = time.time()

    def uno(arg):
        tema, ac, pista, lam = arg
        try:
            r, err = serie(tema, ac, pista, lam)
            return tema, r, err
        except Exception as e:
            return tema, None, "%s: %s" % (type(e).__name__, e)

    trabajos = [(t, a, p, l) for t, (a, p, l) in guiones.items()]
    with ThreadPoolExecutor(max_workers=hilos) as ex:
        for f in as_completed([ex.submit(uno, w) for w in trabajos]):
            tema, r, err = f.result()
            with _lock:
                if err:
                    fallos.append((tema, err))
                    print("  x %-22s %s" % (tema, err), flush=True)
                else:
                    ok.append(r)
                    print("  ok %-21s %.1f s | %.1f MB | %.1f LUFS | pico %.1f"
                          % (tema, r["seg"], r["mb"], r["lufs"], r["pico"]), flush=True)
    return ok, fallos, time.time() - t0
