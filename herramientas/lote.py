"""Motor de lotes para la serie de comunicación.

Reglas duras de composición, derivadas de lo que ya nos ha fallado:
  · NUNCA caras en primer plano ni a media distancia reconocible
  · NUNCA manos visibles
  · Los humanos aparecen como SILUETAS, de espaldas, lejanos o a contraluz
  · Se prefiere el vacío, la niebla, el umbral y la luz dirigida

Cada tema tiene su propio mundo visual y su color de acento, para que los
quince se distingan entre sí sin dejar de ser la misma voz.
"""
import glob, json, os, subprocess, time

from paletas import PALETAS, paleta_de

S = os.path.dirname(os.path.abspath(__file__))
# Dos flujos, y la diferencia NO es cosmética:
#
#   RAPIDO   8 pasos · CFG 1.0 · con LoRA Lightning ·  57 s
#   CALIDAD 30 pasos · CFG 5.5 · SIN LoRA           · 144 s
#
# A CFG 1.0 la guía sin clasificador está DESACTIVADA: el negativo no influye y
# el modelo apenas obedece. Medido con cuatro variantes de la misma escena: con
# veto y sin veto salieron píxel a píxel idénticas. Todo lo que creíamos ganado
# con el veto venía de los pesos en positivo.
#
# Para producción en serie el rápido va bien: la escena manda y basta. Para algo
# que exija OBEDIENCIA —un personaje fiel, un objeto concreto, una composición
# pedida— hay que usar el de calidad y pagar los 144 segundos.
RAPIDO = "/Users/maity/Desktop/Confy Imagenes/workflows/LAB-ESPARTANO-v2---rapido.json"
CALIDAD = "/Users/maity/Desktop/Confy Imagenes/workflows/LAB-ESPARTANO-v2---CALIDAD.json"
BASE = RAPIDO
SALIDA = "/Users/maity/comfy/output/reels"

NOIR = ("black and white film noir, extreme contrast, deep black shadows and bright white "
        "highlights, hard directional light, heavy atmosphere, hyper detailed textures")

# El negativo hace el trabajo pesado: bloquea justo lo que SDXL hace mal.
NEG = ("(face:1.6), (faces:1.6), (portrait:1.5), (close-up face:1.6), (facial features:1.5), "
       "(eyes:1.4), (hands:1.6), (fingers:1.6), (visible hands:1.5), (arms in foreground:1.3), "
       "blurry, low quality, deformed, extra limbs, disfigured, watermark, text, letters, "
       "signature, logo, cartoon, plastic skin, flat lighting, modern clothing, smartphone, "
       # el estilo pedía épico y salía de terror: el veto de ánimo importa tanto
       # como el de color. Sin esto, «sombra dura» + «niebla» = película de miedo.
       "(horror:1.4), (creepy:1.4), (sinister:1.3), (ominous:1.3), (bleak:1.2), "
       "(desolate:1.2), (decay:1.2), (grimdark:1.3), (nightmare:1.3), (haunted:1.3), "
       "(oppressive:1.2), (murky:1.2), muddy colors, washed out")


def flujo(slug, escena, objeto, encuadre, aire, luz, ancho=768, alto=1344, ropa="",
          paleta=None, look=None, negativo=None, base=None,
          semilla=None, pasos=None, cfg=None):
    """paleta: nombre de PALETAS. Por defecto noir (blanco y negro).

    El color entra por DOS sitios, no uno: la instrucción en positivo y el VETO
    en el negativo. Medido: solo con el positivo, cinco de ocho paletas salían
    azul-cian porque a CFG 1.0 manda la escena. Con el veto, la mostaza pasó de
    156° (verde) a 36° (ámbar) y su saturación de 10,7 a 42,5.

    look y negativo: texto crudo, para reproducir una receta guardada tal cual.
    Ganan sobre `paleta`. Existen porque el recetario resucita imágenes ya
    aprobadas, y esas llevan su tratamiento escrito, no un nombre de paleta.
    """
    _, p_look, veto = PALETAS.get(paleta, ("", NOIR, "")) if paleta else ("", NOIR, "")
    look = look or p_look
    neg = negativo or (
        NEG + ("".join(", (%s:1.3)" % c for c in veto.split(", ")) if veto else ""))
    wf = json.load(open(base or BASE))
    for n in wf["nodes"]:
        i = n["id"]
        if i == 11: n["widgets_values"] = [escena]
        elif i == 12: n["widgets_values"] = [ropa or "dark simple clothing"]
        elif i == 13: n["widgets_values"] = [objeto]
        elif i == 14: n["widgets_values"] = [encuadre]
        elif i == 15: n["widgets_values"] = [aire]
        elif i == 16: n["widgets_values"] = [luz]
        elif i == 17: n["widgets_values"] = [look]
        elif i == 5:  n["widgets_values"] = [neg]
        elif i == 6:  n["widgets_values"] = [ancho, alto, 1]
        elif i == 9:  n["widgets_values"] = ["reels/" + slug]
        # El KSampler NO se tocaba nunca, y ése era el agujero: la semilla se
        # quedaba con lo que trajese el JSON. Consecuencias reales, las tres
        # medidas en una auditoría:
        #   · no había forma de pedir una variante — mismo prompt, misma imagen
        #   · `contrato.py` resolvía `semilla` y `variar_semilla` y esos campos
        #     NO llegaban a ningún sitio: código muerto
        #   · si alguien guardaba la plantilla desde la interfaz con
        #     «aleatorizar», se perdía la reproducibilidad sin un solo error
        #
        # Se escribe siempre "fixed": la variación se pide cambiando `semilla`,
        # no dejando que el JSON decida a nuestras espaldas.
        elif i == 7:
            v = list(n["widgets_values"])
            n["widgets_values"] = [
                semilla if semilla is not None else v[0], "fixed",
                pasos if pasos is not None else v[2],
                cfg if cfg is not None else v[3], v[4], v[5], v[6]]
    # Los flujos generados son DESECHABLES: ComfyUI copia el prompt cuando lo
    # recibe, así que el fichero no vuelve a leerse nunca. Llegaron a acumularse
    # 214 (5 MB) sin que nadie los mirase.
    #
    # Se escriben porque `comfy run --workflow` necesita una ruta, pero se
    # rotan: solo sobreviven los últimos TOPE_FLUJOS, suficiente para inspeccionar
    # lo que se acaba de encolar si algo sale raro.
    #
    # La memoria de lo que funciona NO vive aquí: vive en `recetario.py`, que la
    # recupera de los metadatos del propio PNG. Eso es mejor porque queda atado
    # al resultado real, no a la intención.
    d = os.path.join(S, "flujos")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "L-%s.json" % slug)
    json.dump(wf, open(p, "w"), indent=1)
    _rotar(d)
    return p


TOPE_FLUJOS = 40


def _rotar(d, tope=None):
    """Deja solo los flujos más recientes. Son regenerables: no hay nada que
    perder y sí un directorio que mantener legible."""
    tope = tope or TOPE_FLUJOS
    fs = sorted((os.path.getmtime(x), x)
                for x in glob.glob(os.path.join(d, "L-*.json")))
    for _, x in fs[:-tope]:
        try:
            os.remove(x)
        except OSError:
            pass


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
