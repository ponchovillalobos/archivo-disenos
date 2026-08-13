"""Monta un tema completo: copia fondos, compone láminas, hace el reel y le pone música."""
import sys, os, glob, shutil, time
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S)
from reel3 import montar
from audio import poner_musica, medir, SEGMENTOS
P = "/Users/maity/Desktop/Confy Imagenes"; O = P + "/out"
SRC = "/Users/maity/comfy/output/reels"

def serie(tema, acento, pista, laminas, patron="{tema}-{i}", nuevo=True):
    """patron: cómo se llaman los PNG de ComfyUI para este tema.

    El lote 3 los nombró `tema-c1`, con una «c» que los anteriores no tenían,
    así que el buscador no encontraba nada y el montaje fallaba con «falta el
    fondo». El patrón se declara en vez de suponerse.

    nuevo=True toma la versión MÁS RECIENTE de cada lámina. Es lo que se quiere
    al regenerar; para rescatar una antigua se copia a mano sobre f<i>.png.
    """
    d = f"{O}/com-{tema}"; os.makedirs(d, exist_ok=True)
    fondos = []
    for i in range(1, len(laminas) + 1):
        g = sorted(glob.glob(f"{SRC}/{patron.format(tema=tema, i=i)}_*.png"),
                   reverse=nuevo)
        if not g: return None, f"falta el fondo {patron.format(tema=tema, i=i)}"
        dst = f"{d}/f{i}.png"; shutil.copy(g[0], dst); fondos.append(f"f{i}.png")
    L = [dict(l, fondo=fondos[i]) for i, l in enumerate(laminas)]
    mudo = f"{P}/_mudo-{tema}.mp4"
    n, seg, dur = montar(L, d, mudo, d + "/CAPAS", acento=acento)
    # directo a descargas: antes caía en la raíz del proyecto y el catálogo lo
    # buscaba en sitio/descargas, así que hacía falta una copia a mano que no
    # estaba en ningún módulo
    os.makedirs(f"{P}/sitio/descargas", exist_ok=True)
    final = f"{P}/sitio/descargas/reel-com-{tema}.mp4"
    poner_musica(mudo, pista, SEGMENTOS[pista], final)
    os.remove(mudo)
    dd, v, a, lufs, pico = medir(final)
    return dict(tema=tema, seg=seg, mb=os.path.getsize(final)/1e6,
                lufs=lufs, pico=pico, audio=a, dur=dd), None
