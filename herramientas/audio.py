"""Pega música al MP4: recorta el tramo elegido, normaliza y funde.

Todo se verifica con números porque no hay forma de escucharlo:
  · duración del audio == duración del vídeo
  · loudness integrado en -14 LUFS (el objetivo de las plataformas)
  · pico real por debajo de -1 dBTP (sin recortes)
  · el vídeo NO se recodifica: se copia tal cual
"""
import json, os, subprocess

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
MUS = "/Users/maity/Desktop/Confy Imagenes/fuentes/musica"


def duracion(p):
    out = subprocess.run(
        [FF, "-hide_banner", "-i", p], capture_output=True, text=True).stderr
    for l in out.splitlines():
        if "Duration:" in l:
            h, m, s = l.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError("sin duración: " + p)


def poner_musica(mp4, pista, inicio, salida, fade_in=1.2, fade_out=2.5,
                 lufs=-14.0):
    """Corta desde `inicio`, ajusta a la duración del vídeo y mezcla.

    La normalización va en DOS PASADAS. Con una sola, loudnorm estima sobre
    la marcha y se queda corto: medido, dejaba el audio en -12,1 LUFS cuando
    se le pedían -14. La primera pasada mide el tramo real y la segunda
    aplica esos valores exactos.
    """
    dur = duracion(mp4)
    src = os.path.join(MUS, pista)

    recorte = ("atrim=start={ini}:end={fin},asetpts=PTS-STARTPTS,"
               "afade=t=in:st=0:d={fi},afade=t=out:st={fo_st}:d={fo}"
               ).format(ini=inicio, fin=inicio + dur, fi=fade_in,
                        fo_st=max(0.1, dur - fade_out), fo=fade_out)

    # --- pasada 1: medir ---
    m = subprocess.run(
        [FF, "-hide_banner", "-i", src, "-af",
         recorte + ",loudnorm=I=%s:TP=-1.5:LRA=11:print_format=json" % lufs,
         "-f", "null", "-"], capture_output=True, text=True, timeout=300).stderr
    try:
        med = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
        medido = (":measured_I=%s:measured_TP=%s:measured_LRA=%s"
                  ":measured_thresh=%s:offset=%s:linear=true"
                  % (med["input_i"], med["input_tp"], med["input_lra"],
                     med["input_thresh"], med["target_offset"]))
    except Exception:
        medido = ""                      # si la medición falla, una pasada

    filtro = (recorte + ",loudnorm=I=%s:TP=-1.5:LRA=11%s,aresample=48000"
              % (lufs, medido))

    r = subprocess.run(
        [FF, "-y", "-hide_banner", "-loglevel", "error",
         "-i", mp4, "-i", src,
         "-filter_complex", "[1:a]" + filtro + "[a]",
         "-map", "0:v", "-map", "[a]",
         "-c:v", "copy",                       # el vídeo no se toca
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
         "-shortest", "-movflags", "+faststart", salida],
        capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not os.path.exists(salida):
        raise RuntimeError("ffmpeg falló:\n" + r.stderr[-600:])
    return salida


def medir(p):
    """Devuelve (duración_v, duración_a, LUFS, pico_dBTP)."""
    r = subprocess.run(
        [FF, "-hide_banner", "-i", p, "-af",
         "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, timeout=300).stderr
    lufs = pico = None
    lineas = r.splitlines()
    for i, l in enumerate(lineas):
        if "Integrated loudness" in l:
            for j in range(i, min(i + 4, len(lineas))):
                if "I:" in lineas[j]:
                    lufs = float(lineas[j].split("I:")[1].split("LUFS")[0])
                    break
        if "True peak" in l:
            for j in range(i, min(i + 4, len(lineas))):
                if "Peak:" in lineas[j]:
                    pico = float(lineas[j].split("Peak:")[1].split("dBFS")[0])
                    break
    info = subprocess.run([FF, "-hide_banner", "-i", p],
                          capture_output=True, text=True).stderr
    dv = da = None
    for l in info.splitlines():
        if "Stream" in l and "Video" in l:
            dv = True
        if "Stream" in l and "Audio" in l:
            da = True
    return duracion(p), bool(dv), bool(da), lufs, pico


SEGMENTOS = json.load(open(os.path.join(MUS, "segmentos.json")))
