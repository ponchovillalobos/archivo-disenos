# Plan nocturno — 15 reels sobre comunicación

Fecha: 11-ago-2026, noche. Autor: tu asistente. Objetivo: que por la mañana esté todo
hecho, catalogado y verificado, sin que hayas tenido que aprobar nada.

---

## LO ÚNICO QUE NECESITO DE TI ANTES DE DORMIR

**Que mis herramientas no pidan permiso.** Si cada comando espera tu aprobación, el proceso
se para en el primero y por la mañana no habrá nada. Ponlo en modo que no pregunte
(en Claude Code: Shift+Tab hasta *bypass permissions*, o `/permissions`).

Es lo único. Todo lo demás lo resuelvo yo.

**No apagues el Mac ni cierres ComfyUI.** Yo me encargo de que no se duerma.

---

## Higiene antes de arrancar (lo hago yo)

Tu Mac está al **96% del swap** (16.725 MB de 17.408). Con 90 imágenes por delante, eso
revienta a mitad de noche. Antes de empezar:

1. Reiniciar ComfyUI para liberar los 6,6 GB del modelo y la memoria acumulada
2. Cerrar los Chromium huérfanos de las composiciones
3. `caffeinate` para que el Mac no se duerma (ahora mismo tiene `sleep 1`, es decir,
   se dormiría al minuto en cuanto nada lo impida)
4. Comprobar swap otra vez antes de lanzar el lote

---

## Los 15 temas

Cada uno con un **gancho verificable**, no una frase motivacional. Es lo que separa esta
serie de las mil cuentas que repiten lo mismo.

| # | Tema | Gancho (dato a verificar) |
|---|---|---|
| 1 | La estadística falsa | El 7-38-55 de Mehrabian está mal citado; él lleva décadas pidiendo que paren |
| 2 | Escuchar | Los médicos interrumpen al paciente a los **11 segundos** (Singh Ospina, 2019) |
| 3 | Preguntas | Las preguntas de seguimiento te hacen caer mejor (Huang, 2017, *JPSP*) |
| 4 | El silencio | Cuatro segundos de pausa bastan para que una conversación se sienta rota |
| 5 | Negociar | Quien pone la primera cifra ancla el resultado (Galinsky y Mussweiler, 2001) |
| 6 | Diferenciarse | La maldición del conocimiento: predijeron 50% de acierto, fue 2,5% (Newton, 1990) |
| 7 | Historias | Entrar en un relato reduce el contraargumentar (Green y Brock, 2000) |
| 8 | No verbal | Las «poses de poder» **no replicaron** (Ranehill, 2015) |
| 9 | Emociones | Lo que activa se comparte; lo que apaga se olvida (Berger y Milkman, 2012) |
| 10 | Persuasión | La prueba social del 75% **falló al replicarse** en Alemania (Bohner, 2014) |
| 11 | Vender | La proporción hablar/escuchar en llamadas que cierran *(dato de industria, se marcará)* |
| 12 | El gancho | La curiosidad nace de un hueco específico, no de un misterio vago (Loewenstein, 1994) |
| 13 | Argumentar | Refutar antes de que te ataquen te blinda (teoría de la inoculación, McGuire, 1961) |
| 14 | Objeciones | Admitir una debilidad **sube** la credibilidad (mensajes bilaterales, metaanálisis) |
| 15 | Decir que no | «No lo hago» funciona; «no puedo» no (Patrick y Hagtvedt, 2012) |

**Antes de escribir un solo guion**, lanzo agentes a verificar cada cita en la fuente. Si
alguna no aguanta, se cambia el tema. No publico un dato que no haya comprobado.

---

## La restricción honesta sobre las caras

Me pides humanos en las fotos y ninguna imagen con caras o dedos deformes. **Las dos cosas a la
vez tienen un límite técnico real** que conviene que sepas antes de dormir:

- SDXL falla con las **manos** de forma estructural. No es cuestión de suerte ni de prompt.
- Falla con las **caras en primer plano** con bastante frecuencia. A distancia media o lejana,
  acierta casi siempre.

**Mi estrategia**, la misma que ya nos funcionó en las tres series anteriores:

| Sí | No |
|---|---|
| Figuras humanas a media y larga distancia | Primeros planos de cara |
| De espaldas, de perfil, a contraluz | Manos en primer plano |
| Siluetas contra ventanas, focos, niebla | Grupos con muchas caras pequeñas |
| Manos ocultas, en sombra o fuera de encuadre | Dedos manipulando objetos |

Va a haber humanos en casi todas, con presencia y fuerza. Lo que no habrá son retratos
frontales nítidos, porque ahí la tasa de fallo es alta y prefiero un encuadre potente y
limpio a un retrato con un ojo mal puesto.

**Auditoría:** miro cada imagen a tamaño completo, y recorto y amplío al 300% cualquier cara o
mano visible. Lo que no pase, se regenera. Ese fue el proceso que rechazó el águila literal,
las caras emborronadas de los niños y la torre asiática.

---

## Estética

Misma familia que las tres series anteriores —noir con **color selectivo**— para que todo el
archivo se reconozca como una sola voz. Pero cada tema con su acento, y paisajes y elementos
místicos donde el tema lo pida: nieblas, focos de teatro, salas vacías, tormentas, ventanas,
umbrales, mesas de negociación, escenarios.

---

## Cronograma estimado

Basado en **54 generaciones cronometradas** en esta máquina (mediana 52 s por imagen).

| Fase | Contenido | Tiempo |
|---|---|---|
| 0 | Higiene de memoria + verificación de citas (agentes en paralelo) | 20 min |
| 1 | 15 guiones con estructura de densidad y giro en la lámina 3 | 40 min |
| 2 | **90 fondos** 720×1280 en lotes de 6 | **~80 min** de GPU |
| 3 | Auditoría de las 90 + regeneración de rechazos (~25% esperado) | ~30 min |
| 4 | Composición de 90 láminas con Chromium | ~4 min |
| 5 | Montaje de 15 vídeos con ffmpeg | ~11 min |
| 6 | 15 PDF + ZIP + catálogo + sitio + envío a GitHub | ~15 min |
| 7 | Informe final de verificación | 5 min |
| | **Total** | **≈ 3 a 3,5 horas** |

---

## Qué vas a encontrarte por la mañana

- **15 vídeos** MP4 1080×1920, con deriva de cámara constante y fundidos suaves
- **15 PDF** y **15 ZIP** descargables
- **90 láminas** compuestas, todas auditadas
- Todo en **Fuente Primaria**, agrupado por secciones, buscable y filtrable
- Un **informe** con: qué se generó, qué se rechazó y por qué, qué citas se verificaron y
  cuáles no aguantaron

## Qué NO voy a hacer sin tu permiso

- Publicar nada en redes
- Hacer público el repositorio (sigue como está)
- Instalar nada que requiera tu contraseña
- Borrar nada de lo que ya existe

## Si algo se rompe

No te despierto. Sigo con lo que sí se pueda y **lo dejo escrito en el informe**: qué falló,
en qué punto, y qué opciones hay. Prefiero 12 reels buenos y un informe honesto que 15
mediocres.
