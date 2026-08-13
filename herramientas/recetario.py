"""Recetario: la memoria de lo que SÍ funcionó.

Cada imagen buena es una receta reproducible, y hasta ahora la estábamos
tirando. ComfyUI escribe el flujo entero dentro del PNG —semilla, pasos, CFG,
muestreador, modelo, LoRA y los seis fragmentos de prompt—, así que no hace
falta haber guardado nada: se puede recuperar de las imágenes ya generadas.

La idea es que el sistema mejore con el uso. Una imagen que pasó la auditoría
—sin caras deformes, sin manos raras, sin objetos literales absurdos— vale
mucho más que el archivo: vale su receta, porque con la misma semilla y el
mismo prompt vuelve a salir, y cambiando una sola pieza salen variantes que
heredan lo que funcionaba.

**Aprobada** significa que la imagen acabó publicada en un proyecto (está en
`out/com-*/` o en los carruseles). Eso ya pasó por la hoja de contacto, así que
es el filtro más honesto que tenemos: no lo que yo crea que está bien, sino lo
que sobrevivió hasta publicarse.
"""
import glob
import hashlib
import json
import os

from PIL import Image

S = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.dirname(S)
SALIDA = "/Users/maity/comfy/output/reels"
ARCHIVO = os.path.join(PROY, "recetario.json")

# los seis campos de texto del flujo, en el orden en que se concatenan
CAMPOS = {11: "escena", 12: "ropa", 13: "objeto", 14: "encuadre",
          15: "aire", 16: "luz", 17: "tratamiento"}


def receta(png):
    """Saca la receta completa de un PNG generado por ComfyUI. None si no la lleva."""
    try:
        info = Image.open(png).info
    except Exception:
        return None
    if "prompt" not in info:
        return None
    try:
        d = json.loads(info["prompt"])
    except Exception:
        return None

    r = {"imagen": os.path.basename(png), "textos": {}}
    for nid, n in d.items():
        c, e = n.get("class_type"), n.get("inputs", {})
        if c == "KSampler":
            r.update(semilla=e.get("seed"), pasos=e.get("steps"), cfg=e.get("cfg"),
                     muestreador=e.get("sampler_name"), planificador=e.get("scheduler"),
                     denoise=e.get("denoise"))
        elif c == "CheckpointLoaderSimple":
            r["modelo"] = e.get("ckpt_name")
        elif c == "LoraLoaderModelOnly":
            r["lora"] = e.get("lora_name")
            r["lora_peso"] = e.get("strength_model")
        elif c == "EmptyLatentImage":
            r["ancho"], r["alto"] = e.get("width"), e.get("height")
        elif c == "PrimitiveStringMultiline":
            v = e.get("value", "")
            if isinstance(v, str) and v:
                r["textos"][CAMPOS.get(int(nid), "n%s" % nid)] = v
        elif c == "CLIPTextEncode":
            t = e.get("text")
            # el negativo llega como texto plano; el positivo llega enlazado
            if isinstance(t, str) and "(face:" in t:
                r["negativo"] = t
    if not r.get("semilla"):
        return None
    r["huella"] = hashlib.sha1(
        json.dumps([r.get("semilla"), r["textos"]], sort_keys=True).encode()
    ).hexdigest()[:12]
    return r


def publicadas():
    """Las que llegaron a un proyecto: ya pasaron la auditoría visual."""
    vistas = set()
    for p in glob.glob(os.path.join(PROY, "out", "*", "f*.png")) + \
             glob.glob(os.path.join(PROY, "out", "carrusel-*", "*.png")):
        try:
            with open(p, "rb") as f:
                vistas.add(hashlib.md5(f.read()).hexdigest())
        except OSError:
            pass
    return vistas


def construir(solo_aprobadas=False):
    aprobadas = publicadas()
    fichas, sin_datos = [], 0
    for png in sorted(glob.glob(os.path.join(SALIDA, "*.png"))):
        r = receta(png)
        if not r:
            sin_datos += 1
            continue
        with open(png, "rb") as f:
            r["aprobada"] = hashlib.md5(f.read()).hexdigest() in aprobadas
        if solo_aprobadas and not r["aprobada"]:
            continue
        fichas.append(r)
    return fichas, sin_datos


def reproducir(huella_o_imagen, slug, cambios=None, archivo=ARCHIVO):
    """Reconstruye el flujo de una receta guardada, con los cambios que se pidan.

    Es lo que convierte el archivo en un sistema que mejora con el uso: una
    imagen aprobada se vuelve a lanzar tal cual, o se le cambia UNA pieza
    —el tratamiento de color, el objeto, el tamaño— y la variante hereda todo
    lo que ya funcionaba en lugar de empezar de cero.

    cambios: {"tratamiento": "...", "objeto": "...", "ancho": 1344, ...}
    """
    import lote
    d = json.load(open(archivo, encoding="utf-8"))
    r = next((x for x in d["recetas"]
              if huella_o_imagen in (x["huella"], x["imagen"])), None)
    if r is None:
        raise KeyError("no encuentro esa receta: " + huella_o_imagen)
    t = dict(r["textos"])
    cambios = dict(cambios or {})
    ancho = cambios.pop("ancho", r.get("ancho", 720))
    alto = cambios.pop("alto", r.get("alto", 1280))
    t.update(cambios)
    return lote.flujo(slug, t.get("escena", ""), t.get("objeto", ""),
                      t.get("encuadre", ""), t.get("aire", ""), t.get("luz", ""),
                      ancho=ancho, alto=alto, ropa=t.get("ropa", ""),
                      look=t.get("tratamiento"))


def guardar():
    fichas, sin = construir()
    ap = sum(f["aprobada"] for f in fichas)
    semillas = {}
    for f in fichas:
        semillas.setdefault(f["semilla"], [0, 0])
        semillas[f["semilla"]][0] += 1
        semillas[f["semilla"]][1] += f["aprobada"]
    datos = {"total": len(fichas), "aprobadas": ap, "sin_metadatos": sin,
             "semillas": {str(k): {"usos": v[0], "publicadas": v[1]}
                          for k, v in sorted(semillas.items())},
             "recetas": fichas}
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    return datos


if __name__ == "__main__":
    d = guardar()
    print("  %d recetas · %d publicadas · %d sin metadatos"
          % (d["total"], d["aprobadas"], d["sin_metadatos"]))
    print("  semilla    usos  publicadas")
    for s, v in sorted(d["semillas"].items(), key=lambda x: -x[1]["publicadas"])[:10]:
        print("   %-10s %4d  %4d" % (s, v["usos"], v["publicadas"]))


# ---------------------------------------------------------------------------
# QUÉ FUNCIONA — la memoria que faltaba
#
# El recetario sabía QUÉ se hizo, pero no QUÉ SALIÓ BIEN. Y la diferencia
# importa: con 371 recetas y 126 aprobadas, hay señal de sobra para no volver a
# probar a ciegas.
#
# «Aprobada» = la imagen llegó a publicarse. No es una opinión: es el resultado
# de haber pasado la hoja de contacto, así que mide lo que de verdad interesa.
#
# UN SESGO QUE HAY QUE TENER EN CUENTA AL LEER LOS NÚMEROS: las paletas
# antiguas (noir, y en parte rojo-carbón) se usaron en una época en que se
# generaba de más y se descartaba mucho; las nuevas se generan por pedido y se
# usan casi todas. Parte de la diferencia es el cambio de método, no solo la
# calidad de la paleta. Lo que el dato SÍ sostiene es la dirección: el noir con
# niebla producía descartes que las paletas con veto no producen.
# ---------------------------------------------------------------------------

def _paleta_de_receta(r):
    """Deduce la paleta a partir del tratamiento escrito en el PNG.

    No se puede leer el nombre —el flujo guarda el texto, no la clave—, así que
    se busca la paleta cuyo `look` coincide. Es exacto porque el texto sale
    literal de `paletas.PALETAS`."""
    import paletas
    t = (r.get("textos", {}) or {}).get("tratamiento", "")
    if not t:
        return None
    for nombre, (_, look, _) in paletas.PALETAS.items():
        if look[:40] and look[:40] in t:
            return nombre
    return None


def _animo_de_receta(r):
    import paletas
    aire = (r.get("textos", {}) or {}).get("aire", "")
    for nombre, (a, _l) in paletas.ANIMOS.items():
        if a and a[:30] in aire:
            return nombre
    return None


def que_funciona(archivo=ARCHIVO):
    """Tasa de aprobación por paleta y por ánimo, con el volumen detrás.

    Devuelve solo lo que tiene muestra suficiente: por debajo de 6 imágenes un
    porcentaje no dice nada y confunde más que ayuda.
    """
    d = json.load(open(archivo, encoding="utf-8"))
    por_pal, por_ani = {}, {}
    for r in d["recetas"]:
        for clave, tabla in ((_paleta_de_receta(r), por_pal),
                             (_animo_de_receta(r), por_ani)):
            if not clave:
                continue
            t = tabla.setdefault(clave, [0, 0])
            t[0] += 1
            t[1] += bool(r.get("aprobada"))

    def ordena(tabla, minimo=6):
        fuera = [(k, n, ok, ok / n) for k, (n, ok) in tabla.items() if n >= minimo]
        return sorted(fuera, key=lambda x: -x[3])

    return {"paletas": ordena(por_pal), "animos": ordena(por_ani),
            "total": d["total"], "aprobadas": d["aprobadas"]}


def informe():
    q = que_funciona()
    print("  %d recetas · %d aprobadas (%.0f %%)"
          % (q["total"], q["aprobadas"], q["aprobadas"] / max(1, q["total"]) * 100))
    for titulo, filas in (("PALETAS", q["paletas"]), ("ÁNIMOS", q["animos"])):
        if not filas:
            continue
        print("\n  %s — tasa de aprobación (mín. 6 imágenes)" % titulo)
        for k, n, ok, tasa in filas:
            barra = "█" * int(tasa * 24)
            print("   %-14s %3d img · %3d ok · %3.0f %% %s" % (k, n, ok, tasa * 100, barra))
    return q
