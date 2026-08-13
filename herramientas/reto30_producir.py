"""Produce el reto de 30 días sin vigilancia, y publica según avanza.

Nace de un fallo medido: la primera tanda se degradó de 57 s a **17 minutos por
imagen** porque el swap llegó a 10.396 MB. A ese ritmo las 180 imágenes eran 33
horas en vez de 3. Reiniciar ComfyUI liberó 7 GB de golpe y devolvió el ritmo.

Así que este productor hace tres cosas que el anterior no hacía:

  1. **Mide el ritmo real** y reinicia ComfyUI cuando una imagen tarda más del
     triple de lo normal. No espera a un umbral de swap: el swap es la causa,
     pero el síntoma que importa es el tiempo por imagen.
  2. **Encola por tandas pequeñas.** Reiniciar pierde la cola, así que una cola
     de 180 significa perder 180. Con tandas de 18 se pierde como mucho una.
  3. **Monta y publica cada día en cuanto tiene sus seis imágenes**, en vez de
     esperar al final. Si algo se tuerce a mitad, lo hecho ya está arriba.

Y no repite trabajo: al arrancar mira qué imágenes existen ya y encola solo lo
que falta, así que se puede matar y relanzar sin perder nada.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
PROY = os.path.dirname(S)
SALIDA = "/Users/maity/comfy/output/reels"
BIN = "/Users/maity/comfy-env/bin"
ENV = dict(os.environ, PATH=BIN + ":" + os.environ.get("PATH", ""))
REG = os.path.join(PROY, "reto30.log")

TANDA = 18            # imágenes por tanda: al reiniciar se pierde como mucho una
NORMAL = 60           # segundos por imagen en condiciones sanas
FACTOR_ALARMA = 3.0   # por encima de esto, algo va mal y se reinicia
ENC = ("wide cinematic shot, ancient Sparta, bronze and stone, no people or one "
       "tiny distant silhouette seen from behind, no faces, no hands, vast space")


def di(m):
    linea = "%s  %s" % (time.strftime("%H:%M:%S"), m)
    with open(REG, "a", buffering=1) as f:
        f.write(linea + "\n")
    print(" ", linea, flush=True)


def cola():
    try:
        with urllib.request.urlopen("http://127.0.0.1:8188/queue", timeout=10) as r:
            q = json.load(r)
        return len(q.get("queue_running", [])) + len(q.get("queue_pending", []))
    except Exception:
        return -1


def swap_mb():
    s = subprocess.run(["sysctl", "-n", "vm.swapusage"],
                       capture_output=True, text=True).stdout
    m = re.search(r"used\s*=\s*([\d.]+)M", s)
    return float(m.group(1)) if m else 0.0


def reiniciar():
    di("reiniciando ComfyUI (swap %.0f MB)" % swap_mb())
    subprocess.run([BIN + "/comfy", "stop"], capture_output=True, env=ENV)
    time.sleep(8)
    subprocess.Popen(
        [BIN + "/comfy", "--workspace", "/Users/maity/comfy", "launch",
         "--background", "--", "--listen", "127.0.0.1", "--port", "8188",
         "--use-pytorch-cross-attention"],
        env=dict(ENV, PYTORCH_ENABLE_MPS_FALLBACK="1"),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(45):
        if cola() >= 0:
            di("ComfyUI de vuelta · swap %.0f MB" % swap_mb())
            return True
        time.sleep(5)
    di("ComfyUI no volvió")
    return False


def hechas(dia):
    return [i for i in range(1, 7)
            if glob.glob("%s/esp%02d-%d_*.png" % (SALIDA, dia, i))]


def faltan_todas():
    from reto30 import DIAS
    return [(d, i) for d in sorted(DIAS) for i in range(1, 7)
            if i not in hechas(d)]


def encolar(pares, plan):
    import paletas
    from lote import flujo
    from reto30 import escenas
    n = 0
    for dia, i in pares:
        p = plan["%d" % dia] if "%d" % dia in plan else plan[dia]
        aire, luz = paletas.ANIMOS[p["animo"]]
        esc = escenas(dia)[i - 1]
        r = flujo("esp%02d-%d" % (dia, i), "epic cinematic film still of " + esc,
                  esc.split(",")[0], ENC, aire, luz,
                  ancho=720, alto=1280, paleta=p["paleta"])
        n += subprocess.run([BIN + "/comfy", "--skip-prompt", "run",
                             "--workflow", r], capture_output=True,
                            env=ENV, timeout=300).returncode == 0
    return n


def montar_dia(dia, plan):
    """Monta el día y lo deja en descargas. Devuelve el resumen o None."""
    from audio import SEGMENTOS, medir, poner_musica
    from reel3 import montar
    from reto30 import laminas
    p = plan.get("%d" % dia, plan.get(dia))
    d = os.path.join(PROY, "out", "esp-%02d" % dia)
    os.makedirs(d, exist_ok=True)
    for i in range(1, 7):
        g = sorted(glob.glob("%s/esp%02d-%d_*.png" % (SALIDA, dia, i)),
                   reverse=True)
        if not g:
            return None
        shutil.copy(g[0], "%s/f%d.png" % (d, i))
    mudo = os.path.join(PROY, "_mudo-esp%02d.mp4" % dia)
    montar(laminas(dia), d, mudo, d + "/CAPAS", acento=p["acento"])
    _componer_laminas(d, len(laminas(dia)))
    final = os.path.join(PROY, "sitio", "descargas", "reel-esp-%02d.mp4" % dia)
    os.makedirs(os.path.dirname(final), exist_ok=True)
    pista = p["pista"]
    poner_musica(mudo, pista, SEGMENTOS.get(pista, 0), final)
    os.remove(mudo)
    dd, v, a, lufs, pico = medir(final)
    return {"dia": dia, "mb": os.path.getsize(final) / 1e6, "seg": dd,
            "lufs": lufs, "pico": pico}


def _componer_laminas(d, n):
    """Fondo + capa de texto = lámina. SIN ESTO EL PROYECTO NO APARECE.

    El montador solo dejaba las capas transparentes y el MP4. La ficha del
    portal exige `LAMINAS/l-NN.png`, así que `piezas()` devolvía vacío y el
    catálogo descartaba el proyecto **con un `continue`, sin un solo error**:
    cinco vídeos existían en disco y ninguno aparecía en la página.
    """
    from PIL import Image
    import reel2
    import reel3
    reel3.formato(1080, 1920)
    lam = os.path.join(d, "LAMINAS")
    os.makedirs(lam, exist_ok=True)
    for i in range(1, n + 1):
        f = os.path.join(d, "f%d.png" % i)
        c = os.path.join(d, "CAPAS", "capa-%02d.png" % i)
        if not (os.path.exists(f) and os.path.exists(c)):
            continue
        fondo = Image.open(f).convert("RGB").resize((1080, 1920), Image.LANCZOS)
        fondo.paste(reel2.NEGRO, (0, 0), reel2.SCRIM)
        capa = Image.open(c).convert("RGBA")
        fondo.paste(capa, (0, 0), capa)
        fondo.save(os.path.join(lam, "l-%02d.png" % i))


def publicar():
    import catalogo
    try:
        catalogo.construir(minimo_proyectos=38)
        return True
    except Exception as e:
        di("catálogo: %s" % str(e)[:120])
        return False


def main():
    from guardian import Guardian, salud
    from reto30 import DIAS
    plan = json.load(open(os.path.join(PROY, "reto30-plan.json"), encoding="utf-8"))
    # reparto de música: pistas épicas medidas, sin repetir en días seguidos
    sel = json.load(open(os.path.join(PROY, "fuentes", "musica",
                                      "seleccion-espartana.json"), encoding="utf-8"))
    for k in list(plan):
        plan[k]["pista"] = sel[int(k) % len(sel)] + ".mp3"

    montados = set()
    # el guardián mide el ritmo real y reinicia solo. Ya no se duerme a ciegas:
    # tres veces se degradó la generación y las tres lo descubrió el usuario.
    g = Guardian(SALIDA + "/esp*.png", normal=NORMAL, factor=FACTOR_ALARMA,
                 al_avisar=di)
    di("arranco · faltan %d imágenes · salud %s"
       % (len(faltan_todas()), salud()))

    while True:
        pend = faltan_todas()
        if not pend:
            di("todas las imágenes están")
            break

        if cola() <= 2:
            n = encolar(pend[:TANDA], plan)
            di("tanda de %d encolada · faltan %d · ritmo %.0f s/imagen"
               % (n, len(pend), g.ritmo))

        g.esperar(60)

        # montar y publicar lo que ya esté completo
        nuevos = [d for d in sorted(DIAS)
                  if d not in montados and len(hechas(d)) == 6]
        for d in nuevos:
            try:
                r = montar_dia(d, plan)
                if r:
                    montados.add(d)
                    di("día %02d montado · %.0f s · %.1f MB · %.1f LUFS"
                       % (d, r["seg"], r["mb"], r["lufs"]))
            except Exception as e:
                di("día %02d falló: %s" % (d, str(e)[:110]))
        if nuevos:
            publicar()
            di("portal actualizado · %d días listos" % len(montados))

    # última pasada por si quedó alguno
    for d in sorted(DIAS):
        if d not in montados and len(hechas(d)) == 6:
            try:
                r = montar_dia(d, plan)
                if r:
                    montados.add(d)
                    di("día %02d montado (final)" % d)
            except Exception as e:
                di("día %02d falló: %s" % (d, str(e)[:110]))
    publicar()
    di("TERMINADO · %d de %d días · %s" % (len(montados), len(DIAS), g.resumen()))


if __name__ == "__main__":
    main()
