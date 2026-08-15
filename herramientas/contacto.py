"""Hoja de contacto: ver muchas imágenes a la vez para poder auditarlas.

## Por qué existe

La regla dura del proyecto es **auditar cada imagen**. Con seis láminas se hace
abriéndolas. Con 104 no: se mira la primera, la segunda, y a la décima ya no se
está mirando, se está pasando.

Y el fallo que eso deja pasar es siempre el mismo — **caras y manos**. SDXL las
rompe de forma estructural, y un dedo de más se ve al instante en una rejilla y
no se ve nunca revisando de una en una.

La contact sheet es como se ha auditado material fotográfico desde siempre, y
por el mismo motivo: **la comparación es lo que delata al fallo.** Una mano rara
aislada parece una mano; junto a once manos bien, salta.

## Qué marca

Debajo de cada miniatura va su nombre, para poder pedir la regeneración de esa y
solo esa — que es la otra regla: se regenera la imagen, no el lote.
"""
import glob
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)

SALIDA = "/Users/maity/comfy/output/reels"


def hoja(patron, destino, columnas=6, ancho=320, pie=26, margen=8):
    """Monta la rejilla. `patron` es un glob relativo a la carpeta de salida.

    320 px de ancho por miniatura no es capricho: por debajo de ~280 una mano
    de seis dedos ya no se distingue, y auditar deja de servir para nada.
    """
    from PIL import Image, ImageDraw, ImageFont
    ps = sorted(glob.glob(os.path.join(SALIDA, patron)))
    if not ps:
        return None

    try:
        f = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 13)
    except OSError:
        f = ImageFont.load_default()

    ims = []
    for p in ps:
        try:
            im = Image.open(p).convert("RGB")
        except OSError:
            continue
        im.thumbnail((ancho, ancho * 3), Image.LANCZOS)
        ims.append((os.path.basename(p).split("_")[0], im))
    if not ims:
        return None

    alto = max(i.height for _, i in ims)
    filas = (len(ims) + columnas - 1) // columnas
    W = columnas * (ancho + margen) + margen
    H = filas * (alto + pie + margen) + margen
    hoja = Image.new("RGB", (W, H), (18, 16, 17))
    d = ImageDraw.Draw(hoja)

    for k, (nombre, im) in enumerate(ims):
        c, r = k % columnas, k // columnas
        x = margen + c * (ancho + margen) + (ancho - im.width) // 2
        y = margen + r * (alto + pie + margen)
        hoja.paste(im, (x, y))
        d.text((margen + c * (ancho + margen), y + alto + 6), nombre,
               font=f, fill=(190, 180, 178))

    hoja.save(destino, "PNG")
    return {"imagenes": len(ims), "destino": destino,
            "tam": "%d×%d" % (W, H)}


if __name__ == "__main__":
    patron = sys.argv[1] if len(sys.argv) > 1 else "r1-*.png"
    dest = sys.argv[2] if len(sys.argv) > 2 else "/tmp/contacto.png"
    r = hoja(patron, dest)
    print("  %s" % (r or "sin imágenes que casen"))
