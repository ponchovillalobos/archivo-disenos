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

## FUNCIONA. Y hacen falta DOS cosas, no una

**MEDIDO** sobre cinco vistas del mismo objeto:

    SDXL, cinco tomas por prompt .....  0,731   probablemente otro objeto
    IPAdapter, capa 3 en -0,5 ........  0,768   el mismo, con variación
    Zero123-C, cinco ángulos .........  0,884   EL MISMO, SIN DUDA

El mínimo pasó de 0,638 a 0,800: ni el peor par baja de «el mismo objeto».

### 1. Arrancar ComfyUI con `--gpu-only`

Sin esa bandera las imágenes salen **negras de forma intermitente** — misma
semilla, mismos flags, mismo proceso. Medido: **2 de 5 limpias sin ella, 11 de
11 con ella**.

No es precisión. Se descartaron midiendo `--fp32-unet` (1 de 3), `--force-fp32`
(0 de 2), `--bf16-unet` (0 de 1) y `--force-upcast-attention`, que además es un
**no-op**: ComfyUI ya lo activa solo en macOS ≥ 14.5, con este comentario en su
propio código —

    # black image bug on recent versions of macOS,
    # I don't think it's ever getting fixed

El negro es **NaN**, y nace **dentro del UNet** en la primera llamada. Lo que
arregla `--gpu-only` es que los tensores dejan de ir y venir entre Metal y el
procesador entre nodos: la corrupción estaba en esos traslados.

**Trampa de diagnóstico ya pagada:** el fallo es intermitente, así que una tanda
que sale bien no prueba nada. Llegamos a concluir que «azimut 0 funciona y las
rotaciones no» — era casualidad.

### 2. Preparar la imagen al formato oficial

Del preprocesado de Zero-1-to-3 (`ldm/util.py`, `load_and_preprocess`):

    1. segmentar y poner el fondo en BLANCO PURO
    2. recortar al rectángulo del objeto
    3. redimensionar: el lado largo, 200 px como mucho
    4. centrar en un lienzo blanco de 256x256

Una fotografía de una habitación entera da un borrón: el modelo no sabe qué
parte girar. Y **no subir la resolución del nodo**: se entrenó a 256x256.

Atajo que evita necesitar un quitafondos: **generar el objeto ya sobre fondo
blanco** con SDXL —`isolated on a plain pure white background, product
photograph, soft even studio light`— y recortarlo con un umbral simple.

## La licencia, que casi nos cuesta el proyecto

Dos ficheros, nombres casi idénticos, licencias opuestas:

    stable_zero123.ckpt     objetos CC-BY-NC -> NO COMERCIAL
    stable_zero123_c.ckpt   solo CC-BY y CC0 -> Stability Community License,
                            comercial por debajo de 1 M USD/año

Usamos **el de la «c»**. El fabricante dice que rinden igual.

## Lo que NO resuelve

**No sabe dibujar texto legible.** Lo dice su propia ficha: *«el modelo no puede
renderizar texto legible»*. Para un objeto con marca o etiqueta hay que componer
el texto real encima — que es lo que hacen los profesionales.
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
