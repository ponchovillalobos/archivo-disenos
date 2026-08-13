"""«Idea 1» — primer vídeo hecho a partir de un audio.

Los once bloques salen de los tiempos REALES de las palabras, no del troceador
automático: el transcriptor se comió los puntos del último tercio y dejó tres
ideas pegadas. Los tiempos delataron dónde estaban las fronteras — las palabras
«Antes», «No» y «El» duran más de un segundo cada una, y ese segundo es la
pausa que el ASR metió dentro de la palabra.

Paleta **rojo-carbón** elegida a mano, no por el hash. El sorteo daba sepia, que
es cálido y nostálgico: no le pega a un vídeo sobre adrenalina. Y `analogia`
acababa de llevarse sepia en el mismo lote, así que repetirla habría quitado
justo la variedad que se busca.

Cero caras y cero manos, como siempre. Y aquí importa más de lo normal: el
guion habla de corazón acelerado y manos frías, que es exactamente la imagen
que NO se puede generar. Se resuelve por objetos y espacios vacíos.

Aviso sobre el dato: la afirmación «son la misma sensación, exacta» es más
fuerte de lo que sostiene Brooks (2014). Comparten activación alta; no son
idénticas. Verificar en fuente antes de publicar.
"""
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
from lote import flujo                      # noqa: E402

# Cambiada de rojo-carbón a dorado-selva: el carbón con acento carmesí quedaba
# de película de terror, y lo que se busca es crecimiento, alegría y misterio.
# El dorado a través del verde transmite justo eso sin perder el aire épico.
PALETA = "dorado-selva"
ACENTO = "#e0b53c"
AUDIO = os.path.join(os.path.dirname(S), "audio", "procesados", "Idea 1.wav")

ENC_V = ("vertical composition, wide cinematic shot, uplifting and inviting, no people in frame or a tiny "
         "distant silhouette seen from behind, no faces, no hands")

# En apaisado el encuadre cambia de verdad, no solo el lienzo: en vertical la
# escena se apila hacia arriba y el texto ocupa el tercio superior; en apaisado
# hay que llenar los lados y dejar libre el tercio inferior, que es donde va el
# texto y donde el reproductor pone sus controles.
ENC_H = ("wide horizontal cinematic composition, uplifting and inviting, subject offset to one side, "
         "generous empty space across the lower third, no people in frame or a "
         "tiny distant silhouette seen from behind, no faces, no hands")
# Antes: «aire pesado» y «sombras negras profundas». Eso era el terror.
AIRE = "clear luminous air, fine golden particles drifting in the light"
LUZ = "warm generous light flooding the scene, luminous and open, soft shadows"

# (inicio, texto en pantalla, escena)
BLOQUES = [
 (0.00, "El miedo y la emoción son la misma sensación. Exacta.",
  "an empty rollercoaster track cresting against a black night sky, one crimson "
  "warning lamp burning on the rail, city far below"),

 (5.20, "Corazón acelerado, manos frías, vacío en el estómago.",
  "looking straight up an enormous empty elevator shaft, one red lamp far above, "
  "steel walls receding into darkness"),

 (10.30, "¿Montaña rusa o hablar en público?",
  "an empty rollercoaster car stopped at the very top of a drop at night, seen "
  "from behind, a sea of small lights far below"),

 (13.10, "Tu cuerpo no sabe la diferencia. Solo tú se la pones.",
  "two identical closed doors side by side in a vast dark wall, crimson light "
  "spilling under one of them only"),

 (18.40, "«Estoy muerto de miedo» y tu cerebro se prepara para huir.",
  "a very long dark corridor with a small illuminated doorway at the far end, "
  "one tiny silhouette walking away from the camera"),

 (22.70, "«Estoy emocionado» y se prepara para atacar.",
  # el modelo metió unas piernas corriendo en primer plano donde pedí tacos
  # vacíos: aquí los humanos van lejanos, nunca en primer plano. Se quita la
  # palabra «running», que es la que invoca al corredor.
  "completely deserted athletics track at night, empty starting blocks in the "
  "foreground, crimson lane markings receding, nobody present, stadium lights "
  "high above, low angle"),

 (27.16, "Misma sensación. Resultado opuesto.",
  "a fork in a dark stone tunnel, two identical passages, one glowing crimson "
  "and the other cold white"),

 (30.00, "Antes de esa llamada, no digas «qué nervios». Di «qué emoción».",
  "an old telephone alone on a bare desk under one hard lamp, everything else "
  "in black, a small red light glowing on it"),

 (36.52, "Antes del aumento, no «me va a temblar la voz», sino «esto me prende».",
  "an empty boardroom at night, one chair pulled back from a long polished "
  "table, city lights burning through the glass wall"),

 (43.80, "No estás mintiendo: es la misma energía con otro nombre.",
  "a single filament bulb glowing deep crimson in an enormous pitch black "
  "space, the filament sharp and hot"),

 (48.76, "El miedo no se quita. Se renombra.",
  "a heavy stage curtain parting onto an empty lit stage, crimson light "
  "pouring through the gap into a dark auditorium"),
]


def generar(ancho=720, alto=1280, prefijo=None):
    """720×1280 para reel · 1344×768 para apaisado (múltiplos de 64, que es lo
    que SDXL entiende: 1280×720 es 16:9 exacto pero 720 no es múltiplo de 64)."""
    apaisado = ancho > alto
    enc = ENC_H if apaisado else ENC_V
    prefijo = prefijo or ("idea1h" if apaisado else "idea1")
    return [flujo("%s-%02d" % (prefijo, i), "epic cinematic film still of " + esc,
                  esc.split(",")[0], enc, AIRE, LUZ,
                  ancho=ancho, alto=alto, paleta=PALETA)
            for i, (_, _, esc) in enumerate(BLOQUES, 1)]


def laminas(prefijo="idea1"):
    """Lo que consume el montador: fondo + texto + arranque en el audio."""
    return [{"fondo": "f%02d.png" % i, "titular": txt, "inicio": ini}
            for i, (ini, txt, _) in enumerate(BLOQUES, 1)]


if __name__ == "__main__":
    for r in generar():
        print("  ", os.path.basename(r))
