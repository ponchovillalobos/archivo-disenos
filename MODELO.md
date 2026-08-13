# El modelo de imagen, y todo lo que costó descubrir

Si te descargas este repositorio, esto es lo que más te va a ahorrar. Cada cosa
que hay aquí salió de un fallo pagado con horas de GPU, no de leer
documentación.

---

## La pila

| Pieza | Fichero | Peso | Dónde va |
|---|---|---|---|
| **Checkpoint** | `juggernautXL_v9.safetensors` | 6,62 GB | `comfy/models/checkpoints/` |
| **LoRA** | `sdxl_lightning_8step_lora.safetensors` | 0,37 GB | `comfy/models/loras/` |
| **VAE** | `sdxl_vae_fp16fix.safetensors` | 0,31 GB | `comfy/models/vae/` |

**No están en el repositorio**: suman 7,3 GB y `.gitignore` los excluye. Son
descargas públicas — el checkpoint de Civitai, el LoRA de ByteDance en Hugging
Face, el VAE de madebyollin.

```
pasos          8
cfg            1.0
muestreador    euler
planificador   sgm_uniform
semilla        101010
denoise        1.0
```

Todo vive en `voz/fuente-primaria.yaml`, no disperso por el código.

---

## Por qué cada pieza

**Juggernaut XL v9** — SDXL fotorrealista con el ecosistema de LoRAs más grande.
En 16 GB de memoria unificada cabe cómodo; Flux dev no es práctico (se reportan
minutos u horas por imagen) y Flux schnell en GGUF Q4 corre pero lento.

**SDXL-Lightning de 8 pasos** — baja de los 25-30 pasos normales a **8**. Es lo
que hace viable generar 180 imágenes en una tarde: **57 segundos por imagen** en
lugar de tres o cuatro minutos.

**VAE fp16fix** — el VAE original de SDXL produce artefactos en precisión media,
que es la que usa Metal. Este está parcheado para eso.

---

## La consecuencia grande: CFG 1.0

El LoRA Lightning **obliga a CFG 1.0**. Y a ese valor el modelo **casi no
obedece una instrucción de color en positivo**: hace lo que le dicta la escena.

Medido sobre ocho paletas con el mismo encuadre:

| paleta | pedida en positivo | lo que salió |
|---|---|---|
| mostaza | amarillo ~50° | **156° — verde** |
| purpura | violeta ~285° | **204° — azul** |
| magenta-cian | magenta | **184° — solo cian** |

**Cinco de ocho cayeron en la franja azul-cian de 156-204°.**

### La solución: el veto

No se convence al modelo de poner amarillo. Se le **quita el azul**.

Cada paleta lleva tres campos, no uno: el acento tipográfico, la instrucción en
positivo **con pesos**, y el **veto** — los colores rivales que van al negativo
con peso 1.3.

Resultado sobre las mismas escenas:

| paleta | solo positivo | con peso + veto |
|---|---|---|
| mostaza | 156° verde, sat 10,7 | **36° ámbar, sat 42,5** |
| purpura | 204° azul | **321° violeta, sat 35,3** |
| magenta-cian | 184° cian, sat 15,4 | **292° magenta, sat 26,8** |

Está en `herramientas/paletas.py`. **Es el hallazgo más rentable del proyecto.**

Dos detalles que ahorran tiempo:

- **Las escenas con ventanas arrastran todo a azul** (luz de día). Para probar
  color, usa corredores o arcos, no salas con ventanales.
- **Los pasteles no se consiguen.** `lavanda` está fuera de la rotación: un
  violeta pastel no lo acierta ni el prompt (dio 14°, naranja) ni el grado
  posterior (330°, rosa). Mejor 15 paletas que funcionan que 16 con una rota.

---

## La semilla no es lo que crees

**366 de 371 imágenes generadas usan `101010`.** Nunca se cambió.

Lo que produce la variación no es la semilla: es la **arquitectura del prompt**,
seis campos separados que se concatenan.

| Nodo | Campo | Ejemplo |
|---|---|---|
| 11 | escena | `epic cinematic film still of an empty rollercoaster track…` |
| 12 | ropa | `dark simple clothing` |
| 13 | objeto | `two doors, one open` |
| 14 | encuadre | `wide cinematic shot, no faces, no hands, vast space` |
| 15 | aire | `luminous air with soft moving highlights` |
| 16 | luz | `bright indirect light with a gentle shimmer` |
| 17 | tratamiento | la paleta, con pesos |
| 5 | negativo | las reglas duras + el veto de color |

Separarlos importa: permite cambiar **una sola pieza** y que la variante herede
lo que ya funcionaba. Eso es lo que hace `recetario.reproducir()`.

### El recetario

**ComfyUI escribe el flujo entero dentro de cada PNG** (clave `prompt` en los
metadatos). No hace falta guardar nada por adelantado: se recupera de las
imágenes ya generadas.

En este repositorio hay **371 recetas recuperadas, 126 marcadas como
aprobadas** — aprobada significa que la imagen llegó a publicarse, que es el
filtro más honesto que existe.

---

## El negativo, y por qué lleva pesos

```
(face:1.6), (faces:1.6), (portrait:1.5), (close-up face:1.6),
(facial features:1.5), (eyes:1.4), (hands:1.6), (fingers:1.6),
(visible hands:1.5), (arms in foreground:1.3), blurry, low quality,
deformed, extra limbs, disfigured, watermark, text, letters, signature,
logo, cartoon, plastic skin, flat lighting, modern clothing, smartphone,
(horror:1.4), (creepy:1.4), (sinister:1.3), (ominous:1.3), (bleak:1.2),
(desolate:1.2), (decay:1.2), (grimdark:1.3), (nightmare:1.3),
(haunted:1.3), (oppressive:1.2), (murky:1.2), muddy colors, washed out
```

**Caras y manos** — SDXL falla ahí de forma estructural. No es cuestión de
suerte con la semilla: hay que resolverlo por composición. Los humanos van como
siluetas lejanas, de espaldas, a contraluz o en niebla.

Matiz aprendido después: **un cuerpo sin cara no es motivo de rechazo.** Unas
piernas corriendo o una espalda valen si la imagen se ve bien. Lo que no entra
son caras —ni de frente ni de perfil— y manos.

**El bloque de terror** se añadió tarde y hacía falta. Con «sombra dura» y
«niebla» en el prompt base, todo salía de película de miedo aunque se pidiera
épico. El veto de ánimo importa tanto como el de color.

---

## Trampas de interpretación literal

SDXL toma las metáforas al pie de la letra. Tres que nos costaron regeneraciones:

| Se pidió | Salió |
|---|---|
| `leaf-shaped spearhead` | una **hoja gigante** |
| `clear air over water` como cualidad de luz | **cuatro interiores inundados** |
| `empty starting blocks on a running track` | una persona **corriendo en primer plano** |

**Regla:** describe la cualidad, nunca un objeto que pueda aparecer. El ánimo
`reflejo` decía «aire claro sobre el agua» y ahora dice «aire luminoso con
reflejos suaves».

---

## Tamaños que SDXL entiende

Los buckets de entrenamiento son **múltiplos de 64**.

| Destino | Latente | Publicación |
|---|---|---|
| Reel / TikTok / Shorts | **720×1280** | 1080×1920 |
| Carrusel Instagram | 864×1080 | 1080×1350 |
| Apaisado / YouTube | **1344×768** | 1920×1080 |

**Cuidado con el apaisado.** 1280×720 es 16:9 exacto pero **720 no es múltiplo
de 64**. La ruta correcta es 1344×768 y recortar. Lo afirmé mal una vez y salió
en la documentación antes de comprobarlo.

---

## Rendimiento medido en un M4 de 16 GB

| | |
|---|---|
| Una imagen 720×1280, 8 pasos | **57 s** (mediana de 54 muestras) |
| Con `--use-pytorch-cross-attention` | **27 % más rápido** (medido) |
| Seis imágenes de un tema | 5,4 min |
| Un reel completo, de guion a MP4 | ≈ 8 min |

**El cuello de botella nunca fue la GPU**: es escribir el guion y auditar las
imágenes.

### La degradación por memoria — el fallo más caro

Con 16 GB, el swap crece hasta que la generación se hunde:

```
sano ................  57 s por imagen
degradado ..........  541 s  (9×)
peor caso medido ... 1.066 s (18×)
```

A ese ritmo, 180 imágenes pasaban de 3 horas a **33**.

**Pasó tres veces y las tres lo descubrió el usuario, no el sistema.** El fallo
de diseño no era el swap: era que nadie medía. Por eso existe
`herramientas/guardian.py`, que vigila **el ritmo contra su propia mediana** —no
un umbral de swap inventado— y reinicia ComfyUI solo. Reiniciar libera entre 4 y
7 GB de golpe.

Con 32 GB de RAM probablemente no haga falta nunca.

---

## Lo que NO hay que hacer

- **No toques `sysctl iogpu.wired_limit_mb`** (el truco de «dar más RAM a la
  GPU»). En 16 GB sube el riesgo de congelar el sistema y el beneficio es
  marginal.
- **No uses precisión fp8.** Está rota o es lentísima en Metal. Se trabaja en
  fp16.
- **No confíes en `comfy model download` para ficheros grandes: no reanuda.** Una
  descarga de 7 GB se cortó al 88 % y hubo que empezar de cero. Usa
  `curl -L -C - --retry 8 --retry-all-errors`.
- **No edites módulos de un proceso que está corriendo.** Python los carga al
  arrancar. Una hora de ediciones no llegó nunca al productor vivo, que publicó
  17 vídeos que nadie podía ver.

---

## Qué funciona, medido sobre 599 recetas

El recetario no solo guarda qué se hizo: cruza cada receta contra las que
llegaron a publicarse y saca la tasa de aprobación.

```
python -c "import sys;sys.path.insert(0,'herramientas');from recetario import informe;informe()"
```

Sobre 599 recetas y 438 aprobadas:

| Paleta | Imágenes | Aprobadas |
|---|---|---|
| `noir` | 265 | **48 %** |
| `rojo-carbon` | 60 | 60 % |
| las 12 restantes | 6-46 cada una | **100 %** |

| Ánimo | Imágenes | Aprobadas |
|---|---|---|
| `niebla` | 346 | **61 %** |
| los 9 restantes | 12-28 cada uno | **100 %** |

**Léelo con este sesgo delante:** las paletas antiguas se usaron en una época en
que se generaba de más y se descartaba mucho; las nuevas se generan por pedido y
se usan casi todas. Parte de la diferencia es el método, no la paleta.

Lo que el dato **sí** sostiene: el `noir` con `niebla` producía descartes que las
paletas con veto no producen. Si empiezas de cero, empieza por una paleta con
veto y un ánimo luminoso.

---

## El sistema se limpia solo

Tres cosas crecen sin freno: los PNG de ComfyUI (llegaron a 664 MB), la caché de
capas de texto y los registros.

```
python herramientas/mantenimiento.py             # solo informa
python herramientas/mantenimiento.py --limpiar   # ejecuta
```

**La regla que lo hace seguro: nunca borra un archivo cuyo contenido esté
publicado.** No compara por nombre —que puede coincidir por accidente— sino por
md5 contra todo lo que vive en `out/`. Lo que sí borra son **versiones
superadas**: ComfyUI numera `_00001_`, `_00002_`… y el sistema siempre usa la
más reciente.

Lleva freno: si el barrido quiere borrar más de 300 imágenes, se para y avisa.
Eso no es limpieza, es un fallo.

Y **`prueba_sistema.py` avisa antes** de que estorbe: falla si quedan menos de
15 GB libres o si hay más de 250 versiones sin barrer. La limpieza es una
decisión, no un accidente.

---

## Cómo empezar sin romper nada

```bash
python herramientas/prueba_sistema.py
```

18 comprobaciones en unos segundos. Entre ellas: que ComfyUI esté vivo **y no
degradado**, que el negativo conserve los vetos de cara, de color y de terror,
que las paletas declaren solo ejes tipográficos que las fuentes tengan de
verdad, y que ningún archivo entregable exista sin aparecer en el portal.

Cada una nació de un fallo real.
