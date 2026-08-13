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


def salud_de_produccion():
    """Que ComfyUI viva no basta: hay que saber si está degradado.

    Tres veces la generación cayó de 57 s a más de 10 min por imagen y las tres
    lo descubrió el usuario. El swap por encima de ~9 GB es la señal temprana.
    """
    from guardian import salud
    s = salud()
    assert s["comfyui"], "ComfyUI no responde o no está en MPS"
    assert s["swap_mb"] < 9000, (
        "swap en %d MB: la generación se degradará. Reinicia ComfyUI"
        % s["swap_mb"])
    return "MPS · cola %d · swap %d MB" % (s["cola"], s["swap_mb"])


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


def catalogo_de_fuentes():
    """Cada familia declarada tiene que existir en disco Y tener los ejes que
    dice. Pedir un eje que la fuente no tiene no da error: el navegador lo
    ignora en silencio y uno cree que la fuente no responde."""
    from fontTools.ttLib import TTFont
    from fuentes import CATALOGO, VOCES, ruta, voz
    for fam, (_, _, ejes, _) in CATALOGO.items():
        f = TTFont(ruta(fam), lazy=True)
        reales = {a.axisTag for a in f["fvar"].axes} if "fvar" in f else set()
        faltan = set(ejes) - reales
        assert not faltan, "%s declara ejes que no tiene: %s" % (fam, faltan)
    for v in VOCES:
        css, _ = voz(v)
        assert css.count("@font-face") == 3, "la voz %s no trae tres caras" % v
    return "%d familias · %d voces · ejes verificados" % (len(CATALOGO), len(VOCES))


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


def contrato_congruente():
    """Pedir lo mismo dos veces tiene que dar lo mismo, y el pedido resuelto
    no puede conservar un solo valor ambiguo: eso es la garantía entera."""
    import glob
    import json as _j
    import contrato
    rutas = sorted(glob.glob(os.path.join(PROY, "pedidos", "*.yaml")))
    assert rutas, "no hay ningún pedido que comprobar"
    for r_ in rutas:
        a, errs = contrato.plan(r_)
        assert not errs, "%s: %s" % (os.path.basename(r_), errs[0])
        b, _ = contrato.plan(r_)
        assert contrato.huella(a) == contrato.huella(b), \
            "%s no es reproducible" % os.path.basename(r_)
        crudo = _j.dumps(contrato._serializable(a), ensure_ascii=False)
        assert '"auto"' not in crudo, "%s conserva un `auto`" % os.path.basename(r_)
    # y el validador tiene que rechazar lo que no cabe
    voz = contrato.cargar_voz("fuente-primaria")
    malo = contrato.cargar_pedido(rutas[0])
    malo["salidas"] = []
    assert contrato.validar(malo, voz), "el validador aceptó un pedido sin salidas"
    return "%d pedidos · reproducibles · sin ambigüedad" % len(rutas)


def voz_no_diverge():
    """La voz no puede desviarse del código en silencio. Si alguien cambia una
    constante en un módulo y no en la voz, el contrato quedaría mintiendo."""
    import contrato
    import paletas
    import reel2
    v = contrato.cargar_voz("fuente-primaria")
    assert v["tipografia"]["escala"] == reel2.ESCALA, "la escala no coincide"
    assert set(v["paletas_activas"]) | set(v["paletas_fuera_de_sorteo"]) \
        == set(paletas.PALETAS), "las paletas de la voz no son las del código"
    assert set(v["animos_luminosos"]) == set(paletas.LUMINOSOS), \
        "los ánimos luminosos no coinciden"
    assert v["video"]["fps"] == reel2.FPS, "los fps no coinciden"
    return "escala, paletas, ánimos y fps cuadran con el código"


def nada_huerfano():
    """Ningún archivo entregable puede existir sin aparecer en el portal.

    Pasó y costó: 17 vídeos vivían en `descargas/` y ninguno se veía, porque el
    catálogo los descartaba con un `continue` al faltarles las láminas. La causa
    de fondo fue peor — el productor llevaba una hora corriendo con una versión
    vieja del código en memoria, así que editar el módulo no cambió nada.

    Esta prueba compara DISCO contra CATÁLOGO. Si algo se produce y no se
    publica, salta aquí y no dentro de dos horas.
    """
    import glob
    S_ = os.path.join(PROY, "sitio")
    h = open(os.path.join(S_, "index.html"), encoding="utf-8").read()
    d = json.loads(re.search(r'<script id="datos"[^>]*>(.*?)</script>',
                             h, re.S).group(1))
    en_cat = {os.path.basename(p["video"]) for p in d["proyectos"] if p.get("video")}
    en_cat |= {os.path.basename(v["url"]) for p in d["proyectos"]
               for v in p.get("videos", [])}
    en_disco = {os.path.basename(x) for x in glob.glob(S_ + "/descargas/*.mp4")}
    sueltos = sorted(en_disco - en_cat)
    assert not sueltos, ("%d vídeos existen y NO se ven en el portal: %s"
                         % (len(sueltos), ", ".join(sueltos[:4])))
    assert d.get("sello"), "el catálogo se publicó sin sello: la página no se "\
                           "auto-actualizará"
    return "%d vídeos en disco, %d en el portal, 0 sueltos" % (
        len(en_disco), len(en_cat))


def higiene():
    """Avisa ANTES de que la basura estorbe, no cuando el disco se llene.

    Tres cosas crecen sin freno: los PNG de ComfyUI, la caché de capas de texto
    y los registros. Ninguna es urgente hoy, y ése es el problema: no lo será
    hasta que el disco reviente a mitad de una tanda nocturna.

    Esta prueba NO limpia. Solo mide y falla si hay demasiado pendiente, para
    que la limpieza sea una decisión y no un accidente.
    """
    import mantenimiento
    libre = mantenimiento.disco_libre_gb()
    assert libre > 15, "quedan %.0f GB libres: limpia antes de producir" % libre
    r = mantenimiento.revisar(seco=True)
    assert r["versiones"] < 250, (
        "%d versiones superadas acumuladas (%.0f MB). Ejecuta "
        "`python herramientas/mantenimiento.py --limpiar`" % (r["versiones"], r["mb"]))
    return "%.0f GB libres · %d por barrer (%.0f MB)" % (libre, r["versiones"], r["mb"])


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
    ("salud de producción", salud_de_produccion),
    ("flujo de imagen + vetos", flujo_de_imagen),
    ("paletas y ánimos", paletas_y_animos),
    ("catálogo de fuentes", catalogo_de_fuentes),
    ("composición tipográfica", composicion_tipografica),
    ("carrusel PDF + ZIP", pdf_y_zip),
    ("transcriptor", transcriptor),
    ("troceo y líneas", troceo),
    ("ritmo del audio", ritmo_de_audio),
    ("montadores de vídeo", montadores),
    ("catálogo sin enlaces rotos", catalogo_sin_roturas),
    ("guardián del catálogo", guardian_del_catalogo),
    ("contrato congruente", contrato_congruente),
    ("la voz no diverge", voz_no_diverge),
    ("nada huérfano", nada_huerfano),
    ("higiene", higiene),
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
