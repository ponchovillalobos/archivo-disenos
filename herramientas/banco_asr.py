"""Banco de pruebas de transcripción en español. Mide, no opina.

Existe porque «este modelo es mejor» sin números no vale nada. Compara
configuraciones sobre un texto del que conocemos la verdad exacta —generado con
la voz del sistema— y saca el WER (proporción de palabras erradas).

El texto de prueba carga a propósito contra lo que ya sabemos que falla:

  · **Nombres propios extranjeros** — «Loewenstein» salió «Levenstein» en la
    primera prueba real. Es el error más caro: un dato bien citado con el
    apellido mal escrito parece descuido.
  · **Cifras** — años, porcentajes y miles con separador.
  · **Puntuación** — en «Idea 1» el ASR se comió los puntos del último tercio y
    tres ideas quedaron pegadas en un solo bloque. Sin puntos no hay bloques, y
    sin bloques no hay imágenes.
  · **Grafías del español** — eñes, tildes y diéresis.

El WER se calcula sobre texto normalizado (sin tildes ni signos) para medir
palabras; la puntuación se puntúa aparte, porque nos importa por otra razón.
"""
import json
import os
import re
import subprocess
import sys
import time
import unicodedata

S = os.path.dirname(os.path.abspath(__file__))
ASR = "/Users/maity/asr/.venv"
# El banco vivía en /private/tmp y el sistema puede borrarlo. Es la ÚNICA
# evidencia de por qué el transcriptor es el que es (turbo+contexto, 5,70 % WER
# contra 7,44 % de parakeet); si desaparece, la decisión queda sin respaldo.
TMP = os.path.join(os.path.dirname(S), "pruebas", "asr")

FRASES = [
 "Loewenstein demostró en mil novecientos noventa y cuatro que la curiosidad es privación.",
 "Cialdini y Kahneman coinciden: el anclaje replicó en treinta y seis muestras de treinta y seis.",
 "El estudio analizó seis mil novecientos cincuenta y seis artículos del New York Times.",
 "Nitobe Inazō publicó el Bushidō en mil novecientos, en Filadelfia, y lo escribió en inglés.",
 "¿Montaña rusa o hablar en público? Tu cuerpo no sabe la diferencia. Solo tú se la pones.",
 "La proporción era cuarenta y tres sobre cincuenta y siete, pero Gong la actualizó después.",
 "El niño pequeño añoraba el cariño de su abuela, que le enseñaba a distinguir la cigüeña.",
 "Dana Carney escribió que ya no cree que los efectos sean reales, y dejó de enseñarlo.",
]

CONFIGS = {
 "turbo":            dict(modelo="mlx-community/whisper-large-v3-turbo"),
 "turbo+contexto":   dict(modelo="mlx-community/whisper-large-v3-turbo", contexto=True),
 "large-v3":         dict(modelo="mlx-community/whisper-large-v3-mlx"),
 "large-v3+contexto": dict(modelo="mlx-community/whisper-large-v3-mlx", contexto=True),
}

# lo que se le sopla al modelo para que sepa de qué va y cómo puntuar
CONTEXTO = ("Transcripción en español con puntuación completa. Aparecen apellidos "
            "extranjeros como Loewenstein, Cialdini, Kahneman, Nitobe Inazō, Carney, "
            "y cifras como 1994, 43/57, 6.956.")


def normalizar(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w\s]", " ", t).split()


def wer(ref, hip):
    """Distancia de edición sobre palabras, normalizada por la referencia."""
    r, h = normalizar(ref), normalizar(hip)
    d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1):
        d[i][0] = i
    for j in range(len(h) + 1):
        d[0][j] = j
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1,
                          d[i - 1][j - 1] + (r[i - 1] != h[j - 1]))
    return d[-1][-1] / max(1, len(r))


def signos(t):
    return sum(t.count(c) for c in ".,;:¿?¡!")


def preparar_audio():
    os.makedirs(TMP, exist_ok=True)
    rutas = []
    for i, f in enumerate(FRASES, 1):
        w = os.path.join(TMP, "f%02d.wav" % i)
        if not os.path.exists(w):
            a = os.path.join(TMP, "f%02d.aiff" % i)
            subprocess.run(["say", "-v", "Monica", "-o", a, f],
                           capture_output=True)
            if not os.path.exists(a):          # sin voz Monica, la que haya
                subprocess.run(["say", "-o", a, f], capture_output=True)
            subprocess.run([ASR + "/bin/ffmpeg", "-i", a, "-ar", "16000",
                            "-ac", "1", "-y", w], capture_output=True)
            os.remove(a)
        rutas.append(w)
    return rutas


def probar(nombre, cfg, rutas):
    import mlx_whisper
    kw = {}
    if cfg.get("contexto"):
        kw["initial_prompt"] = CONTEXTO
    errores, sig_ref, sig_hip, t0 = [], 0, 0, time.time()
    textos = []
    for ruta, verdad in zip(rutas, FRASES):
        r = mlx_whisper.transcribe(ruta, path_or_hf_repo=cfg["modelo"],
                                   language="es", condition_on_previous_text=False,
                                   **kw)
        t = r["text"].strip()
        textos.append(t)
        errores.append(wer(verdad, t))
        sig_ref += signos(verdad)
        sig_hip += signos(t)
    return {"config": nombre,
            "wer": round(sum(errores) / len(errores) * 100, 2),
            "peor": round(max(errores) * 100, 2),
            "signos_ref": sig_ref, "signos_obt": sig_hip,
            "segundos": round(time.time() - t0, 1),
            "textos": textos}


def main():
    os.environ["PATH"] = ASR + "/bin:" + os.environ.get("PATH", "")
    rutas = preparar_audio()
    salida = []
    for nombre, cfg in CONFIGS.items():
        try:
            r = probar(nombre, cfg, rutas)
        except Exception as e:
            r = {"config": nombre, "error": str(e)[:200]}
        salida.append(r)
        print("  %-20s %s" % (nombre, json.dumps(
            {k: v for k, v in r.items() if k != "textos"}, ensure_ascii=False)),
            flush=True)
    with open(os.path.join(S, "..", "banco-asr.json"), "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    if not sys.executable.startswith(ASR):
        os.execv(ASR + "/bin/python", [ASR + "/bin/python", __file__] + sys.argv[1:])
    main()
