"""¿La imagen cuenta SU escena, o el modelo ignoró lo que le pedimos?

Esta métrica existe por un error propio. Medíamos solo coherencia de personaje
—cuánto se parecen las seis imágenes entre sí— y celebrábamos un 0,990. Pero un
0,990 se consigue de la peor forma posible: **generando seis veces la misma
imagen**. Si el modelo desobedece las escenas y repite el mismo plano, la
coherencia sale perfecta y el cuento no existe.

O sea que la coherencia sola no solo es insuficiente: **premia el fracaso**.

## Cómo se mide la obediencia

CLIP sabe puntuar cuánto se parece una imagen a un texto. Con eso se monta una
prueba de identificación: se puntúa CADA imagen contra TODAS las escenas, no
solo contra la suya.

    imagen 3  vs  escena 1 ....... 0,21
              vs  escena 2 ....... 0,22
              vs  escena 3 ....... 0,29   ← la suya, y gana
              vs  escena 4 ....... 0,20

Si cada imagen reconoce su propia escena, el modelo obedeció. Si la imagen 3 se
parece más a la escena 5, es que pintó otra cosa.

Dos cifras salen de ahí:

  **aciertos** — cuántas imágenes identifican su propia escena. 6 de 6 es
  obediencia total; 1 de 6 es azar puro.

  **margen** — cuánto le saca cada imagen a su escena frente a la media de las
  demás. Los aciertos son binarios y esconden los casos justos; el margen dice
  si ganó por goleada o por un pelo. Un margen alto es la señal de que las seis
  imágenes son escenas de verdad distintas.

## Las dos juntas, y no cada una por su lado

    coherencia alta + margen alto ..... lo que buscamos: mismo personaje,
                                        seis momentos distintos
    coherencia alta + margen bajo ..... trampa: seis veces la misma imagen
    coherencia baja + margen alto ..... seis escenas buenas, seis personajes
    ambas bajas ....................... no funciona nada

Por eso `puntuar()` devuelve siempre las dos, y `nota()` solo da un aprobado
cuando las dos pasan. Nunca se decide un ganador con una sola cifra.

## El texto se recorta a 77 tokens

CLIP corta ahí, igual que al generar. Para medir se usan descripciones CORTAS de
cada escena —una línea, lo esencial— no el prompt entero de generación. Un
prompt de 158 tokens medido con un codificador que lee 77 mediría la mitad.
"""
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)

import coherencia                                     # noqa: E402


def vectores_texto(textos):
    """Codifica los textos con el mismo CLIP que las imágenes, para que vivan
    en el mismo espacio y el coseno signifique algo."""
    import torch
    modelo, proceso = coherencia._cargar()
    ent = proceso(text=textos, return_tensors="pt", padding=True,
                  truncation=True, max_length=77)
    with torch.no_grad():
        v = modelo.get_text_features(**ent)
    # transformers 5 devuelve un objeto-diccionario en vez del tensor pelado.
    # Mismo apaño que en coherencia.vectores: buscar por clave, no con getattr.
    if not torch.is_tensor(v):
        for clave in ("text_embeds", "pooler_output"):
            cand = v[clave] if clave in v else None
            if cand is not None and torch.is_tensor(cand):
                v = cand
                break
        else:
            raise TypeError("no encuentro el vector de texto; claves: %s"
                            % list(v.keys()))
    return (v / v.norm(dim=-1, keepdim=True)).cpu().numpy()


def adherencia(rutas, escenas):
    """rutas[i] debe corresponder a escenas[i]. Devuelve aciertos y margen."""
    import numpy as np
    if len(rutas) != len(escenas):
        raise ValueError("%d imágenes contra %d escenas: no se pueden emparejar"
                         % (len(rutas), len(escenas)))
    n = len(rutas)
    if n < 2:
        return None
    vi = coherencia.vectores(rutas)
    vt = vectores_texto(escenas)
    m = vi @ vt.T                       # m[i][j] = imagen i contra escena j

    aciertos, margenes, fallos = 0, [], []
    for i in range(n):
        propia = m[i][i]
        otras = np.delete(m[i], i)
        if int(np.argmax(m[i])) == i:
            aciertos += 1
        else:
            fallos.append((i + 1, int(np.argmax(m[i])) + 1))
        margenes.append(float(propia - otras.mean()))

    return {"n": n, "aciertos": aciertos,
            "margen": round(float(np.mean(margenes)), 4),
            "margen_min": round(float(np.min(margenes)), 4),
            "confusiones": fallos}


# Umbrales. No son opinión: el margen se calibró contra series ya vistas —las
# que copiaban el encuadre daban margen ≈ 0,00-0,01, y la serie E/G que sí
# obedeció la escena dio claramente por encima.
MIN_COHERENCIA = 0.90      # lo que pidió el usuario: 90-95 % de parecido
MIN_MARGEN = 0.020         # por debajo de esto, las escenas no se distinguen
MIN_ACIERTOS = 0.66        # dos tercios identifican su propia escena


def fidelidad(rutas, ficha):
    """¿Sale el personaje que pedimos? Cada imagen contra la ficha, en texto.

    Esta métrica existe porque la coherencia estaba midiendo lo que no era. El
    coseno entre dos imágenes completas codifica el fondo, el encuadre y la luz
    tanto como al sujeto: dos fotos casi iguales puntúan 0,99 aunque el
    personaje haya cambiado, y dos escenas distintas del MISMO personaje puntúan
    bajo aunque sea idéntico. Pedir «0,90 de coherencia con seis escenas
    distintas» era casi una contradicción.

    Comparar cada imagen contra la FICHA en texto rompe esa trampa: el texto no
    dice nada del fondo, así que la puntuación habla del personaje y de nada
    más. No mide que las seis se parezcan entre sí; mide que las seis se
    parezcan a lo que pedimos, que es lo que de verdad queríamos.

    Lo caro y exacto sería recortar al sujeto y comparar los recortes —es lo que
    hace la literatura—, pero hace falta un segmentador, y los detectores
    entrenados con fotos fallan justo donde más nos importa: acuarela, tinta y
    vector plano. Esto no necesita descargar nada y funciona igual en los siete
    estilos."""
    import numpy as np
    vi = coherencia.vectores(rutas)
    vt = vectores_texto([ficha])[0]
    s = np.array([float(v @ vt) for v in vi])
    return {"media": round(float(s.mean()), 4),
            "minimo": round(float(s.min()), 4),
            "peor": int(np.argmin(s)) + 1}


def puntuar(rutas, escenas, ficha=None):
    """Las tres métricas de una vez, que es como hay que mirarlas.

        parecido   se parecen entre sí (la vieja «coherencia»)
        margen     cada una cuenta SU escena
        fidelidad  el personaje es el que pedimos

    `parecido` alto ya no es un mérito por sí solo: con seis escenas de verdad
    distintas tiene que bajar. Se conserva porque un desplome delata que el
    personaje se perdió, pero quien manda para la identidad es `fidelidad`."""
    c = coherencia.coherencia(rutas)
    a = adherencia(rutas, escenas)
    if not c or not a:
        return None
    r = {"coherencia": c["media"], "desviacion": c["desviacion"],
         "minimo": c["minimo"], "aciertos": a["aciertos"], "n": a["n"],
         "margen": a["margen"], "margen_min": a["margen_min"],
         "confusiones": a["confusiones"]}
    if ficha:
        f = fidelidad(rutas, ficha)
        r["fidelidad"] = f["media"]
        r["fidelidad_min"] = f["minimo"]
        r["peor_imagen"] = f["peor"]
    return r


MIN_FIDELIDAD = 0.33      # calibrado con las series ya vistas, no inventado


def nota(p):
    """El veredicto sale de FIDELIDAD y ACIERTOS. El parecido es informativo.

    Antes exigía `coherencia >= 0,90` como si fuera un mérito, y eso quedó
    obsoleto el mismo día que se escribió `fidelidad`: con seis escenas distintas
    de verdad el parecido **tiene que bajar**. Pedirlo alto era pedir la trampa.

    El fallo se vio en la serie del guerrero: siete imágenes con el personaje
    impecable y la historia inexistente, y el veredicto dijo «escenas bien,
    personaje se pierde» — justo al revés de lo que se veía en pantalla. La tabla
    ya se había corregido; el veredicto se quedó atrás.

    Manda `aciertos`, que es lo único que dice si cada imagen cuenta SU escena.
    """
    if not p:
        return "sin datos"
    fid = p.get("fidelidad")
    ok_f = fid >= MIN_FIDELIDAD if fid is not None else p["coherencia"] >= MIN_COHERENCIA
    ok_a = p["aciertos"] / p["n"] >= MIN_ACIERTOS
    ok_m = p["margen"] >= MIN_MARGEN

    if ok_f and ok_a and ok_m:
        return "APROBADO"
    if ok_f and not ok_a:
        return "TRAMPA: personaje bien, escenas repetidas"
    if ok_a and not ok_f:
        return "escenas bien, personaje se pierde"
    return "no llega"


def tabla(resultados):
    """resultados: {nombre: puntuación}. Ordena por lo que de verdad importa.

    El criterio de orden cambió después de la asamblea. Antes mandaba el
    parecido entre imágenes, y eso premiaba justo al que copiaba el plano. Ahora
    manda la FIDELIDAD al personaje —cuando está medida— y el parecido pasa a
    ser informativo.

    Sobre la escala de `fidelidad`: el coseno CLIP entre texto e imagen NO va de
    0 a 1 como el de imagen contra imagen. Los valores buenos rondan 0,20-0,35 y
    un 0,9 no existe. Por eso no hay umbral fijo aquí: lo que vale es el ORDEN
    entre estilos, y el umbral se calibrará cuando estén las 42 medidas. Poner
    un número redondo antes de tener los datos sería inventárselo."""
    filas = [(n, p) for n, p in resultados.items() if p]
    hay_fid = any("fidelidad" in p for _, p in filas)
    if hay_fid:
        filas.sort(key=lambda x: (x[1]["margen"] >= MIN_MARGEN,
                                  x[1].get("fidelidad", 0)), reverse=True)
        ls = ["  %-14s fidelid.  margen  parecido  acierta  veredicto" % "serie"]
        for n, p in filas:
            ls.append("   %-14s  %.4f   %+.3f   %.3f    %d/%d    %s"
                      % (n, p.get("fidelidad", 0), p["margen"], p["coherencia"],
                         p["aciertos"], p["n"], nota(p)))
    else:
        filas.sort(key=lambda x: (x[1]["margen"] >= MIN_MARGEN,
                                  x[1]["coherencia"]), reverse=True)
        ls = ["  %-22s coher.  desv   margen  acierta  veredicto" % "serie"]
        for n, p in filas:
            ls.append("   %-22s %.3f  %.3f  %+.3f   %d/%d    %s"
                      % (n, p["coherencia"], p["desviacion"], p["margen"],
                         p["aciertos"], p["n"], nota(p)))
    return "\n".join(ls), filas
