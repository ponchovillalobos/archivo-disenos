"""El estudio de una noche: qué combinación mantiene un personaje al 90 %.

Corre solo, sin nadie delante, y tiene que seguir vivo por la mañana. Eso manda
sobre el diseño entero:

  · **Cada fase escribe su resultado en disco al terminarla.** Si algo revienta
    a las 3 de la mañana, lo hecho hasta entonces está guardado y medido. Ya
    perdimos 90 minutos de producción una vez por no tener esto.
  · **Nada de `time.sleep()` a pelo.** Se espera con el Guardián, que mide el
    ritmo contra su propia mediana y reinicia ComfyUI si se degrada. La
    generación ya se hundió de 57 s a 17 minutos por presión de memoria, y sin
    vigilancia una noche entera se convierte en cuatro imágenes.
  · **Se libera la memoria de ComfyUI antes de medir.** Medir carga CLIP (2,5 GB)
    y ComfyUI tiene el modelo entero residente: juntos provocan justo el swap
    que hunde el ritmo. Se descarga, se mide, y la siguiente fase lo recarga.

## Las cuatro fases, y por qué en este orden

    1  ESTILO       6 estilos × 6 escenas, sin IPAdapter, semilla fija.
                    Aísla UNA variable: el estilo gráfico. Es la pregunta de
                    verdad y todo lo demás depende de su respuesta.

    2  REFERENCIA   los 3 mejores estilos × 3 modos de IPAdapter.
                    Solo sobre lo que ya funciona: meter IPAdapter en un estilo
                    que pierde al personaje no arregla nada, y son 90 minutos.

    3  AJUSTE       el ganador × pasos, CFG y muestreador.
                    Lo más barato de mover y lo último que se toca, porque su
                    efecto es pequeño comparado con los dos anteriores.

    4  DEFINITIVA   la mejor combinación entera, medida y archivada.

Cada fase se decide con los NÚMEROS de la anterior, no con lo que yo esperaba.

## El listón

    coherencia ≥ 0,90   el personaje se mantiene (lo que pidió el usuario)
    margen     ≥ 0,020  y las seis escenas son distintas de verdad

Las dos, siempre. Una coherencia de 0,99 con margen cero significa que el modelo
pintó seis veces la misma imagen: el número perfecto para el peor resultado.
"""
import glob
import json
import os
import sys
import time
import urllib.request

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
PROY = os.path.dirname(S)

import adherencia                                     # noqa: E402
import estudio_estilos as ee                          # noqa: E402
import flujo_referencia as fr                         # noqa: E402
import guardian as gd                                 # noqa: E402

SALIDA = "/Users/maity/comfy/output/reels"
REGISTRO = os.path.join(PROY, "noche.log")
RESULTADOS = os.path.join(PROY, "noche.json")
N = len(ee.ESCENAS)


def log(*a):
    m = time.strftime("%H:%M:%S") + "  " + " ".join(str(x) for x in a)
    print(m, flush=True)
    try:
        with open(REGISTRO, "a", buffering=1) as f:
            f.write(m + "\n")
    except OSError:
        pass


def guardar(datos):
    """Se reescribe entero cada vez. Es pequeño y así nunca queda a medias."""
    tmp = RESULTADOS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    os.replace(tmp, RESULTADOS)      # atómico: o está el viejo o el nuevo


def cargar():
    try:
        with open(RESULTADOS, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def liberar():
    """Descarga los modelos de ComfyUI. Sin esto, medir provoca swap."""
    try:
        d = json.dumps({"unload_models": True, "free_memory": True}).encode()
        req = urllib.request.Request("http://127.0.0.1:8188/free", data=d,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=20).read()
        time.sleep(3)
        return True
    except Exception as e:
        log("  no pude liberar memoria:", e)
        return False


def hechas(prefijo):
    return sum(1 for i in range(1, N + 1)
               if glob.glob(os.path.join(SALIDA, "%s-%d_*.png" % (prefijo, i))))


def producir(prefijo, hacer, tope_min=45):
    """Encola una serie y espera a que salgan las seis, vigilando el ritmo.

    `hacer` es una función sin argumentos que encola. Se vuelve a llamar si el
    Guardián reinicia ComfyUI: un reinicio VACÍA LA COLA, y sin reencolar el
    productor se quedaría esperando para siempre algo que ya no existe. Eso ya
    pasó y por eso está escrito así."""
    if hechas(prefijo) >= N:
        log("  ya estaba:", prefijo)
        return True
    hacer()
    g = gd.Guardian(os.path.join(SALIDA, prefijo + "-*.png"), normal=150.0,
                    al_avisar=lambda m: log("  guardián:", m))
    t0 = time.time()
    while time.time() - t0 < tope_min * 60:
        g.esperar(45)
        n = hechas(prefijo)
        if n >= N:
            log("  %s listo · %d imágenes · ritmo %.0f s" % (prefijo, n, g.ritmo))
            return True
        if g.reinicios and gd.cola() == 0 and n < N:
            log("  la cola se vació tras un reinicio · reencolo", prefijo)
            hacer()
            g.reinicios = 0
    log("  ¡AGOTADO EL TIEMPO! %s se quedó en %d de %d" % (prefijo, hechas(prefijo), N))
    return False


def medir(prefijo):
    p = ee.medir(prefijo, SALIDA)
    if p:
        log("  %-24s coher %.3f · margen %+.3f · acierta %d/%d · %s"
            % (prefijo, p["coherencia"], p["margen"], p["aciertos"], p["n"],
               adherencia.nota(p)))
    else:
        log("  %s: faltan imágenes, no se puede medir" % prefijo)
    return p


# ── FASE 1 · ¿qué estilo sostiene al personaje? ─────────────────────────────
def fase_estilo(datos):
    log("=" * 70)
    log("FASE 1 · ESTILO — 6 estilos × 6 escenas, sin referencia, semilla fija")
    r = datos.setdefault("estilo", {})
    for nombre in ee.ESTILOS:
        pre = "est-" + nombre
        if r.get(nombre):
            log("  ya medido:", nombre)
            continue
        log(" ", nombre)
        producir(pre, lambda n=nombre, p=pre: ee.serie(n, prefijo=p))
        liberar()
        r[nombre] = medir(pre)
        guardar(datos)
    return r


# ── FASE 2 · ¿ayuda una imagen de referencia? ───────────────────────────────
# Se prueban tres modos porque hacen cosas distintas y solo uno sirve aquí:
#   style transfer   toma el ASPECTO, deja la composición al prompt
#   linear tardío    entra en el paso 20 %, cuando la composición ya está fijada
#   linear fuerte    el que ya sabemos que copia el plano — va de control
MODOS = [("est-0.7", dict(tipo_peso="style transfer", peso=0.7)),
         ("tar-0.6", dict(tipo_peso="linear", peso=0.6, inicio=0.25)),
         ("lin-0.5", dict(tipo_peso="linear", peso=0.5))]


def fase_referencia(datos, mejores):
    log("=" * 70)
    log("FASE 2 · REFERENCIA — los 3 mejores estilos × 3 modos de IPAdapter")
    r = datos.setdefault("referencia", {})
    for estilo in mejores:
        base = sorted(glob.glob(os.path.join(SALIDA, "est-%s-1_*.png" % estilo)))
        if not base:
            log("  sin imagen 1 de %s, no hay de dónde referenciar" % estilo)
            continue
        ref = fr.poner_referencia(base[-1])
        for etiqueta, cfg in MODOS:
            clave = "%s|%s" % (estilo, etiqueta)
            pre = "ref-%s-%s" % (estilo, etiqueta.replace(".", ""))
            if r.get(clave):
                continue
            log("  %s + %s" % (estilo, etiqueta))
            producir(pre, lambda e=estilo, p=pre, c=cfg:
                     ee.serie(e, prefijo=p, referencia=ref, **c))
            liberar()
            r[clave] = medir(pre)
            guardar(datos)
    return r


# ── FASE 3 · ajuste fino del ganador ────────────────────────────────────────
AJUSTES = [("p40-c5.5", dict(pasos=40, cfg=5.5)),
           ("p30-c7.0", dict(pasos=30, cfg=7.0)),
           ("p30-c4.0", dict(pasos=30, cfg=4.0)),
           ("p20-c5.5", dict(pasos=20, cfg=5.5))]


def fase_ajuste(datos, estilo, extra):
    log("=" * 70)
    log("FASE 3 · AJUSTE — %s, moviendo pasos y CFG" % estilo)
    r = datos.setdefault("ajuste", {})
    for etiqueta, cfg in AJUSTES:
        clave = "%s|%s" % (estilo, etiqueta)
        pre = "aj-%s-%s" % (estilo, etiqueta.replace(".", ""))
        if r.get(clave):
            continue
        log(" ", etiqueta)
        producir(pre, lambda p=pre, c=cfg: ee.serie(estilo, prefijo=p,
                                                    **dict(extra, **c)))
        liberar()
        r[clave] = medir(pre)
        guardar(datos)
    return r


def top(resultados, n=3):
    """Los mejores, descartando primero a los tramposos.

    Un estilo con margen bajo pintó seis veces lo mismo: su coherencia altísima
    es el síntoma del fallo, no un mérito. Se ordena por coherencia SOLO entre
    los que superan el margen mínimo."""
    val = [(k, v) for k, v in resultados.items() if v]
    limpios = [x for x in val if x[1]["margen"] >= adherencia.MIN_MARGEN]
    fuente = limpios or val
    if not limpios and val:
        log("  aviso: ninguna serie supera el margen mínimo; ordeno igualmente")
    fuente.sort(key=lambda x: -x[1]["coherencia"])
    return [k for k, _ in fuente[:n]]


def main():
    log("\n" + "#" * 70)
    log("ESTUDIO DE PERSONAJE · arranca", time.strftime("%d/%m %H:%M"))
    log("listón: coherencia ≥ %.2f Y margen ≥ %.3f"
        % (adherencia.MIN_COHERENCIA, adherencia.MIN_MARGEN))
    if not gd.viva():
        log("ComfyUI no responde · lo levanto")
        gd.reiniciar()
    datos = cargar()
    datos["arranque"] = time.strftime("%Y-%m-%d %H:%M")

    r1 = fase_estilo(datos)
    t, _ = adherencia.tabla(r1)
    log("\nRESULTADO FASE 1\n" + t + "\n")

    mejores = top(r1, 3)
    log("pasan a fase 2:", ", ".join(mejores) or "ninguno")
    datos["mejores_estilo"] = mejores
    guardar(datos)

    r2 = fase_referencia(datos, mejores) if mejores else {}
    if r2:
        t, _ = adherencia.tabla(r2)
        log("\nRESULTADO FASE 2\n" + t + "\n")

    # ¿Gana con referencia o sin ella? Se compara de verdad, no por costumbre.
    mejor_sin = max((v["coherencia"], k) for k, v in r1.items() if v) if any(r1.values()) else (0, None)
    mejor_con = max(((v["coherencia"], k) for k, v in r2.items()
                     if v and v["margen"] >= adherencia.MIN_MARGEN), default=(0, None))
    log("mejor sin referencia: %s (%.3f)" % (mejor_sin[1], mejor_sin[0]))
    log("mejor con referencia: %s (%.3f)" % (mejor_con[1], mejor_con[0]))

    extra, estilo = {}, mejor_sin[1]
    if mejor_con[0] > mejor_sin[0] and mejor_con[1]:
        estilo, etiqueta = mejor_con[1].split("|")
        extra = dict(MODOS)[etiqueta]
        base = sorted(glob.glob(os.path.join(SALIDA, "est-%s-1_*.png" % estilo)))
        if base:
            extra["referencia"] = fr.poner_referencia(base[-1])
        log("la referencia SÍ mejora · sigo con %s + %s" % (estilo, etiqueta))
    else:
        log("la referencia no mejora · sigo sin ella, con %s" % estilo)

    datos["ganador_fase2"] = {"estilo": estilo, "extra": {k: v for k, v in extra.items()}}
    guardar(datos)

    if estilo:
        r3 = fase_ajuste(datos, estilo, extra)
        if r3:
            t, _ = adherencia.tabla(r3)
            log("\nRESULTADO FASE 3\n" + t + "\n")

    todo = {}
    for grupo in ("estilo", "referencia", "ajuste"):
        for k, v in datos.get(grupo, {}).items():
            if v:
                todo["%s/%s" % (grupo, k)] = v
    t, filas = adherencia.tabla(todo)
    log("\n" + "#" * 70)
    log("TABLA COMPLETA DE LA NOCHE\n" + t)
    if filas:
        n, p = filas[0]
        log("\nGANA: %s · coherencia %.3f · margen %+.3f · %s"
            % (n, p["coherencia"], p["margen"], adherencia.nota(p)))
        datos["ganador"] = {"serie": n, **p}
    datos["fin"] = time.strftime("%Y-%m-%d %H:%M")
    guardar(datos)
    log("terminado", time.strftime("%d/%m %H:%M"))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        log("REVENTÓ:\n" + traceback.format_exc())
        raise
