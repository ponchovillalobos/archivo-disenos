"""Diez maneras distintas de maquetar una lámina.

Hasta ahora había UNA (`estudio2.plantilla`): texto arriba a la izquierda,
degradado desde arriba, siempre. Con una sola disposición, seis láminas
seguidas son seis veces la misma imagen con distintas palabras — y un carrusel
de historia se ve igual que uno de datos.

Las diez no son variaciones decorativas: cada una resuelve un problema de
lectura distinto.

  · Las que **superponen** texto sobre la foto (`alto`, `bajo`, `esquina`)
    necesitan degradado y sombra, y solo funcionan si la zona del texto tiene
    poco detalle. Son las más cinematográficas y las más frágiles.
  · Las que **separan** texto y foto (`banda`, `partido`, `marco`, `placa`)
    no necesitan degradado: el texto va sobre color plano y siempre se lee.
    Son las que aguantan cualquier imagen.
  · Las que hacen del **texto la imagen** (`cita`, `dato`, `portada`) usan la
    foto como textura de fondo, muy apagada. Para el gancho y el remate.

Regla de uso: dentro de un carrusel se alternan familias. Seis láminas
superpuestas cansan; seis separadas parecen un folleto. Lo que engancha es el
contraste entre unas y otras — de ahí `secuencia()`.

Todo se compone con las voces de `fuentes.py`, así que cualquier disposición
funciona con cualquier voz.
"""
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
from fuentes import ejes_css, voz                        # noqa: E402

W, H = 1080, 1350          # 4:5, el formato de carrusel de Instagram
MARGEN = 88
ESCALA = [32, 43, 57, 76, 101, 135]        # 32 × 1,333ⁿ

# familia de cada disposición, para poder alternarlas
FAMILIAS = {
    "superpuesta": ["alto", "bajo", "esquina"],
    "separada": ["banda", "partido", "marco", "placa"],
    "tipografica": ["cita", "dato", "portada"],
}
TODAS = [d for v in FAMILIAS.values() for d in v]


def _base(css_voz, extra):
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><style>
{css_voz}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{position:relative;background:#0b0a09}}
.foto{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.k{{font-family:P;font-weight:600;font-size:{ESCALA[0] - 6}px;letter-spacing:.22em;
  text-transform:uppercase;text-indent:-.02em}}
h1{{font-family:D;font-weight:900;line-height:.93;letter-spacing:-.022em;
  text-wrap:balance;text-indent:-.055em}}
p.c{{font-family:T;font-weight:400;font-size:{ESCALA[1]}px;line-height:1.42;
  text-wrap:pretty}}
.filete{{height:6px;border:0}}
.pie{{font-family:T;font-weight:600;font-size:{ESCALA[0]}px;letter-spacing:.06em;
  font-variant-numeric:tabular-nums}}
{extra}
</style></head><body>"""


# ---------------------------------------------------------------- superpuestas

def alto(f, k, t, c, lista, pie, ac, css, fam, tam):
    """La de siempre: texto en el tercio superior, degradado desde arriba."""
    return _base(css, f"""
.scrim{{position:absolute;inset:0;background:linear-gradient(to bottom in oklch,
  oklch(0% 0 0/.86) 0%,oklch(0% 0 0/.78) 22%,oklch(0% 0 0/.52) 45%,
  oklch(0% 0 0/.14) 68%,oklch(0% 0 0/0) 84%)}}
.caja{{position:absolute;left:{MARGEN}px;top:{MARGEN + 34}px;width:{W - 2 * MARGEN}px;
  display:flex;flex-direction:column;gap:22px}}
.k{{color:{ac}}} h1{{font-size:{tam}px;color:#fff;{ejes_css(fam['display'], opsz=144, WONK=1, wght=900)}
  text-shadow:0 2px 26px rgba(0,0,0,.55)}}
p.c{{color:#eae6e4;max-width:760px;text-shadow:0 1px 14px rgba(0,0,0,.6)}}
.filete{{width:104px;background:{ac}}}
.pie{{position:absolute;right:{MARGEN}px;bottom:{MARGEN - 14}px;color:#efeceb;
  text-shadow:0 1px 12px rgba(0,0,0,.7)}}""") + f"""
<img class="foto" src="data:image/png;base64,{f}"><div class="scrim"></div>
<div class="caja"><p class="k">{k}</p><h1>{t}</h1>{_cuerpo(c)}{_lista(lista, ac, fam)}
<hr class="filete"></div><p class="pie">{pie}</p></body></html>"""


def bajo(f, k, t, c, lista, pie, ac, css, fam, tam):
    """Texto abajo. El degradado sube desde el pie, así que la mitad superior
    de la foto queda limpia — sirve cuando el motivo está arriba."""
    return _base(css, f"""
.scrim{{position:absolute;inset:0;background:linear-gradient(to top in oklch,
  oklch(0% 0 0/.90) 0%,oklch(0% 0 0/.80) 26%,oklch(0% 0 0/.46) 50%,
  oklch(0% 0 0/.10) 72%,oklch(0% 0 0/0) 88%)}}
.caja{{position:absolute;left:{MARGEN}px;bottom:{MARGEN + 30}px;width:{W - 2 * MARGEN}px;
  display:flex;flex-direction:column;gap:20px}}
.k{{color:{ac}}} h1{{font-size:{tam}px;color:#fff;{ejes_css(fam['display'], opsz=144, WONK=1, wght=900)}
  text-shadow:0 2px 26px rgba(0,0,0,.6)}}
p.c{{color:#eae6e4;max-width:780px;text-shadow:0 1px 14px rgba(0,0,0,.65)}}
.filete{{width:104px;background:{ac}}}
.pie{{position:absolute;right:{MARGEN}px;top:{MARGEN - 10}px;color:#efeceb;
  text-shadow:0 1px 12px rgba(0,0,0,.7)}}""") + f"""
<img class="foto" src="data:image/png;base64,{f}"><div class="scrim"></div>
<div class="caja"><hr class="filete"><p class="k">{k}</p><h1>{t}</h1>{_cuerpo(c)}{_lista(lista, ac, fam)}</div>
<p class="pie">{pie}</p></body></html>"""


def esquina(f, k, t, c, lista, pie, ac, css, fam, tam):
    """Texto pequeño en una esquina y la foto casi entera. Para respirar entre
    dos láminas densas."""
    return _base(css, f"""
.scrim{{position:absolute;inset:0;background:radial-gradient(120% 90% at 12% 88%,
  oklch(0% 0 0/.88) 0%,oklch(0% 0 0/.55) 34%,oklch(0% 0 0/0) 62%)}}
.caja{{position:absolute;left:{MARGEN}px;bottom:{MARGEN}px;width:{int(W * .56)}px;
  display:flex;flex-direction:column;gap:16px}}
.k{{color:{ac}}} h1{{font-size:{int(tam * .62)}px;color:#fff;{ejes_css(fam['display'], opsz=96, WONK=1, wght=800)}}}
p.c{{color:#ded9d6;font-size:{ESCALA[0]}px}}
.filete{{width:72px;background:{ac}}}
.pie{{position:absolute;right:{MARGEN}px;bottom:{MARGEN}px;color:#efeceb}}""") + f"""
<img class="foto" src="data:image/png;base64,{f}"><div class="scrim"></div>
<div class="caja"><p class="k">{k}</p><h1>{t}</h1>{_cuerpo(c)}<hr class="filete"></div>
<p class="pie">{pie}</p></body></html>"""


# ------------------------------------------------------------------- separadas

def banda(f, k, t, c, lista, pie, ac, css, fam, tam):
    """Foto arriba, banda de color abajo con el texto. Sin degradado: el texto
    va sobre plano y se lee siempre, venga la imagen que venga."""
    alto_foto = int(H * .54)
    return _base(css, f"""
.foto{{height:{alto_foto}px;inset:auto 0 auto 0;top:0}}
.banda{{position:absolute;left:0;right:0;top:{alto_foto}px;bottom:0;background:#12100e;
  padding:{MARGEN - 20}px {MARGEN}px;display:flex;flex-direction:column;gap:18px}}
.k{{color:{ac}}} h1{{font-size:{int(tam * .82)}px;color:#f6f3f1;{ejes_css(fam['display'], opsz=120, WONK=1, wght=900)}}}
p.c{{color:#c8c2be}}
.filete{{width:104px;background:{ac}}}
.pie{{position:absolute;right:{MARGEN}px;bottom:{MARGEN - 34}px;color:#8b8380}}""") + f"""
<img class="foto" src="data:image/png;base64,{f}">
<div class="banda"><p class="k">{k}</p><h1>{t}</h1>{_cuerpo(c)}{_lista(lista, ac, fam)}<hr class="filete"></div>
<p class="pie">{pie}</p></body></html>"""


def partido(f, k, t, c, lista, pie, ac, css, fam, tam):
    """Foto a la izquierda, texto a la derecha sobre plano. La más legible de
    todas, y la que mejor aguanta un cuerpo largo."""
    return _base(css, f"""
.foto{{width:{int(W * .46)}px;inset:0 auto 0 0}}
.col{{position:absolute;left:{int(W * .46)}px;right:0;top:0;bottom:0;background:#12100e;
  padding:{MARGEN}px {MARGEN - 24}px;display:flex;flex-direction:column;
  justify-content:center;gap:20px}}
.k{{color:{ac}}} h1{{font-size:{int(tam * .60)}px;color:#f6f3f1;{ejes_css(fam['display'], opsz=96, WONK=1, wght=900)}}}
p.c{{color:#c8c2be;font-size:{ESCALA[0] + 2}px}}
.filete{{width:80px;background:{ac}}}
.pie{{position:absolute;right:{MARGEN - 24}px;bottom:{MARGEN - 40}px;color:#8b8380}}""") + f"""
<img class="foto" src="data:image/png;base64,{f}">
<div class="col"><p class="k">{k}</p><h1>{t}</h1>{_cuerpo(c)}{_lista(lista, ac, fam)}<hr class="filete"></div>
<p class="pie">{pie}</p></body></html>"""


def marco(f, k, t, c, lista, pie, ac, css, fam, tam):
    """La foto como lámina enmarcada y el texto debajo, como el pie de una
    ilustración de libro. Da aire y sensación de objeto impreso."""
    return _base(css, f"""
body{{background:#f4f1ec}}
.foto{{inset:{MARGEN - 20}px {MARGEN - 20}px auto {MARGEN - 20}px;
  height:{int(H * .58)}px;width:auto}}
.caja{{position:absolute;left:{MARGEN - 20}px;right:{MARGEN - 20}px;
  top:{int(H * .58) + MARGEN}px;display:flex;flex-direction:column;gap:16px}}
.k{{color:{ac}}} h1{{font-size:{int(tam * .66)}px;color:#17140f;{ejes_css(fam['display'], opsz=110, WONK=1, wght=800)}}}
p.c{{color:#4a443c;font-size:{ESCALA[0] + 4}px}}
.filete{{width:64px;background:{ac}}}
.pie{{position:absolute;right:{MARGEN - 20}px;bottom:{MARGEN - 46}px;color:#8d857a}}""") + f"""
<img class="foto" src="data:image/png;base64,{f}">
<div class="caja"><p class="k">{k}</p><h1>{t}</h1>{_cuerpo(c)}{_lista(lista, ac, fam, oscuro=True)}<hr class="filete"></div>
<p class="pie">{pie}</p></body></html>"""


def placa(f, k, t, c, lista, pie, ac, css, fam, tam):
    """Tarjeta flotando sobre la foto desenfocada. Para el dato duro: la
    información queda encapsulada y separada del ruido de la imagen."""
    return _base(css, f"""
.foto{{filter:blur(14px) brightness(.42);transform:scale(1.08)}}
.tarj{{position:absolute;left:{MARGEN - 26}px;right:{MARGEN - 26}px;
  top:50%;transform:translateY(-50%);background:#faf7f2;
  padding:{MARGEN - 16}px {MARGEN - 22}px;display:flex;flex-direction:column;gap:18px;
  box-shadow:0 40px 90px rgba(0,0,0,.55)}}
.k{{color:{ac}}} h1{{font-size:{int(tam * .70)}px;color:#17140f;{ejes_css(fam['display'], opsz=110, WONK=1, wght=900)}}}
p.c{{color:#4a443c}}
.filete{{width:72px;background:{ac}}}
.pie{{position:absolute;right:{MARGEN}px;bottom:{MARGEN - 30}px;color:#efeceb}}""") + f"""
<img class="foto" src="data:image/png;base64,{f}">
<div class="tarj"><p class="k">{k}</p><h1>{t}</h1>{_cuerpo(c)}{_lista(lista, ac, fam, oscuro=True)}<hr class="filete"></div>
<p class="pie">{pie}</p></body></html>"""


# ----------------------------------------------------------------- tipográficas

def cita(f, k, t, c, lista, pie, ac, css, fam, tam):
    """La frase ES la lámina. Foto casi apagada, comilla enorme de adorno.
    Para el giro del guion."""
    return _base(css, f"""
.foto{{filter:brightness(.24) saturate(.7)}}
.comilla{{position:absolute;left:{MARGEN - 30}px;top:{MARGEN - 60}px;
  font-family:D;font-size:340px;line-height:1;color:{ac};opacity:.30}}
.caja{{position:absolute;left:{MARGEN}px;right:{MARGEN}px;top:50%;
  transform:translateY(-50%);display:flex;flex-direction:column;gap:26px}}
h1{{font-size:{int(tam * 1.10)}px;color:#fff;{ejes_css(fam['display'], opsz=144, WONK=1, wght=700)}
  font-style:italic;line-height:1.02}}
.k{{color:{ac};align-self:flex-end}}
.pie{{position:absolute;right:{MARGEN}px;bottom:{MARGEN - 20}px;color:#cfc9c4}}""") + f"""
<img class="foto" src="data:image/png;base64,{f}"><div class="comilla">&ldquo;</div>
<div class="caja"><h1>{t}</h1><p class="k">{k}</p></div>
<p class="pie">{pie}</p></body></html>"""


def dato(f, k, t, c, lista, pie, ac, css, fam, tam):
    """Una cifra gigante y su explicación. El número se compone con la fuente
    de cifras, con `tabular-nums` para que no baile."""
    cifra, resto = _partir_cifra(t)
    return _base(css, f"""
.foto{{filter:brightness(.28) saturate(.75)}}
.caja{{position:absolute;left:{MARGEN}px;right:{MARGEN}px;top:50%;
  transform:translateY(-50%);display:flex;flex-direction:column;gap:14px}}
.cifra{{font-family:D;font-weight:900;font-size:{int(H * .30)}px;line-height:.82;
  color:{ac};font-variant-numeric:tabular-nums;letter-spacing:-.04em;
  {ejes_css(fam['display'], opsz=144, WONK=1, wght=900)}}}
h1{{font-size:{int(tam * .70)}px;color:#fff;{ejes_css(fam['display'], opsz=110, wght=700)}}}
.k{{color:#a49c96}} p.c{{color:#cfc9c4;max-width:820px}}
.pie{{position:absolute;right:{MARGEN}px;bottom:{MARGEN - 20}px;color:#cfc9c4}}""") + f"""
<img class="foto" src="data:image/png;base64,{f}">
<div class="caja"><p class="k">{k}</p><div class="cifra">{cifra}</div>
<h1>{resto}</h1>{_cuerpo(c)}</div><p class="pie">{pie}</p></body></html>"""


def portada(f, k, t, c, lista, pie, ac, css, fam, tam):
    """Solo el titular, al mayor tamaño que aguante. Primera lámina."""
    return _base(css, f"""
.scrim{{position:absolute;inset:0;background:linear-gradient(to bottom in oklch,
  oklch(0% 0 0/.62) 0%,oklch(0% 0 0/.42) 50%,oklch(0% 0 0/.72) 100%)}}
.caja{{position:absolute;left:{MARGEN}px;right:{MARGEN}px;bottom:{MARGEN + 24}px;
  display:flex;flex-direction:column;gap:24px}}
h1{{font-size:{int(tam * 1.34)}px;color:#fff;{ejes_css(fam['display'], opsz=144, WONK=1, wght=900)}
  line-height:.88;text-shadow:0 4px 40px rgba(0,0,0,.6)}}
.k{{color:{ac}}} .filete{{width:150px;background:{ac}}}
.pie{{position:absolute;right:{MARGEN}px;top:{MARGEN}px;color:#efeceb}}""") + f"""
<img class="foto" src="data:image/png;base64,{f}"><div class="scrim"></div>
<div class="caja"><p class="k">{k}</p><h1>{t}</h1><hr class="filete"></div>
<p class="pie">{pie}</p></body></html>"""


# ---------------------------------------------------------------------- apoyos

def _cuerpo(c):
    return f'<p class="c">{c}</p>' if c else ""


def _lista(lista, ac, fam, oscuro=False):
    if not lista:
        return ""
    col = "#4a443c" if oscuro else "#e6e2e0"
    filas = "".join(f"<b>{t}</b><span>{g}</span>" for t, g in lista)
    return (f'<div class="lst" style="display:grid;'
            f'grid-template-columns:max-content 1fr;column-gap:26px;row-gap:13px;'
            f'align-items:baseline;max-width:860px;font-family:T;'
            f'font-size:{ESCALA[1] - 5}px;line-height:1.3;color:{col}">'
            f'<style>.lst b{{font-family:D;font-weight:800;'
            f'font-size:{ESCALA[1]}px;color:{ac};letter-spacing:-.01em}}</style>'
            f'{filas}</div>')


def _partir_cifra(t):
    """Separa la cifra que abre el titular del resto. «93,3 % de la gente» →
    («93,3 %», «de la gente»). Si no abre con cifra, devuelve el titular entero
    como resto y la disposición se comporta como un titular normal."""
    ps = t.split()
    cif = []
    for p in ps:
        if any(ch.isdigit() for ch in p) or p in ("%", "de"):
            cif.append(p)
            if "%" in p or (cif and len(cif) >= 2):
                break
        else:
            break
    if not cif:
        return "", t
    return " ".join(cif), " ".join(ps[len(cif):])


DISPOSICIONES = {
    "alto": alto, "bajo": bajo, "esquina": esquina,
    "banda": banda, "partido": partido, "marco": marco, "placa": placa,
    "cita": cita, "dato": dato, "portada": portada,
}


def componer(disposicion, fondo_b64, kicker, titular, cuerpo=None, lista=None,
             pie="", acento="#d8353d", nombre_voz="fuente-primaria",
             tam=ESCALA[4]):
    css, fam = voz(nombre_voz)
    fn = DISPOSICIONES[disposicion]
    return fn(fondo_b64, kicker, titular, cuerpo, lista, pie, acento, css, fam, tam)


def secuencia(n=6, semilla=0, con_portada=True):
    """Reparte disposiciones a lo largo de un carrusel alternando familias.

    Seis superpuestas cansan; seis separadas parecen un folleto. Lo que
    engancha es el contraste, así que nunca van dos de la misma familia
    seguidas y la densa (`placa`, `partido`) cae en el centro, que es donde
    va el dato del guion.
    """
    orden = ["superpuesta", "separada", "superpuesta", "tipografica",
             "separada", "superpuesta"]
    fuera = []
    for i in range(n):
        fam = orden[i % len(orden)]
        opciones = FAMILIAS[fam]
        fuera.append(opciones[(i + semilla) % len(opciones)])
    if con_portada and n:
        fuera[0] = "portada"
    return fuera
