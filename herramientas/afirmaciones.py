"""Afirmaciones RETIRADAS: cosas que dimos por ciertas y resultaron falsas.

## Por qué existe

El proyecto tiene **5.436 líneas de memoria** repartidas en cuatro sitios que no
se hablan entre sí:

    documentos .md de la raíz .............  2.940 líneas
    docstrings de los módulos .............  1.168
    cuerpos de los mensajes de commit .....    806
    fichas de memoria persistente .........    522

El problema medido **no es que falte memoria: es que hay demasiada y nada obliga
a que diga lo mismo.**

Prueba: la afirmación «el veto de color en el negativo es lo que hace obedecer
al modelo» era **falsa** —cuatro variantes controladas salieron idénticas píxel
a píxel— y estaba escrita como verdad en **cinco sitios**. Se corrigió en cuatro
y el quinto sobrevivió un día entero dentro de un fichero que se estaba editando
esa misma tarde.

Añadir un grafo de conocimiento encima habría sido **un sexto sitio donde puede
pudrirse**. Lo que faltaba no era dónde escribir: era **una comprobación que
falle cuando un desmentido reaparece**.

## Cómo funciona

Cada entrada tiene el patrón que delata la afirmación muerta y el porqué. La
prueba del sistema recorre la memoria y **falla si alguno reaparece** fuera de
un contexto de corrección.

Es el mismo principio que el resto de `prueba_sistema.py`: cada comprobación
nació de un fallo real, y existe para que ese fallo no vuelva en silencio.

## Cómo se retira una afirmación

Cuando una prueba controlada tumbe algo que dábamos por cierto:

1. Se corrige donde esté escrito (`grep -rn` sobre los cuatro sitios).
2. Se añade aquí su patrón, con la medición que lo tumbó.
3. La prueba del sistema ya no deja que vuelva.
"""
import os
import re
import subprocess
import sys

S = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.dirname(S)
MEM = os.path.expanduser(
    "~/.claude/projects/-Users-maity-Desktop-Confy-Imagenes/memory")

# (patrón, qué se creía, qué se midió)
RETIRADAS = [
 (r"veto es (lo que|la pieza)",
  "que el veto de color en el negativo hacía obedecer al modelo",
  "cuatro variantes controladas de la misma escena y semilla salieron IDÉNTICAS "
  "píxel a píxel con veto y sin él: a CFG 1.0 ComfyUI ni evalúa el negativo. "
  "El mérito era de los pesos en positivo."),

 (r"hallazgo más rentable del proyecto",
  "que el veto era el hallazgo más rentable",
  "mismo desmentido. Estuvo publicado semanas."),

 (r"CLIP corta en 77",
  "que CLIP trunca el prompt en el token 77",
  "ComfyUI NO trunca: trocea en bloques de 77 y los concatena. Lo que sí es "
  "cierto es que el vector pooled sale solo del primer bloque."),

 (r"IPAdapter — No instalado|IPAdapter.{0,12}no instalado",
  "que IPAdapter no estaba instalado",
  "está instalado y funcionando desde el 13-ago-2026."),

 (r"coherencia alta.{0,30}(buen|éxito|mérito)",
  "que una coherencia CLIP alta era un buen resultado",
  "premia el fracaso: sube a 0,99 cuando el modelo repite el mismo plano. "
  "Hacen falta margen y fidelidad además."),
]

# Dónde se busca. Los cuatro sitios donde vive la memoria.
def _corpus():
    import glob
    fs = glob.glob(os.path.join(PROY, "*.md"))
    fs += [x for x in glob.glob(os.path.join(S, "*.py"))
           if os.path.basename(x) != "afirmaciones.py"]
    fs += glob.glob(os.path.join(MEM, "*.md"))
    return fs


# Una línea que habla DE la corrección no es una recaída. Se reconoce por estas
# marcas, que es como se escriben los desmentidos en este repositorio.
PERDON = re.compile(r"decía|CORRECC|corregi|\bfalso\b|desmen|retirad|era falsa"
                    r"|MAL PLANTEADO|no es cierto|resultó",
                    re.I)


def recaidas():
    """Devuelve [(fichero, línea, texto, qué se creía)] de lo que reapareció."""
    fuera = []
    for f in _corpus():
        try:
            ls = open(f, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            continue
        for n, linea in enumerate(ls, 1):
            if PERDON.search(linea):
                continue
            for pat, creia, _ in RETIRADAS:
                if re.search(pat, linea, re.I):
                    fuera.append((os.path.relpath(f, PROY), n,
                                  linea.strip()[:90], creia))
    return fuera


def contradicciones_de_tamano():
    """El caso que se coló hoy: dos tamaños incompatibles, ambos documentados.

    720×1280 es 9:16 EXACTO pero no es múltiplo de 64 ni cubo de SDXL.
    768×1344 es cubo de SDXL pero da 0,571 y las redes lo recortan.

    No hay respuesta correcta: hay que elegir a sabiendas. Esta comprobación no
    falla, avisa — para que la decisión sea consciente y no un accidente de
    quien editó el último."""
    import glob
    sitios = {"720x1280": [], "768x1344": []}
    for f in glob.glob(os.path.join(PROY, "*.md")):
        t = open(f, encoding="utf-8", errors="replace").read()
        for k, pat in (("720x1280", r"720[×x]1280"), ("768x1344", r"768[×x]1344")):
            if re.search(pat, t):
                sitios[k].append(os.path.basename(f))
    return sitios


def informe():
    r = recaidas()
    print("  afirmaciones retiradas vigiladas: %d" % len(RETIRADAS))
    print("  ficheros de memoria revisados:    %d" % len(_corpus()))
    if not r:
        print("  recaídas: NINGUNA")
    else:
        print("  RECAÍDAS: %d" % len(r))
        for f, n, txt, creia in r:
            print("   %s:%d" % (f, n))
            print("     %s" % txt)
            print("     se creía: %s" % creia)
    s = contradicciones_de_tamano()
    print()
    print("  tamaño de reel — decisión que hay que tomar a sabiendas:")
    for k, fs in s.items():
        print("   %-9s en %s" % (k, ", ".join(fs) or "ningún documento"))
    return r


if __name__ == "__main__":
    sys.exit(1 if informe() else 0)
