"""Limpia lo que crece sin freno, sin tocar nunca lo que está publicado.

Tres cosas crecen para siempre en este sistema y ninguna se limpiaba sola:

    /comfy/output/reels/*.png   664 MB · 631 imágenes
    herramientas/cache-texto/   una capa por estado de texto
    los registros               salud.jsonl, reto30.log, buzon.log…

Ninguna es urgente hoy, y ése es justo el problema: no lo será hasta que el
disco se llene a mitad de una tanda nocturna.

## La regla que hace esto seguro

**Nunca se borra un archivo cuyo contenido esté publicado.** No se compara por
nombre —que puede coincidir por accidente— sino por md5 del contenido contra
todo lo que vive en `out/`. Si una imagen acabó en un proyecto, es intocable
aunque tenga diez versiones más nuevas.

Lo que sí se borra: **versiones superadas**. ComfyUI numera `_00001_`,
`_00002_`… y el sistema siempre usa la más reciente. Las anteriores, si no
llegaron a publicarse, no las va a mirar nadie nunca.

## Por qué no borra más

`out/` ocupa 1,5 GB y **no se toca**: ahí viven los fondos, las capas y las
láminas de cada proyecto publicado. `sitio/img/` tampoco: son las derivadas del
portal, y ya tienen su propio barrido con guardián en `catalogo.py`.

Borrar de más es peor que no borrar: `out/` y `sitio/img/` están en `.gitignore`
y no hay copia. Ese guardián existe porque una vez estuvimos a punto de perder
1.016 derivadas en silencio.
"""
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import time

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
PROY = os.path.dirname(S)
SALIDA = "/Users/maity/comfy/output/reels"

TOPE_CACHE_DIAS = 21     # una capa de texto que lleva tres semanas sin usarse
TOPE_REGISTRO = 2000     # líneas por fichero de registro
TOPE_BORRADO = 300       # freno: más que esto y algo va mal, se para


def _publicadas():
    """md5 de todo lo que vive en un proyecto. Intocable."""
    vistas = set()
    for p in (glob.glob(os.path.join(PROY, "out", "*", "f*.png")) +
              glob.glob(os.path.join(PROY, "out", "*", "LAMINAS", "*.png")) +
              glob.glob(os.path.join(PROY, "out", "carrusel-*", "*.png"))):
        try:
            with open(p, "rb") as f:
                vistas.add(hashlib.md5(f.read()).hexdigest())
        except OSError:
            pass
    return vistas


def versiones_superadas(seco=True):
    """Borra las versiones antiguas de cada imagen que NO estén publicadas."""
    publicadas = _publicadas()
    grupos = {}
    for p in glob.glob(os.path.join(SALIDA, "*.png")):
        base = re.sub(r"_\d+_?\.png$", "", os.path.basename(p))
        grupos.setdefault(base, []).append(p)

    fuera, peso = [], 0
    for ps in grupos.values():
        if len(ps) < 2:
            continue
        for p in sorted(ps)[:-1]:            # todas menos la más reciente
            try:
                with open(p, "rb") as f:
                    if hashlib.md5(f.read()).hexdigest() in publicadas:
                        continue
                peso += os.path.getsize(p)
                fuera.append(p)
            except OSError:
                pass

    if len(fuera) > TOPE_BORRADO:
        raise RuntimeError(
            "el barrido quería borrar %d imágenes (tope %d). Eso no es limpieza, "
            "es un fallo. No se ha borrado nada." % (len(fuera), TOPE_BORRADO))
    if not seco:
        for p in fuera:
            try:
                os.remove(p)
            except OSError:
                pass
    return len(fuera), peso


def cache_de_texto(seco=True, dias=TOPE_CACHE_DIAS):
    """Las capas de texto se cachean por el sha1 de su HTML. Cambiar la fuente,
    el tamaño o la versión del navegador las deja huérfanas para siempre."""
    d = os.path.join(S, "cache-texto")
    if not os.path.isdir(d):
        return 0, 0
    limite = time.time() - dias * 86400
    fuera = [p for p in glob.glob(d + "/*.png") if os.path.getmtime(p) < limite]
    peso = sum(os.path.getsize(p) for p in fuera)
    if not seco:
        for p in fuera:
            try:
                os.remove(p)
            except OSError:
                pass
    return len(fuera), peso


def registros(seco=True, tope=TOPE_REGISTRO):
    """Recorta los registros por la cabeza, conservando lo reciente.

    No se borran: lo que cuentan es la única forma de saber cuándo empezó a
    torcerse algo. Pero tampoco pueden crecer para siempre."""
    tocados = 0
    for nombre in ("salud.jsonl", "reto30.log", "alimentador.log", "idea1.log",
                   os.path.join("audio", "buzon.log")):
        p = os.path.join(PROY, nombre)
        if not os.path.exists(p):
            continue
        try:
            ls = open(p, encoding="utf-8", errors="replace").readlines()
        except OSError:
            continue
        if len(ls) <= tope:
            continue
        tocados += 1
        if not seco:
            with open(p, "w", encoding="utf-8") as f:
                f.write("# recortado por mantenimiento: se conservan las "
                        "últimas %d líneas\n" % tope)
                f.writelines(ls[-tope:])
    return tocados


def temporales(seco=True):
    """Restos de montajes interrumpidos. `_mudo-*.mp4` queda si ffmpeg muere
    entre el vídeo y la música."""
    fuera = (glob.glob(os.path.join(PROY, "_mudo-*.mp4")) +
             glob.glob(os.path.join(S, "_capa*.html")) +
             glob.glob(os.path.join(S, "_lamina*.html")) +
             glob.glob(os.path.join(PROY, "**", "__pycache__"), recursive=True))
    peso = 0
    for p in fuera:
        try:
            peso += (os.path.getsize(p) if os.path.isfile(p)
                     else sum(os.path.getsize(os.path.join(r, x))
                              for r, _, xs in os.walk(p) for x in xs))
        except OSError:
            pass
    if not seco:
        for p in fuera:
            try:
                os.remove(p) if os.path.isfile(p) else shutil.rmtree(p, True)
            except OSError:
                pass
    return len(fuera), peso


def revisar(seco=True):
    """Pasa todo. `seco=True` solo informa; nada se toca."""
    r = {}
    r["versiones"], p1 = versiones_superadas(seco)
    r["cache"], p2 = cache_de_texto(seco)
    r["temporales"], p3 = temporales(seco)
    r["registros"] = registros(seco)
    r["mb"] = round((p1 + p2 + p3) / 1e6, 1)
    r["seco"] = seco
    return r


def disco_libre_gb():
    st = os.statvfs("/")
    return st.f_bavail * st.f_frsize / 1e9


if __name__ == "__main__":
    seco = "--limpiar" not in sys.argv
    r = revisar(seco)
    print("  %s" % ("REVISIÓN (nada se ha tocado)" if seco else "LIMPIEZA"))
    print("   versiones superadas  %4d" % r["versiones"])
    print("   capas de texto viejas %3d" % r["cache"])
    print("   temporales            %3d" % r["temporales"])
    print("   registros recortados  %3d" % r["registros"])
    print("   espacio               %.1f MB" % r["mb"])
    print("   disco libre           %.0f GB" % disco_libre_gb())
    if seco:
        print("\n  para ejecutarlo de verdad:  python herramientas/mantenimiento.py --limpiar")
