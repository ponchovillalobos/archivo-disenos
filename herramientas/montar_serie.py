"""Monta un tema completo: copia fondos, compone láminas, hace el reel y le pone música."""
import sys, os, glob, shutil, time
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S)
from reel3 import montar
from audio import poner_musica, medir, SEGMENTOS
P = "/Users/maity/Desktop/Confy Imagenes"; O = P + "/out"
SRC = "/Users/maity/comfy/output/reels"

def serie(tema, acento, pista, laminas):
    d = f"{O}/com-{tema}"; os.makedirs(d, exist_ok=True)
    fondos = []
    for i in range(1, 7):
        g = sorted(glob.glob(f"{SRC}/{tema}-{i}_*.png"))
        if not g: return None, f"falta el fondo {tema}-{i}"
        dst = f"{d}/f{i}.png"; shutil.copy(g[0], dst); fondos.append(f"f{i}.png")
    L = [dict(l, fondo=fondos[i]) for i, l in enumerate(laminas)]
    mudo = f"{P}/_mudo-{tema}.mp4"
    n, seg, dur = montar(L, d, mudo, d + "/CAPAS", acento=acento)
    final = f"{P}/reel-com-{tema}.mp4"
    poner_musica(mudo, pista, SEGMENTOS[pista], final)
    os.remove(mudo)
    dd, v, a, lufs, pico = medir(final)
    return dict(tema=tema, seg=seg, mb=os.path.getsize(final)/1e6,
                lufs=lufs, pico=pico, audio=a, dur=dd), None
