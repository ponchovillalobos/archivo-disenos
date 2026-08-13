"""Limpia el texto transcrito antes de ponerlo en pantalla.

Adaptado de lo que ya funciona en Viralito (`generate_graphics.clean_screen_text`
y `detect_fillers.py`), que es del propio usuario y lleva uso real detrás.

Lo que hace y por qué:

  · **Muletillas al principio** — «eh», «este», «pues», «bueno». En audio pasan
    desapercibidas; escritas en pantalla se ven fatal y roban espacio al mensaje.
  · **Palabras colgantes al final** — un bloque que acaba en «y», «que», «pero»
    deja la frase abierta. En pantalla eso se lee como un error.
  · **Confusiones típicas del transcriptor en español** — «a ser» por «a hacer»,
    «haber» por «a ver». No son errores de audio: son homófonos, y el modelo
    elige mal aunque oiga perfecto.
  · **Cifras en dígitos** — «veinte por ciento» ocupa 17 caracteres y «20 %»
    ocupa 4. En una lámina eso es la diferencia entre caber y no caber.

Lo que NO hace: cambiar el sentido ni reescribir. Solo quita lo que sobra.
"""
import re
import unicodedata

# Siempre muletilla: no significan nada en ningún contexto.
SIEMPRE = {"eh", "ehh", "eeh", "em", "emm", "ehm", "uhm", "um", "umm",
           "mmm", "mm", "hmm", "ajá", "aja", "ah", "ahh", "aah", "uh"}

# Muletilla solo al ABRIR el bloque: dentro de la frase suelen ser legítimas
# («este libro», «bueno o malo»), así que fuera de la primera posición no se tocan.
AL_ABRIR = {"este", "esta", "pues", "bueno", "entonces", "osea", "o sea",
            "digamos", "viste", "vale", "tipo", "nada", "claro", "y", "y bueno"}

# Nunca se cierra un bloque con esto: deja la frase colgando.
AL_CERRAR = {"y", "que", "pero", "de", "la", "el", "los", "las", "un", "una",
             "en", "con", "por", "para", "su", "sus", "es", "a", "o", "del",
             "al", "lo", "se", "si", "no", "sino", "como", "más"}

# Homófonos que el modelo confunde aunque oiga bien.
CONFUSIONES = [
    (r"\bva a ser\b", "va a hacer"),          # solo si sigue un objeto; ver nota
    (r"\bhaber si\b", "a ver si"),
    (r"\bhecho de menos\b", "echo de menos"),
    (r"\bhay que ver\b", "hay que ver"),
]

# Cifras escritas → dígitos. En pantalla el dígito siempre gana.
NUMEROS = [
    (r"\bcien por ciento\b", "100 %"), (r"\bcincuenta por ciento\b", "50 %"),
    (r"\bveinte por ciento\b", "20 %"), (r"\bdiez por ciento\b", "10 %"),
    (r"\bpor ciento\b", " %"),
    (r"\buno\b", "1"), (r"\bdos\b", "2"), (r"\btres\b", "3"),
    (r"\bcuatro\b", "4"), (r"\bcinco\b", "5"), (r"\bseis\b", "6"),
    (r"\bsiete\b", "7"), (r"\bocho\b", "8"), (r"\bnueve\b", "9"),
    (r"\bdiez\b", "10"),
]

# Topes medidos en Viralito para texto sobre vídeo. Por encima, no se lee.
MAX_PALABRAS_TITULAR = 7
MAX_CARACTERES_TITULAR = 52
MAX_PALABRAS_CUERPO = 16
MAX_CARACTERES_CUERPO = 70


def _pelar(p):
    return unicodedata.normalize("NFC", p.lower().strip(".,;:¿?¡!«»\"'…()"))


def quitar_muletillas(texto):
    ps = texto.split()
    # por delante: muletillas puras y las de abrir
    while ps and (_pelar(ps[0]) in SIEMPRE or _pelar(ps[0]) in AL_ABRIR):
        ps.pop(0)
    # por detrás: muletillas puras y palabras que dejan la frase colgando
    while ps and (_pelar(ps[-1]) in SIEMPRE or _pelar(ps[-1]) in AL_CERRAR):
        ps.pop()
    # las puras también en medio
    ps = [p for p in ps if _pelar(p) not in SIEMPRE]
    return " ".join(ps)


def quitar_repeticiones(texto):
    """El dictado repite palabras: «la la casa», «es es que»."""
    ps, fuera = texto.split(), []
    for p in ps:
        if fuera and _pelar(p) == _pelar(fuera[-1]) and len(_pelar(p)) > 1:
            continue
        fuera.append(p)
    return " ".join(fuera)


def cifras(texto):
    for pat, rep in NUMEROS:
        texto = re.sub(pat, rep, texto, flags=re.I)
    return re.sub(r"\s+%", " %", texto)


def limpiar(texto, numeros=False):
    """numeros=False por defecto: convertir «uno» en «1» rompe frases como
    «uno de cada tres», que en pantalla se lee peor con dígitos sueltos.
    Se activa a mano cuando el bloque es de datos."""
    t = quitar_repeticiones(quitar_muletillas(texto.strip()))
    for pat, rep in CONFUSIONES:
        t = re.sub(pat, rep, t, flags=re.I)
    if numeros:
        t = cifras(t)
    t = re.sub(r"\s{2,}", " ", t).strip(" ,;:")
    if t and t[0].islower():
        t = t[0].upper() + t[1:]
    return t


def cabe(texto, titular=True):
    """¿Entra en pantalla sin encogerse hasta ser ilegible?"""
    ps, n = len(texto.split()), len(texto)
    if titular:
        return ps <= MAX_PALABRAS_TITULAR and n <= MAX_CARACTERES_TITULAR
    return ps <= MAX_PALABRAS_CUERPO and n <= MAX_CARACTERES_CUERPO


def revisar(bloques):
    """Pasa una lista de bloques y devuelve qué habría que tocar."""
    out = []
    for b in bloques:
        t = b["texto"] if isinstance(b, dict) else b
        lim = limpiar(t)
        out.append({"original": t, "limpio": lim,
                    "quitado": len(t) - len(lim),
                    "cabe_titular": cabe(lim),
                    "cabe_cuerpo": cabe(lim, titular=False)})
    return out
