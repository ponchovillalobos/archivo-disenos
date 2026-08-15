"""Constructor del catálogo, por PROYECTO.

Regla nueva y permanente: cada proyecto es UNA ficha con TODO dentro —
vídeo, PDF, ZIP, láminas con texto, fondos sin texto y la carpeta local.
Nada de tener el reel en un sitio y los fondos en otro.
"""
from PIL import Image
from urllib.parse import quote
import json, os, re, shutil

PROY = "/Users/maity/Desktop/Confy Imagenes"
OUT = os.path.join(PROY, "out")
SITIO = os.path.join(PROY, "sitio")
IMG = os.path.join(SITIO, "img")
DESC = os.path.join(SITIO, "descargas")
TAM = {400: 55, 1024: 60, 1600: 63}

# --- los proyectos de comunicación: mismo esqueleto para todos ---
COM = [
 ("vacio", "El vacío", "La curiosidad no nace del misterio, nace del hueco.",
  "Loewenstein, 1994: la curiosidad es privación. Necesitas saber qué te falta, no que falta algo.",
  ["curiosidad", "gancho"]),
 ("relato", "El relato", "Una historia no convence: baja la guardia.",
  "Green y Brock, 2000. Reducir el pensamiento crítico es el efecto más débil del modelo: r = −0,18 sobre solo 7 estudios.",
  ["historia", "narrativa"]),
 ("emocion", "La emoción", "La tristeza no se comparte.",
  "Berger y Milkman, 6.956 artículos del New York Times. Ira +34 %, asombro +30 %.",
  ["viralidad", "emoción"]),
 ("prueba-social", "La prueba social", "El dato más citado de la persuasión falló al repetirlo.",
  "Réplica alemana de 2014: el mensaje ecológico de siempre ganó, 93,3 % frente a 76,5 %.",
  ["persuasión", "réplica"]),
 ("indignacion", "La indignación", "Vende, y arruina el negocio.",
  "Center for Media Engagement, 1.535 personas: baja el clic, el comentario y la intención de pagar.",
  ["ética", "clickbait"]),
 ("manipular", "Persuadir o manipular", "No son lo mismo, y hay una prueba.",
  "Sunstein: manipular es esquivar la capacidad del otro de decidir. Cuanto mejor funciona, peor es.",
  ["ética", "persuasión"]),
 ("poses-poder", "Las poses de poder", "La coautora desmintió su propio estudio.",
  "Dana Carney, por escrito: «No creo que los efectos sean reales. Ya no lo enseño en mis clases.»",
  ["no verbal", "mito"]),
 ("el-nombre", "Tu propio nombre", "«El sonido más dulce» es una frase de 1936 sin datos.",
  "Carnegie no citó ningún estudio. Al comprobarlo —el nombre en el asunto de un email— el efecto fue cero.",
  ["mito", "persuasión"]),
 ("ratio-ventas", "El 43/57", "La regla la enterró quien la inventó.",
  "Gong la actualizó en 2025 con 326.000 llamadas: el 57 % es lo que HABLA, no lo que escucha.",
  ["ventas", "mito"]),
 ("escuchar", "Once segundos", "Lo que tarda un médico en interrumpirte.",
  "112 consultas grabadas. Mediana de 11 s, y solo el 36 % llegó a preguntar por el problema.",
  ["escucha", "salud"]),
 ("preguntas", "La segunda pregunta", "Preguntar gusta, y nadie lo espera.",
  "Huang, 2017: 1.961 citas rápidas. Las preguntas de seguimiento consiguen más segundas citas.",
  ["preguntas", "conversación"]),
 ("negociar", "La primera cifra", "Quien abre, ancla. Y tiene precio.",
  "El anclaje replicó en 36 de 36 muestras. Pero aumenta las rupturas y empeora la satisfacción del otro.",
  ["negociación", "anclaje"]),
 ("maldicion", "La maldición del saber", "Creían que la mitad lo adivinaría. Acertó el 2,5 %.",
  "Newton, 1990. Tres aciertos en 120 intentos. Ni el título del estudio se cita bien.",
  ["claridad", "sesgo"]),
 ("silencio", "Cuatro segundos", "El silencio que nadie nota y a todos afecta.",
  "Se eligieron cuatro segundos precisamente porque pasan desapercibidos. El malestar es inconsciente.",
  ["silencio", "grupo"]),
 ("decir-no", "«No lo hago»", "Cambia una palabra y cambia de quién es la decisión.",
  "8 de 10 aguantaron diez días con «no lo hago»; 1 de 10 con «no puedo». Ojo: 10 personas por grupo.",
  ["decisión", "límites"]),
 ("objeciones", "Admitir un fallo", "Sube la credibilidad un 0,8 %.",
  "Metaanálisis de 107 estudios: si solo admites, eres MENOS persuasivo. Solo funciona si además refutas.",
  ["argumentar", "objeciones"]),
 ("preguntar", "El chef y el alérgico", "Servimos soluciones sin preguntar qué necesita el otro.",
  "Pieza de opinión, no de dato. Diez láminas, cada una con una disposición distinta: portada, banda, esquina, cita, placa, marco.",
  ["preguntas", "escucha", "ventas"]),
 ("analogia", "La analogía", "Explicar es traducir.",
  "No expliques mejor. Explica desde otro sitio.",
  ['explicar', 'analogía', 'comunicación']),
 ("autoridad", "La autoridad", "La autoridad no se reclama. Se concede.",
  "Se te concede mientras la mereces. Ni un minuto más.",
  ['autoridad', 'credibilidad', 'comunicación']),
 ("cerrar", "Cerrar", "Cerrar no es empujar.",
  "No cierres. Quita lo que estorba y deja cerrar.",
  ['ventas', 'cierre', 'comunicación']),
 ("compromiso", "El compromiso", "Lo que se dice en voz alta pesa distinto.",
  "No pidas la decisión. Pide el primer paso.",
  ['decisión', 'coherencia', 'comunicación']),
 ("contraste", "El contraste", "Nada significa nada solo.",
  "No describas más. Pon algo al lado.",
  ['contraste', 'comparación', 'comunicación']),
 ("el-orden", "El orden", "El mismo argumento, en otro orden, es otro argumento.",
  "No cuentes lo que pasó. Cuenta lo que hace falta saber para entenderlo.",
  ['estructura', 'orden', 'comunicación']),
 ("el-tono", "El tono", "El tono llega antes que las palabras.",
  "Antes de elegir las palabras, elige cómo van a sonar.",
  ['no verbal', 'tono', 'comunicación']),
 ("escasez", "La escasez", "Lo que se acaba se mira distinto.",
  "No inventes urgencia. Explica la que ya hay.",
  ['escasez', 'urgencia', 'comunicación']),
 ("jerga", "La jerga", "La jerga no es precisión. Es un peaje.",
  "Habla el idioma del otro, no el tuyo.",
  ['claridad', 'jerga', 'comunicación']),
 ("la-brevedad", "La brevedad", "Ser breve no es decir menos.",
  "No hables menos. Habla de menos cosas.",
  ['brevedad', 'edición', 'comunicación']),
 ("la-memoria", "La memoria", "No recuerdan lo que dijiste. Recuerdan lo que hicieron con ello.",
  "No lo repitas. Dale un sitio y un momento.",
  ['memoria', 'recuerdo', 'comunicación']),
 ("la-prueba", "La prueba", "Una afirmación sin prueba es una opinión con tono seguro.",
  "No afirmes más fuerte. Di de dónde lo sacas.",
  ['evidencia', 'rigor', 'comunicación']),
 ("primera-impresion", "La primera impresión", "La primera impresión no se corrige. Se arrastra.",
  "No la compenses. Empieza otra vez.",
  ['primera impresión', 'sesgo', 'comunicación']),
 ("primeras-palabras", "Las primeras palabras", "La primera frase no informa. Decide si hay una segunda.",
  "No abras explicando. Abre dando una razón para seguir.",
  ['gancho', 'apertura', 'comunicación']),
 ("reciprocidad", "La reciprocidad", "Dar primero cambia la conversación.",
  "Da algo que no puedas cobrar.",
  ['reciprocidad', 'ética', 'comunicación']),
 ("repeticion", "La repetición", "Repetir no convence. Familiariza.",
  "Repite cómo lo cuentas. No repitas la conclusión.",
  ['repetición', 'sesgo', 'comunicación']),
 ("inoculacion", "La inoculación", "Avisar antes del engaño funciona.",
  "McGuire, años sesenta. Probado hoy en 22.632 personas en YouTube: efectos reales, pero pequeños.",
  ["desinformación", "defensa"]),
]

# --- las series históricas, con su estructura propia ---
HIST = [
 ("termopilas", "Las Termópilas", "Una batalla perdida que cambió la guerra.",
  "Tratamiento noir con color selectivo: el único color que sobrevive es el carmesí de la capa.",
  ["espartano", "historia", "noir"],
  f"{OUT}/carrusel-espartano/CON-TEXTO", "termopilas-%02d.png",
  f"{OUT}/carrusel-espartano", ["c1-gancho.png","c2-ejercito.png","c3-espalda.png",
                                "c4-escudo.png","c5-falange.png","c6-casco.png"],
  "reel-las-termopilas.mp4", "carrusel-las-termopilas.pdf", "termopilas-laminas.zip"),
 ("bushido", "Bushidō", "Un código que no es tan antiguo como todos creen.",
  "Nitobe Inazō lo publicó en 1900, en Filadelfia, en inglés. El color que sobrevive es el añil.",
  ["samurái", "historia", "noir"],
  f"{OUT}/carrusel-samurai/CON-TEXTO", "bushido-%02d.png",
  f"{OUT}/carrusel-samurai", ["s1-gancho.png","s2-mito.png","s3-pincel.png",
                              "s4-seiza.png","s5-cordones.png","s6-kabuto.png"],
  "reel-bushido.mp4", "carrusel-bushido.pdf", "bushido-laminas.zip"),
 ("azteca", "Disciplina mexica", "El imperio que hizo obligatoria la escuela para todos.",
  "También para las niñas y los plebeyos, siglos antes que Europa. El color que sobrevive es el turquesa.",
  ["azteca", "historia", "noir"],
  f"{OUT}/carrusel-azteca/CON-TEXTO", "azteca-%02d.png",
  f"{OUT}/carrusel-azteca", ["az1-gancho.png","az2-mito.png","az3-codice.png",
                             "az4-escuela.png","az5-espinas.png","az6-tocado.png"],
  "reel-azteca.mp4", "carrusel-azteca.pdf", "azteca-laminas.zip"),
]


MANIFIESTO = os.path.join(IMG, ".manifiesto.json")
_cache = {}
_vivos = set()


def _cargar_cache():
    """Qué derivadas existen ya y de qué original salieron.

    Sin esto, cada reconstrucción borraba sitio/img y volvía a convertir las
    1016 derivadas: 47 segundos. Con caché son ~2 s cuando nada cambió, y eso
    importa porque la regla es actualizar el portal SIEMPRE, y algo que cuesta
    47 segundos se actualiza menos.
    """
    global _cache
    try:
        with open(MANIFIESTO, encoding="utf-8") as f:
            _cache = json.load(f)
    except (OSError, ValueError):
        _cache = {}


def _guardar_cache():
    with open(MANIFIESTO, "w", encoding="utf-8") as f:
        json.dump(_cache, f)


def _sello(p):
    """mtime y tamaño: basta para saber si el original cambió, y es instantáneo
    frente a leer y hashear 66 MB de PNG."""
    st = os.stat(p)
    return [int(st.st_mtime), st.st_size]


def derivar(origen, base):
    clave = base
    sello = _sello(origen)
    guardado = _cache.get(clave)
    if guardado and guardado["sello"] == sello and all(
            os.path.exists(os.path.join(IMG, v))
            for k, v in guardado["src"].items() if k != "max"):
        _vivos.update(v for k, v in guardado["src"].items() if k != "max")
        return guardado["src"], guardado["w"], guardado["h"]

    im = Image.open(origen).convert("RGB")
    w0, h0 = im.size
    anchos = [a for a in TAM if a <= w0]
    if w0 not in anchos and w0 > min(TAM):
        anchos.append(w0)
    if not anchos:
        anchos = [w0]
    grande, sal = max(anchos), {}
    for a in sorted(anchos):
        red = im if a == w0 else im.resize((a, round(h0 * a / w0)), Image.LANCZOS)
        n = "%s-%d.avif" % (base, a)
        red.save(os.path.join(IMG, n), "AVIF", quality=TAM.get(a, 62))
        sal[a] = n
        if a == min(grande, 1024):
            j = "%s-%d.jpg" % (base, a)
            red.save(os.path.join(IMG, j), "JPEG", quality=82, optimize=True)
            sal["jpg"] = j
    sal["max"] = sal[grande]
    sal = {str(k): v for k, v in sal.items()}
    _cache[clave] = {"sello": sello, "src": sal, "w": w0, "h": h0}
    _vivos.update(v for k, v in sal.items() if k != "max")
    return sal, w0, h0


def piezas(idp, carpeta, patron, n=6, sufijo=""):
    out = []
    for i in range(1, n + 1):
        arch = patron % i if "%" in patron else patron
        p = os.path.join(carpeta, arch)
        if not os.path.exists(p):
            return None
        src, w, h = derivar(p, "%s%s-%02d" % (idp, sufijo, i))
        out.append({"pie": "Lámina %d" % i, "w": w, "h": h, "src": src})
    return out


def existe(p):
    return os.path.exists(os.path.join(DESC, p))


# --- proyectos nacidos de un audio: una ficha, los dos formatos dentro ---
AUDIO = [
 ("idea1", "Idea 1", "El miedo y la emoción son la misma sensación.",
  "Primer vídeo hecho a partir de un audio: transcripción con marcas por palabra, "
  "troceado por las pausas reales y once escenas escritas para cada bloque. "
  "Vertical y apaisado desde el mismo audio.",
  ["audio", "comunicación", "rojo-carbón"], 11),
]


def desde_audio():
    """Una ficha con los DOS formatos dentro, no dos fichas.

    La regla del portal no cambia porque el vídeo venga de un audio: un proyecto
    es una ficha con todo. Aquí «todo» incluye vertical y apaisado, que son el
    mismo contenido en dos lienzos.
    """
    fuera = []
    for slug, tit, res, nota, tags, n in AUDIO:
        vids, desc, con, sin = [], [], [], []
        for etq in ("vertical", "horizontal"):
            d = f"{OUT}/{slug}-{etq}"
            # dos montajes del mismo material: el de fundidos largos y el de
            # ritmo (34 planos cortados sobre el pulso del habla)
            # «ritmo-» se retiró: cortaba entre encuadres de la misma imagen
            # fija y eso se lee como fallo de reproducción, no como edición
            for pref, nombre in (("flujo-", "texto vivo"), ("", "reposado")):
                mp4 = f"{slug}-{pref}{etq}.mp4"
                if existe(mp4):
                    vids.append({"etq": "Ver %s · %s" % (etq, nombre),
                                 "url": "descargas/" + mp4})
                    desc.append({"etq": "Vídeo %s · %s" % (etq, nombre),
                                 "url": "descargas/" + mp4})
            z = f"laminas-{slug}-{etq}.zip"
            if existe(z):
                desc.append({"etq": "ZIP · %d láminas %s" % (n, etq),
                             "url": "descargas/" + z})
            c = piezas(f"{slug}-{etq}", f"{d}/LAMINAS", "l-%02d.png", n=n)
            if c:
                con += c
            s_ = piezas(f"{slug}-{etq}", d, "f%02d.png", n=n, sufijo="-sin")
            if s_:
                sin += s_
        if not con:
            print("  ! sin láminas:", slug)
            continue
        fuera.append({
            "id": slug, "titulo": tit, "serie": "Desde audio",
            "resumen": res, "nota": nota, "etiquetas": tags + ["desde audio"],
            "fecha": "2026-08-12", "formato": "1080×1920 y 1920×1080",
            "video": vids[0]["url"] if vids else None, "videos": vids,
            "descargas": desc, "piezas": con, "sin_texto": sin,
            "carpeta": "file://" + quote(f"{OUT}/{slug}-vertical"),
            "rutaAbs": f"{OUT}/{slug}-vertical",
        })
    return fuera


# Cuántas derivadas puede barrer una reconstrucción sin sospechar. Un proyecto
# son ~48, así que 60 permite rehacer uno entero y se planta si desaparecen dos.
TOPE_BARRIDO = 60


# --- reto de 30 días: el camino del espartano ---
ESPARTA = [
 (1, "Día 01 · Apertura", "Nadie nace espartano.", "Empieza hoy. Mañana ya son veintinueve.", ['apertura', 'espartano', 'reto30']),
 (2, "Día 02 · Justicia", "Lo justo cuesta cuando te toca a ti.", "Justo es quien se corrige a sí mismo primero.", ['justicia', 'espartano', 'reto30']),
 (3, "Día 03 · Justicia", "El reparto habla más que el discurso.", "El reparto es el mensaje.", ['justicia', 'espartano', 'reto30']),
 (4, "Día 04 · Justicia", "Defender al ausente cuesta un segundo.", "Al ausente lo defiende quien tiene poco que ganar.", ['justicia', 'espartano', 'reto30']),
 (5, "Día 05 · Justicia", "La regla que aplicas a otros es la tuya.", "La misma vara. Siempre. Empezando por ti.", ['justicia', 'espartano', 'reto30']),
 (6, "Día 06 · Valor", "El valor no es no tener miedo.", "El miedo no se va. Se camina con él.", ['valor', 'espartano', 'reto30']),
 (7, "Día 07 · Valor", "Decir «no sé» es una forma de coraje.", "El que admite el límite es el que tiene autoridad dentro de él.", ['valor', 'espartano', 'reto30']),
 (8, "Día 08 · Valor", "Lo difícil primero.", "Lo que aplazas no descansa. Trabaja contra ti.", ['valor', 'espartano', 'reto30']),
 (9, "Día 09 · Valor", "Pedir ayuda no es rendirse.", "Solo llegas antes. Acompañado llegas.", ['valor', 'espartano', 'reto30']),
 (10, "Día 10 · Compasion", "La fuerza que no sabe ser suave es solo dureza.", "El escudo protege al de al lado, no a ti.", ['compasion', 'espartano', 'reto30']),
 (11, "Día 11 · Compasion", "Casi nadie te está atacando.", "Casi nadie madruga para hacerte daño.", ['compasion', 'espartano', 'reto30']),
 (12, "Día 12 · Compasion", "El que se equivoca ya lo sabe.", "El que puede confesar un error, corrige dos.", ['compasion', 'espartano', 'reto30']),
 (13, "Día 13 · Compasion", "Dar sin que se note es dar dos veces.", "Da algo que no puedas cobrar.", ['compasion', 'espartano', 'reto30']),
 (14, "Día 14 · Respeto", "El respeto se ve en los detalles pequeños.", "La puntualidad es la primera forma del respeto.", ['respeto', 'espartano', 'reto30']),
 (15, "Día 15 · Respeto", "Escuchar es más caro que hablar.", "Quien escucha entero, decide mejor.", ['respeto', 'espartano', 'reto30']),
 (16, "Día 16 · Respeto", "El nombre de la gente importa.", "Con el nombre empieza el trato.", ['respeto', 'espartano', 'reto30']),
 (17, "Día 17 · Respeto", "Al que no te sirve de nada.", "Se te juzga por cómo tratas a quien no puede pagarte.", ['respeto', 'espartano', 'reto30']),
 (18, "Día 18 · Verdad", "La palabra dada, sin contrato.", "La palabra pesa lo que pesa la última que cumpliste.", ['verdad', 'espartano', 'reto30']),
 (19, "Día 19 · Verdad", "Decirlo antes de que se sepa.", "La verdad tarde es una mentira que se agotó.", ['verdad', 'espartano', 'reto30']),
 (20, "Día 20 · Verdad", "Exagerar es mentir despacio.", "El que no exagera no tiene que recordar qué dijo.", ['verdad', 'espartano', 'reto30']),
 (21, "Día 21 · Verdad", "La disculpa sin «pero».", "La disculpa entera cabe en una línea.", ['verdad', 'espartano', 'reto30']),
 (22, "Día 22 · Honor", "Lo que haces cuando no te ven.", "El honor no tiene testigos.", ['honor', 'espartano', 'reto30']),
 (23, "Día 23 · Honor", "No aceptar lo que no te has ganado.", "Lo que no ganaste, pesa.", ['honor', 'espartano', 'reto30']),
 (24, "Día 24 · Honor", "Sostener lo que dijiste ayer.", "El que dice lo mismo en dos habitaciones, descansa.", ['honor', 'espartano', 'reto30']),
 (25, "Día 25 · Honor", "Perder bien.", "Se mide más en la derrota que en la victoria.", ['honor', 'espartano', 'reto30']),
 (26, "Día 26 · Lealtad", "La lealtad se demuestra cuando cuesta.", "La lealtad se nota en el mal año.", ['lealtad', 'espartano', 'reto30']),
 (27, "Día 27 · Lealtad", "Criticar de frente. Defender de espaldas.", "De frente cuesta un rato. Por detrás cuesta la relación.", ['lealtad', 'espartano', 'reto30']),
 (28, "Día 28 · Lealtad", "Estar en el sitio de al lado.", "La línea aguanta por los lados, no por el centro.", ['lealtad', 'espartano', 'reto30']),
 (29, "Día 29 · Lealtad", "Contigo mismo también.", "El primero al que hay que serle leal es al de mañana.", ['lealtad', 'espartano', 'reto30']),
 (30, "Día 30 · Cierre", "No eres el que empezó.", "Espartano no es el que resiste treinta días. Es el que sigue el treinta y uno.", ['cierre', 'espartano', 'reto30']),
]


def desde_esparta():
    """Una ficha por día. Solo aparecen los días que YA tienen vídeo, así el
    portal crece según se produce en vez de esperar a los treinta."""
    fuera = []
    for n, tit, res, nota, tags in ESPARTA:
        d = f"{OUT}/esp-{n:02d}"
        mp4 = f"reel-esp-{n:02d}.mp4"
        if not existe(mp4):
            continue
        con = piezas("esp-%02d" % n, f"{d}/LAMINAS", "l-%02d.png")
        sin = piezas("esp-%02d" % n, d, "f%d.png", sufijo="-sin")
        if not con:
            continue
        desc = [{"etq": "Vídeo MP4", "url": "descargas/" + mp4}]
        for etq, arch in (("PDF · 6 páginas", f"carrusel-esp-{n:02d}.pdf"),
                          ("ZIP · 6 láminas", f"laminas-esp-{n:02d}.zip")):
            if existe(arch):
                desc.append({"etq": etq, "url": "descargas/" + arch})
        fuera.append({
            "id": "esp-%02d" % n, "titulo": tit, "serie": "El camino del espartano",
            "resumen": res, "nota": nota, "etiquetas": tags,
            "fecha": "2026-08-13", "formato": "1080×1920",
            "video": "descargas/" + mp4, "videos": [],
            "descargas": desc, "piezas": con, "sin_texto": sin or [],
            "carpeta": "file://" + quote(d), "rutaAbs": d,
        })
    return fuera


def desde_guerrero():
    """El guerrero espartano. Serie propia porque no es una lámina de un reto:
    es una historia de siete tiempos con su vídeo y su carrusel.

    Las láminas van en la raíz del proyecto como `guerrero-NN.png`, no en
    LAMINAS/: `estudio2.componer()` las escribe ahí y no hay motivo para
    moverlas."""
    d = f"{OUT}/guerrero-espartano"
    con = piezas("guerrero", d, "guerrero-%02d.png", n=7)
    if not con:
        return []
    desc = []
    for etq, arch in (("Vídeo MP4", "guerrero-espartano.mp4"),
                      ("PDF · 7 páginas", "carrusel-guerrero-espartano.pdf"),
                      ("ZIP · 7 láminas", "laminas-guerrero-espartano.zip")):
        if existe(arch):
            desc.append({"etq": etq, "url": "descargas/" + arch})
    return [{
        "id": "guerrero-espartano",
        "titulo": "El guerrero que descubre su poder",
        "serie": "Historias",
        "resumen": "Siete tiempos. La armadura que creía que lo protegía era "
                   "lo que lo hundía.",
        "nota": "Reconstruido sobre la receta verificada de RECETA-ESPARTANO.md, "
                "con 104 imágenes de barrido detrás para saber qué controla el "
                "look. Cada lámina auditada en hoja de contacto.",
        "etiquetas": ["espartano", "historia", "cinematográfico"],
        "fecha": "2026-08-15", "formato": "1080×1350",
        "video": "descargas/guerrero-espartano.mp4"
        if existe("guerrero-espartano.mp4") else None,
        "videos": [], "descargas": desc, "piezas": con, "sin_texto": [],
        "carpeta": "file://" + quote(d), "rutaAbs": d,
    }]


def construir(minimo_proyectos=None, barrer=True):
    """minimo_proyectos: se niega a publicar si salen menos.

    Existe porque este constructor podía DESTRUIR TRABAJO EN SILENCIO. Si un
    cambio de pipeline renombraba una salida, `piezas()` devolvía None, el
    proyecto caía de la lista con un `continue`, sus derivadas dejaban de estar
    en `_vivos` y el barrido las borraba. Con código de salida 0 y sin un solo
    error en pantalla. Y `out/` y `sitio/img/` están en .gitignore: no hay copia.
    """
    os.makedirs(IMG, exist_ok=True)
    _cargar_cache()
    proyectos = []
    saltados = []

    proyectos += desde_guerrero()

    for slug, tit, res, nota, tags in COM:
        d = f"{OUT}/com-{slug}"
        con = piezas("com-" + slug, f"{d}/LAMINAS", "l-%02d.png")
        sin = piezas("com-" + slug, d, "f%d.png", sufijo="-sin")
        if not con:
            saltados.append(slug); continue
        desc = []
        for etq, arch in (("Vídeo MP4", f"reel-com-{slug}.mp4"),
                          ("PDF · 6 páginas", f"carrusel-com-{slug}.pdf"),
                          ("ZIP · 6 láminas", f"laminas-com-{slug}.zip")):
            if existe(arch):
                desc.append({"etq": etq, "url": "descargas/" + arch})
        proyectos.append({
            "id": "com-" + slug, "titulo": tit, "serie": "Comunicación",
            "resumen": res, "nota": nota,
            "etiquetas": tags + ["comunicación"], "fecha": "2026-08-12",
            "formato": "1080×1920", "video": "descargas/reel-com-%s.mp4" % slug
            if existe(f"reel-com-{slug}.mp4") else None,
            "descargas": desc, "piezas": con, "sin_texto": sin or [],
            "carpeta": "file://" + quote(d), "rutaAbs": d,
        })

    for (slug, tit, res, nota, tags, dcon, pcon, dsin, arch_sin,
         mp4, pdf, zipf) in HIST:
        con = piezas("h-" + slug, dcon, pcon)
        sin = [x for x in (piezas("h-" + slug, dsin, a, n=1, sufijo="-sin%d" % i)
                           for i, a in enumerate(arch_sin, 1)) if x]
        sin = [x[0] for x in sin]
        if not con:
            saltados.append(slug); continue
        desc = [{"etq": e, "url": "descargas/" + a}
                for e, a in (("Vídeo MP4", mp4), ("PDF · 7 páginas", pdf),
                             ("ZIP · 6 láminas", zipf)) if existe(a)]
        proyectos.append({
            "id": "h-" + slug, "titulo": tit, "serie": "Historia",
            "resumen": res, "nota": nota, "etiquetas": tags,
            "fecha": "2026-08-11", "formato": "1080×1350 y 1080×1920",
            "video": "descargas/" + mp4 if existe(mp4) else None,
            "descargas": desc, "piezas": con, "sin_texto": sin,
            "carpeta": "file://" + quote(dsin), "rutaAbs": dsin,
        })

    proyectos = desde_esparta() + desde_audio() + proyectos

    # Sello del contenido: la página lo consulta cada seis segundos y se
    # recarga sola cuando cambia. Sin esto había que acordarse de pulsar
    # Cmd+Shift+R, y el usuario lo ha tenido que reclamar tres veces. Un portal
    # que crece mientras produces no puede depender de una tecla.
    import hashlib as _h
    sello = _h.sha1("|".join(sorted(
        "%s:%d:%d" % (x["id"], len(x["descargas"]), len(x["piezas"]))
        for x in proyectos)).encode()).hexdigest()[:12]
    with open(os.path.join(SITIO, "sello.json"), "w", encoding="utf-8") as f:
        json.dump({"sello": sello, "proyectos": len(proyectos)}, f)

    datos = {"sello": sello, "generado": "2026-08-12", "proyecto": PROY,
             "url_sitio": "file://" + quote(os.path.join(SITIO, "index.html")),
             "proyectos": proyectos}
    with open(os.path.join(SITIO, "datos.json"), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)

    idx = os.path.join(SITIO, "index.html")
    html = open(idx, encoding="utf-8").read()
    crudo = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    html, n = re.subn(r'(<script id="datos" type="application/json">).*?(</script>)',
                      lambda m: m.group(1) + crudo + m.group(2), html, flags=re.S)
    if n != 1:
        raise RuntimeError("no encontré el bloque de datos en index.html")
    open(idx, "w", encoding="utf-8").write(html)

    if saltados:
        print("  ! sin láminas: %s" % ", ".join(saltados))
    if minimo_proyectos and len(proyectos) < minimo_proyectos:
        raise RuntimeError(
            "solo salieron %d proyectos y se esperaban al menos %d (faltan: %s). "
            "NO se ha barrido nada ni tocado el portal."
            % (len(proyectos), minimo_proyectos, ", ".join(saltados) or "?"))

    # barrer solo lo que ya no referencia nadie, y NUNCA a lo bruto
    sobran = [n for n in os.listdir(IMG)
              if not n.startswith(".") and n not in _vivos]
    if len(sobran) > TOPE_BARRIDO and barrer:
        raise RuntimeError(
            "el barrido quería borrar %d derivadas (tope %d). Eso significa que "
            "un proyecto ha desaparecido de la lista, no que sobren archivos. "
            "Revísalo; no se ha borrado nada." % (len(sobran), TOPE_BARRIDO))
    huerfanos = 0
    if barrer:
        for n in sobran:
            os.remove(os.path.join(IMG, n))
            huerfanos += 1
    for k in [k for k, v in _cache.items()
              if not all(os.path.exists(os.path.join(IMG, x))
                         for kk, x in v["src"].items() if kk != "max")]:
        del _cache[k]
    _guardar_cache()
    if huerfanos:
        print("  %d derivadas huérfanas barridas" % huerfanos)

    nc = sum(len(p["piezas"]) for p in proyectos)
    ns = sum(len(p["sin_texto"]) for p in proyectos)
    nv = sum(1 for p in proyectos if p["video"])
    nd = sum(len(p["descargas"]) for p in proyectos)
    print("  %d proyectos · %d vídeos · %d descargas" % (len(proyectos), nv, nd))
    print("  %d láminas con texto · %d fondos sin texto" % (nc, ns))
    return datos


if __name__ == "__main__":
    construir()
