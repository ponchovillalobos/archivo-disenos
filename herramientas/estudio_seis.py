"""Las 36: seis estilos × seis escenas del mismo cuento. Una sola tanda.

## Por qué esto y no `noche.py`

`noche.py` producía estilo por estilo, y entre uno y otro dejaba que el
Guardián reiniciase ComfyUI. Un reinicio **vacía la cola**, así que había que
reencolar; y si el reinicio llegaba a mitad de un estilo, ese estilo perdía lo
que llevaba. La noche entera se fue en ese bucle.

Aquí se encolan **las 36 de una vez, al principio**. A partir de ahí ComfyUI
tiene toda la lista y la va sacando en orden. Ventajas que importan:

  · Un reinicio ya no puede vaciar «la mitad de un estilo»: se comprueba qué
    falta y se reencola solo eso, comparando contra el disco.
  · No hay decisiones a mitad de camino, o sea que no hay dónde equivocarse.
  · El orden queda intercalado —escena 1 de los seis estilos, luego escena 2…—
    así que si hay que cortar a media tanda, se tienen las seis escenas de
    varios estilos y no seis escenas de uno solo. Un corte deja algo útil.

## El coste, medido y no estimado

    130 s por imagen × 36 = 78 minutos

Los 130 s son de `/history` de ComfyUI esta mañana, tres trabajos seguidos:
125, 132 y 133 segundos. No es una estimación optimista.
"""
import glob
import json
import os
import sys
import time

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
PROY = os.path.dirname(S)

import adherencia                                     # noqa: E402
import estudio_estilos as ee                          # noqa: E402
import flujo_referencia as fr                         # noqa: E402
import guardian as gd                                 # noqa: E402

SALIDA = "/Users/maity/comfy/output/reels"
REGISTRO = os.path.join(PROY, "seis.log")
RESULTADOS = os.path.join(PROY, "seis.json")
SEMILLA = 101010


def log(*a):
    m = time.strftime("%H:%M:%S") + "  " + " ".join(str(x) for x in a)
    print(m, flush=True)
    try:
        with open(REGISTRO, "a", buffering=1) as f:
            f.write(m + "\n")
    except OSError:
        pass


def ruta(estilo, i):
    c = sorted(glob.glob(os.path.join(SALIDA, "est-%s-%d_*.png" % (estilo, i))))
    return c[-1] if c else None


def faltan():
    """Qué falta AHORA MISMO, mirando el disco. La única fuente de verdad.

    No se lleva una lista en memoria de lo encolado: si el proceso muere o
    ComfyUI se reinicia, esa lista miente. El disco no."""
    return [(e, i) for e in ee.ESTILOS
            for i in range(1, len(ee.ESCENAS) + 1) if not ruta(e, i)]


def encolar(pendientes):
    """Escena por escena y estilo por estilo, intercalado a propósito: primero
    la escena 1 de los seis estilos, luego la 2… Si hay que cortar, quedan
    estilos completos en las primeras escenas y no un solo estilo entero."""
    pendientes = sorted(pendientes, key=lambda x: (x[1], x[0]))
    n = 0
    for estilo, i in pendientes:
        esc = ee.ESCENAS_LARGAS[i - 1]
        try:
            fr.generar("est-%s-%d" % (estilo, i), ee.prompt(esc, estilo),
                       ee.negativo(estilo), semilla=SEMILLA)
            n += 1
        except Exception as e:
            log("  no pude encolar %s-%d: %s" % (estilo, i, e))
    return n


def producir(tope_min=180):
    total = len(ee.ESTILOS) * len(ee.ESCENAS)
    p = faltan()
    log("faltan %d de %d · encolo todas de una vez" % (len(p), total))
    log("  encoladas:", encolar(p))

    g = gd.Guardian(os.path.join(SALIDA, "est-*-*.png"), normal=130.0,
                    al_avisar=lambda m: log("  guardián:", m))
    t0 = time.time()
    ultimo = -1
    while time.time() - t0 < tope_min * 60:
        g.esperar(60)
        hechas = total - len(faltan())
        if hechas != ultimo:
            log("  %d de %d · ritmo %.0f s · quedan ~%.0f min"
                % (hechas, total, g.ritmo, (total - hechas) * g.ritmo / 60))
            ultimo = hechas
        if hechas >= total:
            log("las %d están hechas" % total)
            return True
        # Un reinicio vacía la cola. Si ComfyUI está libre y aún falta trabajo,
        # se reencola SOLO lo que el disco dice que falta.
        if gd.cola() == 0:
            p = faltan()
            if p:
                log("  cola vacía con %d pendientes · reencolo" % len(p))
                encolar(p)
    log("agotado el tiempo · %d de %d" % (total - len(faltan()), total))
    return False


def liberar():
    """Descarga los modelos de ComfyUI antes de medir: CLIP pesa 2,5 GB y los
    dos juntos provocan justo el swap que hunde el ritmo."""
    import urllib.request
    try:
        d = json.dumps({"unload_models": True, "free_memory": True}).encode()
        req = urllib.request.Request("http://127.0.0.1:8188/free", data=d,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=20).read()
        time.sleep(3)
    except Exception as e:
        log("  no pude liberar memoria:", e)


def medir():
    liberar()
    r = {}
    for e in ee.ESTILOS:
        p = ee.medir("est-" + e, SALIDA)
        r[e] = p
        if p:
            log("  %-12s coher %.3f · margen %+.3f · acierta %d/%d · %s"
                % (e, p["coherencia"], p["margen"], p["aciertos"], p["n"],
                   adherencia.nota(p)))
        else:
            log("  %-12s incompleto, no se puede medir" % e)
    return r


def main():
    log("\n" + "#" * 70)
    log("ESTUDIO DE SEIS ESTILOS ·", time.strftime("%d/%m %H:%M"))
    if not gd.viva():
        log("ComfyUI no responde · lo levanto")
        gd.reiniciar()
    producir()
    log("\nmidiendo…")
    r = medir()
    t, filas = adherencia.tabla({k: v for k, v in r.items() if v})
    log("\n" + t)
    datos = {"fecha": time.strftime("%Y-%m-%d %H:%M"), "semilla": SEMILLA,
             "estilos": r,
             "orden": [n for n, _ in filas]}
    if filas:
        n, p = filas[0]
        log("\nGANA: %s · coherencia %.3f · margen %+.3f · %s"
            % (n, p["coherencia"], p["margen"], adherencia.nota(p)))
        datos["ganador"] = n
    with open(RESULTADOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    log("terminado", time.strftime("%H:%M"))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        log("REVENTÓ:\n" + traceback.format_exc())
        raise
