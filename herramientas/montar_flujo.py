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

# Apertura de cámara: profunda y siempre de dentro hacia fuera.
Z0, Z1 = 1.22, 1.00
CENTROS = [(.50, .44), (.40, .40), (.60, .50), (.46, .56), (.54, .38)]

GOLPES = 7          # cuántos acentos reciben empuje, en TODO el vídeo
GOLPE_ESCALA = .035  # cuánto empuja. Más que esto y marea
GOLPE_F = 7          # en cuántos fotogramas se resuelve
FUNDIDO = 1.25       # segundos entre imagen e imagen


def _suave(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


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
    _abiertas = {}

    def texto(f):
        p = por_marco.get(f)
        if not p:
            return None
        if p not in _abiertas:
            _abiertas[p] = Image.open(p).convert("RGBA")
        return _abiertas[p]

    # marcos anclados a tiempos absolutos: sin acumulación de redondeo
    bordes = [0]
    t = 0.0
    for d in durs:
        t += d
        bordes.append(round(t * FPS))
    marcos = [bordes[i + 1] - bordes[i] for i in range(len(durs))]
    n_fun = int(FUNDIDO * FPS)
    tramos = [m + (n_fun if i > 0 else 0) for i, m in enumerate(marcos)]
    desfase = [n_fun if i > 0 else 0 for i in range(len(marcos))]

    def base(i, kloc):
        """Fotograma de la imagen i en su posición local kloc."""
        t = kloc / max(1, tramos[i] - 1)
        z = Z0 + (Z1 - Z0) * t
        aw, ah = int(W * z), int(H * z)
        im = fondos[i].resize((aw, ah), Image.LANCZOS)
        ax, ay = CENTROS[i % len(CENTROS)]
        im = im.crop((int((aw - W) * ax), int((ah - H) * ay),
                      int((aw - W) * ax) + W, int((ah - H) * ay) + H))
        im.paste(r2.NEGRO, (0, 0), r2.SCRIM)
        return im

    def golpe(f):
        """Escala extra si estamos justo después de un acento fuerte."""
        for g in golpes:
            if 0 <= f - g < GOLPE_F:
                return GOLPE_ESCALA * (1 - (f - g) / GOLPE_F)
        return 0.0

    cmd = [FFMPEG, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
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
            img = base(i, k + desfase[i])
            if i + 1 < len(fondos) and k >= n - n_fun:
                t = (k - (n - n_fun)) / max(1, n_fun - 1)
                img = Image.blend(img, base(i + 1, int(t * n_fun)), _suave(t))

            e = golpe(g_global)
            if e:
                aw, ah = int(W * (1 + e)), int(H * (1 + e))
                img = img.resize((aw, ah), Image.LANCZOS).crop(
                    ((aw - W) // 2, (ah - H) // 2,
                     (aw - W) // 2 + W, (ah - H) // 2 + H))

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
