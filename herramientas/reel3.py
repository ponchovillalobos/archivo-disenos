"""Montador de reels v3 — solo fundidos, movimiento continuo, ffmpeg real.

Cambios respecto a v2:

· SIN CORTES DUROS. Fuera el empuje vertical y el paso por negro. Las cuatro
  transiciones son fundidos; lo que varía es el micro-zoom que las acompaña,
  no el tipo de corte. Así nunca se ve un salto.
· TRANSICIONES MÁS LARGAS (0,9 s) con suavizado cúbico en ambos extremos.
· EL MOVIMIENTO NO SE DETIENE durante la transición: la lámina entrante ya
  viene moviéndose, así que la imagen siempre parece viva.
· CODIFICACIÓN CON FFMPEG: CRF constante, faststart para que empiece a
  reproducirse antes de descargarse entero, y perfil compatible con móviles.
"""
from PIL import Image
import os, subprocess

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
S = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30

# reutilizamos la maquetación de texto de v2
import sys
sys.path.insert(0, S)
import reel2 as r2
from reel2 import html_texto, capa_texto, duracion, ESCALA, SCRIM, NEGRO


def formato(ancho, alto, y_texto=None, margen=None):
    """Cambia el lienzo. Hay que tocar los dos módulos y recalcular el degradado.

    El tamaño vive como global en `reel3` y en `reel2`, y `reel2` calcula al
    importarse el degradado inferior (SCRIM) y su fondo negro a partir del ancho.
    Cambiar solo `W` deja un degradado del tamaño viejo que no cubre la imagen:
    por eso aquí se recalculan los dos.

    En apaisado el texto no puede ir donde va en vertical —quedaría en el centro
    de la escena—, así que baja al tercio inferior y el margen crece.
    """
    global W, H
    W, H = ancho, alto
    r2.W, r2.H = ancho, alto
    apaisado = ancho > alto
    r2.MARGEN = margen if margen is not None else (int(ancho * 0.075) if apaisado else 72)
    # en apaisado Y_TEXTO es distancia desde ABAJO (ver html_texto); el 13 %
    # deja libre la franja de los controles del reproductor
    r2.Y_TEXTO = y_texto if y_texto is not None else (
        int(alto * 0.13) if apaisado else 300)
    r2.SCRIM = r2._scrim(alto=int(alto * (0.55 if apaisado else 0.73)))
    r2.NEGRO = Image.new("RGB", (ancho, r2.SCRIM.height), (0, 0, 0))
    globals()["SCRIM"], globals()["NEGRO"] = r2.SCRIM, r2.NEGRO
    return W, H


def suavisimo(t):
    """Smootherstep (6t⁵−15t⁴+10t³). Más plano en los extremos que el cúbico:
    el fundido arranca y termina casi imperceptible."""
    return t * t * t * (t * (t * 6 - 15) + 10)


def deriva(t):
    """El movimiento de cámara va LINEAL, a propósito.

    Antes usaba la misma curva suavizada que el fundido, y eso hacía que el
    zoom se quedara casi quieto al principio y al final de cada lámina y
    corriera por el centro. Se notaba como un tirón. Una deriva constante y
    lenta es lo que hace que la imagen parezca viva de principio a fin.
    """
    return t


# Cuatro recorridos, TODOS de dentro hacia fuera y mucho más profundos que
# antes (5 % → 20 %). Se arranca cerca y se abre despacio: la imagen empieza
# íntima y va revelando el espacio, que es lo que da sensación de crecimiento.
# Lo que cambia entre uno y otro es el punto hacia el que se abre, no el
# sentido — un zoom que entra detrás de otro que sale se lee como un tirón.
MOVS = [
    dict(z0=1.22, z1=1.00, ax=.50, ay=.44),   # se abre al centro
    dict(z0=1.20, z1=1.01, ax=.38, ay=.38),   # se abre hacia arriba-izquierda
    dict(z0=1.24, z1=1.02, ax=.62, ay=.50),   # se abre hacia abajo-derecha
    dict(z0=1.18, z1=1.00, ax=.46, ay=.56),   # se abre hacia abajo
]

# Todas son fundidos. Cambia el micro-zoom que los acompaña.
FUNDIDOS = ["limpio", "asentar", "alejar", "largo"]


def fotograma(fondo, t, mov):
    z = mov["z0"] + (mov["z1"] - mov["z0"]) * deriva(t)
    aw, ah = int(W * z), int(H * z)
    im = fondo.resize((aw, ah), Image.LANCZOS)
    x, y = int((aw - W) * mov["ax"]), int((ah - H) * mov["ay"])
    im = im.crop((x, y, x + W, y + H))
    im.paste(NEGRO, (0, 0), SCRIM)
    return im


def _escala(img, z):
    if abs(z - 1) < 1e-4:
        return img
    aw, ah = int(W * z), int(H * z)
    g = img.resize((aw, ah), Image.LANCZOS)
    return g.crop(((aw - W) // 2, (ah - H) // 2, (aw - W) // 2 + W, (ah - H) // 2 + H))


def fundir(a, b, t, tipo):
    """Siempre disolución. El micro-zoom es lo que da variedad."""
    s = suavisimo(t)
    if tipo == "asentar":                 # la entrante llega y se posa
        b = _escala(b, 1.022 - .022 * s)
    elif tipo == "alejar":                # la saliente se retira un poco
        a = _escala(a, 1 + .018 * s)
    elif tipo == "largo":                 # curva más plana: fundido más lento
        s = s ** 1.22
    return Image.blend(a, b, s)


def montar(laminas, fondos_dir, salida_mp4, dir_capas, acento="#d8353d",
           seg_transicion=1.8, crf=20):
    os.makedirs(dir_capas, exist_ok=True)
    piezas, duraciones = [], []
    for i, L in enumerate(laminas, 1):
        fondo = Image.open(os.path.join(fondos_dir, L["fondo"])).convert("RGB")
        if fondo.size != (W, H):
            fondo = fondo.resize((W, H), Image.LANCZOS)
        capa = capa_texto(
            html_texto(L.get("kicker") or "", L["titular"], L.get("cuerpo"),
                       L.get("lista"), "%02d / %02d" % (i, len(laminas)),
                       acento, L.get("tam", ESCALA[4])),
            os.path.join(dir_capas, "capa-%02d.png" % i))
        # con audio manda el audio: si la lámina trae su duración, se respeta
        d = L["dur"] if L.get("dur") else duracion(L)
        piezas.append((fondo, capa, MOVS[(i - 1) % len(MOVS)]))
        duraciones.append(d)
        print("   lámina %d — %.1f s" % (i, d))

    # la transición no puede durar más que el bloque: en vídeo con audio hay
    # bloques de 2,3 s, y un fundido fijo se los comería enteros
    n_tr = int(min(seg_transicion, 0.45 * min(duraciones)) * FPS)

    # Cada lámina es VISIBLE durante su propio tramo MÁS el fundido en el que
    # entra. Su cámara tiene que recorrer todo ese trecho de una vez.
    #
    # Antes no era así y ahí estaba el brinco: durante el fundido la entrante
    # avanzaba del fotograma 0 al 33, y al empezar su tramo volvía al 0. La
    # cámara saltaba hacia atrás en CADA transición. No era falta de suavidad,
    # era un salto de verdad.
    marcos = [int(d * FPS) for d in duraciones]
    tramos = [m + (n_tr if i > 0 else 0) for i, m in enumerate(marcos)]
    desfase = [n_tr if i > 0 else 0 for i in range(len(marcos))]

    cmd = [FFMPEG, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
           "-movflags", "+faststart",          # empieza a verse sin descargar todo
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
           salida_mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    def compuesta(i, k, n):
        fondo, capa, mov = piezas[i]
        base = fotograma(fondo, k / max(1, n - 1), mov)
        base.paste(capa, (0, 0), capa)
        return base

    total = 0
    for i, n in enumerate(marcos):
        for k in range(n):
            img = compuesta(i, k + desfase[i], tramos[i])
            if i + 1 < len(piezas) and k >= n - n_tr:
                t = (k - (n - n_tr)) / max(1, n_tr - 1)
                # la entrante recorre AQUÍ sus primeros n_tr fotogramas y sigue
                # desde ahí en su propio tramo: la cámara nunca retrocede
                img = fundir(img, compuesta(i + 1, int(t * n_tr), tramos[i + 1]),
                             t, FUNDIDOS[i % len(FUNDIDOS)])
            p.stdin.write(img.convert("RGB").tobytes())
            total += 1
    p.stdin.close()
    err = p.stderr.read().decode()[-500:]
    if p.wait() != 0:
        raise RuntimeError("ffmpeg falló:\n" + err)
    return total, total / FPS, duraciones
