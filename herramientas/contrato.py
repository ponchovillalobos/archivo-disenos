"""El contrato: pedir lo mismo dos veces tiene que dar lo mismo.

Hasta ahora un encargo se «especificaba» escribiendo Python — la lista
`BLOQUES` dentro de `idea1.py`, el diccionario `GUIONES` dentro de
`guiones1.py`. Eso no escala a carrusel + reel + apaisado + PDF, y sobre todo
no garantiza nada: dos ejecuciones podían dar resultados distintos sin que
saltara un solo error.

Aquí hay dos ficheros y una función:

    voz/<nombre>.yaml     la identidad. Se elige UNA VEZ y se hereda.
    pedidos/<slug>.yaml   la pieza. Solo declara en qué se desvía.

    resolver(pedido, voz) → un dict SIN un solo `auto` ni `null`

`resolver()` es la garantía. Sustituye cada valor ambiguo por uno concreto y
`huella()` lo resume en 16 caracteres: si dos pedidos dan la misma huella,
producen lo mismo. Y `out/<id>/pedido-efectivo.yaml` deja escrito exactamente
con qué se ejecutó, para que dentro de seis meses se pueda reproducir.

Las cuatro fugas de congruencia que esto cierra, todas encontradas midiendo:

  1. **El sorteo de paletas dependía del orden de un diccionario.** Insertar
     una paleta en medio reasignaba el color de TODO lo ya publicado, en
     silencio. Ahora la lista va explícita y ordenada en la voz.
  2. **La semilla nunca se escribía.** `lote.flujo()` no toca el nodo del
     muestreador: bastaba con que alguien guardara la plantilla desde la
     interfaz con `randomize` para perder la reproducibilidad sin un error.
  3. **Dos políticas opuestas para elegir el fondo.** Un montador tomaba la
     versión más vieja y otro la más nueva, sobre los mismos archivos.
  4. **El ASR no fijaba la temperatura.** Whisper hace fallback cuando la
     compresión sale mal, así que el mismo audio podía dar transcripciones
     distintas y con ellas cortes de bloque distintos.
"""
import copy
import datetime
import hashlib
import json
import os
import sys

import yaml

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
PROY = os.path.dirname(S)

TIPOS_ENTRADA = {"guion", "audio", "tema"}
TIPOS_SALIDA = {"reel", "video", "carrusel_pdf", "laminas", "zip"}
MONTAJES = {"reposado", "texto-vivo"}

# lienzo por defecto de cada tipo de salida
LIENZO_POR_TIPO = {
    "reel": "reel-9-16", "video": "apaisado-16-9",
    "carrusel_pdf": "reel-9-16", "laminas": "reel-9-16", "zip": "reel-9-16",
}
EXT = {"reel": "mp4", "video": "mp4", "carrusel_pdf": "pdf", "zip": "zip"}
PREFIJO = {"reel": "reel", "video": "video", "carrusel_pdf": "carrusel",
           "zip": "laminas"}


def cargar_voz(nombre, raiz=PROY):
    p = os.path.join(raiz, "voz", nombre + ".yaml")
    if not os.path.exists(p):
        raise FileNotFoundError("no existe la voz «%s» en %s" % (nombre, p))
    return yaml.safe_load(open(p, encoding="utf-8"))


def cargar_pedido(ruta):
    return yaml.safe_load(open(ruta, encoding="utf-8"))


def validar(pedido, voz=None):
    """Lista de errores legibles. Vacía = válido. No lanza."""
    e = []
    if pedido.get("contrato") != 1:
        e.append("falta `contrato: 1` o la versión no es la 1")
    if not pedido.get("voz"):
        e.append("falta `voz`")

    pz = pedido.get("pieza") or {}
    if not pz.get("id"):
        e.append("falta `pieza.id`")
    elif not all(c.isalnum() or c == "-" for c in pz["id"]):
        e.append("`pieza.id` solo admite letras, números y guiones: %r" % pz["id"])
    if not pz.get("titulo"):
        e.append("falta `pieza.titulo`")

    en = pedido.get("entrada") or {}
    t = en.get("tipo")
    if t not in TIPOS_ENTRADA:
        e.append("`entrada.tipo` debe ser uno de %s, no %r"
                 % (sorted(TIPOS_ENTRADA), t))
    elif t == "guion" and not en.get("laminas"):
        e.append("con `entrada.tipo: guion` hacen falta `entrada.laminas`")
    elif t == "audio" and not en.get("audio"):
        e.append("con `entrada.tipo: audio` hace falta `entrada.audio`")
    elif t == "tema" and not en.get("tema"):
        e.append("con `entrada.tipo: tema` hace falta `entrada.tema`")

    if t == "audio" and en.get("audio"):
        ruta = os.path.join(PROY, en["audio"])
        if not os.path.exists(ruta):
            e.append("no encuentro el audio: %s" % en["audio"])

    sal = pedido.get("salidas") or []
    if not sal:
        e.append("no has pedido ninguna salida")
    for i, s in enumerate(sal, 1):
        if s.get("tipo") not in TIPOS_SALIDA:
            e.append("salida %d: tipo %r desconocido (usa %s)"
                     % (i, s.get("tipo"), sorted(TIPOS_SALIDA)))
        m = s.get("montaje", "reposado")
        if s.get("tipo") in ("reel", "video") and m not in MONTAJES:
            e.append("salida %d: montaje %r desconocido (usa %s)"
                     % (i, m, sorted(MONTAJES)))
        if voz and s.get("lienzo") and s["lienzo"] not in voz["lienzos"]:
            e.append("salida %d: la voz no define el lienzo %r"
                     % (i, s["lienzo"]))
        if s.get("tipo") == "carrusel_pdf" and s.get("lienzo") == "apaisado-16-9":
            e.append("salida %d: un carrusel PDF apaisado no tiene destino — "
                     "LinkedIn e Instagram consumen vertical o cuadrado" % i)

    # los topes de texto son de la voz, y hasta hoy no los miraba nadie
    if voz and t == "guion":
        topes = voz["tipografia"]["topes"]
        for i, L in enumerate(en.get("laminas") or [], 1):
            tit = (L.get("titular") or "").strip()
            if len(tit) > topes["caracteres_titular"]:
                e.append("lámina %d: el titular tiene %d caracteres y el tope "
                         "es %d — se saldrá" % (i, len(tit),
                                                topes["caracteres_titular"]))
    return e


def _paleta(voz, clave, pedida):
    """Sorteo estable contra la lista EXPLÍCITA de la voz, no contra el orden
    de un diccionario."""
    import paletas
    if pedida and pedida != "auto":
        return pedida
    lista = voz["paletas_activas"]
    h = int(hashlib.sha1(clave.encode()).hexdigest(), 16)
    n = lista[h % len(lista)]
    assert n in paletas.PALETAS, "la voz nombra una paleta que no existe: " + n
    return n


def _animo(voz, clave, pedido_):
    import paletas
    if pedido_ and pedido_ != "auto":
        return pedido_

    def _h(sal):
        return int(hashlib.sha1((sal + clave).encode()).hexdigest(), 16)
    claro = _h("luz:") % 100 < int(voz["sesgo_luz"] * 100)
    grupo = voz["animos_luminosos"] if claro else voz["animos_graves"]
    n = grupo[_h("cual:") % len(grupo)]
    assert n in paletas.ANIMOS, "la voz nombra un ánimo que no existe: " + n
    return n


def resolver(pedido, voz):
    """Devuelve el pedido sin una sola ambigüedad. Esto es lo que se ejecuta."""
    import paletas
    # copia honda con `copy`, no con json: YAML convierte `2026-08-12` en un
    # objeto date que json no serializa
    r = copy.deepcopy(pedido)
    pz, es = r["pieza"], r.setdefault("estilo", {})

    clave = es.get("clave_estilo") or pz["id"]
    es["clave_estilo"] = clave
    es["paleta"] = _paleta(voz, clave, es.get("paleta"))
    es["animo"] = _animo(voz, clave, es.get("animo"))

    acento, look, veto = paletas.PALETAS[es["paleta"]]
    _, aire, luz = (es["animo"],) + paletas.ANIMOS[es["animo"]]
    es["acento"] = es.get("acento") if es.get("acento") not in (None, "auto") else acento
    es["look"] = es.get("look") or look
    es["veto"] = es.get("veto") if es.get("veto") is not None else veto
    es["aire"] = es.get("aire") or aire
    es["luz"] = es.get("luz") or luz
    es.setdefault("negativo_extra", "")

    g = r.setdefault("generar", {})
    g.setdefault("activo", True)
    m = voz["modelo"]
    g["semilla"] = m["semilla"] if g.get("semilla") in (None, "auto") else g["semilla"]
    for k in ("pasos", "cfg", "muestreador", "planificador", "denoise"):
        g[k] = g.get(k) if g.get(k) is not None else m[k]
    g.setdefault("variar_semilla", False)

    for s in r["salidas"]:
        s.setdefault("lienzo", LIENZO_POR_TIPO[s["tipo"]])
        if s["tipo"] in ("reel", "video"):
            s.setdefault("montaje", "reposado")
        if not s.get("nombre") and s["tipo"] in EXT:
            s["nombre"] = "%s-%s.%s" % (PREFIJO[s["tipo"]], pz["id"], EXT[s["tipo"]])
        s.setdefault("crf", voz["video"]["crf"])
        s.setdefault("fps", voz["video"]["fps"])
        s["dimensiones"] = voz["lienzos"][s["lienzo"]]["salida"]
        s["latente"] = voz["lienzos"][s["lienzo"]]["latente"]

    r["_voz"] = voz["nombre"]
    return r


# lo que NO entra en la huella: cambiarlo no cambia lo que se ve
NO_DETERMINA = {"titulo", "resumen", "nota", "etiquetas", "fecha"}


def _serializable(o):
    """Las fechas de YAML son objetos date; para la huella valen como texto."""
    if isinstance(o, dict):
        return {k: _serializable(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_serializable(v) for v in o]
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    return o


def huella(resuelto):
    d = _serializable(copy.deepcopy(resuelto))
    for k in NO_DETERMINA:
        d.get("pieza", {}).pop(k, None)
    for s in d.get("salidas", []):
        s.pop("nombre", None)
    return hashlib.sha256(
        json.dumps(d, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def escribir_efectivo(resuelto, destino=None):
    d = destino or os.path.join(PROY, "out", resuelto["pieza"]["id"])
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "pedido-efectivo.yaml")
    with open(p, "w", encoding="utf-8") as f:
        f.write("# Generado por contrato.resolver(). NO editar a mano.\n"
                "# huella: %s\n" % huella(resuelto))
        yaml.safe_dump(_serializable(resuelto), f,
                       allow_unicode=True, sort_keys=False)
    return p


def plan(ruta_pedido):
    """Lee, valida y resuelve. Devuelve (resuelto, errores)."""
    ped = cargar_pedido(ruta_pedido)
    if not ped.get("voz"):
        return None, ["falta `voz` en el pedido"]
    voz = cargar_voz(ped["voz"])
    errs = validar(ped, voz)
    if errs:
        return None, errs
    return resolver(ped, voz), []


if __name__ == "__main__":
    import glob
    rutas = sys.argv[1:] or sorted(glob.glob(os.path.join(PROY, "pedidos", "*.yaml")))
    for ruta in rutas:
        r, errs = plan(ruta)
        n = os.path.basename(ruta)
        if errs:
            print("  ✗ %s" % n)
            for e in errs:
                print("      %s" % e)
            continue
        print("  ✓ %-26s huella %s · %s/%s · %d salidas: %s"
              % (n, huella(r), r["estilo"]["paleta"], r["estilo"]["animo"],
                 len(r["salidas"]),
                 ", ".join("%s(%s)" % (s["tipo"], s["lienzo"]) for s in r["salidas"])))
