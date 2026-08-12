"""Motor de composición v2 — Chromium headless.

Frente a Pillow gana lo que de verdad importaba:
  · ejes de fuente variable (opsz cambia el DIBUJO de la letra según el tamaño)
  · text-wrap: balance  (reparte las líneas del titular)
  · versalitas y features OpenType
  · degradado del scrim en OKLCH (no se ensucia en los medios tonos)

Sistema numérico fijo, no valores sueltos:
  escala modular  base 32 · ratio 1.333  ->  32 43 57 76 101 135
  rejilla         lienzo 1080×1350 · margen 88 · columna 904
"""
import base64, json, os, subprocess, sys

PROY = "/Users/maity/Desktop/Confy Imagenes"
FUENTES = os.path.join(PROY, "fuentes")
S = os.path.dirname(os.path.abspath(__file__))
BRAVE = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

W, H, MARGEN = 1080, 1350, 88
ESCALA = [32, 43, 57, 76, 101, 135]          # 32 × 1.333^n


def b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()


FUENTE_TIT = b64(os.path.join(FUENTES, "Fraunces.ttf"))
FUENTE_TXT = b64(os.path.join(FUENTES, "Newsreader.ttf"))


def plantilla(fondo_b64, kicker, titular, cuerpo, lista, pie, acento, tam_tit):
    """Devuelve el HTML de una lámina. `lista` es [(término, glosa), ...] o None."""
    bloque_lista = ""
    if lista:
        # todas las filas comparten la misma rejilla para que las glosas
        # queden alineadas entre sí, no una por término.
        filas = "".join(
            f'<b>{t}</b><span>{g}</span>' for t, g in lista)
        bloque_lista = f'<div class="virtudes">{filas}</div>'
    bloque_cuerpo = f'<p class="cuerpo">{cuerpo}</p>' if cuerpo else ""

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><style>
@font-face{{font-family:Fraunces;src:url(data:font/ttf;base64,{FUENTE_TIT})format("truetype");
  font-weight:100 900;font-display:block}}
@font-face{{font-family:Newsreader;src:url(data:font/ttf;base64,{FUENTE_TXT})format("truetype");
  font-weight:200 800;font-display:block}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{position:relative;background:#000}}
.foto{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
/* scrim en OKLCH: el degradado no se ensucia en los medios tonos */
.scrim{{position:absolute;inset:0;background:linear-gradient(
  to bottom in oklch,
  oklch(0% 0 0 / .86) 0%,  oklch(0% 0 0 / .78) 22%,
  oklch(0% 0 0 / .52) 45%, oklch(0% 0 0 / .14) 68%, oklch(0% 0 0 / 0) 84%)}}
.caja{{position:absolute;left:{MARGEN}px;top:{MARGEN + 34}px;width:{W - 2 * MARGEN}px;
  display:flex;flex-direction:column;gap:22px}}
.kicker{{font-family:Newsreader;font-weight:600;font-size:{ESCALA[0] - 6}px;
  font-variation-settings:"opsz" 20;letter-spacing:.22em;text-transform:uppercase;
  color:{acento};text-indent:-.02em}}
h1{{font-family:Fraunces;font-weight:900;font-size:{tam_tit}px;line-height:.93;
  /* opsz 144 = corte display: más estrecho y contrastado que el de texto */
  font-variation-settings:"opsz" 144,"SOFT" 0,"WONK" 1;
  letter-spacing:-.022em;color:#fff;text-wrap:balance;
  text-indent:-.055em;                      /* margen óptico */
  text-shadow:0 2px 26px rgba(0,0,0,.55)}}
.cuerpo{{font-family:Newsreader;font-weight:400;font-size:{ESCALA[1]}px;line-height:1.42;
  font-variation-settings:"opsz" 44;color:#eae6e4;max-width:760px;
  text-wrap:pretty;text-shadow:0 1px 14px rgba(0,0,0,.6)}}
.virtudes{{display:grid;grid-template-columns:max-content 1fr;
  column-gap:26px;row-gap:13px;align-items:baseline;max-width:860px}}
/* la columna del término se dimensiona sola: con ancho fijo, "Makoto" y
   "Chūgi" se salían y chocaban con la glosa. */
.virtudes b,.virtudes span{{font-family:Newsreader;font-size:{ESCALA[1] - 5}px;line-height:1.3;
  font-variation-settings:"opsz" 38;color:#e6e2e0;
  text-shadow:0 1px 12px rgba(0,0,0,.65)}}
.virtudes b{{font-family:Fraunces;font-weight:800;font-size:{ESCALA[1]}px;color:{acento};
  font-variation-settings:"opsz" 60,"WONK" 1;letter-spacing:-.01em}}
.filete{{width:104px;height:6px;background:{acento};margin-top:4px}}
.pie{{position:absolute;right:{MARGEN}px;bottom:{MARGEN - 14}px;font-family:Newsreader;
  font-weight:600;font-size:{ESCALA[0]}px;font-variation-settings:"opsz" 24;
  color:#efeceb;letter-spacing:.06em;font-variant-numeric:tabular-nums;
  text-shadow:0 1px 12px rgba(0,0,0,.7)}}
</style></head><body>
<img class="foto" src="data:image/png;base64,{fondo_b64}" alt="">
<div class="scrim"></div>
<div class="caja">
  <p class="kicker">{kicker}</p>
  <h1>{titular}</h1>
  {bloque_cuerpo}{bloque_lista}
  <div class="filete"></div>
</div>
<p class="pie">{pie}</p>
</body></html>"""


def render(html, salida):
    tmp = os.path.join(S, "_lamina.html")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(html)
    r = subprocess.run(
        [BRAVE, "--headless", "--disable-gpu", "--hide-scrollbars",
         "--default-background-color=00000000",
         "--window-size=%d,%d" % (W, H),
         "--screenshot=" + salida, "file://" + tmp],
        capture_output=True, text=True, timeout=120)
    if not os.path.exists(salida):
        raise RuntimeError("Chromium no generó la imagen:\n" + r.stderr[-600:])
    return salida


def componer(serie, laminas, acento, dir_fondos, dir_salida):
    os.makedirs(dir_salida, exist_ok=True)
    hechas = []
    for i, L in enumerate(laminas, 1):
        fondo = os.path.join(dir_fondos, L["fondo"])
        if not os.path.exists(fondo):
            print("   ! falta el fondo:", L["fondo"])
            continue
        html = plantilla(b64(fondo), L["kicker"], L["titular"],
                         L.get("cuerpo"), L.get("lista"),
                         "%d / %d" % (i, len(laminas)), acento,
                         L.get("tam", ESCALA[4]))
        out = os.path.join(dir_salida, "%s-%02d.png" % (serie, i))
        render(html, out)
        hechas.append(out)
        print("   %d/%d  %s" % (i, len(laminas), os.path.basename(out)))
    return hechas
