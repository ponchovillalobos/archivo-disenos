"""Lote 3 — los dieciséis temas que se generaron de noche y perdieron su guion.

Las imágenes de anoche existen, pero el script que las produjo se escribió al
vuelo y no quedó guardado: solo sobrevivieron los PNG en blanco y negro. Aquí
se reescriben las escenas, y esta vez **cada tema lleva paleta**.

La paleta no se elige a mano: sale de `paleta_de(tema)`, que la deriva del
nombre. Un vídeo entero comparte tono; el siguiente cae en otro. Y como va por
hash y no por azar, el mismo tema da siempre el mismo color y se puede
regenerar idéntico.

Reglas de siempre, sin excepción: ni caras ni manos. Los humanos aparecen como
siluetas lejanas, de espaldas, a contraluz o disueltas en la niebla.
"""
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
from lote import flujo                    # noqa: E402
from paletas import animo_de, paleta_de   # noqa: E402

# AIRE y LUZ ya NO son constantes: eran la causa de que TODO saliera grave.
# Ahora los pone `animo_de(tema)`, con sesgo hacia lo luminoso para compensar.
# Se dejan como respaldo por si algún tema pide expresamente el tono oscuro.
AIRE_GRAVE = "still heavy air, drifting fog"
LUZ_GRAVE = "one hard directional light cutting the darkness"
ENC = ("wide cinematic shot, any human tiny and distant, seen from behind, "
       "no faces, no hands, vast space around")

TEMAS = {
 "analogia": [
  "two identical stone bridges spanning the same gorge, one ancient and one new, seen from far above",
  "a river splitting around a rock and rejoining downstream, aerial view, mist over the water",
  "a vast hall where every column is a different shape but holds the same ceiling",
  "an old map and a modern one pinned side by side on a dark wall, one lamp above them",
  "two doors in an endless wall, identical except one is open, long shadows across the floor",
  "a single tree and its perfect reflection in still black water at dusk",
 ],
 "autoridad": [
  "an empty raised judge's bench in a dark wood courtroom, one shaft of light across it",
  "a lectern alone on a vast stage, a thousand empty seats receding into blackness",
  "a wall of framed diplomas in a dim corridor, glass catching the light, none legible",
  "an enormous ceremonial chair on a stone dais, empty, seen from far below",
  "a long table with one chair at its head and twenty along the sides, all empty",
  "a lone figure in a doorway at the top of a wide staircase, backlit, seen from the bottom",
 ],
 "cerrar": [
  "a heavy door swinging shut at the end of a corridor, light narrowing to a line",
  "a contract lying on a bare table under one lamp, a pen beside it, nobody there",
  "a harbour at dusk, one ship leaving, the pier completely empty",
  "a theatre curtain half fallen, the stage behind it dark and bare",
  "a key left in a lock on an old wooden door, seen close but with no hand near it",
  "a road ending at a closed gate, headlights of a distant car on the horizon",
 ],
 "compromiso": [
  "a single footprint in wet cement on an empty street at night",
  "a rope bridge over a canyon with the first plank missing, seen from the near side",
  "a ledger open on a stone table, columns of writing, one lamp, deep shadow around",
  "a line drawn in sand on an empty beach at dawn, the tide far out",
  "a lone figure standing at the start of a very long straight road, seen from far behind",
  "a padlock closed on an iron gate, the chain taut, fog beyond the bars",
 ],
 "contraste": [
  "one lit window in an entire dark tower block, seen from across the street",
  "a single bare tree in an enormous empty snowfield, aerial view",
  "a black stone standing among a thousand white ones on a vast floor",
  "a corridor half in blinding light and half in total darkness, the line sharp on the floor",
  "one empty chair among rows of full ones in a dark auditorium, seen from above",
  "a lighthouse beam cutting one narrow path across a black sea",
 ],
 "el-orden": [
  "a spiral staircase seen straight down from the top, endless, one light at the bottom",
  "a vast archive of numbered drawers, one pulled open, dust in the beam of light",
  "a domino line curving across a huge dark floor, the first one already tipping",
  "a chessboard the size of a room, pieces mid-game, seen from high above",
  "a queue of identical stone arches receding into fog, each smaller than the last",
  "an orchestra of empty chairs and music stands, arranged perfectly, one spotlight",
 ],
 "el-tono": [
  "a single tuning fork standing upright on a dark polished table, one shaft of light",
  "an empty recording booth seen through thick glass, the microphone alone inside",
  "a vast cathedral interior, completely empty, light falling through high windows",
  "a bell hanging motionless in a stone tower, rope trailing down into darkness",
  "ripples spreading across black water from a single point, seen from directly above",
  "a piano alone on an empty stage, lid open, one light from high above",
 ],
 "escasez": [
  "one apple left on an enormous empty market table at closing time",
  "a nearly empty water tower against a vast dry landscape at dusk",
  "a single seat left in a packed dark theatre, seen from the back row",
  "an hourglass almost run out, standing alone on a stone ledge",
  "the last lit lamp on a long street of dark ones, fog rolling in",
  "one boat left on a beach at low tide, the marks of many others in the sand",
 ],
 "jerga": [
  "a wall covered in dense unreadable script in an abandoned hall, one lamp",
  "a room full of identical closed filing cabinets, no labels, deep shadow",
  "a maze of glass partitions in an empty office at night, reflections multiplying",
  "an old printing press covered in dust, type still set in the frame",
  "a signpost at a crossroads with every arm blank, fog in all directions",
  "a lecture hall of empty seats facing a blackboard covered in erased writing",
 ],
 "la-brevedad": [
  "a single struck match burning in an enormous dark room",
  "one word-sized shaft of light on a vast blank wall",
  "a stone dropped into still water, the first ring only, seen from above",
  "a very short pier ending abruptly over a huge calm lake at dawn",
  "an empty telegram form on a dark desk under one lamp",
  "a bird's single feather falling through a shaft of light in a tall empty hall",
 ],
 "la-memoria": [
  "a room where every surface is covered in dust except one clean rectangle on the table",
  "an abandoned cinema, screen blank, rows of seats under drifting dust",
  "a wall of photographs turned face to the wall in a dim corridor",
  "an old carousel standing still in fog at dawn, completely empty",
  "footprints crossing an empty ballroom floor, no one in sight",
  "a stopped clock in an empty station hall, light falling through the roof",
 ],
 "la-prueba": [
  "a single spotlit table in the middle of an enormous dark hall, one object on it",
  "a laboratory bench at night, glassware catching one hard light, nobody there",
  "a vast wall of identical sealed boxes, one open and lit from inside",
  "a scale balanced perfectly on a stone plinth in an empty vault",
  "a courtroom evidence table under a single hanging lamp, the room black around it",
  "a microscope alone on a dark bench, one beam of light through its stage",
 ],
 "primera-impresion": [
  "a doorway opening onto blinding light, seen from inside a dark room",
  "the prow of a ship emerging from fog, seen from a deserted shore",
  "an enormous curtain lifting a hand's width above a lit stage floor",
  "a single set of footprints entering an untouched snowfield, aerial view",
  "a threshold of pale stone worn smooth, one shaft of light across it",
  "the first light of dawn hitting the top of a vast empty amphitheatre",
 ],
 "primeras-palabras": [
  "an open book on a stone lectern in an empty chapel, one beam of light on the page",
  "a microphone alone on a dark stage, one light, the hall invisible behind it",
  "a wide door standing open at the end of a long dark hall, light pouring through",
  "a blank sheet of paper on a dark desk under one lamp, nothing written",
  "a lone silhouette stepping into a lit doorway, seen from far behind",
  "an empty starting line painted on a vast dark track, fog low over it",
 ],
 "reciprocidad": [
  "two empty chairs facing each other across a small table, one lamp above",
  "a stone bridge meeting exactly in the middle over a dark river, seen from the side",
  "a gift-wrapped box left alone on a doorstep at night, one street lamp",
  "two lights on opposite hillsides across a dark valley, mist between them",
  "a pair of scales in perfect balance on a plinth in an empty hall",
  "an open door on each side of a long corridor, light crossing in the middle",
 ],
 "repeticion": [
  "an endless row of identical arches receding into fog, each lit the same",
  "waves breaking one after another on a dark empty beach, long exposure",
  "a hall of mirrors reflecting one lamp into infinity",
  "a colonnade seen down its length, columns repeating into darkness",
  "an aerial view of identical rooftops stretching to the horizon at dusk",
  "a metronome alone on a dark table, one shaft of light, blurred by motion",
 ],
}


def encolar(temas=None, ancho=720, alto=1280):
    """Genera los flujos con la paleta que a cada tema le toque.

    Devuelve la lista de rutas y el reparto de paletas, para poder auditarlo
    antes de mandarlo a la GPU.
    """
    rutas, reparto = [], {}
    for tema in (temas or TEMAS):
        nombre, acento, _, _ = paleta_de(tema)
        anim, aire, luz = animo_de(tema)
        reparto[tema] = (nombre, acento, anim)
        for i, escena in enumerate(TEMAS[tema], 1):
            rutas.append(flujo(
                "%s-c%d" % (tema, i),
                "epic cinematic film still of " + escena,
                escena.split(",")[0], ENC, aire, luz,
                ancho=ancho, alto=alto, paleta=nombre))
    return rutas, reparto
