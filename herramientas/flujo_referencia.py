"""Genera con IMAGEN DE REFERENCIA. Es lo que de verdad mantiene un personaje.

Los dos intentos anteriores fracasaron y cada uno enseñó algo:

  · **Flujo rápido** (8 pasos, CFG 1.0): ni un rasgo del personaje, ni el cuento.
    A CFG 1.0 la guía sin clasificador está desactivada y el modelo apenas
    obedece — medido con cuatro variantes idénticas por pares.
  · **Flujo de calidad** (30 pasos, CFG 5.5): mejor imagen, mismo fallo de
    personaje. La causa es otra y también está medida: el prompt son **158
    tokens** y CLIP los procesa en trozos de **77**. La ficha de personaje
    empezaba en el token 35 y cruzaba la frontera, así que media ficha caía en
    el segundo trozo, donde pesa mucho menos.

Aquí se corrigen las dos cosas:

  1. **La ficha de personaje va PRIMERA**, dentro de los 77 tokens que pesan.
  2. **IPAdapter** condiciona por imagen: las demás se generan *mirando* una
     referencia, en vez de leyendo adjetivos sobre ella.

Sobre el peso: 0.75 es el punto que la comunidad reporta como equilibrio entre
mantener el sujeto y dejar que la escena cambie. Por encima de 0.9 el modelo
copia la composición entera de la referencia y todas salen iguales; por debajo
de 0.5 vuelve a perder al personaje.

El flujo se emite en formato API y se envía a `/prompt` directamente: no hace
falta pasar por `comfy run`, que espera un fichero en disco.
"""
import json
import os
import shutil
import sys
import urllib.request

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
import lote                                          # noqa: E402

COMFY = "http://127.0.0.1:8188"
ENTRADA = "/Users/maity/comfy/input"
CHECKPOINT = "juggernautXL_v9.safetensors"
PRESET = "PLUS (high strength)"
PESO = 0.75


def _api(positivo, negativo, ancho, alto, slug, referencia=None,
         peso=PESO, pasos=30, cfg=5.5, semilla=101010,
         tipo_peso="linear", inicio=0.0, fin=1.0):
    """Grafo en formato API. Con `referencia` mete IPAdapter en medio."""
    g = {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": CHECKPOINT}},
        "4": {"class_type": "CLIPTextEncode",
              "inputs": {"text": positivo, "clip": ["1", 1]}},
        "5": {"class_type": "CLIPTextEncode",
              "inputs": {"text": negativo, "clip": ["1", 1]}},
        "6": {"class_type": "EmptyLatentImage",
              "inputs": {"width": ancho, "height": alto, "batch_size": 1}},
        "7": {"class_type": "KSampler",
              "inputs": {"seed": semilla, "steps": pasos, "cfg": cfg,
                         "sampler_name": "dpmpp_2m", "scheduler": "karras",
                         "denoise": 1.0, "model": ["1", 0],
                         "positive": ["4", 0], "negative": ["5", 0],
                         "latent_image": ["6", 0]}},
        "8": {"class_type": "VAEDecode",
              "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
        "9": {"class_type": "SaveImage",
              "inputs": {"images": ["8", 0], "filename_prefix": "reels/" + slug}},
    }
    if referencia:
        g["10"] = {"class_type": "LoadImage",
                   "inputs": {"image": referencia}}
        g["11"] = {"class_type": "IPAdapterUnifiedLoader",
                   "inputs": {"model": ["1", 0], "preset": PRESET}}
        g["12"] = {"class_type": "IPAdapterAdvanced",
                   "inputs": {"model": ["11", 0], "ipadapter": ["11", 1],
                              "image": ["10", 0], "weight": peso,
                              "weight_type": tipo_peso, "combine_embeds": "concat",
                              "start_at": inicio, "end_at": fin,
                              "embeds_scaling": "V only"}}
        g["7"]["inputs"]["model"] = ["12", 0]
    return g


def poner_referencia(ruta):
    """Copia la imagen a la carpeta de entrada de ComfyUI y devuelve su nombre."""
    os.makedirs(ENTRADA, exist_ok=True)
    nombre = os.path.basename(ruta)
    shutil.copy(ruta, os.path.join(ENTRADA, nombre))
    return nombre


def encolar(grafo):
    datos = json.dumps({"prompt": grafo}).encode()
    req = urllib.request.Request(COMFY + "/prompt", data=datos,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("prompt_id")


def generar(slug, positivo, negativo, ancho=832, alto=1216, referencia=None,
            peso=PESO, **kw):
    """kw admite tipo_peso, inicio, fin, pasos, cfg, semilla.

    `tipo_peso` es el parámetro que resuelve el conflicto entre personaje y
    escena, y que yo ignoraba usando el valor por defecto:

        linear ............ transfiere identidad Y composición. Copia el plano.
        style transfer .... solo el aspecto. La escena la manda el prompt.
        composition ....... solo el encuadre. Lo contrario de lo que queremos.
        strong style transfer  ídem, más fuerte.

    `inicio` también importa: empezando en 0.2 los primeros pasos los decide el
    prompt —que es donde se fija la composición— y la referencia entra después,
    cuando ya solo queda resolver el aspecto."""
    return encolar(_api(positivo, negativo, ancho, alto, slug,
                        referencia=referencia, peso=peso, **kw))


def prompt_con_personaje_primero(personaje, escena, encuadre, aire, luz, look):
    """El orden importa: CLIP pesa más lo primero y corta en 77 tokens.

    Poniendo la ficha delante, sus rasgos caen dentro del trozo que manda. Lo
    aprendimos midiendo: con el orden anterior, la ficha empezaba en el token 35
    y se partía por la mitad."""
    return ", ".join([personaje, escena, encuadre, aire, luz, look])
