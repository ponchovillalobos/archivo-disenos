"""¿Sabe el modelo rodear un objeto? Cinco tomas, un solo objeto, cero relato.

## Por qué esta prueba es mejor que la del cuento

La del elefantito mezclaba tres cosas a la vez: mantener un personaje, contar
una historia y cambiar de escena. Cuando falló, no se podía saber cuál de las
tres había fallado.

Aquí solo cambia **una variable: el ángulo de cámara**. El objeto es el mismo,
la mesa es la misma, la luz es la misma, la habitación es la misma. Si las cinco
salen bien, el modelo sabe rodear un objeto. Si salen mal, sabemos exactamente
qué es lo que no sabe hacer — y eso vale más que otra tanda ambigua.

Es además la pregunta que de verdad importa para producir: **un carrusel o un
vídeo es el mismo asunto visto desde ángulos distintos.**

## El objeto, y por qué éste

Una caja metálica sobre una mesa. Aburrido a propósito: no queremos que el
modelo se luzca, queremos ver si obedece.

Tres anclajes concretos, la misma lógica que con el elefantito:

    verde oscuro desgastado ..... color, el ancla más fuerte
    cierre de latón ............. detalle metálico, sobrevive al primer plano
    una abolladura en la esquina  asimetría — delata si el modelo la reinventa

La abolladura es la clave del experimento. Un objeto simétrico se puede fingir
desde cualquier ángulo; **una abolladura en una esquina concreta obliga al
modelo a saber dónde está esa esquina en cada toma**. Si aparece siempre en la
misma esquina real, el modelo tiene un modelo tridimensional del objeto. Si
salta de sitio, está dibujando cajas parecidas.

## Los cinco ángulos

Elegidos como los elegiría un director de fotografía, y ordenados de más lejos a
más cerca. Ninguno describe un lugar distinto: es la misma mesa siempre.
"""
import glob
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)

# ── EL OBJETO ───────────────────────────────────────────────────────────────
# 33 tokens. Cabe con holgura y deja sitio para el ángulo y el tratamiento.
OBJETO = ("a weathered dark green metal box with a brass latch and one deep "
          "dent on its front left corner, closed, on a scratched oak table")

# ── EL TRATAMIENTO ──────────────────────────────────────────────────────────
# Describe OFICIO, nunca un lugar: óptica, luz, grano. La lección más cara del
# proyecto — una paleta que nombraba «emerald jungle» se comió cuatro escenas
# de sabana seca porque iba a peso 1,3 contra una escena a peso 1,0.
LOOK = ("cinematic film still, anamorphic lens, single soft key light from the "
        "left, deep shadows, fine film grain")

# ── LOS CINCO ÁNGULOS ───────────────────────────────────────────────────────
# (ángulo para generar, descripción corta para medir)
#
# De más lejos a más cerca. La prueba dura es la abolladura: está declarada en
# la esquina frontal izquierda, y debe aparecer ahí en las cinco.
ANGULOS = [
 ("wide establishing shot from across the room, the box small and centred on "
  "the table",
  "a wide shot of a small box on a table across a room"),

 ("low angle shot from below the table edge, looking up at the box against the "
  "ceiling",
  "a low angle shot looking up at a box from below the table"),

 ("overhead shot looking straight down at the box from directly above",
  "a top down overhead shot of a box on a table"),

 ("three quarter medium shot from the right side, raking light across the metal",
  "a three quarter side view of a metal box on a table"),

 ("extreme close up on the brass latch, very shallow depth of field",
  "an extreme close up of a brass latch on a metal box"),
]

ANGULOS_LARGOS = [a for a, _ in ANGULOS]
ANGULOS_CORTOS = [b for _, b in ANGULOS]

ANGULOS_ES = [
 "Plano general desde el otro lado de la sala",
 "Contrapicado desde debajo del borde de la mesa",
 "Cenital, mirando directamente hacia abajo",
 "Tres cuartos desde la derecha, luz rasante",
 "Primerísimo plano del cierre de latón",
]

# Corto y específico, como recomienda el autor de Juggernaut. El negativo largo
# y genérico de la serie de comunicación aquí no pinta nada: prohíbe caras y
# manos, y esto es un bodegón.
NEG = ("(two boxes:1.4), (multiple boxes:1.4), (people:1.3), (hands:1.3), "
       "(text:1.4), (watermark:1.3), blurry, low quality, deformed, "
       "cluttered, messy background")


def prompt(angulo):
    """Objeto primero, ángulo después, tratamiento al final.

    CLIP lleva máscara causal —cada token solo ve los anteriores— así que lo
    primero se acumula en todo lo demás. Y el vector global que SDXL usa como
    condicionamiento aparte sale SOLO del primer bloque de 77 tokens."""
    return ", ".join([OBJETO, angulo, LOOK])


def generar(prefijo="caja", semilla=101010, **kw):
    """Encola las cinco tomas. kw admite pasos, cfg, referencia, peso…"""
    import flujo_referencia as fr
    return [fr.generar("%s-%d" % (prefijo, i), prompt(a), NEG,
                       ancho=1216, alto=832, semilla=semilla, **kw)
            for i, a in enumerate(ANGULOS_LARGOS, 1)]


def medir(prefijo="caja", carpeta="/Users/maity/comfy/output/reels"):
    """Aquí el parecido alto SÍ es un mérito, al revés que en el cuento.

    En el cuento seis escenas distintas debían parecerse poco. Aquí es el mismo
    objeto en la misma mesa: si el parecido se desploma, es que el modelo cambió
    de caja. Y el margen sigue teniendo que ser alto, porque los cinco ángulos
    han de ser reconociblemente distintos."""
    import adherencia
    rutas = []
    for i in range(1, len(ANGULOS) + 1):
        c = sorted(glob.glob(os.path.join(carpeta, "%s-%d_*.png" % (prefijo, i))))
        if not c:
            return None
        rutas.append(c[-1])
    return adherencia.puntuar(rutas, ANGULOS_CORTOS, ficha=OBJETO)


if __name__ == "__main__":
    from transformers import CLIPTokenizer
    tk = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
    peor = max(len(tk(prompt(a))["input_ids"]) for a in ANGULOS_LARGOS)
    print("  peor caso: %d tokens de 77 -> %s"
          % (peor, "cabe" if peor <= 77 else "SE PASA"))
    for r in generar():
        print("  encolado", r)
