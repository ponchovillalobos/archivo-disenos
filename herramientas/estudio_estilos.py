"""Qué estilo gráfico sostiene mejor a un personaje. El cuento del elefantito.

## La pregunta

Seis imágenes, el mismo personaje, seis momentos distintos. ¿Con qué estilo se
reconoce mejor al personaje: foto realista, dibujo animado, tinta, acuarela,
cómic o vector plano?

La hipótesis, y el motivo de probarla: **el realismo debería perder**. Una foto
tiene infinitos micro-detalles —la piel, la luz, el pelo, el desenfoque— y
ninguno se repite igual dos veces. Un dibujo tiene cuatro formas y tres colores;
hay muchísimo menos que se pueda torcer. Pero es una hipótesis, y aquí se mide.

## Lo que ya se pagó por aprender, y que este módulo respeta

**1. La paleta no puede describir un LUGAR.** `dorado-selva` metía «emerald
jungle» con peso 1,3 y ganaba a la escena, que iba a peso 1,0. Cuatro prompts
distintos dieron la misma foto. Aquí el estilo describe TRAZO y COLOR, jamás un
sitio. Es la corrección más rentable del proyecto.

**2. Nada de pesos altos que compitan.** Si el encuadre lleva 1,0, el estilo no
puede llevar 1,5. Se probó subir el encuadre a 1,5 para compensar y salió peor:
la solución no es gritar más, es callar a quien estorba.

**3. La ficha de personaje va PRIMERA.** CLIP corta en 77 tokens y lo primero
pesa más. Con la ficha empezando en el token 35 se partía por la mitad.

**4. Aquí SÍ hay caras.** La regla de «cero caras y cero manos» del sistema es
para los humanos de la serie de comunicación, donde SDXL las destroza. Un
personaje de cuento necesita su cara: es la mitad de su identidad. Por eso este
estudio usa su propio negativo.

## El personaje

Un elefantito con las orejas enormes que aprende a volar — el arquetipo del
cuento, con diseño propio, no el de ninguna película. Tres anclajes concretos,
que es lo que el modelo sabe repetir:

    orejas desproporcionadas ..... silueta, se reconoce a contraluz
    bufanda amarilla anudada ..... color, el ancla más fuerte de todas
    estrella blanca en la frente .. forma + color, sobrevive a cualquier plano

Nada de «tierno» ni «entrañable»: el modelo no sabe dibujar adjetivos.
"""
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)

# ── EL PERSONAJE ────────────────────────────────────────────────────────────
# 31 tokens, contados con el tokenizador de CLIP, no a ojo.
#
# El presupuesto entero son 77 y hay que repartirlo entre tres cosas:
#     personaje 31  +  escena ~28  +  estilo ~14  =  73
#
# La primera versión gastaba 47 aquí y el prompt entero se iba a 96: diecinueve
# tokens caían fuera del trozo que manda. Cada palabra de más en la ficha es
# una palabra menos de escena, y la escena es la que cuenta el cuento.
PERSONAJE = ("the same tiny baby elephant: huge oversized floppy ears, a bright "
             "yellow scarf, a white star patch on its forehead, blue-grey skin")

# ── LAS SEIS ESCENAS ────────────────────────────────────────────────────────
# El cuento se sostiene en la ALTURA: empieza pegado al suelo y termina sobre
# los árboles. Se puede seguir sin una sola palabra.
#
# (escena para generar, descripción CORTA para medir)
ESCENAS = [
 ("alone at the edge of a green meadow at dawn, its ears dragging on the grass, "
  "other animals grazing far away",
  "a baby elephant alone in a meadow, ears dragging on the ground"),

 ("stumbling and falling forward into a muddy puddle, water splashing around it",
  "a baby elephant falling into a mud puddle"),

 ("a small brown bird perched on its back with wings spread wide open",
  "a small bird with open wings perched on a baby elephant's back"),

 ("running downhill across the meadow, ears spread wide, front feet lifting off "
  "the grass",
  "a baby elephant running downhill with ears spread wide"),

 ("flying high above the treetops, ears beating like wings, its shadow on the "
  "meadow far below",
  "a baby elephant flying in the sky high above the trees"),

 ("landing softly on the meadow at sunset, other animals gathered around "
  "looking up at it",
  "a baby elephant landing in a meadow surrounded by other animals at sunset"),
]

ESCENAS_LARGAS = [a for a, _ in ESCENAS]
ESCENAS_CORTAS = [b for _, b in ESCENAS]

# Para leer, no para medir. Las de arriba van en inglés porque CLIP mide en
# inglés y traducirlas falsearía la puntuación; éstas son las que se enseñan en
# el portal, donde un texto en inglés no le sirve a nadie.
ESCENAS_ES = [
 "Solo al borde del prado, con las orejas arrastrando por la hierba",
 "Tropieza y cae de bruces en un charco de barro",
 "Un pájaro se le posa en el lomo y abre las alas del todo",
 "Baja la cuesta corriendo, las orejas abiertas, las patas ya casi sin tocar",
 "Vuela por encima de las copas de los árboles",
 "Aterriza en el prado al atardecer, y los demás miran hacia arriba",
]

# ── LOS ESTILOS ─────────────────────────────────────────────────────────────
# Cada uno describe SOLO trazo, materia y tratamiento de color. Ninguno nombra
# un lugar, una hora ni un clima: eso le toca a la escena, y si compiten gana
# el estilo y el cuento desaparece. Es la lección que costó cinco intentos.
#
# nombre: (estilo, negativo propio del estilo)
# El positivo va apretado (12-15 tokens): es lo último del prompt y lo que menos
# sitio tiene. El NEGATIVO en cambio puede ser largo — no compite por los 77
# tokens del positivo, va por su propio codificador. Ahí es donde se separa un
# estilo de otro sin gastar presupuesto.
ESTILOS = {
 "foto": (
   "cinematic wildlife photograph, photorealistic, soft natural light",
   "illustration, drawing, cartoon, painting, anime, 3d render, flat colors, "
   "outlines, sketch"),

 "animacion3d": (
   "modern 3d animated movie style, smooth rounded shapes, big expressive eyes",
   "photograph, realistic, live action, sketch, rough lines, grainy, "
   "watercolour, ink, halftone"),

 "tinta": (
   "hand drawn ink illustration, bold black linework, cross hatching",
   "photograph, realistic, 3d render, blurry, soft focus, gradients, noise, "
   "painted, colored pencil"),

 "acuarela": (
   "soft watercolour storybook illustration, paper grain, translucent washes",
   "photograph, realistic, 3d render, hard black outlines, digital, sharp "
   "edges, vector, halftone"),

 "comic": (
   "comic book art, bold black outlines, flat cel shading, halftone dots",
   "photograph, realistic, 3d render, soft gradients, watercolour, blurry, "
   "painterly, subtle shading"),

 "vector": (
   "flat vector illustration, simple geometric shapes, limited palette",
   "photograph, realistic, 3d render, texture, grain, brush strokes, shading, "
   "detail, cross hatching"),

 # Épico ultrarrealista. El estilo más peligroso de los siete y por eso el que
 # más cuidado lleva: «épico» y «cinematográfico» arrastran en el modelo un
 # LUGAR entero —montañas, tormentas, ruinas— y ya sabemos qué pasa cuando el
 # estilo describe un sitio: se come la escena y las seis salen iguales.
 #
 # Así que aquí solo se nombra el OFICIO: la óptica, la luz de contra, el
 # grano, el etalonaje. Nada de «majestuoso», «tierras salvajes» ni «atardecer
 # dramático». La épica tiene que salir del tratamiento, no del decorado.
 "epico": (
   "epic cinematic film still, anamorphic lens, volumetric backlight, "
   "ultra detailed, rich color grading",
   "illustration, drawing, cartoon, painting, anime, 3d render, flat colors, "
   "outlines, low detail, snapshot, amateur"),
}

# ── EL NEGATIVO ─────────────────────────────────────────────────────────────
# Corto a propósito. El negativo largo del sistema (25 términos, muchos con
# peso) es para la serie de humanos y aquí hace daño: prohíbe caras y ojos, que
# es justo lo que da identidad a un personaje de cuento.
NEG = ("(human:1.4), (person:1.4), (people:1.3), (rider:1.3), (text:1.5), "
       "(letters:1.4), (words:1.4), (watermark:1.4), (signature:1.3), "
       "(two elephants:1.5), (herd:1.4), (adult elephant:1.3), "
       "(tusks:1.3), blurry, low quality, deformed, disfigured, extra limbs, "
       "bad anatomy, mutated, cropped")


def prompt(escena, estilo):
    """Ficha primero, escena después, estilo al final y sin pesos.

    El orden no es estético: CLIP lee 77 tokens con fuerza y lo primero manda.
    El estilo va último porque tiñe todo el cuadro aunque llegue tarde — y si
    fuera primero, se comería el sitio del personaje."""
    return ", ".join([PERSONAJE, escena, ESTILOS[estilo][0]])


def negativo(estilo):
    return NEG + ", " + ESTILOS[estilo][1]


def serie(estilo, prefijo=None, semilla=101010, **kw):
    """Encola las seis de un estilo. Devuelve los identificadores de la cola."""
    import flujo_referencia as fr
    pre = prefijo or ("est-" + estilo)
    ids = []
    for i, esc in enumerate(ESCENAS_LARGAS, 1):
        ids.append(fr.generar("%s-%d" % (pre, i), prompt(esc, estilo),
                              negativo(estilo), semilla=semilla, **kw))
    return ids


def medir(prefijo, carpeta="/Users/maity/comfy/output/reels"):
    """Puntúa una serie ya generada. Devuelve None si faltan imágenes."""
    import glob
    import adherencia
    rutas = []
    for i in range(1, len(ESCENAS) + 1):
        c = sorted(glob.glob(os.path.join(carpeta, "%s-%d_*.png" % (prefijo, i))))
        if not c:
            return None
        rutas.append(c[-1])          # la más reciente, si se regeneró alguna
    return adherencia.puntuar(rutas, ESCENAS_CORTAS, ficha=PERSONAJE)


if __name__ == "__main__":
    import adherencia
    r = {e: medir("est-" + e) for e in ESTILOS}
    t, _ = adherencia.tabla({k: v for k, v in r.items() if v})
    print(t or "  todavía no hay series medibles")
