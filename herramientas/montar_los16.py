"""Monta los dieciséis temas que tenían imágenes y no tenían vídeo.

Existe porque se generaron 96 imágenes y ninguna llegó a ser una pieza: las
escenas se reescribieron en `temas3.py` cuando se perdió el script de la
noche, pero los GUIONES no. Sin texto no hay lámina y sin lámina no hay vídeo.

Paleta y acento salen del contrato, no de una lista aparte: es la misma regla
que ya rige todo lo demás, así que el color del texto concuerda con el de la
imagen sin que nadie lo cuadre a mano.
"""
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)

import contrato                                    # noqa: E402
import paletas                                     # noqa: E402
from guiones3 import GUIONES, laminas              # noqa: E402
from paralelo import correr                        # noqa: E402

# el lote 3 nombró los PNG con una «c» que los lotes anteriores no tenían
PATRON = "{tema}-c{i}"

# la música se reparte para que dos seguidos no suenen igual
PISTAS = ["Rites.mp3", "The_Descent.mp3", "Lightless_Dawn.mp3",
          "Ossuary_6_-_Air.mp3", "Echoes_of_Time_v2.mp3", "Heroic_Age.mp3",
          "Anguish.mp3", "Redletter.mp3"]


def encargos(temas=None):
    """{tema: (acento, pista, láminas)} — la forma que espera `paralelo.correr`."""
    voz = contrato.cargar_voz("fuente-primaria")
    fuera = {}
    for i, t in enumerate(sorted(temas or GUIONES)):
        acento = paletas.PALETAS[contrato._paleta(voz, t, None)][0]
        fuera[t] = (acento, PISTAS[i % len(PISTAS)], laminas(t))
    return fuera


if __name__ == "__main__":
    temas = sys.argv[1:] or None
    enc = encargos(temas)
    print("  %d temas · %s" % (len(enc), ", ".join(sorted(enc))))
    ok, fallos, seg = correr(enc, hilos=3)
    print("  montados %d · fallos %d · %.0f min" % (len(ok), len(fallos), seg / 60))
    for f in fallos:
        print("   !", f)
