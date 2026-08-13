"""Montaje correcto: cámara continua, el ritmo lo lleva el texto.

Sustituye a `montar_ritmo.py`, que estaba mal planteado. Aquel cortaba entre
dos encuadres de la misma imagen fija buscando agilidad, y el resultado se lee
como un fallo de reproducción: en vídeo grabado el jump cut funciona porque el
sujeto se movió y hay información nueva; con una imagen congelada el ojo ve los
mismos píxeles reescalados y concluye que algo va mal.

Lo confirma el propio Viralito: cuando recibe una imagen fija le aplica **Ken
Burns continuo y nunca la corta**, y en todo el repositorio no existe un solo
corte entre dos encuadres del mismo material.

De dónde sale entonces el ritmo, medido en ese mismo repositorio:

    subtítulo palabra a palabra ...... 150-210 cambios por minuto
    todos los efectos juntos .........  ~40 por minuto

**El texto genera cuatro o cinco veces más eventos visuales que todo lo demás.**
Esa es la base continua. Encima van unos pocos golpes —siete por vídeo, no por
minuto— donde coinciden varias cosas a la vez.

Así que aquí:

  · **Un plano por imagen**, con apertura lenta y profunda (1,22 → 1,00). Nunca
    se corta dentro de una imagen.
  · **Fundido largo entre imágenes**, con la cámara continua a través de él.
  · **El texto avanza palabra a palabra** sobre las marcas reales del audio.
  · **Golpes en los acentos más fuertes**: un empuje de escala breve, no un
    corte. Se eligen los N picos de energía más separados entre sí, para que no
    se amontonen en el primer tercio (defecto que sí tiene Viralito).
"""
import math
import os
import subprocess
import sys

from PIL import Image

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)

import imageio_ffmpeg                              # noqa: E402
import reel2 as r2                                 # noqa: E402
import reel3                                       # noqa: E402
from montar_audio import duracion_audio, duraciones  # noqa: E402
from ritmo import analizar, energia_en             # noqa: E402
from texto_palabra import capas_de_bloque, indice  # noqa: E402

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
PROY = os.path.dirname(S)
FPS = 30

# Apertura de cámara. La VELOCIDAD es fija, no el recorrido: antes el zoom
# iba siempre de 1,22 a 1,00 en la duración del bloque, y como los bloques van
# de 2,6 a 7,5 s, la cámara corría a 8,5 %/s en unos planos y a 2,9 %/s en
# otros. Casi el triple, sin motivo. En una pieza montada la cámara tiene una
# velocidad, no una duración; con duración se lee como pase automático.
Z0, Z1 = 1.20, 1.00
VELOCIDAD = 0.022        # proporción de zoom por segundo (2,2 %/s, ritmo de cine)
DERIVA = 0.055           # cuánto se desplaza el ancla a lo largo del plano
CENTROS = [(.50, .44), (.40, .40), (.60, .50), (.46, .56), (.54, .38)]

# --- animación del texto, cifras medidas en el motor de Viralito ---
# El texto no debe APARECER: debe LLEGAR. Un cambio instantáneo entre PNG se
# lee como pase de diapositivas; el sobrepaso es la diferencia entera entre
# «aparece un texto» y «el texto llega».
TXT_ENTRADA = 0.35      # s en resolverse (equivale a damping 12/stiffness 200)
TXT_SOBREPASO = 0.035   # cuánto se pasa de tamaño antes de asentar
TXT_SUBIDA = 14         # px que sube al entrar
TXT_FUNDE = 0.08        # s de opacidad al entrar

# Ningún píxel completamente quieto. Un área del cuadro con valor idéntico
# fotograma a fotograma el ojo la lee como IMAGEN, no como vídeo — y ése es el
# delator más silencioso de todos. Con imágenes fijas es letal.
GRANO = 7               # amplitud. Por encima de 15 se ve sucio; por debajo de 4 no existe

GOLPES = 7          # cuántos acentos reciben empuje, en TODO el vídeo
GOLPE_ESCALA = .026  # con ataque real hace falta menos amplitud
GOLPE_F = 12         # en cuántos fotogramas se resuelve
FUNDIDO = 1.25       # segundos entre imagen e imagen


def _suave(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


def _salida_cubica(t):
    """Arranca rápido y frena. Lo que ENTRA y se queda usa esta."""
    return 1 - (1 - t) ** 3


def elegir_golpes(an, dur, n=GOLPES, margen=None):
    """Los n acentos más fuertes, obligándolos a repartirse por todo el vídeo.

    Viralito coloca sus golpes sobre las primeras palabras clave y deja el
    último 40 % del vídeo desnudo. Aquí se exige una separación mínima de
    `duración / n`, así que el reparto cubre la pieza entera.
    """
    margen = margen if margen is not None else dur / max(1, n)
    cand = sorted(an["acentos"], key=lambda t: -energia_en(an, t))
    fuera = []
    for t in cand:
        if all(abs(t - x) >= margen for x in fuera):
            fuera.append(t)
        if len(fuera) >= n:
            break
    return sorted(fuera)


def montar(bloques, palabras, audio, fondos_dir, salida, acento="#e0b53c",
           formato=(1080, 1920), crf=20):
    W, H = formato
    reel3.formato(W, H)
    fin = duracion_audio(audio)
    durs = duraciones(bloques, fin)
    durs[0] += bloques[0]["inicio"]

    an = analizar(audio)
    golpes = [int(t * FPS) for t in elegir_golpes(an, fin)]

    fondos = []
    for b in bloques:
        f = Image.open(os.path.join(fondos_dir, b["fondo"])).convert("RGB")
        if f.size != (W, H):
            f = f.resize((W, H), Image.LANCZOS)
        fondos.append(f)

    capas = capas_de_bloque(palabras, acento, W, H,
                            abajo=(W > H))
    por_marco = indice(capas, FPS)
    # de qué fotograma arranca cada capa, para saber en qué punto de su entrada
    # estamos en cada momento
    arranque = {}
    for ini, _fin, png in capas:
        arranque.setdefault(png, []).append(int(ini * FPS))
    _abiertas = {}

    def _cargar(p):
        if p not in _abiertas:
            _abiertas[p] = Image.open(p).convert("RGBA")
        return _abiertas[p]

    n_ent = max(1, int(TXT_ENTRADA * FPS))
    n_fnd = max(1, int(TXT_FUNDE * FPS))

    def texto(f):
        """Devuelve la capa YA ANIMADA para este fotograma."""
        p = por_marco.get(f)
        if not p:
            return None
        c = _cargar(p)
        arr = [a for a in arranque.get(p, []) if a <= f]
        k = f - max(arr) if arr else 0
        if k >= n_ent:
            return c

        t = k / n_ent
        e = _salida_cubica(t)
        # sobrepasa y asienta: una campana sobre la curva de entrada
        z = 1 + TXT_SOBREPASO * math.sin(math.pi * t) * (1 - t * .35)
        dy = int(TXT_SUBIDA * (1 - e))
        op = min(1.0, k / n_fnd)

        aw, ah = int(W * z), int(H * z)
        g = c.resize((aw, ah), Image.LANCZOS).crop(
            ((aw - W) // 2, (ah - H) // 2, (aw - W) // 2 + W, (ah - H) // 2 + H))
        if dy:
            g = g.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, -dy),
                            resample=Image.BILINEAR)
        if op < 1:
            a = g.getchannel("A").point(lambda v: int(v * op))
            g.putalpha(a)
        return g

    # marcos anclados a tiempos absolutos: sin acumulación de redondeo
    bordes = [0]
    t = 0.0
    for d in durs:
        t += d
        bordes.append(round(t * FPS))
    marcos = [bordes[i + 1] - bordes[i] for i in range(len(durs))]
    # el fundido nunca puede pasar del 40 % del plano más corto: con 1,25 s
    # fijos sobre un bloque de 2,6 s, el 47 % del plano estaba en disolución
    n_fun = int(min(FUNDIDO, 0.40 * min(durs)) * FPS)
    tramos = [m + (n_fun if i > 0 else 0) for i, m in enumerate(marcos)]
    desfase = [n_fun if i > 0 else 0 for i in range(len(marcos))]

    def base(i, kloc, empuje=0.0):
        """Fotograma de la imagen i en su posición local kloc.

        UNA sola transformación afín en coma flotante desde el original. Antes
        eran dos reescalados encadenados con los offsets redondeados a entero,
        y eso dejaba la cámara literalmente PARADA en el 65 % de los fotogramas
        de un plano largo, avanzando a saltos de 1 px. No se percibe como
        movimiento lento: se percibe como temblor a escalones.
        """
        seg = kloc / FPS
        z = max(Z1, Z0 - VELOCIDAD * seg) + empuje
        t = kloc / max(1, tramos[i] - 1)

        src = fondos[i]
        sw, sh = src.size
        # cobertura: la fuente cubre el lienzo sin deformarse (antes se estiraba
        # un 1,6 % porque los PNG de 768×1344 no son exactamente 9:16)
        cob = max(W / sw, H / sh) * z
        vw, vh = W / cob, H / cob

        # el ancla se DESPLAZA a lo largo del plano: un zoom radial puro sobre
        # imagen fija es el efecto más pobre que hay; lo que da vida es la
        # traslación lateral, y antes era exactamente cero
        ax0, ay0 = CENTROS[i % len(CENTROS)]
        ax1, ay1 = CENTROS[(i + 2) % len(CENTROS)]
        ax = ax0 + (ax1 - ax0) * t * DERIVA * 18
        ay = ay0 + (ay1 - ay0) * t * DERIVA * 18
        ax = min(1.0, max(0.0, ax))
        ay = min(1.0, max(0.0, ay))

        x0 = (sw - vw) * ax
        y0 = (sh - vh) * ay
        im = src.transform((W, H), Image.AFFINE,
                           (vw / W, 0, x0, 0, vh / H, y0), Image.BICUBIC)
        im.paste(r2.NEGRO, (0, 0), r2.SCRIM)
        return im

    def golpe(f):
        """Escala extra tras un acento. Con ATAQUE, no de golpe.

        Antes la rampa arrancaba en su valor máximo: del fotograma g-1 al g los
        bordes saltaban 19 px de una vez. Eso no es un acento, es un fallo de
        reproducción. Ahora sube desde cero, pica hacia el 25 % y cae con cola.
        """
        for g in golpes:
            u = (f - g) / GOLPE_F
            if 0 <= u < 1:
                return (GOLPE_ESCALA * math.exp(-4.2 * u)
                        * math.sin(math.pi * min(1.0, u * 1.9)))
        return 0.0

    cmd = [FFMPEG, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
           # allf=t+u re-sortea el patrón CADA fotograma: es lo que impide que
           # haya zonas con el píxel idéntico. Y la viñeta va elíptica, no
           # circular — circular es invisible.
           "-vf", "noise=alls=%d:allf=t+u,vignette=PI/6.5" % GRANO,
           "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
           "-movflags", "+faststart", "-color_primaries", "bt709",
           "-color_trc", "bt709", "-colorspace", "bt709"]
    mudo = os.path.join(PROY, "_mudo-flujo.mp4")
    p = subprocess.Popen(cmd + [mudo], stdin=subprocess.PIPE,
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    g_global = 0
    for i, n in enumerate(marcos):
        for k in range(n):
            img = base(i, k + desfase[i], golpe(g_global))
            if i + 1 < len(fondos) and k >= n - n_fun:
                t = (k - (n - n_fun)) / max(1, n_fun - 1)
                # la entrante avanza SIN redondear: con int() se comía un
                # fotograma y repetía el siguiente, o sea un tropiezo por corte
                kk = t * (n_fun - 1)
                img = Image.blend(img, base(i + 1, kk, golpe(g_global)), _suave(t))


            c = texto(g_global)
            if c is not None:
                img = img.convert("RGBA")
                img.alpha_composite(c)
                img = img.convert("RGB")
            p.stdin.write(img.convert("RGB").tobytes())
            g_global += 1

    p.stdin.close()
    err = p.stderr.read().decode()[-400:]
    if p.wait() != 0:
        raise RuntimeError("ffmpeg falló:\n" + err)

    subprocess.run([FFMPEG, "-y", "-i", mudo, "-i", audio, "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    "-shortest", salida], capture_output=True, check=True)
    os.remove(mudo)

    seg = g_global / FPS
    return {"salida": salida, "imagenes": len(fondos),
            "cambios_de_texto": len(capas),
            "texto_por_min": round(len(capas) / max(0.1, fin) * 60),
            "golpes": len(golpes), "fundidos": len(fondos) - 1,
            "video_s": round(seg, 2), "audio_s": round(fin, 2),
            "desfase_s": round(seg - fin, 2),
            "mb": round(os.path.getsize(salida) / 1e6, 2),
            "formato": "%dx%d" % formato}
