"""Girar un objeto de verdad: Stable Zero123-C.

## Por qué esto no es «otro intento más»

Todo lo anterior le pedía a SDXL que **dibujara** el mismo objeto desde otro
ángulo, y SDXL no puede: no tiene representación tridimensional. Está medido —
cinco tomas dieron cinco cajas distintas, parecido 0,731, y la abolladura
declarada no apareció en ninguna.

Zero123 es otra cosa. No genera desde texto: **no hay prompt en este flujo.**
Toma una imagen de un objeto y produce la vista de ESE objeto desde el ángulo
que le pidas, porque está entrenado con objetos 3D renderizados girando. Le das
un azimut y una elevación en grados, y devuelve esa cara.

La diferencia es la que hay entre pedirle a alguien que dibuje «otra caja
parecida» y pedirle que **gire la que ya tiene delante**.

## La licencia, que casi nos cuesta el proyecto

El repositorio tiene DOS ficheros con nombres casi idénticos y licencias
opuestas:

    stable_zero123.ckpt     entrenado con objetos CC-BY-NC -> NO COMERCIAL
    stable_zero123_c.ckpt   solo CC-BY y CC0 -> Stability Community License,
                            comercial por debajo de 1 M USD/año de facturación

Usamos **el de la «c»**. El fabricante dice que rinden igual. Bajar «el que se
llama bien» habría dejado el proyecto con un modelo que no podemos publicar.

## Limitación conocida antes de probar

Zero123 se entrenó con objetos **recortados, centrados y sobre fondo liso**
(renders de Objaverse). Nuestras imágenes son fotografías de una habitación
entera. Es muy posible que eso lo estropee: el modelo no sabe qué parte de la
imagen es «el objeto» que debe girar.

Se prueba igual con la imagen cruda, porque saberlo medido vale más que
suponerlo. Si falla, el siguiente paso es recortar el objeto y ponerlo sobre
fondo liso — no cambiar de modelo.
"""
import json
import os
import sys
import urllib.request

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
import flujo_referencia as fr                         # noqa: E402

MODELO = "stable_zero123_c.ckpt"
COMFY = "http://127.0.0.1:8188"

# Zero123 se entrenó a 256×256. Subirlo no da más detalle, da artefactos.
LADO = 256


def _api(referencia, slug, azimut, elevacion=0.0, pasos=20, cfg=3.0,
         semilla=101010):
    """El grafo entero. Fíjate en lo que NO hay: ni CLIPTextEncode, ni prompt,
    ni negativo. El condicionamiento sale de la IMAGEN y de dos ángulos."""
    return {
        "1": {"class_type": "ImageOnlyCheckpointLoader",
              "inputs": {"ckpt_name": MODELO}},
        "2": {"class_type": "LoadImage",
              "inputs": {"image": referencia}},
        "3": {"class_type": "StableZero123_Conditioning",
              "inputs": {"clip_vision": ["1", 1], "init_image": ["2", 0],
                         "vae": ["1", 2], "width": LADO, "height": LADO,
                         "batch_size": 1,
                         "elevation": elevacion, "azimuth": azimut}},
        "4": {"class_type": "KSampler",
              "inputs": {"seed": semilla, "steps": pasos, "cfg": cfg,
                         "sampler_name": "euler", "scheduler": "sgm_uniform",
                         "denoise": 1.0, "model": ["1", 0],
                         "positive": ["3", 0], "negative": ["3", 1],
                         "latent_image": ["3", 2]}},
        "5": {"class_type": "VAEDecode",
              "inputs": {"samples": ["4", 0], "vae": ["1", 2]}},
        "6": {"class_type": "SaveImage",
              "inputs": {"images": ["5", 0], "filename_prefix": "reels/" + slug}},
    }


# Azimut = giro alrededor del objeto. Elevación = altura de la cámara.
# Estos cinco cubren una vuelta útil sin repetirse.
VISTAS = [
    ("00", 0.0, 0.0),        # la vista de partida, como control
    ("45", 45.0, 0.0),
    ("90", 90.0, 0.0),
    ("180", 180.0, 0.0),     # la cara opuesta: la prueba más dura
    ("alto", 30.0, 45.0),    # tres cuartos desde arriba
]


def generar(origen, prefijo="z123", **kw):
    """origen: ruta a un PNG. Devuelve los identificadores de la cola."""
    ref = fr.poner_referencia(origen)
    ids = []
    for nombre, az, el in VISTAS:
        g = _api(ref, "%s-%s" % (prefijo, nombre), az, el, **kw)
        datos = json.dumps({"prompt": g}).encode()
        req = urllib.request.Request(COMFY + "/prompt", data=datos,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            ids.append(json.load(r).get("prompt_id"))
    return ids


if __name__ == "__main__":
    origen = (sys.argv[1] if len(sys.argv) > 1
              else "/Users/maity/comfy/output/reels/caja-1_00001_.png")
    print("  girando:", os.path.basename(origen))
    for (n, az, el), i in zip(VISTAS, generar(origen)):
        print("   azimut %-4s elevación %-4s -> %s" % (az, el, i))
