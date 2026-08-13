"""Monta un vídeo cuya duración la manda el audio, no el tiempo de lectura.

Diferencia esencial con `montar_serie.py`: allí cada lámina dura lo que se
tarda en leerla (`1,6 s + caracteres/19`) y la música se estira debajo. Aquí el
audio ya existe y es intocable — el vídeo se pliega a él.

**El detalle que rompe la sincronía si se ignora:** entre un bloque y el
siguiente hay silencio. Si cada lámina durase `fin − inicio`, el vídeo saldría
más corto que el audio y la imagen se adelantaría más y más. Por eso la
duración va **de un arranque al siguiente** (`inicio[i+1] − inicio[i]`), y la
última se estira hasta el final real del archivo. Así el silencio queda dentro
de la lámina que lo precede, que es donde el oído lo espera.

Funciona igual en vertical y en apaisado: `reel3.formato()` decide el lienzo.
"""
import os
import subprocess
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)

import imageio_ffmpeg                       # noqa: E402
import reel3                                # noqa: E402

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
PROY = os.path.dirname(S)


def duracion_audio(ruta):
    r = subprocess.run([FFMPEG, "-i", ruta], capture_output=True, text=True)
    for lin in r.stderr.splitlines():
        if "Duration:" in lin:
            h, m, s = lin.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError("no pude leer la duración de " + ruta)


def duraciones(bloques, fin_audio):
    """De un arranque al siguiente. El silencio pertenece al bloque anterior."""
    ini = [b["inicio"] for b in bloques]
    return [round((ini[i + 1] if i + 1 < len(ini) else fin_audio) - ini[i], 3)
            for i in range(len(ini))]


def montar(bloques, audio, fondos_dir, salida, acento="#d8353d",
           formato=(1080, 1920), crf=20, seg_transicion=1.1):
    """bloques: [{fondo, titular, cuerpo?, kicker?, inicio}] en orden."""
    reel3.formato(*formato)
    fin = duracion_audio(audio)
    durs = duraciones(bloques, fin)

    # el primer bloque casi nunca empieza en 0,00: ese arranque es aire del
    # audio y hay que dárselo a la primera lámina o todo iría adelantado
    durs[0] += bloques[0]["inicio"]

    laminas = [dict(b, dur=d) for b, d in zip(bloques, durs)]
    mudo = os.path.join(PROY, "_mudo-audio.mp4")
    n, seg, _ = reel3.montar(laminas, fondos_dir, mudo,
                             os.path.join(fondos_dir, "CAPAS"),
                             acento=acento, seg_transicion=seg_transicion, crf=crf)

    # el vídeo se copia sin recodificar: pegar el audio cuesta un segundo
    subprocess.run([FFMPEG, "-y", "-i", mudo, "-i", audio,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-shortest", salida],
                   capture_output=True, check=True)
    os.remove(mudo)

    desfase = seg - fin
    return {"salida": salida, "fotogramas": n, "video_s": round(seg, 2),
            "audio_s": round(fin, 2), "desfase_s": round(desfase, 2),
            "mb": round(os.path.getsize(salida) / 1e6, 2),
            "formato": "%dx%d" % formato}
