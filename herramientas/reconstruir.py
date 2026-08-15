"""Reconstruir el look de `out/A1-capa-negra.png`, la referencia del usuario.

## Cómo se encontró

El usuario señaló el fichero. `recetario.receta()` lo abrió y devolvió la receta
completa, porque cada PNG la lleva dentro. Config:

    juggernautXL_v9 + LoRA Lightning · 768×1344 · 8 pasos · CFG 1.0
    euler / sgm_uniform · semilla 101010

**Idéntica a la que se usaba hoy.** El modelo y el muestreo nunca fueron el
problema. La diferencia está entera en el TEXTO, y en tres cosas concretas:

**1. El guerrero es el SUJETO.** No un objeto en el polvo, no una silueta
diminuta al fondo: un hoplita de cuerpo entero ocupando el cuadro. Todo el
trabajo de hoy fue en la dirección contraria.

**2. El encuadre lleva el ÁNGULO DE CÁMARA.** «low camera angle looking up at
him». Es el plano heroico, y encaja con lo único que se midió que obedece de
verdad: el ángulo manda donde la distancia no.

**3. El tratamiento no es una paleta: es una hoja de cámara.** Nueve
especificaciones encadenadas —etalonaje, claroscuro, destello anamórfico,
profundidad de campo, película, grano, texturas— y, al final, **la composición
escrita**: «warrior in the lower third and dramatic sky filling the upper half».

Y el negativo son **diez términos**, no los veinticinco con veto de ánimo y de
color que arrastraba la serie espartana.

## Qué barre esto

La receta se congela y se mueve **una variable por tanda**, que es la regla que
más caro ha salido saltarse:

    fase 1  la receta EXACTA, 4 semillas          4    ¿reproduce?
    fase 2  × 8 etalonajes                       32    ¿es el teal-naranja?
    fase 3  × 6 climas y luces                   24    ¿es la lluvia?
    fase 4  × 5 ángulos de cámara                20    ¿es el contrapicado?
    fase 5  × 6 momentos del cuento              24    ¿aguanta la historia?
                                          total 104

Cada fase parte de la receta original y cambia **un solo campo**. Si una tanda
sale igual que otra, ese campo no es la causa — es la lección de haber probado
cuatro pesos de IPAdapter y obtener siempre lo mismo.
"""
import glob
import json
import os
import sys
import time

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
PROY = os.path.dirname(S)

SALIDA = "/Users/maity/comfy/output/reels"
REGISTRO = os.path.join(PROY, "reconstruir.log")
RESULTADOS = os.path.join(PROY, "reconstruir.json")

# ── LA RECETA ORIGINAL, palabra por palabra ─────────────────────────────────
BASE = {
 "escena": ("epic cinematic film still of a lone Spartan hoplite warrior "
            "standing on a windswept rocky cliff at dawn, bronze Corinthian "
            "helmet with tall crimson horsehair crest"),
 "ropa": "torn black wool cloak whipping in the wind",
 "objeto": "battle-worn bronze hoplon shield and long ash spear",
 "encuadre": ("muscular scarred physique, leather and bronze greaves, "
              "low camera angle looking up at him"),
 "aire": "heavy grey rain",
 "luz": "wet bronze reflecting a dull sky, lightning on the horizon",
 "tratamiento": ("teal and orange color grading, high contrast chiaroscuro "
                 "lighting, anamorphic lens flare, shallow depth of field, "
                 "35mm anamorphic film, heavy film grain, hyper detailed metal "
                 "and skin textures, vertical composition with the warrior in "
                 "the lower third and dramatic sky filling the upper half"),
}

# Diez términos. Ni veto de ánimo ni veto de color: la serie espartana los
# añadía y ninguno estaba aquí.
NEG = ("blurry, low quality, deformed hands, extra fingers, modern clothing, "
       "watermark, text, logo, cartoon, plastic skin, flat lighting")

TAM = (768, 1344)
SEMILLAS = [101010, 202020, 303030, 404040]

# ── LAS VARIABLES, una por fase ─────────────────────────────────────────────
ETALONAJES = {
 "original": BASE["tratamiento"],
 "sin-grado": BASE["tratamiento"].replace("teal and orange color grading, ", ""),
 "magenta": BASE["tratamiento"].replace("teal and orange color grading",
                                        "neon magenta and cyan color grading"),
 "ambar": BASE["tratamiento"].replace("teal and orange color grading",
                                      "deep indigo and warm amber color grading"),
 "sin-grano": BASE["tratamiento"].replace(", heavy film grain", ""),
 "sin-anamorfico": BASE["tratamiento"].replace(
     ", anamorphic lens flare", "").replace("35mm anamorphic film", "35mm film"),
 "sin-composicion": BASE["tratamiento"].split(", vertical composition")[0],
 "solo-grado": "teal and orange color grading, high contrast chiaroscuro lighting",
}

CLIMAS = {
 "original": ("heavy grey rain", BASE["luz"]),
 "tormenta": ("charged air before a storm, low black clouds",
              "one shaft of stormlight breaking through, wet bronze"),
 "amanecer": ("clean cold morning air, thin mist",
              "low golden sunrise raking across him, long shadow"),
 "polvo": ("dry dust hanging in the air",
           "hard low sun, bronze glowing hot, deep shadow"),
 "niebla": ("thick drifting fog", "diffused silver light, silhouette edge"),
 "nocturno": ("cold night air", "moonlight on wet bronze, distant firelight"),
}

ANGULOS = {
 "original": "low camera angle looking up at him",
 "muy-bajo": "extreme low angle from the ground looking steeply up at him",
 "altura": "camera at eye level, full body",
 "tres-cuartos": "low three quarter rear view, camera below him",
 "lejos": "establishing shot, the warrior small against an immense sky",
}

CUENTO = [
 ("kneeling alone on cracked earth, head down", "el peso"),
 ("standing in a narrow stone passage with one shaft of light on him", "la grieta"),
 ("standing against a sunlit wall, his shadow thrown huge behind him", "la sombra"),
 ("light escaping from the seams of his bronze cuirass", "la chispa"),
 ("walking on, his shield and cuirass left on the ground behind him", "la armadura"),
 ("walking away small across an immense plain at dawn", "el camino"),
]


def log(*a):
    m = time.strftime("%H:%M:%S") + "  " + " ".join(str(x) for x in a)
    print(m, flush=True)
    try:
        with open(REGISTRO, "a", buffering=1) as f:
            f.write(m + "\n")
    except OSError:
        pass


def _flujo(slug, campos, semilla):
    import lote
    c = dict(BASE, **campos)
    return lote.flujo(slug, c["escena"], c["objeto"], c["encuadre"],
                      c["aire"], c["luz"], ancho=TAM[0], alto=TAM[1],
                      ropa=c["ropa"], look=c["tratamiento"], negativo=NEG,
                      semilla=semilla)


def encolar(trabajos):
    """trabajos: [(slug, campos, semilla)]. Se salta lo ya hecho."""
    import lote
    rutas = [_flujo(s, c, m) for s, c, m in trabajos
             if not glob.glob(os.path.join(SALIDA, s + "_*.png"))]
    if rutas:
        lote.encolar(rutas)
    return len(rutas)


def esperar(patron, n, tope_min=120):
    import guardian as gd
    g = gd.Guardian(os.path.join(SALIDA, patron), normal=45.0,
                    al_avisar=lambda m: log("  guardián:", m))
    t0, ultimo = time.time(), -1
    while time.time() - t0 < tope_min * 60:
        g.esperar(45)
        h = len(glob.glob(os.path.join(SALIDA, patron)))
        if h != ultimo:
            log("   %d de %d" % (h, n))
            ultimo = h
        if h >= n:
            return True
    return False


def medir(patron):
    """Saturación, contraste y luz. La firma del look: saturado y contrastado."""
    import numpy as np
    from PIL import Image
    out = {}
    for p in sorted(glob.glob(os.path.join(SALIDA, patron))):
        try:
            a = np.asarray(Image.open(p).convert("RGB").resize((256, 256))).astype(float) / 255
        except OSError:
            continue
        mx, mn = a.max(axis=2), a.min(axis=2)
        lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
        out[os.path.basename(p).split("_")[0]] = {
            "saturacion": round(float(np.mean(np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0))), 4),
            "contraste": round(float(lum.std()), 4),
            "luz": round(float(lum.mean()), 4)}
    return out


def fase(nombre, trabajos, patron, datos):
    log("\nFASE %s · %d imágenes" % (nombre, len(trabajos)))
    encolar(trabajos)
    esperar(patron, len(trabajos))
    datos["fases"][nombre] = medir(patron)
    with open(RESULTADOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    log("  medidas %d" % len(datos["fases"][nombre]))


def main():
    log("\n" + "#" * 66)
    log("RECONSTRUCCIÓN de out/A1-capa-negra.png")
    log("config congelada · una variable por fase")
    datos = {"referencia": "out/A1-capa-negra.png", "base": BASE,
             "negativo": NEG, "fases": {}}

    fase("semillas", [("r1-s%d" % m, {}, m) for m in SEMILLAS],
         "r1-*.png", datos)
    fase("etalonaje", [("r2-%s-%d" % (k, i), {"tratamiento": v}, m)
                       for k, v in ETALONAJES.items()
                       for i, m in enumerate(SEMILLAS)],
         "r2-*.png", datos)
    fase("clima", [("r3-%s-%d" % (k, i), {"aire": a, "luz": l}, m)
                   for k, (a, l) in CLIMAS.items()
                   for i, m in enumerate(SEMILLAS[:4])],
         "r3-*.png", datos)
    fase("angulo", [("r4-%s-%d" % (k, i), {"encuadre": BASE["encuadre"].replace(
                        ANGULOS["original"], v)}, m)
                    for k, v in ANGULOS.items()
                    for i, m in enumerate(SEMILLAS[:4])],
         "r4-*.png", datos)
    fase("cuento", [("r5-%d-%d" % (j, i),
                     {"escena": "epic cinematic film still of a lone Spartan "
                                "hoplite warrior " + e +
                                ", bronze Corinthian helmet with tall crimson "
                                "horsehair crest"}, m)
                    for j, (e, _) in enumerate(CUENTO, 1)
                    for i, m in enumerate(SEMILLAS[:4])],
         "r5-*.png", datos)

    total = sum(len(v) for v in datos["fases"].values())
    log("\nTERMINADO · %d imágenes medidas" % total)
    for f, v in datos["fases"].items():
        if not v:
            continue
        mej = max(v.items(), key=lambda x: x[1]["saturacion"] * x[1]["contraste"])
        log("  %-11s mejor: %-22s sat %.3f · contraste %.3f"
            % (f, mej[0], mej[1]["saturacion"], mej[1]["contraste"]))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        log("REVENTÓ:\n" + traceback.format_exc())
        raise
