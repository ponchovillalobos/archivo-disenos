"""Guiones de los dieciséis temas que tenían imágenes y no tenían texto.

Se generaron 96 imágenes con las escenas de `temas3.py` y nunca se escribió el
guion, así que ninguno llegó a ser vídeo. Esto lo cierra.

**Ninguno cita un estudio.** Son piezas de oficio —cómo funciona una analogía,
por qué el orden importa, qué hace el silencio— no de dato. Esa decisión es
deliberada: la regla dura del proyecto es que ningún dato sale sin verificar en
fuente primaria, y escribir dieciséis guiones con cifras habría significado
dieciséis verificaciones. Antes que inventar una cifra, se escribe sin cifra.

Estructura de siempre: poco · medio · poco · MUCHO · medio · poco. El giro cae
en la lámina 3, nunca más tarde. La 4 es la densa, porque es la que se guarda.
"""

# tema: [(kicker, titular, cuerpo), ...] — seis por tema
GUIONES = {

 "analogia": [
  ("", "Explicar es traducir.", None),
  ("Lo que se hace", "Repetir lo mismo más despacio y más alto.",
   "Cuando alguien no entiende, casi todos subimos el volumen en vez de cambiar de mapa."),
  ("El giro", "Si no lo entiende, no es que no escuche. Es que no tiene dónde ponerlo.",
   None),
  ("Cómo funciona una analogía", "Prestas un lugar conocido.",
   "No simplifica la idea: le da un sitio donde aterrizar. Por eso una buena "
   "analogía se recuerda cuando ya se olvidó la explicación."),
  ("El riesgo", "Toda analogía miente en algún punto.",
   "La buena avisa dónde deja de valer. La mala se defiende hasta que se cae."),
  ("", "No expliques mejor. Explica desde otro sitio.", None),
 ],

 "autoridad": [
  ("", "La autoridad no se reclama. Se concede.", None),
  ("Lo que se hace", "Enseñar el título antes que el argumento.", None),
  ("El giro", "El título abre la puerta. Lo que la mantiene abierta es otra cosa.",
   None),
  ("Qué la sostiene", "Cuatro cosas, y ninguna es el cargo.",
   None, [("Precisión", "dices exactamente lo que sabes"),
          ("Límite", "y dónde deja de saber"),
          ("Constancia", "sostienes lo mismo cuando nadie mira"),
          ("Rectificación", "y cambias cuando aparece la prueba")]),
  ("Lo que la rompe", "Una sola afirmación defendida más allá de la evidencia.",
   "Se tarda años en construirla y una frase en gastarla."),
  ("", "Se te concede mientras la mereces. Ni un minuto más.", None),
 ],

 "cerrar": [
  ("", "Cerrar no es empujar.", None),
  ("Lo que se hace", "Insistir cuando ya no hay nada más que decir.", None),
  ("El giro", "Si hay que empujar, es que falta algo. Y ese algo casi nunca es "
   "más presión.", None),
  ("Lo que suele faltar", "Tres cosas, y las tres se preguntan.",
   None, [("Claridad", "no ha entendido qué gana"),
          ("Permiso", "no es él quien decide"),
          ("Momento", "lo ha entendido y hoy no toca")]),
  ("Lo que hace la presión", "Convierte una duda en un no.",
   "Un no dicho para acabar la conversación es mucho más difícil de mover que una duda."),
  ("", "No cierres. Quita lo que estorba y deja cerrar.", None),
 ],

 "compromiso": [
  ("", "Lo que se dice en voz alta pesa distinto.", None),
  ("Lo que se hace", "Pedir un sí grande de entrada.", None),
  ("El giro", "El compromiso no empieza en la decisión. Empieza en el primer "
   "paso pequeño.", None),
  ("Por qué el paso pequeño importa", "Cambia quién crees que eres.",
   "Después del primer paso ya no estás decidiendo si hacerlo: estás siendo "
   "coherente contigo. Y la coherencia cuesta mucho menos que la decisión."),
  ("El reverso", "También funciona en contra.",
   "Quien dice un no pequeño en público se queda atado a él aunque cambie de idea."),
  ("", "No pidas la decisión. Pide el primer paso.", None),
 ],

 "contraste": [
  ("", "Nada significa nada solo.", None),
  ("Lo que se hace", "Describir la cosa con más detalle.", None),
  ("El giro", "Lo que da sentido no es el detalle. Es al lado de qué lo pones.",
   None),
  ("Cómo se usa", "Tres contrastes que cambian una frase entera.",
   None, [("Antes y después", "el mismo hecho, dos momentos"),
          ("Con y sin", "el mismo mundo, quitando una pieza"),
          ("Ellos y nosotros", "el mismo problema, dos respuestas")]),
  ("El abuso", "Un contraste falso convence igual de rápido.",
   "Por eso hay que comprobar que la otra mitad de la comparación existe de verdad."),
  ("", "No describas más. Pon algo al lado.", None),
 ],

 "el-orden": [
  ("", "El mismo argumento, en otro orden, es otro argumento.", None),
  ("Lo que se hace", "Empezar por el principio.", None),
  ("El giro", "El principio de la historia casi nunca es el principio de la "
   "conversación.", None),
  ("Qué va primero", "Lo que hace que lo siguiente importe.",
   "Una cifra antes de que se entienda el problema es ruido. Después del "
   "problema, es la respuesta. Es la misma cifra."),
  ("La prueba", "Léelo al revés.",
   "Si al invertir el orden se entiende mejor, el orden estaba mal."),
  ("", "No cuentes lo que pasó. Cuenta lo que hace falta saber para entenderlo.",
   None),
 ],

 "el-tono": [
  ("", "El tono llega antes que las palabras.", None),
  ("Lo que se hace", "Cuidar mucho qué se dice.", None),
  ("El giro", "El otro decide si te escucha antes de procesar una sola frase.",
   None),
  ("Qué se oye primero", "Tres señales, todas anteriores al contenido.",
   None, [("El ritmo", "prisa o calma"),
          ("El volumen", "cuánto espacio te tomas"),
          ("El cierre", "si la frase baja o sube al final")]),
  ("Lo que no arregla el contenido", "Un buen argumento con tono defensivo se "
   "oye como una excusa.", None),
  ("", "Antes de elegir las palabras, elige cómo van a sonar.", None),
 ],

 "escasez": [
  ("", "Lo que se acaba se mira distinto.", None),
  ("Lo que se hace", "Anunciar que quedan pocos.", None),
  ("El giro", "La escasez funciona porque informa. Si no informa de nada, "
   "solo molesta.", None),
  ("Cuándo informa de verdad", "Cuando la restricción existe antes de contarla.",
   "Un aforo que se llena, un plazo que depende de otra cosa, una pieza que no "
   "se vuelve a fabricar. Eso es información. Un contador que se reinicia cada "
   "noche es decorado."),
  ("El coste de fingirla", "Se descubre una vez y contamina todo lo demás.",
   None),
  ("", "No inventes urgencia. Explica la que ya hay.", None),
 ],

 "jerga": [
  ("", "La jerga no es precisión. Es un peaje.", None),
  ("Lo que se hace", "Usar el término exacto del oficio.", None),
  ("El giro", "El término exacto solo es exacto para quien ya lo conoce. Para "
   "el resto es una puerta cerrada.", None),
  ("Para qué sirve de verdad", "Para dos cosas, y solo una es buena.",
   None, [("Entre iguales", "ahorra tiempo, y mucho"),
          ("Con quien no la tiene", "marca quién está dentro")]),
  ("La prueba", "Dilo sin el término.",
   "Si puedes, el término era un atajo. Si no puedes, tampoco lo entendías tú."),
  ("", "Habla el idioma del otro, no el tuyo.", None),
 ],

 "la-brevedad": [
  ("", "Ser breve no es decir menos.", None),
  ("Lo que se hace", "Cortar palabras.", None),
  ("El giro", "La brevedad no se consigue quitando palabras. Se consigue "
   "quitando ideas.", None),
  ("Qué se quita", "Todo lo que no cambia la conclusión.",
   "El contexto que ya tiene, la salvedad que no aplica, la anécdota que "
   "confirma lo mismo. Cada una parece pequeña. Juntas son la mitad."),
  ("Lo que queda", "Una sola cosa, dicha entera.",
   "Es más difícil que decir cinco a medias, y por eso se nota."),
  ("", "No hables menos. Habla de menos cosas.", None),
 ],

 "la-memoria": [
  ("", "No recuerdan lo que dijiste. Recuerdan lo que hicieron con ello.", None),
  ("Lo que se hace", "Repetir el mensaje para que se fije.", None),
  ("El giro", "Lo que se fija no es lo que se oye. Es lo que se usa.", None),
  ("Qué hace que algo se quede", "Tres cosas, y ninguna es la repetición.",
   None, [("Un lugar", "algo concreto donde ponerlo"),
          ("Un uso", "un momento en que hará falta"),
          ("Una forma", "una frase que se pueda repetir sin ti")]),
  ("Por qué la repetición sola falla", "Aumenta la familiaridad, no la memoria.",
   "Suena conocido y no se puede reconstruir. Es la peor combinación posible."),
  ("", "No lo repitas. Dale un sitio y un momento.", None),
 ],

 "la-prueba": [
  ("", "Una afirmación sin prueba es una opinión con tono seguro.", None),
  ("Lo que se hace", "Afirmar con más convicción.", None),
  ("El giro", "La convicción no es evidencia. Y quien escucha lo nota antes de "
   "poder explicarlo.", None),
  ("Qué cuenta como prueba", "Cuatro niveles, de menos a más.",
   None, [("Me pasó a mí", "el más vívido y el más débil"),
          ("Nos pasó a varios", "empieza a valer"),
          ("Se midió", "vale, si se dice cómo"),
          ("Se repitió", "el único que aguanta solo")]),
  ("La honestidad barata", "Decir en qué nivel estás.",
   "Cuesta una frase y compra toda la credibilidad de lo que venga después."),
  ("", "No afirmes más fuerte. Di de dónde lo sacas.", None),
 ],

 "primera-impresion": [
  ("", "La primera impresión no se corrige. Se arrastra.", None),
  ("Lo que se hace", "Compensarla después con hechos.", None),
  ("El giro", "Los hechos posteriores no la borran: se leen a través de ella.",
   None),
  ("Qué se decide en los primeros segundos", "Dos preguntas, ninguna sobre "
   "lo que dices.",
   None, [("¿Vienes a favor o en contra?", "se responde con el tono"),
          ("¿Sabes de esto?", "se responde con la precisión, no con el cargo")]),
  ("Lo que sí la mueve", "Una rectificación temprana.",
   "Corregirte pronto vale más que acertar tarde, porque cambia la pregunta "
   "de «¿tiene razón?» a «¿es honesto?»."),
  ("", "No la compenses. Empieza otra vez.", None),
 ],

 "primeras-palabras": [
  ("", "La primera frase no informa. Decide si hay una segunda.", None),
  ("Lo que se hace", "Empezar presentándose.", None),
  ("El giro", "Quien escucha no necesita saber quién eres. Necesita saber por "
   "qué le interesa.", None),
  ("Tres aperturas que funcionan", "Y una que casi nunca.",
   None, [("El hueco", "algo que creía saber y no"),
          ("La consecuencia", "qué le pasa si no lo sabe"),
          ("La escena", "un lugar concreto, no una idea"),
          ("El contexto", "la que casi nunca: llega demasiado pronto")]),
  ("Por qué el contexto va después", "Solo se sostiene sobre algo que ya "
   "importa.", None),
  ("", "No abras explicando. Abre dando una razón para seguir.", None),
 ],

 "reciprocidad": [
  ("", "Dar primero cambia la conversación.", None),
  ("Lo que se hace", "Dar algo esperando lo mismo de vuelta.", None),
  ("El giro", "Si esperas la devolución, no diste: prestaste. Y se nota.", None),
  ("Qué separa un regalo de una deuda", "Tres cosas.",
   None, [("Sin condición", "no viene con lo que quieres después"),
          ("A tiempo", "cuando le sirve, no cuando te conviene"),
          ("Sin recordarlo", "en cuanto se menciona, era una factura")]),
  ("El coste de fingirlo", "La deuda disfrazada de regalo ofende dos veces.",
   "Por lo que se pide y por haberlo llamado otra cosa."),
  ("", "Da algo que no puedas cobrar.", None),
 ],

 "repeticion": [
  ("", "Repetir no convence. Familiariza.", None),
  ("Lo que se hace", "Decirlo muchas veces para que cale.", None),
  ("El giro", "Lo que aumenta con la repetición es la sensación de conocido, "
   "no la de cierto.", None),
  ("Por qué eso es peligroso", "Se confunden con facilidad.",
   "Algo que suena conocido se procesa más rápido, y esa fluidez se siente "
   "como verdad. La misma frase repetida gana credibilidad sin ganar una sola "
   "prueba."),
  ("Cuándo sí sirve", "Cuando lo repetido es la estructura, no la afirmación.",
   "Repetir el orden en que se cuentan las cosas ayuda a seguirlas. Repetir la "
   "conclusión solo la vuelve familiar."),
  ("", "Repite cómo lo cuentas. No repitas la conclusión.", None),
 ],
}


def laminas(tema):
    """Convierte el guion en las láminas que consume el montador."""
    from reel2 import ESCALA
    fuera = []
    for i, g in enumerate(GUIONES[tema], 1):
        kicker, titular, cuerpo = g[0], g[1], g[2]
        lista = g[3] if len(g) > 3 else None
        # la lámina 4 es la densa: es la que se guarda, así que va más pequeña
        tam = ESCALA[2] if (lista or (cuerpo and len(cuerpo) > 110)) else ESCALA[4]
        fuera.append({"fondo": "f%d.png" % i, "kicker": kicker,
                      "titular": titular, "cuerpo": cuerpo,
                      "lista": lista, "tam": tam})
    return fuera
