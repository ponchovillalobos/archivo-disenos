"""El camino del espartano — reto de 30 días.

Los siete valores del Bushidō llevados a Esparta: mismas virtudes, imaginería
griega. Un consejo por día, práctico y aplicable mañana. Nada de filosofía
abstracta: «antes de responder, cuenta hasta tres» antes que «cultiva la
templanza».

Reparto: día 1 abre · días 2-29 son siete valores × cuatro días · día 30 cierra.

Cada vídeo lleva su propia paleta y su propia DISPOSICIÓN de texto, para que se
note que son treinta piezas y no una repetida treinta veces. Y ninguna imagen
lleva cara ni manos, como siempre: los espartanos van de espaldas, lejanos, en
silueta o resueltos por sus objetos.

Estructura de cada uno, seis láminas:
    gancho · lo que se cree · el giro · EL CONSEJO · cómo se nota · remate
"""
VALORES = [
    ("justicia",   "Dikaiosýne", "Justicia"),
    ("valor",      "Andreía",    "Valor"),
    ("compasion",  "Philía",     "Compasión"),
    ("respeto",    "Aidós",      "Respeto"),
    ("verdad",     "Alétheia",   "Verdad"),
    ("honor",      "Timé",       "Honor"),
    ("lealtad",    "Pístis",     "Lealtad"),
]

# (kicker, titular, cuerpo|None, escena)
DIAS = {}


def _d(n, valor, laminas):
    DIAS[n] = {"valor": valor, "laminas": laminas}


_d(1, "apertura", [
 ("Día 1", "Nadie nace espartano.", None,
  "a vast empty stone training ground at dawn, mist low over the sand, no people"),
 ("Lo que se cree", "Que la disciplina es apretar los dientes.", None,
  "a bare stone bench in an empty colonnade, first light across it"),
 ("El giro", "La disciplina no es fuerza. Es repetición sin público.", None,
  "a single worn path across a wide grass field, walked a thousand times"),
 ("El trato", "Elige la hora y no la muevas.",
  "Siete de la mañana, o al llegar a la mesa, o antes de dormir. La misma todos los días. Escríbela en el móvil ahora: «Camino — 07:00». Treinta días, un gesto al día.",
  "a row of thirty identical stone markers receding into morning light"),
 ("Cómo se nota", "Al décimo día deja de costar. Al vigésimo eres tú.", None,
  "a bronze cup left on a low wall, worn smooth by use, warm sun"),
 ("", "Empieza hoy. Mañana ya son veintinueve.", None,
  "a wide stone gateway open onto bright open country"),
])

# ── JUSTICIA · Dikaiosýne ────────────────────────────────────────────────────
_d(2, "justicia", [
 ("Día 2 · Justicia", "Lo justo cuesta cuando te toca a ti.", None,
  "an ancient bronze balance scale on a stone plinth, perfectly level, open sky"),
 ("Lo que se cree", "Que ser justo es no hacer daño.", None,
  "an empty stone amphitheatre seen from the highest row, morning light"),
 ("El giro", "Ser justo es reconocer cuando el que gana eres tú.", None,
  "two stone seats of different heights facing each other in an empty hall"),
 ("Hoy", "Devuelve algo que nadie te reclamó.",
  "Tres sitios donde buscarlo: un mérito que te llevaste en una reunión, una idea que era de un compañero, un turno o una guardia que le tocaba a otro. Elige uno, devuélvelo hoy y no lo anuncies.",
  "a bronze coin left alone on a worn stone step, warm light"),
 ("Cómo se nota", "Empiezas a fiarte de ti mismo.", None,
  "a straight paved road running to the horizon under clear sky"),
 ("", "Justo es quien se corrige a sí mismo primero.", None,
  "a stone wall built perfectly level across a hillside at sunrise"),
])

_d(3, "justicia", [
 ("Día 3 · Justicia", "El reparto habla más que el discurso.", None,
  "a long stone table set with equal portions in an empty hall, bright light"),
 ("Lo que se cree", "Que repartir igual es repartir justo.", None,
  "identical bronze cups in a perfect row on a stone shelf"),
 ("El giro", "Justo no es lo mismo para todos. Es lo mismo para quien está igual.",
  None, "two olive trees of different size in the same field, one shaded"),
 ("Hoy", "Mira quién ha hablado menos y dale el turno.",
  "En la reunión, en la mesa, en el grupo. El que no habla casi nunca es el que "
  "no tiene sitio, no el que no tiene qué decir.",
  "an empty speaker's step in a stone assembly, sunlight on it"),
 ("Cómo se nota", "La gente empieza a traerte lo que piensa de verdad.", None,
  "a circle of stone seats, all at the same height, open sky above"),
 ("", "El reparto es el mensaje.", None,
  "bread and water set out in equal portions on a bare stone table"),
])

_d(4, "justicia", [
 ("Día 4 · Justicia", "Defender al ausente cuesta un segundo.", None,
  "an empty stone chair among occupied ones in a bright hall"),
 ("Lo que se cree", "Que callar es neutral.", None,
  "a closed bronze door in a sunlit corridor"),
 ("El giro", "Callar cuando hablan mal del que no está es tomar partido.", None,
  "one long shadow crossing a bright courtyard, the caster out of frame"),
 ("Hoy", "Di una frase por quien no puede oírla.",
  "No hace falta discutir. «Conmigo se portó bien.» «Eso no me consta.» Basta "
  "con que la conversación deje de correr sola.",
  "a bronze shield propped alone against a wall, catching the sun"),
 ("Cómo se nota", "Dejan de contarte cosas que no dirían delante.", None,
  "an open window with clean light pouring into a stone room"),
 ("", "Al ausente lo defiende quien tiene poco que ganar.", None,
  "a single olive tree standing alone on a bright ridge"),
])

_d(5, "justicia", [
 ("Día 5 · Justicia", "La regla que aplicas a otros es la tuya.", None,
  "identical stone blocks cut to the same measure, sunlight raking across"),
 ("Lo que se cree", "Que hay circunstancias.", None,
  "a stone path that forks, both branches equally worn"),
 ("El giro", "Las circunstancias las tienen todos. Solo las tuyas te las sabes.",
  None, "two identical doorways in a sunlit wall, one with light behind"),
 ("Hoy", "Ponte tú en la frase con que juzgaste a alguien.",
  "«Llegó tarde otra vez.» «Se le olvidó.» «No revisó bien.» Coge la que dijiste esta semana, cámbiale el sujeto por tu nombre y mira si la sostienes igual.",
  "a polished bronze mirror leaning against a stone wall, reflecting sky"),
 ("Cómo se nota", "Juzgas menos y entiendes antes.", None,
  "an open sunlit courtyard with a single clean stone bench"),
 ("", "La misma vara. Siempre. Empezando por ti.", None,
  "a measuring rod of bronze resting on level stone, bright light"),
])

# ── VALOR · Andreía ──────────────────────────────────────────────────────────
_d(6, "valor", [
 ("Día 6 · Valor", "El valor no es no tener miedo.", None,
  "a narrow mountain pass at dawn, empty, light coming through"),
 ("Lo que se cree", "Que el valiente no siente nada.", None,
  "a bronze helmet resting alone on a stone ledge, warm light"),
 ("El giro", "El valiente siente lo mismo. Solo que se mueve igual.", None,
  "a single set of footprints crossing wet sand toward the sea"),
 ("Hoy", "Haz la llamada que llevas aplazando.",
  "La del cliente al que le debes un no. La del banco. La de tu padre. Ponle hora ahora mismo y no la prepares más: prepararla otra vez es la forma educada de no hacerla.",
  "an empty stone doorway with bright daylight beyond it"),
 ("Cómo se nota", "Lo aplazado deja de pesar todo el día.", None,
  "a clear morning field with the mist already lifting"),
 ("", "El miedo no se va. Se camina con él.", None,
  "a worn stone path climbing steadily into open light"),
])

_d(7, "valor", [
 ("Día 7 · Valor", "Decir «no sé» es una forma de coraje.", None,
  "an open empty scroll on a stone table, clean light"),
 ("Lo que se cree", "Que reconocerlo te resta.", None,
  "a wall of identical sealed clay jars in a bright storeroom"),
 ("El giro", "Lo que resta es que te pillen sabiendo menos de lo que dijiste.",
  None, "a cracked clay jar among whole ones, light through the crack"),
 ("Hoy", "Di «no lo sé, lo miro y te digo el jueves».",
  "Con esa fecha dentro. Cuando te pregunten un número que no tienes, un plazo que no controlas o una causa que no has mirado. «No lo sé» a secas deja el hueco abierto; con la fecha, lo cierra.",
  "an empty speaker's platform in a sunlit stone hall"),
 ("Cómo se nota", "Cuando dices que sabes, te creen.", None,
  "clear water in a shallow stone basin, bottom visible"),
 ("", "El que admite el límite es el que tiene autoridad dentro de él.", None,
  "a boundary stone standing alone in a bright open field"),
])

_d(8, "valor", [
 ("Día 8 · Valor", "Lo difícil primero.", None,
  "a steep stone stairway rising into morning light, empty"),
 ("Lo que se cree", "Que hay que calentar con lo fácil.", None,
  "a pile of small smooth stones beside one large block"),
 ("El giro", "Lo fácil primero se come el día. Lo difícil se queda para nunca.",
  None, "a long shadow of a sundial across bright stone, late in the day"),
 ("Hoy", "Lo primero de la mañana, lo que más te pesa.",
  "Antes del correo, antes del móvil, antes de la lista. Veinte minutos. Si "
  "solo avanzas veinte minutos, ya no es el mismo día.",
  "first sunlight hitting the top of a stone tower, everything below in shade"),
 ("Cómo se nota", "El resto del día pesa la mitad.", None,
  "an open sunlit courtyard, clean and swept, nothing pending"),
 ("", "Lo que aplazas no descansa. Trabaja contra ti.", None,
  "a heavy stone block already moved, its drag marks in the sand"),
])

_d(9, "valor", [
 ("Día 9 · Valor", "Pedir ayuda no es rendirse.", None,
  "two bronze shields leaning together against a sunlit wall"),
 ("Lo que se cree", "Que el fuerte se basta solo.", None,
  "a single spear standing upright in the sand, alone"),
 ("El giro", "La falange no era fuerte por cada hombre. Era fuerte porque se "
  "tocaban.", None,
  "a line of bronze shields overlapping in bright sun, no people"),
 ("Hoy", "Pide una cosa concreta a una persona concreta.",
  "No «a ver si me echas una mano». Di qué, para cuándo y por qué se lo pides "
  "a él. Lo vago se ignora sin culpa.",
  "an open hand-worn stone doorway, bright light through it"),
 ("Cómo se nota", "Descubres que la gente quería que se lo pidieras.", None,
  "two stone seats side by side facing the same view, sunlit"),
 ("", "Solo llegas antes. Acompañado llegas.", None,
  "a wide stone bridge spanning a gorge, both ends anchored"),
])

# ── COMPASIÓN · Philía ───────────────────────────────────────────────────────
_d(10, "compasion", [
 ("Día 10 · Compasión", "La fuerza que no sabe ser suave es solo dureza.", None,
  "a bronze cup of water left on a stone step in warm light"),
 ("Lo que se cree", "Que la compasión ablanda.", None,
  "a worn wool cloak folded on a stone bench, sunlight on it"),
 ("El giro", "Solo puede ser suave el que podría no serlo.", None,
  "a bronze sword laid flat and sheathed on a stone table"),
 ("Hoy", "Pregunta dos veces: «¿cómo estás?» y luego «¿y de verdad?».",
  "A la persona de la mesa de al lado, al de la llamada de las nueve, a quien vive contigo. La primera pregunta se contesta con «bien». La segunda es la que abre. Y después, cállate un minuto entero.",
  "two stone seats facing each other, close, in gentle morning light"),
 ("Cómo se nota", "La gente empieza a contarte lo segundo que iba a decir.", None,
  "an open courtyard with a small fountain, water catching the light"),
 ("", "El escudo protege al de al lado, no a ti.", None,
  "a bronze shield held out over an empty space, casting shade"),
])

_d(11, "compasion", [
 ("Día 11 · Compasión", "Casi nadie te está atacando.", None,
  "a closed bronze gate with morning light around its edges"),
 ("Lo que se cree", "Que si te hablan mal es contra ti.", None,
  "a stone wall with one dark stain, the rest clean and bright"),
 ("El giro", "Casi siempre es la mañana que ha tenido, no la frase que has "
  "dicho.", None,
  "a storm passing over a bright plain, the sun already returning"),
 ("Hoy", "Ante una respuesta seca, pregunta antes de responder.",
  "«¿Va todo bien?» Cuatro palabras. Cambian la conversación y te ahorran una "
  "discusión que no era tuya.",
  "a calm shallow pool of water reflecting an open sky"),
 ("Cómo se nota", "Dejas de coleccionar enfados que no eran para ti.", None,
  "a clean swept stone floor with long soft morning shadows"),
 ("", "Casi nadie madruga para hacerte daño.", None,
  "an empty road at dawn with the sun coming up straight ahead"),
])

_d(12, "compasion", [
 ("Día 12 · Compasión", "El que se equivoca ya lo sabe.", None,
  "a chipped stone block set into an otherwise perfect wall"),
 ("Lo que se cree", "Que hay que señalarlo para que aprenda.", None,
  "a raised stone platform in an empty sunlit square"),
 ("El giro", "Repetirle el error solo enseña a esconder el siguiente.", None,
  "a closed wooden shutter on a bright stone facade"),
 ("Hoy", "Pregunta «¿qué necesitas?» en vez de «¿qué pasó?».",
  "Se le cayó el pedido, se pasó la fecha, mandó el archivo mal. Lo que pasó ya lo sabéis los dos. Lo que necesita —tiempo, una mano, permiso para pedir ayuda— es lo único que cambia el mañana.",
  "an open toolbox of bronze implements on a workbench, clean light"),
 ("Cómo se nota", "Te enteras de los problemas cuando aún son pequeños.", None,
  "a small crack in a stone wall, caught early, sunlight across it"),
 ("", "El que puede confesar un error, corrige dos.", None,
  "a repaired section of stone wall, the join visible and solid"),
])

_d(13, "compasion", [
 ("Día 13 · Compasión", "Dar sin que se note es dar dos veces.", None,
  "a bundle of grain left at a doorway at dawn, nobody there"),
 ("Lo que se cree", "Que hay que reconocer lo que se da.", None,
  "an inscribed stone tablet in bright sun, letters worn away"),
 ("El giro", "En cuanto se menciona, deja de ser un regalo y pasa a ser una "
  "factura.", None,
  "a bronze coin on a stone counter, beside an empty ledger"),
 ("Hoy", "Quítale un paso a alguien sin decírselo.",
  "Rellena el formulario que le tocaba, reserva la sala que iba a buscar, deja el café hecho, manda tú el correo de seguimiento. Uno solo. Y aguanta las ganas de que se entere: ahí está el ejercicio entero.",
  "a swept path leading to a doorway, the broom left aside"),
 ("Cómo se nota", "Se te quita el hábito de llevar la cuenta.", None,
  "an open empty ledger on a stone table, bright light"),
 ("", "Da algo que no puedas cobrar.", None,
  "an open gate left unlocked at sunrise, path beyond"),
])

# ── RESPETO · Aidós ──────────────────────────────────────────────────────────
_d(14, "respeto", [
 ("Día 14 · Respeto", "El respeto se ve en los detalles pequeños.", None,
  "a pair of worn sandals set neatly by a doorway, morning light"),
 ("Lo que se cree", "Que es cuestión de formas.", None,
  "a formal stone portico, symmetrical and empty, bright sun"),
 ("El giro", "Es cuestión de atención. Las formas solo la hacen visible.", None,
  "a stone step worn in the middle by careful feet, sunlit"),
 ("Hoy", "Sal cinco minutos antes de cada cosa.",
  "De casa, de la reunión anterior, de la comida. No es puntualidad: es margen. Llegar tarde dice que tu tiempo vale más que el suyo, y lo dice sin que tengas que abrir la boca.",
  "a bronze sundial casting a sharp clean shadow at exact noon"),
 ("Cómo se nota", "Empiezan a contar contigo para lo importante.", None,
  "a stone table set for a meeting, everything already in place"),
 ("", "La puntualidad es la primera forma del respeto.", None,
  "clean morning light across an empty, perfectly swept courtyard"),
])

_d(15, "respeto", [
 ("Día 15 · Respeto", "Escuchar es más caro que hablar.", None,
  "an empty stone amphitheatre from the stage, every seat visible"),
 ("Lo que se cree", "Que escuchar es esperar tu turno.", None,
  "a row of bronze trumpets hanging on a sunlit wall"),
 ("El giro", "Si mientras oyes estás preparando tu frase, no estás escuchando.",
  None, "two bronze cups on a table, one full and one empty"),
 ("Hoy", "No interrumpas ni una vez en toda la mañana.",
  "Ni para completar la frase, ni para dar la razón. Aguanta hasta el punto "
  "final. Es más difícil de lo que parece y se nota desde el primer intento.",
  "a still, silent stone courtyard at midday, sharp light"),
 ("Cómo se nota", "La conversación se alarga y aparece lo que importaba.", None,
  "a deep clear well of water in bright stone, bottom visible"),
 ("", "Quien escucha entero, decide mejor.", None,
  "an open scroll fully unrolled on a stone table, clean light"),
])

_d(16, "respeto", [
 ("Día 16 · Respeto", "El nombre de la gente importa.", None,
  "names carved into a bright stone wall, worn but legible"),
 ("Lo que se cree", "Que es un detalle menor.", None,
  "a row of identical unmarked clay jars in a bright storeroom"),
 ("El giro", "Es lo primero que le quitas a alguien cuando lo tratas como "
  "función.", None,
  "one jar with a name scratched on it among the unmarked ones"),
 ("Hoy", "Aprende el nombre de alguien que ves a diario y no sabes.",
  "El del portal, el de la cafetería, el del turno de noche. Pregúntalo, "
  "úsalo, y no lo vuelvas a olvidar.",
  "a small bronze nameplate beside a wooden door, catching the sun"),
 ("Cómo se nota", "El sitio donde trabajas deja de ser un sitio.", None,
  "a busy sunlit market square, empty of people, stalls set up"),
 ("", "Con el nombre empieza el trato.", None,
  "a hand-cut inscription on bright stone, one word, deep and clean"),
])

_d(17, "respeto", [
 ("Día 17 · Respeto", "Al que no te sirve de nada.", None,
  "a modest stone doorway beside a grand one, both open, same light"),
 ("Lo que se cree", "Que se trata bien a quien puede devolvértelo.", None,
  "a tiered stone seating arrangement, the top rows in shade"),
 ("El giro", "Cómo tratas al que no te sirve es lo único que dice cómo eres.",
  None, "two identical bronze cups, one on a high shelf and one on the floor"),
 ("Hoy", "Trata al que no te aporta nada como al que decide.",
  "El becario, el proveedor pequeño, el que llamó por error. Un minuto entero "
  "de atención real. Nadie te va a ver hacerlo, y por eso cuenta.",
  "an empty stone bench in an unremarkable corner, warm light on it"),
 ("Cómo se nota", "Dejas de tener dos caras y descansas.", None,
  "one clean shadow cast by a single figure-less column at noon"),
 ("", "Se te juzga por cómo tratas a quien no puede pagarte.", None,
  "a wide-open gate with no guard, bright country beyond"),
])

# ── VERDAD · Alétheia ────────────────────────────────────────────────────────
_d(18, "verdad", [
 ("Día 18 · Verdad", "La palabra dada, sin contrato.", None,
  "two bronze cups touching on a stone table, sunlit"),
 ("Lo que se cree", "Que basta con cumplir lo firmado.", None,
  "a sealed clay tablet on a stone desk, bright light"),
 ("El giro", "Lo que te define es lo que cumples sin que nadie pueda "
  "reclamártelo.", None,
  "an unsealed scroll left open and unattended in the sun"),
 ("Hoy", "Cumple una promesa pequeña que nadie recuerda.",
  "El «te mando eso», el «te llamo el jueves». Búscala en tu cabeza, que "
  "seguro que hay una, y cúmplela hoy aunque ya no importe.",
  "a bronze bell hanging still, rope reaching down, morning light"),
 ("Cómo se nota", "Empiezas a prometer menos y a valer más.", None,
  "a short row of stone markers, few but perfectly aligned"),
 ("", "La palabra pesa lo que pesa la última que cumpliste.", None,
  "one deep clean chisel mark on bright stone"),
])

_d(19, "verdad", [
 ("Día 19 · Verdad", "Decirlo antes de que se sepa.", None,
  "an open doorway with nothing hidden behind it, full daylight"),
 ("Lo que se cree", "Que hay que esperar al momento oportuno.", None,
  "a closed shutter with light leaking around every edge"),
 ("El giro", "El momento oportuno para una mala noticia es siempre antes.", None,
  "a small crack in a stone wall, caught while still small, bright light"),
 ("Hoy", "Adelanta el problema que va a salir igual.",
  "El retraso, el error, el número que no va a salir. Dilo tú primero y con la "
  "solución al lado. La misma noticia cambia de dueño.",
  "a messenger's empty stone road at first light, straight and open"),
 ("Cómo se nota", "Se acaban las conversaciones incómodas de después.", None,
  "a clean-swept stone floor with nothing under the furniture"),
 ("", "La verdad tarde es una mentira que se agotó.", None,
  "a sundial at exact noon, shadow at its shortest"),
])

_d(20, "verdad", [
 ("Día 20 · Verdad", "Exagerar es mentir despacio.", None,
  "a bronze measuring vessel filled exactly to its line, bright light"),
 ("Lo que se cree", "Que redondear hacia arriba no hace daño.", None,
  "a slightly tilted balance scale, almost level but not quite"),
 ("El giro", "Quien te oye exagerar en lo pequeño te descuenta en lo grande.",
  None, "two identical jars, one with a false bottom, cut away in light"),
 ("Hoy", "Di la cifra exacta, aunque sea peor.",
  "«Casi mil» cuando son ochocientos. «Enseguida» cuando son dos días. "
  "Cámbialo por el número. Cuesta una vez y te compra el resto.",
  "a precise bronze scale in perfect balance on clean stone"),
 ("Cómo se nota", "Tus números dejan de necesitar defensa.", None,
  "clear shallow water over pale stones, everything visible"),
 ("", "El que no exagera no tiene que recordar qué dijo.", None,
  "a single straight measuring rod against a clean stone wall"),
])

_d(21, "verdad", [
 ("Día 21 · Verdad", "La disculpa sin «pero».", None,
  "a plain open stone doorway, nothing beside it, clean light"),
 ("Lo que se cree", "Que hay que explicar el contexto.", None,
  "a long inscribed wall of dense text in bright sun"),
 ("El giro", "Todo lo que va detrás del «pero» borra lo que va delante.", None,
  "a clean stone tablet with a single short line carved on it"),
 ("Hoy", "Discúlpate con una sola frase y cállate.",
  "«Me equivoqué y lo arreglo así.» Sin contexto, sin quién más falló, sin lo "
  "difícil que fue. El silencio de después es la mitad de la disculpa.",
  "one clean chisel line on bright stone, nothing else"),
 ("Cómo se nota", "Se te perdona antes y se te cree después.", None,
  "an open sunlit courtyard, swept, with nothing left standing"),
 ("", "La disculpa entera cabe en una línea.", None,
  "a single short inscription on a bright stone block"),
])

# ── HONOR · Timé ─────────────────────────────────────────────────────────────
_d(22, "honor", [
 ("Día 22 · Honor", "Lo que haces cuando no te ven.", None,
  "an empty training ground at night under a clear moon, footprints in sand"),
 ("Lo que se cree", "Que el honor es reputación.", None,
  "a public stone monument in bright daylight, inscribed"),
 ("El giro", "La reputación es lo que dicen. El honor es lo que sabes.", None,
  "the same monument seen from behind, in shade, plain and unadorned"),
 ("Hoy", "Termina bien algo que nadie va a abrir.",
  "El informe que solo se archiva. La carpeta compartida sin ordenar. El cierre de caja del viernes. Elige uno y déjalo como si lo fueran a inspeccionar el lunes. Y no lo cuentes.",
  "a stone joint finished perfectly on the hidden side of a wall"),
 ("Cómo se nota", "Dejas de necesitar que te lo reconozcan.", None,
  "a solid stone foundation, mostly buried, catching low light"),
 ("", "El honor no tiene testigos.", None,
  "an empty moonlit courtyard, swept clean, no one there"),
])

_d(23, "honor", [
 ("Día 23 · Honor", "No aceptar lo que no te has ganado.", None,
  "a bronze laurel wreath resting on an empty stone plinth"),
 ("Lo que se cree", "Que rechazar un halago es falsa modestia.", None,
  "a decorated stone niche, empty, in bright light"),
 ("El giro", "Aceptar un mérito ajeno te obliga a defenderlo para siempre.",
  None, "a heavy bronze shield hanging too high on a wall"),
 ("Hoy", "Devuelve un elogio a quien le tocaba.",
  "«Eso fue idea suya.» En público, con nombre, en el momento. Cuesta cinco "
  "segundos y te lo devuelven multiplicado.",
  "two bronze wreaths side by side on a stone shelf, equal"),
 ("Cómo se nota", "La gente empieza a querer trabajar contigo.", None,
  "a row of names carved equally on a bright stone wall"),
 ("", "Lo que no ganaste, pesa.", None,
  "an empty plinth in clean light, its inscription blank"),
])

_d(24, "honor", [
 ("Día 24 · Honor", "Sostener lo que dijiste ayer.", None,
  "a stone column standing straight and alone in bright open ground"),
 ("Lo que se cree", "Que cambiar de idea es debilidad.", None,
  "a weather-worn stone marker leaning slightly"),
 ("El giro", "Cambiar de idea con motivo es fuerza. Cambiarla por conveniencia "
  "es otra cosa.", None,
  "the same marker reset upright, fresh stone at its base"),
 ("Hoy", "Repite delante de otros lo que dijiste en privado.",
  "Lo que le dijiste al jefe a solas, dilo en la reunión. Lo que dijiste del proyecto en el pasillo, dilo en el grupo. Si no puedes, tienes dos salidas honradas: explicar qué ha cambiado, o admitir que lo dijiste para quedar bien.",
  "one straight bronze rod set into stone, unbending"),
 ("Cómo se nota", "Tu palabra empieza a valer sin que la defiendas.", None,
  "a long line of identical upright stones across a sunlit field"),
 ("", "El que dice lo mismo en dos habitaciones, descansa.", None,
  "two identical doorways in bright sun, both open onto the same view"),
])

_d(25, "honor", [
 ("Día 25 · Honor", "Perder bien.", None,
  "a broken spear laid neatly on a stone step, morning light"),
 ("Lo que se cree", "Que perder se supera ganando.", None,
  "an empty victory podium of stone in harsh bright sun"),
 ("El giro", "Cómo pierdes se recuerda más que cómo ganas.", None,
  "a bronze shield with a deep dent, polished and hung with care"),
 ("Hoy", "Reconoce en voz alta que el otro tenía razón.",
  "En la discusión que perdiste esta semana. Sin matizar, sin «en parte». "
  "Nadie ha perdido nunca nada por decirlo entero.",
  "two bronze cups raised on a stone table, one slightly lower"),
 ("Cómo se nota", "Discutir contigo deja de ser caro.", None,
  "an open sunlit space where two paths meet and continue as one"),
 ("", "Se mide más en la derrota que en la victoria.", None,
  "a worn stone step, the wear even on both sides"),
])

# ── LEALTAD · Pístis ─────────────────────────────────────────────────────────
_d(26, "lealtad", [
 ("Día 26 · Lealtad", "La lealtad se demuestra cuando cuesta.", None,
  "a line of overlapping bronze shields holding, seen from behind"),
 ("Lo que se cree", "Que es estar cuando todo va bien.", None,
  "a full stone banquet table in bright light, everything laid out"),
 ("El giro", "Cuando todo va bien no hace falta lealtad. Basta con estar "
  "cómodo.", None,
  "the same table, empty and swept, in plain daylight"),
 ("Hoy", "Manda tres líneas: «me acordé de ti, no hace falta que contestes».",
  "Al que se quedó sin trabajo, al que está con su padre en el hospital, al que lleva dos meses callado en el grupo. No preguntes cómo va ni ofrezcas ayuda: eso obliga a responder. Basta con que sepa que lo notaste.",
  "a small lamp burning in a stone window at dusk, seen from outside"),
 ("Cómo se nota", "Descubres quién hizo lo mismo por ti.", None,
  "two lamps lit in two windows across a courtyard"),
 ("", "La lealtad se nota en el mal año.", None,
  "a bronze shield left covering an empty position in the line"),
])

_d(27, "lealtad", [
 ("Día 27 · Lealtad", "Criticar de frente. Defender de espaldas.", None,
  "two stone seats face to face in a bright empty room"),
 ("Lo que se cree", "Que hay que evitar el conflicto.", None,
  "a smooth unbroken stone wall in flat light"),
 ("El giro", "Lo que evita el conflicto no es la paz: es el rumor.", None,
  "the same wall from behind, cracked and unrepaired"),
 ("Hoy", "Dile a la cara la frase exacta que ibas a decir por detrás.",
  "«Creo que llegas tarde a todo.» «Ese trabajo lo entregaste a medias.» La misma frase, sin suavizar, mirándole. Una sola. La que más te cuesta.",
  "an open sunlit doorway between two stone rooms"),
 ("Cómo se nota", "Se acaban las conversaciones paralelas.", None,
  "a single clear path through an open field, no branches"),
 ("", "De frente cuesta un rato. Por detrás cuesta la relación.", None,
  "two stone columns standing at equal height, facing each other"),
])

_d(28, "lealtad", [
 ("Día 28 · Lealtad", "Estar en el sitio de al lado.", None,
  "a gap in a line of bronze shields, exactly one shield wide"),
 ("Lo que se cree", "Que cada uno responde de lo suyo.", None,
  "separate stone plots divided by low walls, bright sun"),
 ("El giro", "En la falange, tu escudo cubría al de tu derecha. No a ti.", None,
  "overlapping shields where each covers the man beside, bright bronze"),
 ("Hoy", "Cubre un hueco que no es tuyo.",
  "El correo que se le pasó, el pedido que no confirmó, la sala que nadie reservó. Hazlo y avísale después, nunca antes: avisar antes es pedir permiso para lucirte.",
  "a single shield moved sideways to close a gap in the line"),
 ("Cómo se nota", "Alguien cubre el tuyo el día que faltas.", None,
  "an unbroken line of shields under bright sun, no gaps"),
 ("", "La línea aguanta por los lados, no por el centro.", None,
  "a long unbroken bronze line receding into bright light"),
])

_d(29, "lealtad", [
 ("Día 29 · Lealtad", "Contigo mismo también.", None,
  "a single set of footprints returning along the same path"),
 ("Lo que se cree", "Que la lealtad es hacia los demás.", None,
  "a crowded row of stone seats, all facing one direction"),
 ("El giro", "El que se falla a sí mismo todos los días acaba fallando a "
  "todos.", None,
  "one seat turned to face the opposite way, bright light on it"),
 ("Hoy", "Haz la cosa de diez minutos que llevas semanas moviendo.",
  "La cita médica que no pides, el recibo que no reclamas, el mensaje que no contestas, los diez minutos de ejercicio. Elige una, ponle hora y táchala hoy.",
  "a lamp lit in an empty stone room at dawn, no one there"),
 ("Cómo se nota", "Vuelves a creerte cuando te dices algo.", None,
  "clean footprints leading straight out of a stone doorway"),
 ("", "El primero al que hay que serle leal es al de mañana.", None,
  "a path continuing straight into bright open country"),
])

_d(30, "cierre", [
 ("Día 30", "No eres el que empezó.", None,
  "a worn stone path seen from its end, the way back visible"),
 ("Lo que se cree", "Que treinta días cambian a alguien.", None,
  "a bronze mirror on a stone table, reflecting only sky"),
 ("El giro", "Treinta días no te cambian. Te enseñan qué eras capaz de "
  "sostener.", None,
  "thirty stone markers behind, one path ahead, bright light"),
 ("Lo que queda", "Escribe los tres que repetirías mañana.",
  "Coge los veintinueve, tacha los que hiciste por obligación y quédate con los tres que menos te costaron y más te cambiaron el día. Esos tres son tu camino. El resto era el examen.",
  "three stone markers standing together in clean morning light"),
 ("Cómo se nota", "Ya no necesitas el reto para hacerlos.", None,
  "a worn path continuing without markers, into open country"),
 ("", "Espartano no es el que resiste treinta días. Es el que sigue el "
  "treinta y uno.", None,
  "an open horizon at sunrise with a single road running into it"),
])


def laminas(dia):
    """Las seis láminas del día, listas para el montador."""
    from reel2 import ESCALA
    fuera = []
    for i, (k, t, c, _esc) in enumerate(DIAS[dia]["laminas"], 1):
        tam = ESCALA[2] if (c and len(c) > 100) else ESCALA[4]
        fuera.append({"fondo": "f%d.png" % i, "kicker": k, "titular": t,
                      "cuerpo": c, "lista": None, "tam": tam})
    return fuera


def escenas(dia):
    return [x[3] for x in DIAS[dia]["laminas"]]
