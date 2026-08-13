"""Montador con ritmo: corte seco dentro de la idea, fundido entre ideas.

La decisión que lo sostiene todo:

  · **Entre planos de la MISMA lámina → corte seco.** Es la misma escena vista
    más de cerca, así que el corte se lee como énfasis, no como cambio. Ahí
    está la agilidad.
  · **Entre láminas distintas → fundido largo.** Cambia la escena Y cambia el
    texto: si eso se cortara en seco, el espectador tendría que releer. Ahí
    está la elegancia.

Así conviven las dos cosas que parecían opuestas: saltos que enganchan y
transiciones muy suaves. No compiten porque no ocurren en el mismo sitio.

Dos detalles que evitan el mareo, ambos deliberados:

  · **El texto NO cambia con el corte.** Un bloque mantiene su frase aunque el
    plano cambie tres veces. Si el texto saltara con cada corte, sería
    ilegible.
  · **Un empujón mínimo en el corte seco** (2 % durante 5 fotogramas). Sin él
    el corte se ve plano; con más, marea. Es la diferencia entre «cortó» y
    «golpeó».
"""
import os
import subprocess
import sys

from PIL import Image

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)

import imageio_ffmpeg                        # noqa: E402
import reel2 as r2                           # noqa: E402
import reel3                                 # noqa: E402
from cortes import ENCUADRES, guionizar, resumen   # noqa: E402
from montar_audio import duracion_audio, duraciones  # noqa: E402
from reel2 import ESCALA, capa_texto, html_texto     # noqa: E402
from ritmo import analizar                    # noqa: E402

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
PROY = os.path.dirname(S)
FPS = 30

EMPUJON = 0.020      # cuánto se abre el plano justo tras el corte seco
EMPUJON_F = 5        # en cuántos fotogramas se resuelve
FUNDIDO_MAX = 1.6    # tope del fundido entre láminas


def _suave(t):
    """Smootherstep: arranca y termina casi imperceptible."""
    return t * t * t * (t * (t * 6 - 15) + 10)


def _plano(fondo, enc, t, W, H, empuje=0.0):
    """Un fotograma del plano. `t` va de 0 a 1 dentro del plano."""
    e = ENCUADRES[enc]
    z = e["z"] + e["deriva"] * t + empuje
    z = max(1.001, z)
    aw, ah = int(W * z), int(H * z)
    im = fondo.resize((aw, ah), Image.LANCZOS)
    x = int((aw - W) * e["ax"])
    y = int((ah - H) * e["ay"])
    im = im.crop((x, y, x + W, y + H))
    im.paste(r2.NEGRO, (0, 0), r2.SCRIM)
    return im


def montar(bloques, audio, fondos_dir, salida, acento="#d8353d",
           formato=(1080, 1920), crf=20, semilla=0):
    W, H = formato
    reel3.formato(W, H)
    fin = duracion_audio(audio)
    durs = duraciones(bloques, fin)
    durs[0] += bloques[0]["inicio"]

    an = analizar(audio)
    planos = guionizar(bloques, durs, an["paso"], semilla=semilla)

    dir_capas = os.path.join(fondos_dir, "CAPAS")
    os.makedirs(dir_capas, exist_ok=True)
    fondos, capas = [], []
    for i, b in enumerate(bloques, 1):
        f = Image.open(os.path.join(fondos_dir, b["fondo"])).convert("RGB")
        if f.size != (W, H):
            f = f.resize((W, H), Image.LANCZOS)
        fondos.append(f)
        capas.append(capa_texto(
            html_texto(b.get("kicker", ""), b["titular"], b.get("cuerpo"),
                       b.get("lista"), "%02d / %02d" % (i, len(bloques)),
                       acento, b.get("tam", ESCALA[4])),
            os.path.join(dir_capas, "capa-%02d.png" % i)))

    # Los fotogramas se cuentan desde el INSTANTE ABSOLUTO de cada corte, no
    # redondeando la duración de cada plano. Redondeando plano a plano, 34
    # redondeos acumulaban 0,63 s de desfase al final; así el error nunca pasa
    # de medio fotograma porque cada frontera se ancla a su tiempo real.
    bordes = [round(pl["inicio"] * FPS) for pl in planos] + [round(fin * FPS)]
    marcos = [max(1, bordes[i + 1] - bordes[i]) for i in range(len(planos))]
    n_fun = int(min(FUNDIDO_MAX, 0.9 * an["paso"] * 2) * FPS)

    def cuadro(idx, k):
        p = planos[idx]
        n = marcos[idx]
        t = k / max(1, n - 1)
        emp = EMPUJON * (1 - min(1, k / EMPUJON_F)) if k < EMPUJON_F else 0.0
        base = _plano(fondos[p["lamina"]], p["encuadre"], t, W, H, emp)
        c = capas[p["lamina"]]
        base.paste(c, (0, 0), c)
        return base

    cmd = [FFMPEG, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
           "-movflags", "+faststart",
           "-color_primaries", "bt709", "-color_trc", "bt709",
           "-colorspace", "bt709", "-"]
    mudo = os.path.join(PROY, "_mudo-ritmo.mp4")
    p = subprocess.Popen(cmd[:-1] + [mudo], stdin=subprocess.PIPE,
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    secos = fundidos = 0
    for i, n in enumerate(marcos):
        siguiente_es_otra = (i + 1 < len(planos)
                             and planos[i + 1]["lamina"] != planos[i]["lamina"])
        for k in range(n):
            img = cuadro(i, k)
            if siguiente_es_otra and k >= n - n_fun:
                t = (k - (n - n_fun)) / max(1, n_fun - 1)
                img = Image.blend(img, cuadro(i + 1, int(t * n_fun)), _suave(t))
            p.stdin.write(img.convert("RGB").tobytes())
        if i + 1 < len(planos):
            fundidos += siguiente_es_otra
            secos += not siguiente_es_otra
    p.stdin.close()
    err = p.stderr.read().decode()[-400:]
    if p.wait() != 0:
        raise RuntimeError("ffmpeg falló:\n" + err)

    subprocess.run([FFMPEG, "-y", "-i", mudo, "-i", audio, "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    "-shortest", salida], capture_output=True, check=True)
    os.remove(mudo)

    seg = sum(marcos) / FPS
    return dict(resumen(planos, durs), salida=salida,
                cortes_secos=secos, fundidos=fundidos,
                paso=an["paso"], pulsos_por_min=an["pulsos_por_min"],
                video_s=round(seg, 2), audio_s=round(fin, 2),
                desfase_s=round(seg - fin, 2),
                mb=round(os.path.getsize(salida) / 1e6, 2),
                formato="%dx%d" % formato)
