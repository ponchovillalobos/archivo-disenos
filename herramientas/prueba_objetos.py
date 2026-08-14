"""Tres objetos, cinco vistas cada uno, con todas las recomendaciones aplicadas.

## Por qué estos tres y no otros

Elegidos para que **puedan fallar de forma visible**. Un objeto simétrico se
puede fingir desde cualquier ángulo; estos no.

  **tetera** — el objeto canónico de las pruebas 3D, y por un motivo: el pico y
  el asa están en lados OPUESTOS. Si el modelo gira de verdad, al pasar de 0° a
  180° el pico y el asa **intercambian su lado**. Si solo dibuja teteras
  parecidas, no lo harán. Es falsable de un vistazo, sin métrica.

  **cámara analógica** — asimetría mecánica: objetivo redondo delante, palanca de
  arrastre a un lado, zapata arriba. Prueba si el modelo mantiene piezas
  pequeñas en su sitio al rodearlo.

  **bota de cuero** — forma orgánica, la más difícil de las tres. Puntera, talón
  y caña definen una orientación clara, y no hay simetría que salve al modelo.

## Las recomendaciones aplicadas

**En el prompt de generación** (`herramientas/CONFIGURACIONES.md` §3, §9):

  · fuera `masterpiece`, `8k`, `award winning` — en SDXL la estética y la
    resolución son entradas numéricas propias del condicionamiento, no palabras.
    Escribirlas gasta tokens de los 75 y no pide nada.
  · fuera `octane render` y `unreal engine` — empujan ACTIVAMENTE hacia render
    3D en un prompt que pide fotografía.
  · el MEDIO va primero, siguiendo la gramática de las plantillas oficiales de
    Stability: `<medio> <sujeto> . <modificadores>`.
  · negativo corto que veta el MEDIO equivocado, no un inventario de anatomía.
    Es lo que hacen los presets oficiales y lo que pide el autor del modelo.
  · fondo blanco desde el principio: así no hace falta segmentar después.

**En el giro** (`herramientas/vistas.py`):

  · ComfyUI con `--gpu-only`, o salen negras de forma intermitente.
  · entrada al formato oficial: blanco puro, recorte al objeto, lado largo
    ≤200 px, centrado en 256×256.

## Lo que se mide

`parecido` entre las cinco vistas. Aquí, al revés que en el cuento, **alto es
bueno**: es el mismo objeto y debe parecerse a sí mismo. La escala está en
`coherencia.py`; por debajo de 0,75 es «probablemente otro objeto».

## RESULTADOS MEDIDOS

    objeto     parecido   veredicto de la métrica
    bota        0,860     el mismo, sin duda
    tetera      0,726     probablemente otro
    cámara      0,538     objetos DISTINTOS

Cada vista contra la original de partida:

               0°     45°    90°    180°   alto
    tetera    0,836  0,750  0,518  0,752  0,587
    cámara    0,735  0,611  0,289  0,353  0,559
    bota      0,780  0,719  0,721  0,637  0,689

### Lo que se ve, y que la métrica no dice

**La prueba dura la pasa.** El pico de la tetera está a la izquierda en la
original y aparece **a la derecha a 180°**, con el mismo esmalte, la misma asa de
madera y el mismo pomo. Es una rotación real, no otra tetera parecida.

**Los 90° rompen en los tres.** Es el ángulo más débil sin excepción: la tetera
pierde el pico y convierte su asa en un arco arquitectónico; la cámara se
degrada hasta un cilindro negro con una espiral naranja, irreconocible.

**La complejidad del objeto manda.** La bota —forma sólida, orgánica, sin piezas
pequeñas— aguanta los cinco ángulos. La cámara —mecánica, con piezas finas y
texto— se desintegra. La tetera queda en medio.

### El aviso más importante: la métrica premió un fallo

**La bota puntuó 0,860, «el mismo sin duda», y a 180° está mal**: generó DOS
botas, un par, en vez de una bota girada. Como el cuero, los cordones y la suela
son correctos, el parecido sale altísimo.

Es la razón de la regla dura de la casa: **se audita cada imagen**. Con la
métrica sola habríamos publicado un par de botas como si fuera una rotación.

### Regla práctica que sale de aquí

    formas sólidas y simples ....  sirve
    45° y 180° ..................  los ángulos fiables
    90° .........................  el que rompe — evitarlo o regenerarlo
    objetos mecánicos con piezas
    finas o con texto ...........  no sirve
"""
import glob
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)

SALIDA = "/Users/maity/comfy/output/reels"
ENTRADA = "/Users/maity/comfy/input"

# El medio delante, el sujeto en medio, los modificadores al final.
MEDIO = "product photograph of"
COLA = ("isolated on a plain pure white background, soft even studio light, "
        "sharp focus, fine detail")

# Corto, y veta el MEDIO equivocado. Nada de inventarios de anatomía.
NEG = ("illustration, drawing, painting, cartoon, anime, 3d render, cgi, "
       "octane render, sketch, background, room, table, floor, wall, scenery, "
       "two objects, multiple objects, people, hands, text, watermark, "
       "blurry, low quality, deformed, cropped")

OBJETOS = {
 # (descripción, por qué es una prueba dura)
 "tetera": (
   "a round ceramic teapot in deep teal glaze with a curved spout on one side, "
   "a wooden handle on the opposite side and a small brass knob on the lid",
   "el pico y el asa están opuestos: al girar 180° deben intercambiar lado"),

 "camara": (
   "a vintage analog film camera with a black leather body, a chrome lens "
   "barrel at the front, a winding lever on the right and a hot shoe on top",
   "asimetría mecánica: palanca a un lado, objetivo delante, zapata arriba"),

 "bota": (
   "a worn brown leather ankle boot with visible stitching, five pairs of brass "
   "eyelets, dark laces and a thick rubber sole",
   "forma orgánica: puntera, talón y caña definen la orientación"),
}


def prompt(descripcion):
    """El medio delante, el sujeto en medio, los modificadores al final.

    Acepta una clave de OBJETOS o una descripción libre, para que esto sirva
    como herramienta y no solo como el ensayo de tres objetos que fue."""
    d = OBJETOS[descripcion][0] if descripcion in OBJETOS else descripcion
    return "%s %s, %s" % (MEDIO, d, COLA)


def base(slug, descripcion, semilla=101010, lado=1024):
    """UNA imagen de partida sobre fondo blanco, lista para girar.

    Cuadrada a propósito: Zero123 trabaja con un lienzo cuadrado, y partir de
    uno cuadrado evita que `preparar` tenga que descartar nada."""
    import flujo_referencia as fr
    return fr.generar("obj-" + slug, prompt(descripcion), NEG,
                      ancho=lado, alto=lado, semilla=semilla)


def generar_base(semilla=101010, ancho=1024, alto=1024):
    """Los tres objetos del ensayo."""
    import flujo_referencia as fr
    return {k: fr.generar("obj-" + k, prompt(k), NEG, ancho=ancho, alto=alto,
                          semilla=semilla)
            for k in OBJETOS}


def preparar(clave, umbral=235, lado_objeto=200, lienzo=256):
    """Al formato exacto que pide Zero123. Devuelve el nombre del fichero.

    El umbral funciona porque generamos sobre blanco a propósito: no hace falta
    un segmentador. Es el atajo que evita descargar 176 MB de quitafondos."""
    import numpy as np
    from PIL import Image
    c = sorted(glob.glob(os.path.join(SALIDA, "obj-%s_*.png" % clave)))
    if not c:
        return None
    a = np.array(Image.open(c[-1]).convert("RGB"))
    fondo = (a > umbral).all(axis=2)
    ys, xs = np.where(~fondo)
    if not len(xs):
        return None
    a[fondo] = 255
    ob = Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    ob.thumbnail((lado_objeto, lado_objeto), Image.LANCZOS)
    lz = Image.new("RGB", (lienzo, lienzo), (255, 255, 255))
    lz.paste(ob, ((lienzo - ob.width) // 2, (lienzo - ob.height) // 2))
    nombre = "z-%s.png" % clave
    lz.save(os.path.join(ENTRADA, nombre))
    return nombre


def girar(clave):
    import vistas
    ref = preparar(clave)
    if not ref:
        return None
    ids = []
    for nombre, az, el in vistas.VISTAS:
        import json
        import urllib.request
        g = vistas._api(ref, "v-%s-%s" % (clave, nombre), az, el)
        d = json.dumps({"prompt": g}).encode()
        r = urllib.request.Request("http://127.0.0.1:8188/prompt", data=d,
                                   headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(r, timeout=30) as resp:
            ids.append(json.load(resp).get("prompt_id"))
    return ids


def medir(clave):
    import coherencia
    import vistas
    rutas = []
    for nombre, _, _ in vistas.VISTAS:
        c = sorted(glob.glob(os.path.join(SALIDA, "v-%s-%s_*.png" % (clave, nombre))))
        if not c:
            return None
        rutas.append(c[-1])
    return coherencia.coherencia(rutas)


if __name__ == "__main__":
    import coherencia
    print("  %-10s parecido  mínimo   veredicto" % "objeto")
    for k in OBJETOS:
        r = medir(k)
        if r:
            print("  %-10s %.3f     %.3f   %s"
                  % (k, r["media"], r["minimo"], coherencia.veredicto(r["media"])))
        else:
            print("  %-10s pendiente" % k)
