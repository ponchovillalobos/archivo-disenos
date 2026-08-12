"""Lote 1 — seis temas cuyas fuentes ya verificamos en esta sesión.

Cada tema tiene su mundo visual y su acento. Ninguna escena lleva caras ni
manos: los humanos aparecen como siluetas lejanas, de espaldas o a contraluz.
"""
import sys, os
S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
from lote import flujo

AIRE = "still heavy air, drifting fog"

TEMAS = [
    # ---------------------------------------------------------------- 1
    ("vacio", "#e0a23c", [
     ("epic cinematic film still of a single door standing ajar at the end of a long dark "
      "corridor, a blade of warm amber light spilling out across the floor, nothing visible "
      "beyond the gap",
      "an empty corridor", "wide symmetrical shot, door small at the end, vast dark walls above"),
     ("epic cinematic film still of a vast library of towering shelves lost in darkness, one "
      "single lamp lit far down an aisle, a tiny silhouette of a person standing under it, seen "
      "from very far behind",
      "endless bookshelves", "extreme wide shot, figure tiny in the lower third, darkness above"),
     ("epic cinematic film still of an unopened sealed envelope lying alone on a bare wooden "
      "table, one shaft of amber light across it, deep shadow all around",
      "a bare wooden table", "overhead close-up, envelope in the lower third, dark empty above"),
     ("epic cinematic film still of a narrow stone staircase spiralling down into darkness, warm "
      "amber light coming from somewhere below, worn steps, dust in the beam",
      "a spiral stone staircase", "looking down the stairwell, steps filling the lower half"),
     ("epic cinematic film still of a wide field of tall dry grass at dusk with a single narrow "
      "path cut through it disappearing over the horizon, one distant figure walking away, seen "
      "from behind and very far",
      "a footpath through tall grass", "extreme wide shot, figure tiny, vast sky filling the top"),
     ("epic cinematic film still of a heavy theatre curtain half drawn, warm amber light escaping "
      "from the gap between the folds, the rest of the frame in deep shadow",
      "a heavy velvet curtain", "centred shot, curtain filling the frame, gap of light in the middle"),
     ]),
    # ---------------------------------------------------------------- 2
    ("relato", "#e07a3c", [
     ("epic cinematic film still of a small campfire burning in a vast dark plain at night, four "
      "distant seated silhouettes around it seen from far behind, sparks rising into the sky",
      "a low campfire", "extreme wide shot, fire and silhouettes tiny in the lower third, huge starry sky"),
     ("epic cinematic film still of an old open book on a table with warm firelight falling across "
      "its pages, the room around it swallowed in darkness",
      "an open book", "overhead close-up, book in the lower two thirds, dark empty space above"),
     ("epic cinematic film still of a single empty rocking chair beside a dying hearth in an old "
      "wooden room, embers glowing, long shadows across the floorboards",
      "an empty rocking chair", "wide shot, chair in the lower half, dark wall above"),
     ("epic cinematic film still of a cave wall covered in ancient ochre handprint-free painted "
      "animals, one torch flame lighting a small circle of it, the rest in blackness",
      "a rough cave wall", "close wide shot, painted wall filling the frame, torchlight circle"),
     ("epic cinematic film still of a lone traveller's silhouette on a ridge at dusk with a vast "
      "valley of mist below, seen from very far behind, warm last light on the horizon",
      "a rocky ridge", "extreme wide shot, figure tiny in the lower quarter, huge sky above"),
     ("epic cinematic film still of a burnt-out campfire at dawn, grey ash and one last ember, cold "
      "mist over an empty plain, no people",
      "cold ashes", "low close shot, ashes in the lower third, pale empty plain above"),
     ]),
    # ---------------------------------------------------------------- 3
    ("emocion", "#9b7fd4", [
     ("epic cinematic film still of a violent lightning storm over a distant city skyline at night, "
      "one tiny silhouette standing on a rooftop far away watching it, seen from behind",
      "a rooftop parapet", "extreme wide shot, figure tiny in the lower quarter, enormous storm sky"),
     ("epic cinematic film still of an enormous wave rising in a dark sea under a violet-lit sky, "
      "spray torn off its crest by the wind, no people",
      "open ocean", "wide shot, wave filling the lower two thirds, storm sky above"),
     ("epic cinematic film still of a vast crowd of small distant silhouettes in a dark square all "
      "facing away toward a single blaze of light on the horizon",
      "a stone square", "very high wide shot from behind the crowd, heads tiny and unreadable"),
     ("epic cinematic film still of a single lit window in a huge black building facade at night, "
      "hundreds of dark windows around it, violet glow spilling out",
      "a building facade", "flat wide shot, facade filling the frame, one window glowing"),
     ("epic cinematic film still of a flock of thousands of birds turning as one against a bruised "
      "violet dusk sky above an empty field",
      "an empty field", "wide shot, murmuration filling the upper half, dark ground below"),
     ("epic cinematic film still of a still black lake at night perfectly reflecting a violet "
      "aurora, one distant silhouette standing at the water's edge seen from far behind",
      "a still lake", "extreme wide shot, figure tiny at the shoreline, sky and reflection dominating"),
     ]),
    # ---------------------------------------------------------------- 4
    ("prueba-social", "#7fc4a0", [
     ("epic cinematic film still of hundreds of identical dark silhouettes standing in perfect rows "
      "in thick fog, all facing the same way, one single figure far off turned the opposite way",
      "rows of standing figures", "high wide shot from behind, all figures small and faceless in fog"),
     ("epic cinematic film still of an enormous flock of sheep flowing along a narrow mountain road "
      "at dawn, seen from high above, mist in the valley",
      "a mountain road", "aerial wide shot, flock in the lower half, empty slope above"),
     ("epic cinematic film still of a hotel corridor of identical closed doors receding into "
      "darkness, one door slightly open with pale green light behind it",
      "a hotel corridor", "wide symmetrical shot down the corridor, doors receding"),
     ("epic cinematic film still of a wall of identical stacked white towels in a dim laundry room, "
      "one single towel pulled out of line",
      "stacked folded towels", "flat close wide shot, towels filling the frame"),
     ("epic cinematic film still of a vast empty stadium at night with every seat empty, floodlights "
      "on, a lone distant silhouette standing at the centre circle seen from very far above",
      "an empty stadium", "extreme aerial wide shot, figure tiny at the centre"),
     ("epic cinematic film still of hundreds of identical footprints in wet sand all going the same "
      "direction, and one single set turning away toward the sea",
      "wet sand", "high overhead shot, footprints filling the frame, no people"),
     ]),
    # ---------------------------------------------------------------- 5
    ("indignacion", "#d8353d", [
     ("epic cinematic film still of a wall of dozens of old television screens all glowing red in a "
      "pitch dark room, static and noise, no people",
      "stacked old televisions", "flat wide shot, screens filling the frame"),
     ("epic cinematic film still of an empty newsroom at night, rows of dark desks, one single "
      "monitor still glowing red at the far end",
      "rows of empty desks", "wide shot down the room, desks in the lower half, dark ceiling above"),
     ("epic cinematic film still of a swarm of moths battering a single red bulb in total darkness",
      "one bare bulb", "close centred shot, bulb and moths in the middle, blackness around"),
     ("epic cinematic film still of a huge bonfire of newspapers burning in an empty street at "
      "night, embers rising, no people",
      "burning newspapers", "wide shot, fire in the lower half, dark street and sky above"),
     ("epic cinematic film still of a long queue of dark distant silhouettes waiting outside a door "
      "spilling red light, seen from far behind in heavy rain",
      "a queue in the rain", "wide shot from behind, figures small and faceless"),
     ("epic cinematic film still of a single cracked smartphone screen face up on wet asphalt at "
      "night, red light glowing through the cracks, rain falling",
      "wet asphalt", "overhead close shot, screen in the lower third, dark ground above"),
     ]),
    # ---------------------------------------------------------------- 6
    ("manipular", "#6f9fc4", [
     ("epic cinematic film still of a forest path splitting into two in thick fog, one lone distant "
      "silhouette standing at the fork seen from far behind, cold blue light",
      "a forked path", "wide shot, figure tiny at the fork, fog and trees filling the frame"),
     ("epic cinematic film still of a marionette control bar with slack strings hanging down into "
      "darkness, no puppet visible, cold blue light from above",
      "hanging strings", "close centred shot, strings descending into black"),
     ("epic cinematic film still of a chessboard mid game on a table in an empty room, one piece "
      "toppled, cold blue window light raking across it, no people",
      "a chess board", "low close shot, board in the lower two thirds, empty room above"),
     ("epic cinematic film still of a hall of tall mirrors reflecting each other endlessly in cold "
      "blue light, one distant silhouette standing among them seen from far behind",
      "facing mirrors", "wide shot, reflections receding, figure small and unreadable"),
     ("epic cinematic film still of a heavy iron scale hanging in an empty stone hall, one pan "
      "weighed down, cold blue light from a high window",
      "an iron balance scale", "centred wide shot, scale in the middle, vast dark hall around"),
     ("epic cinematic film still of a single open door in a bare white room with cold blue daylight "
      "beyond it, and a second identical closed door beside it",
      "two doors", "flat centred wide shot, doors in the lower two thirds, empty wall above"),
     ]),
]


def construir():
    rutas = []
    for tema, _acento, escenas in TEMAS:
        for i, (escena, objeto, encuadre) in enumerate(escenas, 1):
            slug = "%s-%d" % (tema, i)
            rutas.append(flujo(slug, escena, objeto,
                               encuadre + ", no faces, no hands, no close figures",
                               AIRE, "one hard directional light cutting the darkness"))
    return rutas


if __name__ == "__main__":
    r = construir()
    print("\n".join(os.path.basename(x) for x in r))
    print("%d flujos" % len(r))
