"""Prueba de humo: comprueba que TODAS las capacidades siguen vivas.

Nace de una frase del usuario: «el punto es agregar características sin romper
lo que funciona». Hasta ahora eso se comprobaba a ojo y a destiempo — se
descubría que algo estaba roto cuando ya se había entregado.

Cada prueba es barata a propósito (segundos, no minutos): no genera imágenes ni
renderiza vídeos completos, solo verifica que cada eslabón responde. Si esto
pasa, lo que funcionaba sigue funcionando.

Se ejecuta entero antes de dar por terminada cualquier tanda de cambios.
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
PROY = os.path.dirname(S)

VERDE, ROJO, GRIS, FIN = "\033[32m", "\033[31m", "\033[90m", "\033[0m"


class Prueba:
    def __init__(self):
        self.ok = self.mal = 0
        self.fallos = []

    def mide(self, nombre, fn):
        t0 = time.time()
        try:
            detalle = fn()
            self.ok += 1
            print("  %s✓%s %-34s %s%.2f s%s  %s"
                  % (VERDE, FIN, nombre, GRIS, time.time() - t0, FIN,
                     detalle or ""))
        except Exception as e:
            self.mal += 1
            msg = "%s: %s" % (type(e).__name__, str(e)[:120])
            self.fallos.append((nombre, msg))
            print("  %s✗%s %-34s %s" % (ROJO, FIN, nombre, msg))


# ---------------------------------------------------------------- generación
def comfyui():
    import urllib.request
    with urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=8) as r:
        d = json.load(r)
    t = d["devices"][0]["type"]
    assert t == "mps", "ComfyUI no está en MPS sino en " + t
    return "MPS activo"


def flujo_de_imagen():
    from lote import flujo
    p = flujo("zz-humo", "escena", "objeto", "encuadre", "aire", "luz",
              paleta="mostaza")
    w = json.load(open(p))
    n17 = [x for x in w["nodes"] if x["id"] == 17][0]["widgets_values"][0]
    n5 = [x for x in w["nodes"] if x["id"] == 5][0]["widgets_values"][0]
    assert "mustard" in n17, "la paleta no llegó al flujo"
    assert "(face:1.6)" in n5, "el negativo de caras se perdió"
    assert "(horror:1.4)" in n5, "el veto de terror se perdió"
    assert "(green:1.3)" in n5, "el veto de color se perdió"
    os.remove(p)
    return "paleta, veto de color y veto de terror"


def paletas_y_animos():
    from paletas import ANIMOS, LUMINOSOS, PALETAS, animo_de, paleta_de
    assert len(PALETAS) >= 16, "faltan paletas"
    n1, _, _, _ = paleta_de("uno")
    n2, _, _, _ = paleta_de("uno")
    assert n1 == n2, "la paleta no es estable para el mismo tema"
    claros = sum(animo_de("t%d" % i)[0] in LUMINOSOS for i in range(40))
    assert claros >= 16, "el sesgo hacia lo luminoso se perdió (%d/40)" % claros
    return "%d paletas · %d ánimos · %d%% luminosos" % (
        len(PALETAS), len(ANIMOS), claros * 100 // 40)


# ------------------------------------------------------------------- carrusel
def composicion_tipografica():
    from reel2 import capa_texto, html_texto
    import reel3
    reel3.formato(1080, 1920)
    p = "/tmp/zz-capa.png"
    capa_texto(html_texto("", "Prueba de humo", None, None, "01 / 06",
                          "#d8353d", 101), p)
    from PIL import Image
    im = Image.open(p)
    assert im.size == (1080, 1920), "la capa salió en %s" % (im.size,)
    assert im.convert("RGBA").getextrema()[3][1] > 0, "la capa salió vacía"
    os.remove(p)
    return "Chromium compone y la capa lleva píxeles"


def pdf_y_zip():
    import recursos
    temas = [os.path.basename(d)[4:] for d in glob.glob(PROY + "/out/com-*")]
    assert temas, "no hay ningún proyecto de comunicación"
    t = sorted(temas)[0]
    recursos.pdf_y_zip(t, t)
    pdf = "%s/sitio/descargas/carrusel-com-%s.pdf" % (PROY, t)
    assert os.path.getsize(pdf) > 50_000, "el PDF salió sospechosamente pequeño"
    return "PDF de «%s» regenerado" % t


# ---------------------------------------------------------------------- audio
def transcriptor():
    v = "/Users/maity/asr/.venv"
    assert os.path.exists(v + "/bin/ffmpeg"), "falta el enlace a ffmpeg en el venv"
    # `mlx` no expone __version__; la versión se pregunta a los metadatos
    r = subprocess.run(
        [v + "/bin/python", "-c",
         "import mlx_whisper, importlib.metadata as m; print(m.version('mlx'))"],
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, "mlx-whisper no importa: " + r.stderr[-100:]
    m = os.path.expanduser(
        "~/.cache/huggingface/hub/models--mlx-community--whisper-large-v3-turbo")
    assert os.path.isdir(m), "falta el modelo de transcripción"
    return "mlx %s + modelo presente" % r.stdout.strip()


def troceo():
    from bloques import trocear
    from texto_palabra import lineas
    j = glob.glob(PROY + "/audio/transcripciones/*.json")
    assert j, "no hay ninguna transcripción para probar"
    d = json.load(open(j[0], encoding="utf-8"))
    bl = trocear(d["palabras"])
    ln = lineas(d["palabras"])
    assert bl and ln, "el troceo devolvió vacío"
    largo = max(sum(len(x["palabra"]) for x in l) + len(l) - 1 for l in ln)
    assert largo <= 24, "hay una línea de %d caracteres, se saldrá" % largo
    return "%d bloques · %d líneas · máx %d caracteres" % (len(bl), len(ln), largo)


def ritmo_de_audio():
    from ritmo import analizar
    a = glob.glob(PROY + "/audio/procesados/*")
    assert a, "no hay ningún audio procesado"
    an = analizar(a[0])
    assert an["acentos"], "no detectó ni un acento"
    assert 0.2 <= an["paso"] <= 1.2, "paso fuera de rango: %s" % an["paso"]
    return "%d acentos · %.0f pulsos/min" % (len(an["acentos"]), an["pulsos_por_min"])


# --------------------------------------------------------------------- portal
def catalogo_sin_roturas():
    S_ = PROY + "/sitio"
    h = open(S_ + "/index.html", encoding="utf-8").read()
    d = json.loads(re.search(r'<script id="datos"[^>]*>(.*?)</script>',
                             h, re.S).group(1))
    rotos = []
    for p in d["proyectos"]:
        urls = [x["url"] for x in p["descargas"]]
        urls += [v["url"] for v in p.get("videos", [])]
        if p.get("video"):
            urls.append(p["video"])
        for pz in p["piezas"] + p.get("sin_texto", []):
            urls += ["img/" + v for k, v in pz["src"].items() if k != "max"]
        rotos += [u for u in urls if not os.path.exists(os.path.join(S_, u))]
    assert not rotos, "%d enlaces rotos, el primero: %s" % (len(rotos), rotos[0])
    con_pdf = sum(1 for p in d["proyectos"]
                  if any(".pdf" in x["url"] for x in p["descargas"]))
    con_video = sum(1 for p in d["proyectos"] if p.get("video"))
    return "%d fichas · %d con PDF · %d con vídeo · 0 rotos" % (
        len(d["proyectos"]), con_pdf, con_video)


def guardian_del_catalogo():
    """El barrido de derivadas puede destruir trabajo en silencio: si un
    proyecto cae de la lista, sus ~48 AVIF dejan de estar vivos y se borran,
    y ni out/ ni sitio/img están en git. El guardián tiene que saltar."""
    import catalogo
    try:
        catalogo.construir(minimo_proyectos=999, barrer=False)
    except RuntimeError:
        return "salta si desaparecen proyectos"
    raise AssertionError("el guardián del catálogo NO saltó")


def recetario_vivo():
    import recetario
    a = recetario.ARCHIVO
    assert os.path.exists(a), "no existe el recetario"
    d = json.load(open(a, encoding="utf-8"))
    assert d["total"] > 100, "el recetario tiene solo %d recetas" % d["total"]
    return "%d recetas · %d aprobadas" % (d["total"], d["aprobadas"])


def montadores():
    import montar_audio, montar_flujo, reel3
    reel3.formato(1920, 1080)
    import reel2
    assert reel2.SCRIM.height == int(1080 * 0.55), "el degradado no se recalculó"
    reel3.formato(1080, 1920)
    assert reel2.SCRIM.width == 1080, "el degradado no volvió a vertical"
    assert hasattr(montar_flujo, "montar") and hasattr(montar_audio, "montar")
    return "vertical y apaisado conmutan bien"


PRUEBAS = [
    ("ComfyUI en pie", comfyui),
    ("flujo de imagen + vetos", flujo_de_imagen),
    ("paletas y ánimos", paletas_y_animos),
    ("composición tipográfica", composicion_tipografica),
    ("carrusel PDF + ZIP", pdf_y_zip),
    ("transcriptor", transcriptor),
    ("troceo y líneas", troceo),
    ("ritmo del audio", ritmo_de_audio),
    ("montadores de vídeo", montadores),
    ("catálogo sin enlaces rotos", catalogo_sin_roturas),
    ("guardián del catálogo", guardian_del_catalogo),
    ("recetario", recetario_vivo),
]


if __name__ == "__main__":
    print("\n  PRUEBA DE HUMO — Fuente Primaria\n")
    p = Prueba()
    for nombre, fn in PRUEBAS:
        p.mide(nombre, fn)
    print("\n  %d bien · %d mal" % (p.ok, p.mal))
    if p.fallos:
        print("\n  Lo que hay que arreglar:")
        for n, m in p.fallos:
            print("   · %s → %s" % (n, m))
    sys.exit(1 if p.mal else 0)
