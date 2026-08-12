"""Genera TODOS los recursos de un proyecto: láminas con texto, PDF y ZIP.

Cada proyecto queda con la misma estructura, siempre:
  out/com-<tema>/
    ├── f1..f6.png          fondos sin texto
    ├── CAPAS/capa-NN.png   capa de texto transparente
    ├── LAMINAS/l-NN.png    fondo + texto (lo que se publica)
    └── FOTOGRAMAS/         muestras del vídeo
  sitio/descargas/
    ├── reel-com-<tema>.mp4
    ├── carrusel-com-<tema>.pdf
    └── laminas-com-<tema>.zip
"""
import os, sys, glob, zipfile
from PIL import Image

P = "/Users/maity/Desktop/Confy Imagenes"
W, H = 1080, 1920


def laminas(tema):
    """Recompone fondo + capa de texto y guarda las 6 láminas publicables."""
    d = f"{P}/out/com-{tema}"
    out = f"{d}/LAMINAS"; os.makedirs(out, exist_ok=True)
    hechas = []
    for i in range(1, 7):
        fondo = f"{d}/f{i}.png"; capa = f"{d}/CAPAS/capa-{i:02d}.png"
        if not (os.path.exists(fondo) and os.path.exists(capa)):
            return None, f"faltan piezas de la lámina {i}"
        im = Image.open(fondo).convert("RGB")
        # mismo encuadre que el vídeo: escalar a lo ancho y recortar centrado-alto
        nh = round(im.height * W / im.width)
        im = im.resize((W, nh), Image.LANCZOS)
        top = int((nh - H) * .42) if nh > H else 0
        im = im.crop((0, max(0, top), W, max(0, top) + H)) if nh > H else im.resize((W, H))
        # el mismo scrim del vídeo
        from reel2 import SCRIM, NEGRO
        im.paste(NEGRO, (0, 0), SCRIM)
        c = Image.open(capa).convert("RGBA")
        im.paste(c, (0, 0), c)
        p = f"{out}/l-{i:02d}.png"; im.save(p); hechas.append(p)
    return hechas, None


def pdf_y_zip(tema, titulo):
    ls, err = laminas(tema)
    if err: return None, err
    pags = [Image.open(p).convert("RGB") for p in ls]
    pdf = f"{P}/sitio/descargas/carrusel-com-{tema}.pdf"
    pags[0].save(pdf, "PDF", resolution=150.0, save_all=True, append_images=pags[1:])
    z = f"{P}/sitio/descargas/laminas-com-{tema}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
        for i, p in enumerate(ls, 1):
            t = f"/tmp/_l{tema}{i}.jpg"
            Image.open(p).convert("RGB").save(t, "JPEG", quality=92, optimize=True)
            f.write(t, "%02d-%s.jpg" % (i, tema)); os.remove(t)
    return (os.path.getsize(pdf)/1e6, os.path.getsize(z)/1e6), None
