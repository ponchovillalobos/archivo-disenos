"""Trocea una transcripción en bloques narrativos: uno por imagen.

Segunda pieza del circuito audio → vídeo. Toma el JSON que deja `transcribir.py`
y lo parte donde el hablante hace frontera de idea, no cada N segundos.

Tres señales, en este orden de prioridad:
  1. **Fin de frase con pausa** — un punto seguido de aire es la frontera más
     fiable que existe.
  2. **Pausa larga** — donde se respira suele cambiar la idea.
  3. **Duración máxima** — corte forzoso, para que ninguna imagen aguante
     demasiado en pantalla.

Y una regla de arrastre: los trozos demasiado cortos se pegan al bloque
anterior. Medido sobre «Idea 1»: sin esa regla salían 12 bloques y tres eran
fragmentos partidos a media frase («Corazón acelerado, manos frías,» / «vacío
en el estómago.»), que como imagen no significan nada.

El transcriptor no siempre pone el punto. Cuando dos ideas quedan pegadas en un
bloque largo, hay que separarlas a mano al escribir las escenas — se marca con
`sospechoso: True` para no pasarlo por alto.
"""
import json
import os
import sys

PAUSA = 0.45      # s de silencio que cuentan como frontera
PAUSA_FRASE = 0.30  # tras un punto basta con menos aire
DUR_MIN = 2.6     # por debajo, el bloque se pega al anterior
DUR_MAX = 7.5     # por encima, se corta aunque no haya pausa
FIN = (".", "?", "!", "…", ":")


def pausa_oculta(palabras, i, factor=2.8, minimo=1.05):
    """Silencio que el transcriptor escondió DENTRO de la palabra.

    Whisper estira el final de una palabra para cubrir el silencio que viene
    detrás. Medido en «Idea 1»: «Antes», «No» y «El» duraban 1,24 s, 1,16 s y
    1,18 s — imposible para palabras de dos y tres letras. Ese segundo de más
    era la pausa, y como quedaba dentro de la palabra el hueco entre palabras
    salía cero y el troceador no veía la frontera. Resultado: tres ideas
    pegadas en un bloque de 9,4 s.

    Se detecta comparando el ritmo de cada palabra con el ritmo mediano del
    audio: si una palabra tarda casi el triple por letra de lo normal, lo que
    sobra es silencio.

    El umbral de 1,05 s está medido, no elegido a ojo. Con 0,70 s el detector
    se disparaba en «no» y «sino» (0,70 s) y cortaba a mitad de frase; con
    1,05 s coge las tres pausas reales y ninguna falsa.
    """
    w = palabras[i]
    dur = w["fin"] - w["inicio"]
    if dur < minimo:
        return 0.0
    n = max(1, len(w["palabra"].strip(".,;:¿?¡!»«\"")))
    ritmos = sorted((x["fin"] - x["inicio"]) / max(1, len(x["palabra"]))
                    for x in palabras)
    mediano = ritmos[len(ritmos) // 2]
    esperado = mediano * n
    return dur - esperado if dur > esperado * factor else 0.0


def trocear(palabras, dur_min=DUR_MIN, dur_max=DUR_MAX):
    crudos, act = [], []
    for i, w in enumerate(palabras):
        act.append(w)
        hueco = (palabras[i + 1]["inicio"] - w["fin"]) if i + 1 < len(palabras) else 99.0
        # una pausa escondida en la palabra SIGUIENTE es frontera antes de ella
        if i + 1 < len(palabras):
            oculta = pausa_oculta(palabras, i + 1)
            if oculta > 0 and (w["fin"] - act[0]["inicio"]) >= dur_min:
                crudos.append(act)
                act = []
                continue
        dur = act[-1]["fin"] - act[0]["inicio"]
        cierra = (
            (w["palabra"].endswith(FIN) and hueco >= PAUSA_FRASE and dur >= dur_min)
            or (hueco >= PAUSA and dur >= dur_min)
            or dur >= dur_max)
        if cierra:
            crudos.append(act)
            act = []
    if act:
        crudos.append(act)

    # arrastre: nada por debajo del mínimo sobrevive suelto
    fund = []
    for b in crudos:
        d = b[-1]["fin"] - b[0]["inicio"]
        if fund and d < dur_min:
            fund[-1].extend(b)
        else:
            fund.append(b)

    salida = []
    for n, b in enumerate(fund, 1):
        texto = " ".join(x["palabra"] for x in b)
        dur = round(b[-1]["fin"] - b[0]["inicio"], 2)
        # dos ideas pegadas: el ASR se comió el punto
        puntos = sum(texto.count(c) for c in ".?!")
        salida.append({
            "n": n,
            "inicio": round(b[0]["inicio"], 2),
            "fin": round(b[-1]["fin"], 2),
            "duracion": dur,
            "texto": texto,
            "sospechoso": puntos > 1 or dur > dur_max - 0.3,
        })
    return salida


def srt(bloques):
    def ts(s):
        h, r = divmod(s, 3600)
        m, r = divmod(r, 60)
        return "%02d:%02d:%02d,%03d" % (h, m, int(r), round(r % 1 * 1000))
    return "\n".join("%d\n%s --> %s\n%s\n"
                     % (b["n"], ts(b["inicio"]), ts(b["fin"]), b["texto"])
                     for b in bloques)


def desde_json(ruta, **kw):
    d = json.load(open(ruta, encoding="utf-8"))
    return trocear(d["palabras"], **kw)


if __name__ == "__main__":
    ruta = sys.argv[1]
    bl = desde_json(ruta)
    base = os.path.splitext(ruta)[0]
    json.dump(bl, open(base + "-bloques.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    open(base + ".srt", "w", encoding="utf-8").write(srt(bl))
    dudosos = sum(b["sospechoso"] for b in bl)
    print("  %d bloques · %d marcados para revisar" % (len(bl), dudosos))
    for b in bl:
        print("  %2d %s %4.1f–%4.1f (%.1fs)  %s"
              % (b["n"], "!" if b["sospechoso"] else " ",
                 b["inicio"], b["fin"], b["duracion"], b["texto"]))
