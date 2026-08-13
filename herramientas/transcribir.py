"""Audio → transcripción con marcas por palabra.

Primera pieza del circuito audio → vídeo. Sin marcas precisas por palabra no hay
sincronía, y el vídeo se ve mal aunque todo lo demás esté bien.

Dos trampas ya pagadas, para no repetirlas:

  · **`ffmpeg` se llama por nombre.** mlx-whisper lanza `ffmpeg` por subprocess
    confiando en el PATH, así que hay que meter el venv en el PATH aunque se
    invoque el python del venv con ruta absoluta. Es la misma trampa que nos
    costó tiempo con `comfy`. Aquí se arregla dentro, en `_preparar_path()`.

  · **Los nombres propios fallan.** Medido: «Loewenstein» salió «Levenstein».
    La transcripción se revisa antes de publicar; no se da por buena a ciegas.

Vive en un venv APARTE (`~/asr/.venv`) a propósito: ComfyUI necesita torch 2.13
y no se toca por nada.
"""
import json
import os
import subprocess
import sys

ASR = "/Users/maity/asr/.venv"
MODELO = "mlx-community/whisper-large-v3-turbo"
PROY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _preparar_path():
    """mlx-whisper busca `ffmpeg` en el PATH, no donde esté instalado."""
    b = ASR + "/bin"
    if b not in os.environ.get("PATH", ""):
        os.environ["PATH"] = b + ":" + os.environ.get("PATH", "")
    if not os.path.exists(b + "/ffmpeg"):
        raise RuntimeError("falta ffmpeg en %s — enlázalo desde imageio_ffmpeg" % b)


# Lo que se le sopla al modelo antes de empezar. Es la mejora más barata que
# encontramos: MIDE 5,70 % de error frente al 9,17 % sin él —casi la mitad— y
# no cuesta ni un byte de disco. Funciona porque orienta al modelo sobre el
# vocabulario y, sobre todo, sobre el estilo de puntuación.
#
# Banco completo (`banco_asr.py`, ocho frases con verdad conocida):
#   turbo + contexto   5,70 %  · 11,1 s   ← elegido
#   large-v3+contexto  6,92 %  · 15,3 s   (y 3 GB más de disco)
#   parakeet-tdt-v3    7,44 %  ·  7,3 s   (más rápido, más errores)
#   turbo solo         9,17 %  · 18,0 s
CONTEXTO = ("Transcripción en español de España y México, con puntuación completa: "
            "puntos, comas, signos de interrogación y de exclamación. Pueden "
            "aparecer apellidos extranjeros y cifras.")


def transcribir(audio, idioma="es", contexto=CONTEXTO, vocabulario=()):
    """Devuelve {texto, palabras:[{palabra,inicio,fin}], duracion}.

    vocabulario: nombres propios y términos que salgan en ESTE audio. Añadirlos
    es lo que evita que «Loewenstein» acabe en «Levenstein», que es el error
    más caro: un dato bien citado con el apellido mal escrito parece descuido.
    """
    _preparar_path()
    import mlx_whisper
    prompt = contexto
    if vocabulario:
        prompt += " Nombres que aparecen: " + ", ".join(vocabulario) + "."
    r = mlx_whisper.transcribe(
        audio, path_or_hf_repo=MODELO, language=idioma,
        word_timestamps=True,
        initial_prompt=prompt or None,
        # sin esto, un error se arrastra y contamina todo lo que viene detrás
        condition_on_previous_text=False)
    palabras = [{"palabra": w["word"].strip(),
                 "inicio": round(w["start"], 2), "fin": round(w["end"], 2)}
                for s in r["segments"] for w in s.get("words", [])]
    return {"texto": r["text"].strip(),
            "palabras": palabras,
            "duracion": palabras[-1]["fin"] if palabras else 0.0}


def guardar(audio, destino=None):
    d = transcribir(audio)
    destino = destino or os.path.splitext(audio)[0] + ".json"
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    return destino, d


def _en_su_venv():
    return sys.executable.startswith(ASR)


if __name__ == "__main__":
    if not _en_su_venv():
        # relanzarse en el venv correcto en vez de fallar con un ImportError
        os.execv(ASR + "/bin/python", [ASR + "/bin/python", __file__] + sys.argv[1:])
    if len(sys.argv) < 2:
        carpeta = os.path.join(PROY, "audio")
        cand = [os.path.join(carpeta, x) for x in sorted(os.listdir(carpeta))
                if not x.startswith(".") and not x.endswith(".json")]
        if not cand:
            sys.exit("No hay audio en %s" % carpeta)
        audio = cand[0]
    else:
        audio = sys.argv[1]

    print("  transcribiendo:", os.path.basename(audio))
    destino, d = guardar(audio)
    m, s = divmod(int(d["duracion"]), 60)
    print("  %d:%02d de audio · %d palabras" % (m, s, len(d["palabras"])))
    print("  guardado en:", destino)
    print("\n  " + d["texto"][:400])
