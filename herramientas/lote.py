"""Motor de lotes para la serie de comunicación.

Reglas duras de composición, derivadas de lo que ya nos ha fallado:
  · NUNCA caras en primer plano ni a media distancia reconocible
  · NUNCA manos visibles
  · Los humanos aparecen como SILUETAS, de espaldas, lejanos o a contraluz
  · Se prefiere el vacío, la niebla, el umbral y la luz dirigida

Cada tema tiene su propio mundo visual y su color de acento, para que los
quince se distingan entre sí sin dejar de ser la misma voz.
"""
import json, os, subprocess, time

S = os.path.dirname(os.path.abspath(__file__))
BASE = "/Users/maity/reels/workflows/LAB-ESPARTANO-v2---rapido.json"
SALIDA = "/Users/maity/comfy/output/reels"

NOIR = ("black and white film noir, extreme contrast, deep black shadows and bright white "
        "highlights, hard directional light, heavy atmosphere, hyper detailed textures")

# El negativo hace el trabajo pesado: bloquea justo lo que SDXL hace mal.
NEG = ("(face:1.6), (faces:1.6), (portrait:1.5), (close-up face:1.6), (facial features:1.5), "
       "(eyes:1.4), (hands:1.6), (fingers:1.6), (visible hands:1.5), (arms in foreground:1.3), "
       "blurry, low quality, deformed, extra limbs, disfigured, watermark, text, letters, "
       "signature, logo, cartoon, plastic skin, flat lighting, modern clothing, smartphone")


def flujo(slug, escena, objeto, encuadre, aire, luz, ancho=720, alto=1280, ropa=""):
    wf = json.load(open(BASE))
    for n in wf["nodes"]:
        i = n["id"]
        if i == 11: n["widgets_values"] = [escena]
        elif i == 12: n["widgets_values"] = [ropa or "dark simple clothing"]
        elif i == 13: n["widgets_values"] = [objeto]
        elif i == 14: n["widgets_values"] = [encuadre]
        elif i == 15: n["widgets_values"] = [aire]
        elif i == 16: n["widgets_values"] = [luz]
        elif i == 17: n["widgets_values"] = [NOIR]
        elif i == 5:  n["widgets_values"] = [NEG]
        elif i == 6:  n["widgets_values"] = [ancho, alto, 1]
        elif i == 9:  n["widgets_values"] = ["reels/" + slug]
    p = os.path.join(S, "L-%s.json" % slug)
    json.dump(wf, open(p, "w"), indent=1)
    return p


def encolar(rutas):
    """Envía por MCP no; aquí usamos comfy-cli directo para no depender del turno."""
    env = dict(os.environ, PATH="/Users/maity/comfy-env/bin:" + os.environ.get("PATH", ""))
    ids = []
    for r in rutas:
        out = subprocess.run(["comfy", "--skip-prompt", "run", "--workflow", r],
                             capture_output=True, text=True, env=env, timeout=300)
        ids.append((os.path.basename(r), out.returncode))
    return ids


def pendientes():
    import urllib.request
    with urllib.request.urlopen("http://127.0.0.1:8188/queue", timeout=10) as r:
        q = json.load(r)
    return len(q.get("queue_running", [])) + len(q.get("queue_pending", []))


def esperar(limite=0, cada=20, tope=3600):
    t0 = time.time()
    while time.time() - t0 < tope:
        n = pendientes()
        if n <= limite:
            return n
        time.sleep(cada)
    return pendientes()
