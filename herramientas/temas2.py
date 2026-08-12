"""Lote 2 — doce temas más. Las imágenes no dependen de la verificación de
citas (eso solo afecta al texto), así que se pueden generar ya.

Sin caras. Sin manos. Humanos siempre como siluetas lejanas o de espaldas.
"""
import sys, os
S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
from lote import flujo

AIRE = "still heavy air, drifting fog"
LUZ = "one hard directional light cutting the darkness"

def T(nombre, acento, escenas):
    return (nombre, acento, escenas)

TEMAS = [
 T("escuchar", "#8fb8d0", [
  "a single empty consulting room chair facing another across a bare desk, cold window light, no people",
  "an enormous ear-shaped stone amphitheatre carved into a hillside at dawn, completely empty, mist pooling in the seats",
  "a stopwatch lying alone on a dark table, its hand frozen, one shaft of light across the glass",
  "a long hospital corridor at night, one door open spilling pale light, a distant silhouette walking away seen from behind",
  "an old telephone receiver off the hook hanging by its cord in a dark empty hallway",
  "two chairs facing each other in an empty white room, one slightly turned away, long shadows"]),

 T("preguntas", "#c9a227", [
  "an ancient iron key resting in the lock of a huge weathered wooden door, warm light through the keyhole",
  "a stone labyrinth seen from high above at dusk, one tiny silhouette standing at its entrance",
  "a deep stone well with a rope disappearing into blackness, one beam of light striking the water far below",
  "a corridor of many identical closed doors with a single one ajar, warm light escaping",
  "a compass lying open on a weathered map on a wooden table, lamplight raking across",
  "a narrow crack in a vast rock face with golden light pouring out of it"]),

 T("silencio", "#a8b0b8", [
  "a vast snow field at dawn with no tracks at all, one distant silhouette standing motionless, seen from far behind",
  "an anechoic chamber lined with grey foam wedges, empty, one cold light above",
  "a huge bronze bell hanging still in an empty stone tower, dust in the light",
  "a frozen lake surface with a single crack running across it, no people, pale flat light",
  "an empty concert hall from the stage, every seat empty, one work light on a stand",
  "a monastery cloister at dawn, empty arches, mist in the courtyard"]),

 T("negociar", "#b0763c", [
  "a very long empty polished table in a dark boardroom with a single chair at each far end",
  "a heavy iron anchor half buried in wet sand at low tide, chain trailing into the water",
  "an old brass balance scale on a desk, one pan clearly lower, cold window light",
  "two chess kings standing alone on an otherwise empty board, raking light",
  "a rope bridge over a deep gorge in fog, one distant silhouette standing at its start seen from behind",
  "a stack of unopened envelopes on a bare table, one pushed slightly forward"]),

 T("maldicion", "#7ea87e", [
  "a metronome standing alone on a dark piano lid, one shaft of light across it",
  "concentric ripples spreading on perfectly still black water from a single point",
  "a pane of glass with breath fog on one side only, light behind it",
  "a wall of identical sheet music pages pinned up, one covered in ink annotations",
  "a lit room seen from outside through a window on a dark street, one silhouette inside seen from behind",
  "a tuning fork standing upright on a stone surface, everything else in darkness"]),

 T("poses-poder", "#9a8fb0", [
  "a colossal empty stone pedestal in a vast plaza at dusk, the statue long gone",
  "an enormous monument silhouette against a bruised sky, one tiny figure at its base seen from far behind",
  "a single spotlight on an empty stage floor with nobody standing in it",
  "a long shadow of a standing figure cast across cobblestones, the figure itself out of frame",
  "an ornate empty throne in a dark stone hall, one shaft of light across the seat",
  "a wall of identical framed portraits turned to face the wall in a dim gallery"]),

 T("inoculacion", "#6fa88f", [
  "a single green shoot growing out of a crack in a vast concrete slab, hard light",
  "a firebreak cut through a dense dark forest seen from high above at dusk",
  "an ancient city wall with one small reinforced gate, mist at its base",
  "a shield propped alone against a stone wall, deep scratches across its face",
  "a controlled burn line on a dry grassland at night, thin flames advancing, no people",
  "a lightning rod on a rooftop against a storm sky, no people"]),

 T("decir-no", "#c25b4e", [
  "a single line drawn in wet sand at the edge of the tide, nothing else",
  "a heavy closed iron door in a bare stone wall, one bolt thrown across it",
  "a boundary stone standing alone in an empty moor at dusk, fog behind it",
  "a narrow mountain pass blocked by a single fallen boulder, cold light",
  "a lantern hanging outside a shut gate at night, rain falling",
  "a chain across a road at dusk, empty landscape beyond it"]),

 T("objeciones", "#c9903c", [
  "a cracked ceramic bowl repaired with visible gold seams, on a dark table, raking light",
  "a stone wall with one deliberate opening where the light comes through",
  "an old ship hull with a patched plank clearly visible, dry dock, cold light",
  "a shattered window with the light coming through the broken pane, dark room",
  "a scarred wooden shield laid flat on a table, the scars catching the light",
  "a mended fishing net hanging in a boathouse, the repair visible, sea light"]),

 T("concreto", "#7f9ec4", [
  "one perfectly sharp stone in the foreground and an entire mountain range lost in fog behind",
  "a single lit lamp post in an enormous field of fog at night, nothing else visible",
  "a nail hammered into a beam, everything else in the workshop out of focus",
  "a single red apple on an empty grey table, hard light, deep shadow",
  "one clear footprint in deep mud, the rest of the ground churned and unreadable",
  "a lighthouse beam cutting through thick fog over a black sea"]),

 T("estructura", "#a08a6a", [
  "an ancient stone arch standing alone in a field, keystone visible, dawn light",
  "the wooden scaffolding around an unfinished cathedral vault, empty, dust in the light",
  "the exposed foundations of a huge building, deep trenches, cold overcast light",
  "a suspension bridge cable close up with the span disappearing into fog",
  "a dry stone wall being built, one gap left where a stone will go",
  "a spiral staircase seen from directly below, receding upward into darkness"]),

 T("emociones-transmitir", "#c47f9e", [
  "a single candle flame reflected in a dark window with rain running down the glass",
  "a vast empty church interior with one shaft of coloured light across the stone floor",
  "a lone tree bending in a storm on an empty hill, no people",
  "an old violin lying in an open case on a dark floor, one light above",
  "a distant silhouette standing at the end of a pier in heavy fog, seen from far behind",
  "embers rising from a dying fire against a black night sky"]),
]


def construir():
    rutas = []
    for tema, _ac, escenas in TEMAS:
        for i, esc in enumerate(escenas, 1):
            rutas.append(flujo(
                "%s-%d" % (tema, i),
                "epic cinematic film still of " + esc,
                "the scene as described",
                "wide cinematic composition, subject in the lower half, vast empty space above, "
                "no faces, no hands, no close figures, no people near the camera",
                AIRE, LUZ))
    return rutas


if __name__ == "__main__":
    r = construir()
    print("%d flujos, %d temas" % (len(r), len(TEMAS)))
