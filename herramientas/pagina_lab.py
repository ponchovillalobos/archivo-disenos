"""Construye la página del laboratorio: el cuento en seis estilos.

## Por qué una página nueva y no una sección más del índice

`index.html` es un archivo de piezas terminadas: cada tarjeta es un carrusel o
un vídeo que ya se publicó. Esto es otra cosa —una prueba con su método, sus
números y sus conclusiones— y mezclarlo ensuciaría las dos.

Comparten casa: la misma tipografía, la misma paleta, el mismo cambio de tema
claro/oscuro. Se navega de una a otra por arriba.

## Dos maneras de mirar lo mismo, y las dos hacen falta

    POR ESTILO   eliges un estilo y recorres las seis escenas.
                 Contesta: ¿este estilo cuenta el cuento?

    POR ESCENA   eliges una escena y ves los seis estilos a la vez.
                 Contesta: ¿qué estilo aguanta mejor al personaje?

La segunda es la que responde a la pregunta del estudio, porque poner las seis
versiones del mismo momento una al lado de otra es la única forma de ver a ojo
lo que la coherencia mide con un número.

## Las imágenes van a `sitio/img-lab/`, aparte a propósito

`catalogo.py` barre `sitio/img/` y borra lo que no reconoce — así se limpian las
derivadas huérfanas. Si estas imágenes vivieran ahí, el primer barrido se las
llevaría en silencio. Carpeta propia, y el barrido no las ve nunca.

Se generan en AVIF (ligero) con JPEG de respaldo, en dos anchos.
"""
import glob
import json
import os
import re
import sys
from html import escape

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
PROY = os.path.dirname(S)
SITIO = os.path.join(PROY, "sitio")
IMGLAB = os.path.join(SITIO, "img-lab")
SALIDA = "/Users/maity/comfy/output/reels"
PAGINA = os.path.join(SITIO, "laboratorio.html")
TIPO = os.path.join(SITIO, "tipografia.css")

import estudio_estilos as ee                          # noqa: E402

ANCHOS = [560, 1000]

NOMBRES = {
 "foto": ("Fotográfico", "Fotografía de naturaleza, luz natural, 85 mm"),
 "animacion3d": ("Animación 3D", "Formas redondeadas, ojos expresivos, render de estudio"),
 "tinta": ("Tinta", "Línea negra a mano, tramado cruzado, papel blanco"),
 "acuarela": ("Acuarela", "Aguadas translúcidas, grano de papel, bordes sueltos"),
 "comic": ("Cómic", "Contorno grueso, color plano, trama de puntos"),
 "vector": ("Vector plano", "Formas geométricas, paleta corta, sin contorno"),
}


def derivar(origen, base):
    """AVIF ligero + JPEG de respaldo, en dos anchos. Se salta el trabajo si
    el original no ha cambiado: comparar mtime y tamaño es instantáneo frente a
    releer y recomprimir un PNG de 1,8 MB."""
    from PIL import Image
    os.makedirs(IMGLAB, exist_ok=True)
    st = os.stat(origen)
    marca = os.path.join(IMGLAB, base + ".sello")
    sello = "%d-%d" % (st.st_mtime, st.st_size)
    salida = {"avif": {}, "jpg": None}
    if os.path.exists(marca) and open(marca).read() == sello:
        for a in ANCHOS:
            n = "%s-%d.avif" % (base, a)
            if os.path.exists(os.path.join(IMGLAB, n)):
                salida["avif"][a] = n
        j = "%s-%d.jpg" % (base, ANCHOS[0])
        if os.path.exists(os.path.join(IMGLAB, j)):
            salida["jpg"] = j
        if salida["jpg"] and len(salida["avif"]) == len(ANCHOS):
            return salida

    im = Image.open(origen).convert("RGB")
    w0, h0 = im.size
    for a in ANCHOS:
        red = im.resize((a, round(h0 * a / w0)), Image.LANCZOS) if a < w0 else im
        n = "%s-%d.avif" % (base, a)
        red.save(os.path.join(IMGLAB, n), "AVIF", quality=58)
        salida["avif"][a] = n
        if a == ANCHOS[0]:
            j = "%s-%d.jpg" % (base, a)
            red.save(os.path.join(IMGLAB, j), "JPEG", quality=80, optimize=True)
            salida["jpg"] = j
    open(marca, "w").write(sello)
    return salida


def tipografia():
    """Saca los @font-face de index.html a un CSS propio.

    Son ~4 MB de fuente en base64. Duplicarlos dentro de la página nueva la
    haría inservible; enlazándolos, el navegador los cachea y sirven para las
    dos páginas."""
    idx = os.path.join(SITIO, "index.html")
    if not os.path.exists(idx):
        return False
    h = open(idx, encoding="utf-8").read()
    caras = re.findall(r"@font-face\{[^}]*\}", h)
    if not caras:
        return False
    open(TIPO, "w", encoding="utf-8").write("\n".join(caras))
    return True


def reunir():
    """Qué imágenes existen, por estilo y escena. Mira el disco, no una lista."""
    datos = {}
    for e in ee.ESTILOS:
        fila = []
        for i in range(1, len(ee.ESCENAS) + 1):
            c = sorted(glob.glob(os.path.join(SALIDA, "est-%s-%d_*.png" % (e, i))))
            fila.append(derivar(c[-1], "%s-%d" % (e, i)) if c else None)
        datos[e] = fila
    return datos


def medidas():
    p = os.path.join(PROY, "seis.json")
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


CSS = """
:root{
  --papel:#faf7f6; --tarjeta:#fffdfd; --tinta:#171214; --media:#6d6165; --leve:#9c9095;
  --filete:#e9e1e0; --sangre:#a81d26; --hueso:#efe7e5;
  --display:Fraunces,"Didot",Georgia,serif;
  --texto:Newsreader,"Iowan Old Style",Georgia,serif;
  --ui:Recursive,-apple-system,"Segoe UI",Helvetica,sans-serif;
  --mono:Recursive,ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --papel:#100c0d; --tarjeta:#191314; --tinta:#f6f1f0; --media:#a89ea1; --leve:#786e71;
  --filete:#2b2223; --sangre:#e85159; --hueso:#241c1d;
}}
:root[data-theme="dark"]{
  --papel:#100c0d; --tarjeta:#191314; --tinta:#f6f1f0; --media:#a89ea1; --leve:#786e71;
  --filete:#2b2223; --sangre:#e85159; --hueso:#241c1d;
}
*{box-sizing:border-box}
[hidden]{display:none!important}
body{margin:0;background:var(--papel);color:var(--tinta);font:16px/1.6 var(--ui);
  -webkit-font-smoothing:antialiased}
.w{max-width:1240px;margin:0 auto;padding:0 26px}
img{display:block;max-width:100%}
a{color:inherit}
button{font:inherit;color:inherit;background:none;border:none;cursor:pointer}
:focus-visible{outline:2px solid var(--sangre);outline-offset:3px;border-radius:3px}

/* --- barra de navegación entre las páginas de la casa --- */
.barra{display:flex;gap:20px;align-items:center;padding:16px 0;
  border-bottom:1px solid var(--filete);font-size:13px}
.barra a{color:var(--media);text-decoration:none;letter-spacing:.03em}
.barra a:hover{color:var(--tinta)}
.barra a[aria-current]{color:var(--sangre);font-weight:700}
.barra .der{margin-left:auto}

header{padding:52px 0 26px}
.eyebrow{margin:0;font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;
  font-weight:700;color:var(--sangre)}
h1{font-family:var(--display);font-weight:700;margin:12px 0 0;
  font-size:clamp(46px,8vw,92px);line-height:.88;letter-spacing:-.042em}
.lema{margin:18px 0 0;font-family:var(--display);font-style:italic;
  font-size:clamp(17px,2vw,21px);color:var(--media);max-width:48ch}
.regla{height:1px;background:var(--filete);margin-top:30px;position:relative}
.regla::after{content:"";position:absolute;left:0;top:0;width:72px;height:3px;
  background:var(--sangre)}

/* --- secciones --- */
section{padding:54px 0 0;scroll-margin-top:70px}
.st{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;
  padding-bottom:11px;border-bottom:1px solid var(--filete);margin-bottom:22px}
.st h2{font-family:var(--display);margin:0;font-size:27px;font-weight:700;
  letter-spacing:-.02em}
.st p{margin:0;font-size:13.5px;color:var(--leve);flex:1}
.nota{max-width:70ch;color:var(--media);font-family:var(--texto);font-size:17px}
.nota strong{color:var(--tinta)}

/* --- selectores --- */
.chips{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:20px}
.chip{font-size:12.5px;padding:7px 13px;border:1px solid var(--filete);
  border-radius:999px;color:var(--media);background:var(--tarjeta);transition:.13s}
.chip:hover{border-color:var(--leve)}
.chip[aria-pressed="true"]{background:var(--sangre);border-color:var(--sangre);color:#fff}

/* --- carrusel: desplazamiento horizontal con anclaje ---
   Se usa scroll nativo con scroll-snap en vez de JavaScript moviendo posiciones:
   funciona con el dedo en el móvil, con la rueda en el escritorio y con el
   teclado, y no se rompe si el JS falla. */
.carro{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;
  padding-bottom:14px;scrollbar-width:thin}
.carro>figure{flex:0 0 clamp(230px,26vw,320px);scroll-snap-align:start;margin:0}
.carro img{width:100%;border-radius:9px;background:var(--hueso);
  border:1px solid var(--filete)}
.carro figcaption{font-size:12px;color:var(--leve);padding-top:8px;line-height:1.45}
.carro figcaption b{color:var(--media);font-weight:700;display:block;font-size:11px;
  letter-spacing:.09em;text-transform:uppercase;margin-bottom:2px}
.falta{aspect-ratio:832/1216;border:1px dashed var(--filete);border-radius:9px;
  display:grid;place-items:center;color:var(--leve);font-size:12px;
  background:var(--tarjeta)}

/* --- rejilla de comparación por escena --- */
.rejilla{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px}
.rejilla figure{margin:0}
.rejilla img{width:100%;border-radius:9px;background:var(--hueso);
  border:1px solid var(--filete)}
.rejilla figcaption{font-size:11.5px;color:var(--media);padding-top:7px;
  letter-spacing:.06em;text-transform:uppercase;font-weight:700}

/* --- tabla de medición --- */
.tabla{width:100%;border-collapse:collapse;font-size:14px;
  font-variant-numeric:tabular-nums}
.tabla th{text-align:left;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--leve);font-weight:700;padding:0 12px 9px 0;border-bottom:1px solid var(--filete)}
.tabla td{padding:11px 12px 11px 0;border-bottom:1px solid var(--filete)}
.tabla tr:last-child td{border-bottom:none}
.tabla .n{font-weight:700}
.bien{color:#2e7d4f;font-weight:700}
.mal{color:var(--sangre);font-weight:700}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .bien{color:#5fbe86}}
:root[data-theme="dark"] .bien{color:#5fbe86}

/* --- fichas de hallazgo --- */
.hall{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
.h{background:var(--tarjeta);border:1px solid var(--filete);border-radius:11px;padding:20px}
.h h3{margin:0 0 8px;font-size:15px;letter-spacing:-.01em}
.h p{margin:0;font-size:14px;color:var(--media);line-height:1.6}
.h code{font-family:var(--mono);font-size:12.5px;background:var(--hueso);
  padding:1px 5px;border-radius:4px;color:var(--tinta)}
.h .dato{font-family:var(--mono);font-size:12px;color:var(--leve);
  display:block;margin-top:10px;padding-top:10px;border-top:1px solid var(--filete);
  white-space:pre-wrap;line-height:1.7}

footer{padding:60px 0 50px;margin-top:50px;border-top:1px solid var(--filete);
  color:var(--leve);font-size:12.5px}
"""

JS = """
// Selector de estilo: enseña un carrusel y esconde los demás. Sin animaciones
// ni transiciones de opacidad — con seis imágenes por carrusel, cualquier
// efecto se nota como tirón en un Mac que además está generando.
function selector(grupo, prefijo){
  var bs = document.querySelectorAll('[data-g="'+grupo+'"]');
  bs.forEach(function(b){
    b.addEventListener('click', function(){
      bs.forEach(function(o){ o.setAttribute('aria-pressed', o===b); });
      document.querySelectorAll('[data-p="'+prefijo+'"]').forEach(function(p){
        p.hidden = (p.dataset.k !== b.dataset.k);
      });
    });
  });
}
selector('estilo','est');
selector('escena','esc');
"""


def _img(d, alt, clase=""):
    if not d:
        return '<div class="falta">pendiente</div>'
    src = "img-lab/" + d["jpg"]
    conj = ", ".join("img-lab/%s %dw" % (d["avif"][a], a)
                     for a in sorted(d["avif"]))
    return ('<picture><source type="image/avif" srcset="%s" sizes="(max-width:700px) 60vw, 300px">'
            '<img src="%s" alt="%s" loading="lazy" decoding="async"%s></picture>'
            % (conj, src, escape(alt), (' class="%s"' % clase) if clase else ""))


def construir():
    tipografia()
    datos = reunir()
    med = medidas()
    est = med.get("estilos", {})
    orden = med.get("orden") or list(ee.ESTILOS)
    hechas = sum(1 for f in datos.values() for x in f if x)
    total = len(ee.ESTILOS) * len(ee.ESCENAS)

    p = []
    p.append('<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">')
    p.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    p.append('<title>Laboratorio · Fuente Primaria</title>')
    p.append('<meta name="description" content="El mismo cuento en seis estilos '
             'gráficos, medido: qué estilo mantiene mejor al personaje.">')
    p.append('<link rel="stylesheet" href="tipografia.css">')
    p.append("<style>%s</style></head><body>" % CSS)

    p.append('<div class="w"><nav class="barra">')
    p.append('<a href="index.html">Archivo</a>')
    p.append('<a href="laboratorio.html" aria-current="page">Laboratorio</a>')
    p.append('<span class="der" style="color:var(--leve)">%d de %d imágenes</span>'
             % (hechas, total))
    p.append('</nav></div>')

    p.append('<div class="w"><header>')
    p.append('<p class="eyebrow">Estudio de consistencia</p>')
    p.append('<h1>El mismo cuento,<br>seis estilos</h1>')
    p.append('<p class="lema">Un elefantito aprende a volar. Seis escenas sin una '
             'sola palabra, dibujadas seis veces de seis maneras distintas, para '
             'averiguar qué estilo gráfico sostiene mejor a un personaje.</p>')
    p.append('<div class="regla"></div></header>')

    # ── el cuento ───────────────────────────────────────────────────────────
    p.append('<section id="cuento"><div class="st"><h2>El cuento</h2>'
             '<p>Seis tiempos · sin texto · se sigue por la altura</p></div>')
    p.append('<div class="nota"><p>El cuento se sostiene en una sola idea visual: '
             '<strong>empieza pegado al suelo y termina sobre los árboles</strong>. '
             'Se entiende sin leer nada, que es la prueba de que las imágenes '
             'cuentan y no solo ilustran.</p></div>')
    p.append('<ol class="nota" style="padding-left:20px">')
    for corta in ee.ESCENAS_ES:
        p.append("<li>%s</li>" % escape(corta))
    p.append("</ol></section>")

    # ── por estilo ──────────────────────────────────────────────────────────
    p.append('<section id="estilos"><div class="st"><h2>Por estilo</h2>'
             '<p>Elige un estilo y recorre las seis escenas</p></div>')
    p.append('<div class="chips" role="group" aria-label="Estilo">')
    for k, e in enumerate(orden):
        p.append('<button class="chip" data-g="estilo" data-k="%s" aria-pressed="%s">%s</button>'
                 % (e, "true" if k == 0 else "false", escape(NOMBRES[e][0])))
    p.append("</div>")
    for k, e in enumerate(orden):
        p.append('<div data-p="est" data-k="%s"%s>' % (e, "" if k == 0 else " hidden"))
        p.append('<p class="nota" style="font-size:14px;margin:0 0 14px">%s</p>'
                 % escape(NOMBRES[e][1]))
        p.append('<div class="carro">')
        for i, d in enumerate(datos[e]):
            p.append('<figure>%s<figcaption><b>Escena %d</b>%s</figcaption></figure>'
                     % (_img(d, "%s, escena %d" % (NOMBRES[e][0], i + 1)),
                        i + 1, escape(ee.ESCENAS_ES[i])))
        p.append("</div></div>")
    p.append("</section>")

    # ── por escena ──────────────────────────────────────────────────────────
    p.append('<section id="escenas"><div class="st"><h2>Por escena</h2>'
             '<p>El mismo momento en los seis estilos, uno al lado de otro</p></div>')
    p.append('<div class="nota"><p>Ésta es la vista que contesta la pregunta. '
             'Poner el mismo instante seis veces seguidas es la única forma de '
             '<strong>ver a ojo lo que la coherencia mide con un número</strong>.</p></div>')
    p.append('<div class="chips" role="group" aria-label="Escena" style="margin-top:18px">')
    for i in range(len(ee.ESCENAS)):
        p.append('<button class="chip" data-g="escena" data-k="%d" aria-pressed="%s">Escena %d</button>'
                 % (i, "true" if i == 0 else "false", i + 1))
    p.append("</div>")
    for i in range(len(ee.ESCENAS)):
        p.append('<div data-p="esc" data-k="%d"%s>' % (i, "" if i == 0 else " hidden"))
        p.append('<p class="nota" style="font-size:14px;margin:0 0 14px">%s</p>'
                 % escape(ee.ESCENAS_ES[i]))
        p.append('<div class="rejilla">')
        for e in orden:
            p.append('<figure>%s<figcaption>%s</figcaption></figure>'
                     % (_img(datos[e][i], "%s, escena %d" % (NOMBRES[e][0], i + 1)),
                        escape(NOMBRES[e][0])))
        p.append("</div></div>")
    p.append("</section>")

    # ── la medición ─────────────────────────────────────────────────────────
    p.append('<section id="medicion"><div class="st"><h2>La medición</h2>'
             '<p>Dos métricas, y hay que pasar las dos</p></div>')
    p.append('<div class="nota"><p><strong>Coherencia</strong> es cuánto se parecen '
             'las seis imágenes entre sí — el 90 % que buscamos. Pero sola se puede '
             'falsificar: sube a 0,99 generando seis veces la misma imagen. Por eso '
             'va acompañada del <strong>margen</strong>, que mide si cada imagen '
             'cuenta su propia escena y no la del vecino. '
             'Una serie con coherencia altísima y margen cero no es un éxito: es el '
             'modelo ignorando el cuento.</p></div>')
    if est:
        p.append('<table class="tabla" style="margin-top:22px"><thead><tr>'
                 '<th>Estilo</th><th>Coherencia</th><th>Margen</th>'
                 '<th>Acierta</th><th>Veredicto</th></tr></thead><tbody>')
        import adherencia
        for e in orden:
            v = est.get(e)
            if not v:
                p.append('<tr><td class="n">%s</td><td colspan="4" '
                         'style="color:var(--leve)">sin medir</td></tr>'
                         % escape(NOMBRES[e][0]))
                continue
            nota = adherencia.nota(v)
            cl = "bien" if nota == "APROBADO" else "mal"
            p.append('<tr><td class="n">%s</td><td>%.3f</td><td>%+.3f</td>'
                     '<td>%d/%d</td><td class="%s">%s</td></tr>'
                     % (escape(NOMBRES[e][0]), v["coherencia"], v["margen"],
                        v["aciertos"], v["n"], cl, escape(nota)))
        p.append("</tbody></table>")
    else:
        p.append('<p class="nota" style="color:var(--leve)">Las imágenes se están '
                 'generando. La tabla aparece cuando estén las 36.</p>')
    p.append("</section>")

    # ── hallazgos ───────────────────────────────────────────────────────────
    p.append('<section id="hallazgos"><div class="st"><h2>Lo que aprendimos</h2>'
             '<p>Cada uno con su medición · nada aquí es opinión</p></div>')
    p.append('<div class="hall">')
    for t, c, d in HALLAZGOS:
        p.append('<div class="h"><h3>%s</h3><p>%s</p><span class="dato">%s</span></div>'
                 % (t, c, escape(d)))
    p.append("</div></section>")

    # ── ficha ───────────────────────────────────────────────────────────────
    p.append('<section id="ficha"><div class="st"><h2>Ficha técnica</h2>'
             '<p>Para poder repetirlo igual</p></div>')
    p.append('<div class="hall">')
    p.append('<div class="h"><h3>El personaje</h3><p>Tres anclajes concretos, '
             'nada de adjetivos: el modelo no sabe dibujar «tierno».</p>'
             '<span class="dato">%s</span></div>' % escape(ee.PERSONAJE))
    p.append('<div class="h"><h3>Configuración</h3><p>Idéntica en las 36. Lo único '
             'que cambia entre series es el estilo.</p><span class="dato">%s</span></div>'
             % ("modelo   Juggernaut XL v9 (SDXL)\nmuestreo  dpmpp_2m · karras\n"
                "pasos    30\nCFG      5.5\nsemilla  %s\ntamaño   832 × 1216\n"
                "ritmo    130 s por imagen"
                % med.get("semilla", 101010)))
    p.append("</div></section>")

    p.append('<footer><div>Fuente Primaria · laboratorio · %s</div></footer>'
             % escape(med.get("fecha", "en curso")))
    p.append("</div><script>%s</script></body></html>" % JS)

    html = "\n".join(p)
    with open(PAGINA, "w", encoding="utf-8") as f:
        f.write(html)
    return {"pagina": PAGINA, "bytes": len(html), "imagenes": hechas,
            "total": total, "medidas": len(est)}


HALLAZGOS = [
 ("La paleta pisaba la escena",
  "Nuestras paletas no describían color: describían un <em>lugar</em>. "
  "<code>dorado-selva</code> metía «emerald jungle» con peso 1,3 contra una escena "
  "a peso 1,0, y ganaba. Cuatro prompts muy distintos daban la misma foto. "
  "Afecta a las 16 paletas del sistema, no solo a esta prueba.",
  "prueba controlada · 4 variantes, misma imagen\n"
  "quitando la paleta salió la escena pedida a la primera"),

 ("CLIP solo lee 77 símbolos",
  "El prompt llegó a tener 158. Todo lo que cae después del símbolo 77 pesa "
  "muchísimo menos, y la ficha de personaje empezaba en el 35: se partía por la "
  "mitad. Ahora la ficha va primera y el prompt entero cabe.",
  "antes  158 símbolos · ficha partida\n"
  "ahora   71 en el peor caso, de 77"),

 ("A CFG 1.0 el negativo no hace nada",
  "El flujo rápido usa CFG 1.0, y ahí la guía sin clasificador está desactivada: "
  "el prompt negativo no influye. Se comprobó con cuatro variantes y salieron "
  "idénticas píxel a píxel. Lo habíamos documentado como «el hallazgo más "
  "rentable del proyecto», y era falso.",
  "con veto y sin veto · idénticas\n"
  "el mérito era de los pesos en positivo"),

 ("El vigilante rompía lo que vigilaba",
  "El Guardián reiniciaba si una imagen tardaba más de 450 s. Las imágenes "
  "tardaban 18 minutos. Las mataba siempre, justo antes de terminar. Trece veces "
  "en seis horas. La prueba: al morir el estudio a las 03:56, las imágenes que "
  "faltaban salieron solas entre las 04:13 y las 07:40.",
  "umbral antes  450 s inventado\n"
  "umbral ahora  medido de ComfyUI · suelo de 30 min\n"
  "y no reinicia si detecta CPU o avance"),

 ("La coherencia sola premia el fracaso",
  "Medíamos solo cuánto se parecen las seis imágenes. Ese número sube a 0,99 "
  "cuando el modelo <em>ignora</em> las escenas y repite el mismo plano. "
  "Celebramos un 0,990 que significaba exactamente eso.",
  "hace falta una segunda métrica: el margen\n"
  "aprueba solo quien pasa las dos"),

 ("Subir el peso no es la palanca",
  "Cuando la escena no salía, la reacción fue reforzarla con <code>(extreme wide "
  "shot:1.5)</code>. Salió peor. Lo que funcionó fue quitar lo que competía. "
  "Gritar más alto no arregla que alguien esté gritando encima.",
  "encuadre a 1.5 · peor resultado\n"
  "paleta fuera · escena correcta a la primera"),
]


if __name__ == "__main__":
    r = construir()
    print("  página   %s" % r["pagina"])
    print("  peso     %.0f KB" % (r["bytes"] / 1024))
    print("  imágenes %d de %d · series medidas %d"
          % (r["imagenes"], r["total"], r["medidas"]))
