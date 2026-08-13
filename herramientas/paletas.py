"""Paletas de color con VETO.

Lección medida: a CFG 1.0 (que es lo que impone el LoRA Lightning) el modelo casi
no obedece una instrucción de color en positivo. De ocho paletas probadas, cinco
salieron en la franja azul-cian de 156-204° porque la ESCENA mandaba, no la paleta.

Por eso cada paleta lleva tres cosas y no una:
  acento → color de la tipografía, para que el texto y la imagen concuerden
  look   → la instrucción en positivo, CON PESOS
  veto   → los colores que hay que meter en el negativo

El veto es la pieza que faltaba: es más fácil quitarle al modelo el azul por
defecto que convencerle de poner amarillo.
"""

# nombre: (acento, look, veto)
PALETAS = {
 "teal-naranja": ("#e08a3c",
   "(cinematic teal and orange color grade:1.4), (turquoise shadows:1.3), "
   "(warm amber highlights:1.3), high contrast, 35mm grain",
   "green, magenta, purple"),

 "indigo-ambar": ("#e0a23c",
   "(deep indigo shadows:1.4), (one warm amber key light:1.4), (golden glow:1.2), "
   "strong contrast, anamorphic flare",
   "green, teal, magenta"),

 "magenta-cian": ("#d84f9e",
   "(neon magenta and cyan:1.5), (hot pink glow:1.4), (saturated night palette:1.3), "
   "wet reflective surfaces, deep blacks",
   "green, yellow, orange, sepia"),

 "oliva": ("#9fbf5a",
   "(olive green and khaki color grade:1.5), (moss green tones:1.3), "
   "earthy desaturated palette, soft contrast, 16mm grain",
   "blue, cyan, teal, magenta, purple"),

 "sepia": ("#d9a05b",
   "(warm sepia and bronze grade:1.4), (aged photograph tones:1.3), "
   "(golden dust in the air:1.2), gentle contrast",
   "blue, cyan, teal, green, magenta"),

 "rojo-carbon": ("#d8353d",
   "(deep charcoal blacks:1.3), (one saturated crimson red accent:1.5), "
   "(scarlet glow:1.3), everything else near monochrome, hard contrast",
   "blue, cyan, teal, green, yellow"),

 "purpura": ("#a98fd4",
   "(violet and deep purple:1.6), (lilac light:1.4), (magenta twilight sky:1.3), "
   "saturated night grade, cinematic haze",
   "blue, cyan, teal, green, yellow, orange"),

 "azul-hielo": ("#7fc4e0",
   "(icy pale blue and white grade:1.4), (cold winter light:1.3), very high key, "
   "clean contrast",
   "orange, red, yellow, green, magenta"),

 "dorado-selva": ("#c9a227",
   "(golden light through deep green foliage:1.5), (emerald jungle:1.3), "
   "(warm sun shafts:1.3), rich saturated contrast",
   "blue, cyan, magenta, purple, grey"),

 "esmeralda": ("#4fc4a0",
   "(emerald green and deep teal:1.5), (saturated jade water tones:1.3), "
   "cool highlights, cinematic depth",
   "orange, red, yellow, magenta, purple"),

 "cobre": ("#c47a4a",
   "(burnished copper and warm rust:1.5), (orange oxidised metal:1.3), "
   "cool grey stone around it, saturated metal highlights",
   "blue, cyan, green, magenta, purple"),

 "vino": ("#b8563c",
   "(deep wine red and burnt orange:1.5), (candlelit warm darkness:1.3), "
   "(maroon shadows:1.3), heavy shadows",
   "blue, cyan, teal, green, magenta"),

 "menta": ("#7fd4c0",
   "(cool mint green and graphite:1.5), (pale seafoam tones:1.3), "
   "clean modern palette, soft highlights",
   "orange, red, yellow, magenta, purple, blue"),

 "mostaza": ("#d4a017",
   "(mustard yellow and petrol blue:1.6), (ochre yellow light:1.4), "
   "(golden wheat tones:1.3), bold retro film stock, strong contrast",
   "green, magenta, purple, grey, monochrome"),

 "ladrillo": ("#c85a3c",
   "(terracotta and burnt sienna:1.5), (warm brick red walls:1.4), "
   "(clay orange tones:1.3), dry warm light",
   "blue, cyan, teal, green, magenta, purple"),

 "noir": ("#e6e6e6",
   "black and white film noir, extreme contrast, deep black shadows",
   ""),
}

# lavanda salió de la rotación: un pastel violeta no lo acierta ni el prompt
# (dio 14°, naranja) ni el grado posterior (330°, rosa). Mejor 15 que funcionan.
_SORTEO = [k for k in PALETAS if k != "noir"]


def paleta_de(tema):
    """Estable por tema: el mismo tema da siempre el mismo color y se puede
    regenerar idéntico. Parece aleatorio y es reproducible."""
    import hashlib
    h = int(hashlib.sha1(tema.encode()).hexdigest(), 16)
    n = _SORTEO[h % len(_SORTEO)]
    return (n,) + PALETAS[n]


# ---------------------------------------------------------------------------
# ÁNIMOS
#
# Hasta ahora todo salía grave, y no era culpa del color: el prompt base pedía
# «niebla espesa» y «una luz dura cortando la oscuridad» en TODOS los temas.
# Con eso, hasta una paleta cálida sale sombría.
#
# El ánimo es el par (aire, luz), y va por hash igual que la paleta: un vídeo
# mantiene el suyo, el siguiente cae en otro. La mitad de la lista es luminosa
# a propósito, para que la serie respire.
# ---------------------------------------------------------------------------
ANIMOS = {
 # --- graves, los de siempre ---
 "niebla":     ("still heavy air, drifting fog",
                "one hard directional light cutting the darkness"),
 "tormenta":   ("charged air before rain, low heavy clouds",
                "stormlight breaking through in one narrow shaft"),
 "nocturno":   ("cold night air, faint mist near the ground",
                "distant artificial light, deep unlit space around"),
 "polvo":      ("dry dust suspended in the air",
                "one low raking light across the surfaces"),

 # --- luminosos, la mitad que faltaba ---
 "amanecer":   ("clean cool morning air, thin low mist burning off",
                "soft golden sunrise light flooding in from one side"),
 "mediodia":   ("crystal clear air, sharp visibility",
                "bright open daylight, luminous, gentle shadows"),
 "brisa":      ("light airy atmosphere, drifting pollen and seeds in the sun",
                "warm diffused daylight, high key, soft and open"),
 "reflejo":    ("clear air over water",
                "bright light bouncing off water, shimmering highlights"),
 "ventanal":   ("calm still interior air, fine dust in the beams",
                "generous daylight pouring through tall windows, airy and bright"),
 "verano":     ("warm shimmering air, heat haze on the horizon",
                "high summer sun, brilliant and clean"),
}

LUMINOSOS = ["amanecer", "mediodia", "brisa", "reflejo", "ventanal", "verano"]
GRAVES = ["niebla", "tormenta", "nocturno", "polvo"]


def animo_de(tema, sesgo_luz=0.6):
    """(nombre, aire, luz) estable por tema.

    sesgo_luz: proporción de temas que caen en un ánimo luminoso. 0,6 por
    defecto porque la serie venía demasiado oscura y hay que compensar, no
    solo empatar.
    """
    import hashlib
    # DOS hashes distintos, no uno partido: sacando el grupo y el miembro del
    # mismo número quedaban correlacionados y «brisa» salía 4 de cada 10 veces.
    def _h(sal):
        return int(hashlib.sha1((sal + tema).encode()).hexdigest(), 16)
    grupo = LUMINOSOS if _h("luz:") % 100 < int(sesgo_luz * 100) else GRAVES
    n = grupo[_h("cual:") % len(grupo)]
    return (n,) + ANIMOS[n]
