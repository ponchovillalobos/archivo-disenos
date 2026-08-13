"""Montador de reels v2.

Tres cosas nuevas frente a v1:

1. DURACIÓN POR TIEMPO DE LECTURA. Cada lámina dura lo que se tarda en
   leerla, no cuatro segundos fijos. Base 1,6 s (fijar la vista) más
   caracteres/19 — el ritmo de subtítulo cómodo en español, ~17-19 car/s.
   Acotado entre 3,4 y 9,5 s para que ninguna se eternice.

2. TRANSICIONES VARIADAS Y SUTILES. Cuatro tipos que se alternan, ninguno
   llamativo: disolución, paso por negro, empuje vertical y disolución con
   escala. La variedad es lo que hace que no se note el patrón.

3. MOVIMIENTO ALTERNADO. El zoom no siempre entra: alterna acercarse y
   alejarse, y varía el punto de anclaje. Dos láminas seguidas nunca se
   mueven igual.
"""
from PIL import Image
import base64, math, os, subprocess

import av
import numpy as np

PROY = "/Users/maity/Desktop/Confy Imagenes"
FUENTES = os.path.join(PROY, "fuentes")
S = os.path.dirname(os.path.abspath(__file__))
BRAVE = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

W, H = 1080, 1920
MARGEN, Y_TEXTO = 72, 300
ESCALA = [32, 43, 57, 76, 101, 135]
FPS = 30

BASE_SEG, CAR_POR_SEG = 1.6, 19.0
MIN_SEG, MAX_SEG = 4.4, 10.5


def b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()


TIT, TXT = b64(FUENTES + "/Fraunces.ttf"), b64(FUENTES + "/Newsreader.ttf")


def duracion(L):
    """Segundos que necesita esta lámina para leerse sin agobio."""
    n = len(L["titular"])
    if L.get("cuerpo"):
        n += len(L["cuerpo"].replace("<br>", " ").replace("<i>", "").replace("</i>", ""))
    for t, g in L.get("lista", []):
        n += len(t) + len(g) + 2
    return max(MIN_SEG, min(MAX_SEG, BASE_SEG + n / CAR_POR_SEG))


def html_texto(kicker, titular, cuerpo, lista, pie, acento, tam):
    # Anclaje del bloque de texto. En vertical va desde ARRIBA (el diseño de la
    # serie pone el titular en el tercio superior). En apaisado va desde ABAJO:
    # anclando arriba, un bloque de dos líneas deja medio cuadro vacío y otro de
    # cuatro se sale. Anclado abajo aguanta cualquier número de líneas y respeta
    # la franja donde el reproductor pone sus controles.
    ANCLA = ("bottom:%dpx;" % Y_TEXTO) if W > H else ("top:%dpx;" % Y_TEXTO)
    bloque = ""
    if lista:
        bloque = '<div class="v">' + "".join(
            f"<b>{t}</b><span>{g}</span>" for t, g in lista) + "</div>"
    elif cuerpo:
        bloque = f'<p class="c">{cuerpo}</p>'
    kick = f'<p class="k">{kicker}</p>' if kicker else ""
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><style>
@font-face{{font-family:F;src:url(data:font/ttf;base64,{TIT})format("truetype");
  font-weight:100 900;font-display:block}}
@font-face{{font-family:N;src:url(data:font/ttf;base64,{TXT})format("truetype");
  font-weight:200 800;font-display:block}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;background:transparent;overflow:hidden}}
.caja{{position:absolute;left:{MARGEN}px;{ANCLA}width:{W - 2 * MARGEN}px;
  display:flex;flex-direction:column;gap:24px}}
.k{{font-family:N;font-weight:600;font-size:{ESCALA[0] - 4}px;
  font-variation-settings:"opsz" 20;letter-spacing:.24em;text-transform:uppercase;
  color:{acento};text-shadow:0 2px 18px rgba(0,0,0,.9)}}
h1{{font-family:F;font-weight:900;font-size:{tam}px;line-height:.94;
  font-variation-settings:"opsz" 144,"SOFT" 0,"WONK" 1;letter-spacing:-.022em;
  color:#fff;text-wrap:balance;text-indent:-.055em;
  text-shadow:0 3px 30px rgba(0,0,0,.92),0 1px 4px rgba(0,0,0,.8)}}
.c{{font-family:N;font-weight:400;font-size:{ESCALA[1] + 3}px;line-height:1.4;
  font-variation-settings:"opsz" 46;color:#f0eceb;max-width:820px;text-wrap:pretty;
  text-shadow:0 2px 20px rgba(0,0,0,.92)}}
.v{{display:grid;grid-template-columns:max-content 1fr;column-gap:26px;row-gap:14px;
  align-items:baseline}}
.v b,.v span{{font-family:N;font-size:{ESCALA[1]}px;line-height:1.28;
  font-variation-settings:"opsz" 40;color:#f0eceb;text-shadow:0 2px 18px rgba(0,0,0,.92)}}
.v b{{font-family:F;font-weight:800;font-size:{ESCALA[1] + 5}px;color:{acento};
  font-variation-settings:"opsz" 60,"WONK" 1}}
.f{{width:110px;height:7px;background:{acento};margin-top:6px;
  box-shadow:0 2px 14px rgba(0,0,0,.7)}}
.p{{position:absolute;left:{MARGEN}px;top:{Y_TEXTO - 78}px;font-family:N;font-weight:700;
  font-size:{ESCALA[0] - 2}px;font-variation-settings:"opsz" 22;color:#fff;opacity:.55;
  letter-spacing:.14em;font-variant-numeric:tabular-nums;
  text-shadow:0 2px 14px rgba(0,0,0,.9)}}
</style></head><body>
<p class="p">{pie}</p>
<div class="caja">{kick}<h1>{titular}</h1>{bloque}<div class="f"></div></div>
</body></html>"""


def capa_texto(html, salida):
    tmp = os.path.join(S, "_capa2.html")
    open(tmp, "w", encoding="utf-8").write(html)
    subprocess.run([BRAVE, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--default-background-color=00000000",
                    "--window-size=%d,%d" % (W, H),
                    "--screenshot=" + salida, "file://" + tmp],
                   capture_output=True, timeout=120)
    if not os.path.exists(salida):
        raise RuntimeError("Chromium no generó la capa de texto")
    return Image.open(salida).convert("RGBA")


def _scrim(alto=1400, alpha=150, curva=2.2):
    """Degradado bajo el texto.

    alpha era 234 sobre 255 —un negro al 92 %— cubriendo el 73 % del alto. Con
    eso el montaje partía la luminosidad de la imagen por la mitad (49,9 → 24)
    y duplicaba la sombra (36 % → 74 %). Llevábamos horas ajustando la
    GENERACIÓN cuando el estrago estaba aquí, después.

    150 con curva 2,2 da contraste de sobra bajo el texto y devuelve la imagen.
    """
    g = Image.new("L", (1, alto))
    px = g.load()
    for y in range(alto):
        v = alpha * (1 - y / alto) ** curva
        # medio nivel de ruido antes de cuantizar: sin esto la cola del
        # degradado sale en franjas planas de hasta 36 px sobre un cielo liso
        px[0, y] = max(0, min(255, int(v + (0.5 if y % 2 else -0.5))))
    return g.resize((W, alto))


SCRIM = _scrim()
NEGRO = Image.new("RGB", (W, SCRIM.height), (0, 0, 0))
SUAVE = lambda t: t * t * (3 - 2 * t)          # arranque y frenada suaves


# ---- movimiento del fondo: 4 patrones que se alternan ----
MOVS = [
    dict(z0=1.00, z1=1.07, ax=.50, ay=.42),    # acercarse, centrado
    dict(z0=1.07, z1=1.00, ax=.50, ay=.45),    # alejarse
    dict(z0=1.05, z1=1.09, ax=.38, ay=.36),    # acercarse desplazado
    dict(z0=1.08, z1=1.02, ax=.60, ay=.50),    # alejarse desplazado
]


def fotograma(fondo, t, mov):
    z = mov["z0"] + (mov["z1"] - mov["z0"]) * SUAVE(t)
    aw, ah = int(W * z), int(H * z)
    im = fondo.resize((aw, ah), Image.LANCZOS)
    x, y = int((aw - W) * mov["ax"]), int((ah - H) * mov["ay"])
    im = im.crop((x, y, x + W, y + H))
    im.paste(NEGRO, (0, 0), SCRIM)
    return im


# ---- transiciones: sutiles, y ninguna se repite dos veces seguidas ----
TRANS = ["disolver", "negro", "empujar", "escalar"]


def transicion(a, b, t, tipo):
    """a = fotograma saliente, b = entrante, t en [0,1]."""
    s = SUAVE(t)
    if tipo == "negro":                       # paso breve por negro
        if s < .5:
            return Image.blend(a, Image.new("RGB", a.size, (0, 0, 0)), s * 2)
        return Image.blend(Image.new("RGB", a.size, (0, 0, 0)), b, (s - .5) * 2)
    if tipo == "empujar":                     # la nueva entra por abajo
        d = int(H * (1 - s))
        out = Image.new("RGB", (W, H))
        out.paste(a.crop((0, d, W, H)), (0, 0))
        out.paste(b.crop((0, 0, W, d)), (0, H - d))
        return Image.blend(out, b, s * .35)   # un punto de disolución: menos brusco
    if tipo == "escalar":                     # la nueva crece muy poco al entrar
        z = 1.045 - .045 * s
        bw, bh = int(W * z), int(H * z)
        gr = b.resize((bw, bh), Image.LANCZOS).crop(
            ((bw - W) // 2, (bh - H) // 2, (bw - W) // 2 + W, (bh - H) // 2 + H))
        return Image.blend(a, gr, s)
    return Image.blend(a, b, s)               # disolver


def montar(laminas, fondos_dir, salida_mp4, dir_capas, acento="#d8353d",
           seg_transicion=0.62, bitrate=8_000_000):
    os.makedirs(dir_capas, exist_ok=True)
    piezas, duraciones = [], []
    for i, L in enumerate(laminas, 1):
        fondo = Image.open(os.path.join(fondos_dir, L["fondo"])).convert("RGB")
        if fondo.size != (W, H):
            fondo = fondo.resize((W, H), Image.LANCZOS)
        capa = capa_texto(
            html_texto(L.get("kicker", ""), L["titular"], L.get("cuerpo"),
                       L.get("lista"), "%02d / %02d" % (i, len(laminas)),
                       acento, L.get("tam", ESCALA[4])),
            os.path.join(dir_capas, "capa-%02d.png" % i))
        d = duracion(L)
        piezas.append((fondo, capa, MOVS[(i - 1) % len(MOVS)]))
        duraciones.append(d)
        print("   lámina %d — %.1f s" % (i, d))

    n_tr = int(seg_transicion * FPS)
    cont = av.open(salida_mp4, "w")
    st = cont.add_stream("h264_videotoolbox", rate=FPS)
    st.width, st.height, st.pix_fmt = W, H, "yuv420p"
    st.bit_rate = bitrate

    def compuesta(i, k, n):
        fondo, capa, mov = piezas[i]
        base = fotograma(fondo, k / max(1, n - 1), mov)
        base.paste(capa, (0, 0), capa)
        return base

    total = 0
    for i, d in enumerate(duraciones):
        n = int(d * FPS)
        for k in range(n):
            img = compuesta(i, k, n)
            if i + 1 < len(piezas) and k >= n - n_tr:
                t = (k - (n - n_tr)) / max(1, n_tr - 1)
                n_sig = int(duraciones[i + 1] * FPS)
                img = transicion(img, compuesta(i + 1, int(t * n_tr), n_sig),
                                 t, TRANS[i % len(TRANS)])
            for p in st.encode(av.VideoFrame.from_ndarray(
                    np.asarray(img.convert("RGB")), format="rgb24")):
                cont.mux(p)
            total += 1
    for p in st.encode():
        cont.mux(p)
    cont.close()
    return total, total / FPS, duraciones
