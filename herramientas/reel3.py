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
from reel2 import html_texto, capa_texto, duracion, ESCALA, SCRIM, NEGRO


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


# Cuatro recorridos de cámara, ninguno se detiene. El recorrido total es
# corto (≈5%) porque a lo largo de 7-9 segundos eso ya es movimiento de sobra.
MOVS = [
    dict(z0=1.00, z1=1.052, ax=.50, ay=.42),   # acercarse
    dict(z0=1.052, z1=1.00, ax=.50, ay=.46),   # alejarse
    dict(z0=1.03, z1=1.078, ax=.38, ay=.35),   # acercarse hacia un lado
    dict(z0=1.078, z1=1.028, ax=.60, ay=.51),  # alejarse desde el otro
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
           seg_transicion=1.45, crf=20):
    os.makedirs(dir_capas, exist_ok=True)
    piezas, duraciones = [], []
    for i, L in enumerate(laminas, 1):
        fondo = Image.open(os.path.join(fondos_dir, L["fondo"])).convert("RGB")
        if fondo.size != (W, H):
            fondo = fondo.resize((W, H), Image.LANCZOS)
        capa = capa_texto(
            html_texto(L.get("kicker", ""), L["titular"], L.get("cuerpo"),
                       L.get("lista"), "%02d / %02d" % (i, len(laminas)),
                       acento, L.get("tam", ESCALA[4])),
            os.path.join(dir_capas, "capa-%02d.png" % i))
        d = duracion(L)
        piezas.append((fondo, capa, MOVS[(i - 1) % len(MOVS)]))
        duraciones.append(d)
        print("   lámina %d — %.1f s" % (i, d))

    n_tr = int(seg_transicion * FPS)

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
    for i, d in enumerate(duraciones):
        n = int(d * FPS)
        for k in range(n):
            img = compuesta(i, k, n)
            if i + 1 < len(piezas) and k >= n - n_tr:
                t = (k - (n - n_tr)) / max(1, n_tr - 1)
                n_sig = int(duraciones[i + 1] * FPS)
                # la entrante ya viene en movimiento: nada se congela
                img = fundir(img, compuesta(i + 1, int(t * n_tr), n_sig),
                             t, FUNDIDOS[i % len(FUNDIDOS)])
            p.stdin.write(img.convert("RGB").tobytes())
            total += 1
    p.stdin.close()
    err = p.stderr.read().decode()[-500:]
    if p.wait() != 0:
        raise RuntimeError("ffmpeg falló:\n" + err)
    return total, total / FPS, duraciones
