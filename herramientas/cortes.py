"""Convierte once imágenes fijas en treinta y tantos planos.

La idea, que nace de nuestra limitación y la vuelve ventaja:

En vídeo grabado, un jump cut sirve para **quitar** tiempo muerto — cortas y el
sujeto salta de postura. Con imágenes fijas eso no existe: no hay tiempo que
quitar. Pero sí se puede **añadir** ritmo, cortando entre encuadres DISTINTOS
de la MISMA imagen. El espectador ve un corte real (cambia el plano) sobre
contenido continuo (es la misma escena). Se siente ágil sin marear, porque el
cerebro no tiene que reinterpretar dónde está.

Once imágenes × tres o cuatro encuadres = treinta y tantos planos, sin generar
una sola imagen más.

Lo que lo hace homogéneo y no nervioso: **todos los cortes caen en la rejilla
del habla**. En «Idea 1» el paso medido es 0,44 s (136 pulsos por minuto), así
que los planos duran 2, 3 o 4 pasos — nunca un valor suelto. Igual que en
música: la duración cambia, el pulso no.

Y una regla que evita el mareo: **dentro de un mismo bloque los encuadres van
de fuera hacia dentro**, nunca al revés ni a saltos. La cámara parece que se
adentra en la escena mientras la voz desarrolla la idea; al cambiar de bloque,
se vuelve a abrir. Es un latido, no una coctelera.
"""
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)

# Encuadres disponibles sobre una misma imagen.
#   z  = cuánto se entra
#   ax, ay = hacia dónde (0 izquierda/arriba · 1 derecha/abajo)
#   deriva = cuánto se mueve DURANTE el plano (siempre abriendo, siempre poco)
ENCUADRES = {
    "abierto":  dict(z=1.06, ax=.50, ay=.46, deriva=-.06),
    "medio":    dict(z=1.24, ax=.48, ay=.44, deriva=-.05),
    "dentro":   dict(z=1.46, ax=.42, ay=.40, deriva=-.05),
    "detalle":  dict(z=1.72, ax=.58, ay=.52, deriva=-.04),
    "lateral":  dict(z=1.32, ax=.24, ay=.46, deriva=-.04),
    "bajo":     dict(z=1.30, ax=.52, ay=.74, deriva=-.04),
    "alto":     dict(z=1.28, ax=.50, ay=.20, deriva=-.04),
}

# Secuencias de encuadre por bloque, siempre de fuera hacia dentro.
# La variedad está en POR DÓNDE se entra, no en el sentido.
SECUENCIAS = [
    ["abierto", "medio", "dentro"],
    ["abierto", "lateral", "detalle"],
    ["abierto", "alto", "medio", "dentro"],
    ["abierto", "medio", "bajo"],
    ["abierto", "lateral", "medio", "detalle"],
    ["abierto", "bajo", "dentro"],
]

# Un plano dura un número ENTERO de pasos de la rejilla. Nunca menos de dos:
# con uno solo el ojo no llega a leer la imagen y ahí empieza el mareo.
PASOS_MIN, PASOS_MAX = 2, 5


def planos_de_bloque(inicio, fin, paso, seq, minimo=0.95):
    """Reparte el bloque en planos de duración entera en pasos de rejilla."""
    dur = fin - inicio
    n_pasos = max(PASOS_MIN, int(round(dur / paso)))
    # cuántos planos caben respetando el mínimo por plano
    max_planos = max(1, min(len(seq), n_pasos // PASOS_MIN))
    n = max(1, min(max_planos, int(dur // minimo) or 1))

    base, resto = divmod(n_pasos, n)
    repartos = [base + (1 if i < resto else 0) for i in range(n)]
    # ningún plano por debajo del mínimo ni por encima del máximo
    repartos = [max(PASOS_MIN, min(PASOS_MAX, r)) for r in repartos]

    fuera, t = [], inicio
    for i, r in enumerate(repartos):
        d = r * paso
        if i == len(repartos) - 1:
            d = fin - t                      # el último cuadra el bloque exacto
        if d <= 0.05:
            continue
        fuera.append({"inicio": round(t, 3), "duracion": round(d, 3),
                      "encuadre": seq[i % len(seq)]})
        t += d
    return fuera


def guionizar(bloques, duraciones, paso, semilla=0):
    """bloques: los del vídeo (con su texto). duraciones: lo que dura cada uno.

    Devuelve la lista de planos, cada uno sabiendo de qué lámina sale y qué
    texto le toca — el texto NO cambia con el corte: un bloque mantiene su
    frase aunque el plano cambie tres veces. Eso es lo que evita que el
    espectador se pierda.
    """
    planos, t = [], 0.0
    for i, (b, d) in enumerate(zip(bloques, duraciones)):
        seq = SECUENCIAS[(i + semilla) % len(SECUENCIAS)]
        for p in planos_de_bloque(t, t + d, paso, seq):
            p.update(lamina=i, texto=b.get("titular", ""), bloque=i)
            planos.append(p)
        t += d
    return planos


def resumen(planos, duraciones):
    n = len(planos)
    dur = [p["duracion"] for p in planos]
    return {"planos": n, "laminas": len(duraciones),
            "planos_por_lamina": round(n / max(1, len(duraciones)), 2),
            "duracion_media": round(sum(dur) / max(1, n), 2),
            "mas_corto": round(min(dur), 2), "mas_largo": round(max(dur), 2)}
