"""El guerrero que descubre su poder. Siete láminas, con su texto.

## La idea

No es «entrena y se hace fuerte». Es: **la armadura que creía que lo protegía
era lo que lo hundía.** El poder no llega de fuera — se destapa quitando peso.

Por eso el giro no es una batalla, es el momento en que **suelta el escudo**. Y
por eso la última lámina lo devuelve pequeño, como la primera: lo que cambió no
es su tamaño.

## Sobre qué se construye

La receta verificada de `RECETA-ESPARTANO.md`, que reproduce píxel a píxel la
imagen de referencia del usuario. Configuración congelada:

    juggernautXL_v9 + LoRA Lightning · 768×1344 · 8 pasos · CFG 1.0
    euler / sgm_uniform

Y las tres cosas que la hacen funcionar, que se respetan aquí:

  1. **El guerrero es el sujeto**, de cuerpo entero. No un objeto, no una
     silueta lejana.
  2. **El tratamiento es una hoja de cámara**, no una paleta: etalonaje,
     claroscuro, óptica, película, grano, texturas — y la **composición
     escrita**, que es la línea que nadie documenta.
  3. **El negativo son diez términos**, sin vetos de ánimo ni de color.

## El escudo: el fallo que quedaba

En la tanda anterior salía **de cometa medieval** justo en la lámina donde es el
protagonista. La causa está medida: `shield` tiene en CLIP un centroide visual
medieval —miles de fotos de armas medievales y portadas de fantasía— y dos
palabras de contexto no mueven un centroide.

El arreglo no es pedir «escudo espartano». Es que **la palabra que carga el peso
sea la FORMA**:

    round bowl-shaped bronze shield

más el veto explícito de las formas rivales. `aspis` no sirve: es token débil y
además colisiona con un género de víbora. `hoplon` es históricamente falso.

## Cara y manos

No se vetan: **se tapan con el atrezo**. El casco corintio cubre la cara por
construcción, y el escudo tapa la mano que sujeta el arma. Es lo que permite
poner al personaje en el centro del cuadro en vez de esconderlo al fondo — y es
la diferencia entre estas imágenes y las que se hicieron vetando.
"""
import glob
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
PROY = os.path.dirname(S)

SALIDA = "/Users/maity/comfy/output/reels"

# ── EL PERSONAJE, con la forma del escudo por delante ───────────────────────
HEROE = ("a lone Spartan hoplite warrior, bronze Corinthian helmet with tall "
         "crimson horsehair crest, large round bowl-shaped bronze shield, "
         "torn dark red wool cloak")

OBJETO = "large round bowl-shaped bronze shield and long plain ash spear"

ENCUADRE = ("bronze cuirass and bronze greaves, "
            "low camera angle looking up at him")

AIRE = "heavy grey rain"
LUZ = "wet bronze reflecting a dull sky, lightning on the horizon"

# La hoja de cámara. La última línea coloca al personaje: no se deja al azar.
TRATAMIENTO = ("teal and orange color grading, high contrast chiaroscuro "
               "lighting, anamorphic lens flare, shallow depth of field, "
               "35mm anamorphic film, heavy film grain, hyper detailed metal "
               "textures, vertical composition with the warrior in the lower "
               "third and dramatic sky filling the upper half")

# Diez términos de la receta original + el veto de forma del escudo, que es lo
# único que se añade y por un motivo medido.
NEG = ("blurry, low quality, deformed hands, extra fingers, modern clothing, "
       "watermark, text, logo, cartoon, plastic skin, flat lighting, "
       "kite shield, heater shield, pointed shield, teardrop shield, "
       "heraldry, coat of arms, medieval, knight")

# ── LAS SIETE ───────────────────────────────────────────────────────────────
# (escena, titular)
LAMINAS = [
 ("kneeling alone on cracked earth under an immense empty sky, head down, "
  "seen from behind",
  "Creíste que el peso era la prueba."),

 ("standing in a narrow stone passage, one shaft of light falling on his "
  "shoulders, seen from behind",
  "Nadie viene a levantarte."),

 ("standing against a sunlit stone wall, his shadow thrown across it far "
  "taller than he is",
  "Lo primero que crece es la sombra."),

 ("hot golden light bursting out through the seams of his bronze cuirass, "
  "glowing from inside his chest, dark storm behind him",
  "Y entonces algo se enciende dentro."),

 ("his round bronze shield and cuirass abandoned on the rocks in the "
  "foreground, and far behind them he walks away carrying nothing",
  "La armadura no te protegía. Te hundía."),

 ("standing at the centre of a vast stone hall, light pouring out of him and "
  "pushing the darkness to the walls",
  "El poder no llegó. Estaba tapado."),

 ("walking away small across an immense plain at dawn, seen from behind, "
  "establishing shot",
  "Y ahora pesa menos, y llega más lejos."),
]

ESCENAS = [a for a, _ in LAMINAS]
TITULARES = [b for _, b in LAMINAS]

# teal-naranja: es el etalonaje de la receta, y el acento tipográfico sale de
# la misma paleta para que texto e imagen concuerden.
PALETA = "teal-naranja"


def generar(prefijo="gu", semillas=(101010, 202020, 303030)):
    """Varias semillas por lámina: se elige la mejor auditando, no la primera.

    Es lo que separó las cuatro láminas que salieron a la primera de las dos que
    hubo que rehacer: con una sola muestra no hay de dónde elegir."""
    import lote
    rutas = []
    for i, esc in enumerate(ESCENAS, 1):
        for j, m in enumerate(semillas):
            slug = "%s-%d-%d" % (prefijo, i, j)
            if glob.glob(os.path.join(SALIDA, slug + "_*.png")):
                continue
            rutas.append(lote.flujo(
                slug, "epic cinematic film still of " + HEROE + " " + esc,
                OBJETO, ENCUADRE, AIRE, LUZ, ancho=768, alto=1344,
                look=TRATAMIENTO, negativo=NEG, semilla=m))
    return lote.encolar(rutas) if rutas else []


def componer(elegidas, serie="espartano"):
    """elegidas: {n_lamina: slug}. Compone la lámina con su titular."""
    import shutil
    import estudio2
    from paletas import PALETAS
    fon = os.path.join(PROY, "out", serie, "_fondos")
    out = os.path.join(PROY, "out", serie)
    os.makedirs(fon, exist_ok=True)
    ls = []
    for i, t in enumerate(TITULARES, 1):
        slug = elegidas.get(i)
        c = sorted(glob.glob(os.path.join(SALIDA, "%s_*.png" % slug))) if slug else []
        if not c:
            print("   ! falta la lámina %d" % i)
            continue
        n = "f%02d.png" % i
        shutil.copy(c[-1], os.path.join(fon, n))
        ls.append({"fondo": n, "kicker": "%d DE 7" % i, "titular": t})
    return estudio2.componer(serie, ls, PALETAS[PALETA][0], fon, out)


if __name__ == "__main__":
    for i, t in enumerate(TITULARES, 1):
        print("  %d. %s" % (i, t))
    print()
    for n, rc in generar():
        print("   %s %s" % (n, "ok" if rc == 0 else "FALLO"))
