"""Mide si un personaje se mantiene entre imágenes. Con números, no a ojo.

«¿Se parecen?» no es una pregunta que se pueda contestar mirando: dos personas
ven cosas distintas y ninguna puede comparar veinte combinaciones. Hace falta
una cifra.

## Qué se mide y por qué así

**Similitud semántica con CLIP.** Se codifica cada imagen con el mismo
codificador visual que usa IPAdapter —CLIP-ViT-H-14, que ya está descargado— y
se compara el coseno entre vectores. Eso mide si el modelo «ve» lo mismo, no si
los píxeles coinciden.

La diferencia importa: dos fotos del mismo elefante desde ángulos opuestos
tienen píxeles completamente distintos y CLIP las reconoce como el mismo animal.
Un hash perceptual diría que no se parecen en nada.

**Se compara TODO contra TODO**, no cada una contra la primera. Una serie puede
tener la primera imagen rara y las otras cinco perfectamente coherentes entre
sí; medir contra la primera lo escondería.

## Cómo leer el número

Sobre pares del mismo sujeto en escenas distintas, la referencia práctica:

    > 0,85   el mismo personaje, sin duda
    0,75-0,85 el mismo, con variaciones de ángulo o luz
    0,60-0,75 parecido pero probablemente otro individuo
    < 0,60   son sujetos distintos

La **desviación** importa tanto como la media: una serie con 0,80 de media y
poca dispersión es homogénea; con la misma media y mucha dispersión hay imágenes
sueltas que rompen.
"""
import glob
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)

_modelo = None
_proceso = None


def _cargar():
    """CLIP de Hugging Face, no el .safetensors suelto de ComfyUI.

    Se baja una vez (~1,7 GB) y queda en la caché. Se usa el mismo tamaño de
    codificador que IPAdapter (ViT-H) para que la medida hable de lo mismo que
    el condicionamiento."""
    global _modelo, _proceso
    if _modelo is None:
        import torch
        from transformers import CLIPModel, CLIPProcessor
        nombre = "laion/CLIP-ViT-H-14-laion2B-s32B-b79K"
        _proceso = CLIPProcessor.from_pretrained(nombre)
        _modelo = CLIPModel.from_pretrained(nombre, dtype=torch.float32).eval()
    return _modelo, _proceso


def vectores(rutas):
    import torch
    from PIL import Image
    modelo, proceso = _cargar()
    ims = [Image.open(p).convert("RGB") for p in rutas]
    ent = proceso(images=ims, return_tensors="pt")
    with torch.no_grad():
        v = modelo.get_image_features(**ent)
    # transformers 5 devuelve un objeto, no el tensor. Se acepta cualquiera de
    # las dos formas para que esto no se rompa al actualizar la librería.
    # transformers 5 devuelve `BaseModelOutputWithPooling`, que además es un
    # diccionario: `getattr` no basta y hay que buscar por clave. El vector útil
    # es `pooler_output`, la representación global de la imagen.
    if not torch.is_tensor(v):
        for clave in ("image_embeds", "pooler_output"):
            cand = v[clave] if clave in v else None
            if cand is not None and torch.is_tensor(cand):
                v = cand
                break
        else:
            raise TypeError("no encuentro el vector de imagen; claves: %s"
                            % list(v.keys()))
    return (v / v.norm(dim=-1, keepdim=True)).cpu().numpy()


def coherencia(rutas):
    """Devuelve la media y la desviación de TODOS los pares, y el par peor."""
    import numpy as np
    if len(rutas) < 2:
        return None
    v = vectores(rutas)
    n = len(rutas)
    pares = [(i, j, float(v[i] @ v[j])) for i in range(n) for j in range(i + 1, n)]
    s = np.array([p[2] for p in pares])
    peor = min(pares, key=lambda p: p[2])
    return {"n": n, "media": round(float(s.mean()), 3),
            "desviacion": round(float(s.std()), 3),
            "minimo": round(float(s.min()), 3),
            "maximo": round(float(s.max()), 3),
            "par_peor": (os.path.basename(rutas[peor[0]]),
                         os.path.basename(rutas[peor[1]]), round(peor[2], 3))}


def veredicto(media):
    if media > 0.85:
        return "el mismo personaje, sin duda"
    if media > 0.75:
        return "el mismo, con variación de ángulo o luz"
    if media > 0.60:
        return "parecido, probablemente otro individuo"
    return "sujetos distintos"


def de_patron(patron):
    rutas = sorted(glob.glob(patron))
    return (coherencia(rutas), rutas) if rutas else (None, [])


def comparar(series):
    """series: {nombre: patrón}. Imprime la tabla ordenada por coherencia."""
    filas = []
    for nombre, patron in series.items():
        r, rutas = de_patron(patron)
        if r:
            filas.append((nombre, r))
    filas.sort(key=lambda x: -x[1]["media"])
    print("  %-26s  n   media   desv   mín    veredicto" % "serie")
    for nombre, r in filas:
        print("   %-26s %d   %.3f  %.3f  %.3f  %s"
              % (nombre, r["n"], r["media"], r["desviacion"], r["minimo"],
                 veredicto(r["media"])))
    return filas


if __name__ == "__main__":
    comparar({
        "rápido (8 pasos, cfg 1)": "/Users/maity/comfy/output/reels/elef-*_*.png",
        "calidad (30 pasos, cfg 5.5)": "/Users/maity/comfy/output/reels/elefQ-*_*.png",
        "calidad + IPAdapter 0.75": "/Users/maity/comfy/output/reels/elefIP-*_*.png",
    })
