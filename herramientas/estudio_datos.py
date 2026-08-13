"""Vuelca todo lo que el estudio visual necesita saber, en un solo JSON.

El estudio (`sitio/estudio.html`) es una página estática: no puede importar
Python. Así que todo lo que decide cómo sale una pieza —paletas con su color
real, ánimos con su descripción, lienzos, disposiciones de carrusel, voces
tipográficas y los pedidos que ya existen— se vuelca aquí y se incrusta en la
página.

Se incrusta, no se enlaza: en `file://` el navegador bloquea `fetch()` y la
página saldría en blanco. Ya nos pasó una vez con el catálogo.

Además genera las MUESTRAS: un PNG pequeño por paleta y por disposición, para
que elegir sea mirar y no leer. Una paleta descrita con palabras no se puede
elegir; una paleta que se ve, sí.
"""
import base64
import glob
import io
import json
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
PROY = os.path.dirname(S)

import contrato                                    # noqa: E402
import disposiciones                               # noqa: E402
import paletas                                     # noqa: E402
from fuentes import CATALOGO, VOCES                # noqa: E402

MUESTRAS = os.path.join(PROY, "sitio", "muestras")


def _duo(nombre):
    """Los dos tonos con que se pinta la muestra de una paleta."""
    from grado import DUOS
    return DUOS.get(nombre, ((20, 20, 22), (230, 230, 230)))


def muestra_paleta(nombre, ancho=96, alto=140):
    """Degradado de dos tonos + la banda del acento. Es la paleta, no un icono."""
    from PIL import Image, ImageDraw
    import numpy as np
    som, luz = (np.array(c, float) for c in _duo(nombre))
    y = np.linspace(0, 1, alto)[:, None, None]
    arr = som + (luz - som) * y
    im = Image.fromarray(np.repeat(arr.astype("uint8"), ancho, axis=1))
    d = ImageDraw.Draw(im)
    ac = paletas.PALETAS[nombre][0]
    d.rectangle([0, alto - 16, ancho, alto], fill=ac)
    b = io.BytesIO()
    im.save(b, "PNG")
    return base64.b64encode(b.getvalue()).decode()


def volcar():
    os.makedirs(MUESTRAS, exist_ok=True)
    voz = contrato.cargar_voz("fuente-primaria")

    pal = []
    for n in voz["paletas_activas"] + voz["paletas_fuera_de_sorteo"]:
        ac, look, veto = paletas.PALETAS[n]
        pal.append({"nombre": n, "acento": ac,
                    "look": " ".join(look.split())[:150],
                    "veto": veto,
                    "sorteo": n in voz["paletas_activas"],
                    "muestra": muestra_paleta(n)})

    anim = []
    for n, (aire, luz) in paletas.ANIMOS.items():
        anim.append({"nombre": n, "aire": aire, "luz": luz,
                     "luminoso": n in voz["animos_luminosos"]})

    disp = []
    for n in disposiciones.TODAS:
        fam = next(f for f, v in disposiciones.FAMILIAS.items() if n in v)
        doc = (disposiciones.DISPOSICIONES[n].__doc__ or "").strip().split("\n")[0]
        disp.append({"nombre": n, "familia": fam, "nota": doc})

    peds = []
    for r in sorted(glob.glob(os.path.join(PROY, "pedidos", "*.yaml"))):
        crudo = contrato.cargar_pedido(r)
        res, errs = contrato.plan(r)
        peds.append({
            "archivo": os.path.basename(r),
            "crudo": contrato._serializable(crudo),
            "errores": errs,
            "huella": contrato.huella(res) if res else None,
            "paleta": res["estilo"]["paleta"] if res else None,
            "animo": res["estilo"]["animo"] if res else None,
            "acento": res["estilo"]["acento"] if res else None,
            "salidas": [{"tipo": s["tipo"], "lienzo": s["lienzo"],
                         "montaje": s.get("montaje"), "nombre": s.get("nombre")}
                        for s in (res or {}).get("salidas", [])],
        })

    return {
        "voz": {"nombre": voz["nombre"], "titulo": voz["titulo_publico"],
                "lema": voz["lema"], "prohibido": voz.get("prohibido", [])},
        "paletas": pal,
        "animos": anim,
        "disposiciones": disp,
        "lienzos": [{"nombre": k, **v} for k, v in voz["lienzos"].items()],
        "tipografias": [{"nombre": k, "display": v[0], "texto": v[1], "palo": v[2]}
                        for k, v in VOCES.items()],
        "familias": [{"nombre": k, "papel": v[1], "ejes": list(v[2]), "nota": v[3]}
                     for k, v in CATALOGO.items()],
        "tipos_salida": sorted(contrato.TIPOS_SALIDA),
        "montajes": sorted(contrato.MONTAJES),
        "tipos_entrada": sorted(contrato.TIPOS_ENTRADA),
        "pedidos": peds,
    }


if __name__ == "__main__":
    d = volcar()
    p = os.path.join(PROY, "sitio", "estudio-datos.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    print("  %d paletas · %d ánimos · %d disposiciones · %d pedidos · %.0f KB"
          % (len(d["paletas"]), len(d["animos"]), len(d["disposiciones"]),
             len(d["pedidos"]), os.path.getsize(p) / 1024))
