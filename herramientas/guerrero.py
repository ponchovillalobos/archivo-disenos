"""El guerrero que descubre su poder interior. Siete láminas, en objetos.

## Lo que salió mal la primera vez, y por qué se rehízo entero

La primera versión inventó un personaje —silueta de guerrero con capa roja,
escudo y lanza— y lo dibujó con el flujo de calidad. Salieron siete imágenes
bonitas, con el personaje idéntico y **la historia inexistente**: la lámina que
pedía «de rodillas» salió de pie, y la que pedía la armadura en el suelo salió
con la armadura puesta.

El error de fondo no fue el prompt: fue **inventar en vez de leer el recetario**.
Hay 184 láminas espartanas aprobadas y publicadas, cada una con su receta dentro
del PNG, y no las miré.

## Lo que de verdad hace que aquellas funcionen

Al leerlas aparece algo que no se ve en una sola imagen:

> **El sujeto casi nunca es una persona. Son OBJETOS.** Un escudo apoyado contra
> un muro, una lanza clavada en la arena, unas huellas que vuelven por el mismo
> camino. El guerrero está implícito.

Por eso funcionan y por eso parecen cine. No hay cuerpo, no hay cara, no hay
problema de consistencia — el que llevamos días peleando **no existe** en este
idioma visual. Y el significado lo lleva el objeto, que es más fuerte que una
pose.

La fórmula exacta, sacada de las 184:

    escena      "epic cinematic film still of " + el objeto y lo que le pasa
    encuadre    IDÉNTICO en las 184 (ver ENCUADRE abajo)
    aire y luz  un ánimo de paletas.py
    tratamiento una paleta con pesos
    flujo       RÁPIDO: 8 pasos, CFG 1.0, euler/sgm_uniform, LoRA Lightning

Nótese `epic cinematic film still of`. Hoy documentamos que `epic` arrastra
decorado de fantasía — **y aquí no lo hace**, porque el encuadre fija el mundo
(«ancient Sparta, bronze and stone») y no deja hueco a la montaña genérica. La
regla sigue siendo válida: `epic` es peligroso **suelto**; anclado a un mundo
concreto, no.

## La historia, contada en objetos

La idea no cambia —**la armadura que creía que lo protegía era lo que lo
hundía**— pero ahora se cuenta con siete objetos y no con siete poses.
"""
import glob
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)

SALIDA = "/Users/maity/comfy/output/reels"

# Palabra por palabra de las 184 láminas aprobadas. No se toca.
ENCUADRE = ("wide cinematic shot, ancient Sparta, bronze and stone, no people "
            "or one tiny distant silhouette seen from behind, no faces, "
            "no hands, vast space")

PALETA = "indigo-ambar"     # sombra fría y UNA luz cálida: el par del cine

# ── LAS SIETE ───────────────────────────────────────────────────────────────
# (escena, objeto, corta para medir, titular)
LAMINAS = [
 ("a heavy bronze shield lying half sunk in the dust, too heavy to have been "
  "carried further",
  "a heavy bronze shield sunk in dust",
  "a heavy bronze shield abandoned in the dust",
  "Creíste que el peso era la prueba."),

 ("a narrow crack of light entering a dark stone chamber through a doorway, "
  "falling across the empty floor",
  "a crack of light in a dark stone room",
  "a shaft of light entering a dark stone chamber",
  "Nadie viene a levantarte."),

 ("a single spear standing upright against a wall, and its shadow on the stone "
  "far longer and taller than the spear itself",
  "a spear and its very long shadow",
  "a spear casting a shadow much longer than itself",
  "Lo primero que crece es la sombra."),

 ("a bronze breastplate lying closed on the stone floor with light escaping "
  "from the seams between its plates",
  "light escaping from the seams of a breastplate",
  "a breastplate on the floor glowing from within",
  "Y entonces algo se enciende dentro."),

 ("an open empty bronze breastplate on the ground and a set of footprints "
  "leading away from it, lighter than the ones arriving",
  "an empty breastplate and footprints leading away",
  "an open empty armour on the ground with footprints leaving",
  "La armadura no te protegía. Te hundía."),

 ("a vast empty stone hall flooded with light coming from its centre, the "
  "darkness pushed back against the far walls",
  "a stone hall flooded with light from its centre",
  "a huge stone hall filled with light from the middle",
  "El poder no llegó. Estaba tapado."),

 ("a stone road opening onto an immense plain at dawn, a single set of "
  "footprints going away and not returning",
  "footprints on a stone road going away at dawn",
  "a road at dawn with footprints leading away into a plain",
  "Y ahora pesa menos, y llega más lejos."),
]

ESCENAS = [a for a, _, _, _ in LAMINAS]
OBJETOS = [b for _, b, _, _ in LAMINAS]
CORTAS = [c for _, _, c, _ in LAMINAS]
TITULARES = [d for _, _, _, d in LAMINAS]


def generar(prefijo="gob", ancho=768, alto=1344, semilla=101010):
    """El flujo RÁPIDO, que es con el que se hicieron las 184 aprobadas.

    768×1344 y no 720×1280: los workflows ya lo traían bien y `lote.flujo` lo
    pisaba con un valor que no es múltiplo de 64 ni cubo de SDXL. Corregido hoy.
    """
    import lote
    from paletas import ANIMOS
    aire, luz = ANIMOS["amanecer"]
    rutas = []
    for i, esc in enumerate(ESCENAS, 1):
        rutas.append(lote.flujo(
            "%s-%d" % (prefijo, i),
            "epic cinematic film still of " + esc,
            OBJETOS[i - 1], ENCUADRE, aire, luz,
            ancho=ancho, alto=alto, paleta=PALETA, semilla=semilla))
    return lote.encolar(rutas)


# ── LA SELECCIÓN FINAL ──────────────────────────────────────────────────────
# Auditadas a ojo una por una, que es la regla. El prefijo dice de qué tanda
# salió cada una: se regeneró la LÁMINA, nunca el lote.
#
# Y el guerrero sí aparece —en tres de las siete— porque el encuadre aprobado lo
# permite: «no people **or one tiny distant silhouette seen from behind**».
# Aparece donde su presencia ES el sentido: cuando está caído (2), cuando es la
# fuente de la luz (6) y cuando se marcha (7). En las otras cuatro el objeto
# cuenta mejor que una pose.
ELEGIDAS = {
 1: ("gob",  "el escudo hundido en el polvo"),
 2: ("gob2", "el guerrero en el paso de piedra"),      # ← aparece
 3: ("gob",  "la lanza y su sombra, más larga que ella"),
 4: ("gob3", "la coraza que brilla por las juntas"),
 5: ("gob",  "las huellas que se alejan"),
 6: ("gob3", "la sala de luz, y él pequeño en el centro"),   # ← aparece
 7: ("gob2", "el camino al amanecer"),                 # ← aparece
}


def rutas(prefijo=None):
    """Sin argumento, devuelve la SELECCIÓN FINAL auditada."""
    out = []
    for i in range(1, len(LAMINAS) + 1):
        pre = prefijo or ELEGIDAS[i][0]
        c = sorted(glob.glob(os.path.join(SALIDA, "%s-%d_*.png" % (pre, i))))
        if not c:
            return None
        out.append(c[-1])
    return out


def medir(prefijo=None):
    """Aquí NO se mide fidelidad de personaje: no hay personaje. Lo que importa
    es que las siete sean escenas distintas y que se reconozca cada una."""
    import adherencia
    r = rutas(prefijo)
    return adherencia.puntuar(r, CORTAS) if r else None


if __name__ == "__main__":
    for i, t in enumerate(TITULARES, 1):
        print("  %d. %s" % (i, t))
    print()
    print("  encolando…")
    for n, rc in generar():
        print("   %s %s" % (n, "ok" if rc == 0 else "FALLO"))
