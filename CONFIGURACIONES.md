# Configuraciones verificadas

Lo que hay que poner y por qué, sacado de fuentes primarias — fichas oficiales de
modelo, código de ComfyUI, papers — y contrastado contra esta máquina.

**Cómo se lee cada afirmación:**

- **OFICIAL** — lo dice el autor del modelo en su ficha.
- **CÓDIGO** — verificado leyendo el código de ComfyUI o de PyTorch.
- **MEDIDO** — hay un número obtenido aquí o en una fuente con metodología.
- **COMUNIDAD** — consenso sin medición. Se marca para no confundirlo.

**La regla que manda sobre todas:** investigar dice qué probar; **medir dice qué
es verdad aquí**. Tres de las mejores recomendaciones de esta investigación
resultaron falsas al medirlas en esta máquina, y están anotadas abajo.

---

## 1. El filtro que va primero: la licencia

Producimos contenido **comercial**. Esto descarta más cosas de las que parece, y
casi siempre las más populares.

**Cómo se comprueba, sin adivinar:**

```bash
curl -s "https://civitai.com/api/v1/models/<id>" | python3 -c \
  "import json,sys; print(json.load(sys.stdin)['allowCommercialUse'])"
```

| valor | qué permite |
|---|---|
| `Image` | **vender o publicar las imágenes generadas** ← el único que importa |
| `Rent` | servir el modelo en servicios de terceros |
| `RentCivit` | **solo dentro del generador de Civitai** — no sirve |
| `Sell` | vender el modelo |
| `[]` | nada |

### Trampas ya detectadas

**Dos ficheros, nombres casi iguales, licencias opuestas:**

    stable_zero123.ckpt    objetos CC-BY-NC  ->  NO COMERCIAL
    stable_zero123_c.ckpt  solo CC-BY y CC0  ->  comercial hasta 1 M USD/año

**El LoRA de libro infantil más descargado de SDXL** (8.460 descargas) es
`RentCivit`: no se puede publicar con él.

**Todo el catálogo de EauDeNoire** —más de 30 LoRAs cinematográficos, la mitad
de la primera página al buscar «cinematic SDXL»— es `RentCivit`.

**Escaladores:** `4x-UltraSharp`, `4x-UltraSharpV2` y `4x-AnimeSharp` son
CC-BY-NC. Los limpios son **Siax y Superscale (WTFPL)**, **RealESRGAN_x4plus
(BSD-3)**, **Nomos8kSC (CC-BY-4.0)**.

**Zero123++** tiene el código Apache 2.0 pero **los pesos son CC-BY-NC**. Y
arrastra a InstantMesh, cuya etapa multivista es un UNet derivado de él.

Un permiso marcado tampoco cubre el material de origen: hay LoRAs con permiso
comercial entrenados sobre obra de ilustradores vivos identificados por nombre.

---

## 2. El modelo que usamos

**OFICIAL** — ficha de Juggernaut XL v9 (RunDiffusion), en Hugging Face y Civitai:

```
resolución  832×1216 · 1216×832 · 768×1344     (las tres son cubos de SDXL)
pasos       30-40
CFG         3-7  ("menos = más realista")      HF
            3-6                                Civitai
muestreador DPM++ 2M Karras                    HF
            DPM++ 2M SDE                       Civitai
negativo    "empieza SIN ninguno y añade solo lo que no quieras ver"
VAE         ya viene dentro del checkpoint
hires       4xNMKD-Siax_200k · 15 pasos · denoise 0.3 · 1.5×
```

**Las dos fuentes oficiales se contradicen** en muestreador y CFG. No hay una
respuesta correcta: hay que medir cuál va mejor con nuestras escenas.

**CÓDIGO** — nunca usar las variantes `_gpu` del muestreador (`dpmpp_2m_sde_gpu`):
generan el ruido en el acelerador, así que la misma semilla da otra imagen entre
Mac y PC. El archivo de semillas dejaría de valer al migrar.

**Nuestro VAE externo sobra:** `sdxl_vae_fp16fix` es **bit a bit idéntico** al
que trae el checkpoint (248 tensores comparados, diferencia máxima 0,0).

---

## 3. Cómo se escribe un prompt aquí

### 3.1 El presupuesto de 75 tokens, y el motivo real

**CÓDIGO.** ComfyUI **no trunca**: trocea en bloques de 77 y los concatena. Pero:

- **El vector *pooled* sale solo del primer bloque.** En SDXL ese vector es una
  entrada de condicionamiento propia, **la que más empuja identidad y estilo**.
  Todo lo que va después del token 75 **no lo toca jamás**.
- **No hay atención entre bloques.** Un concepto partido pierde su contexto.
- **El relleno no es inerte**: SDXL se crea sin máscaras de atención.

**Regla:** lo que no te puedes permitir perder, en los primeros 75 tokens.

### 3.2 El orden importa, con dos pruebas

**CÓDIGO** — el codificador de CLIP lleva máscara causal: cada token solo ve los
anteriores, así que lo primero se acumula en todo lo demás.

**MEDIDO** — *A Cat Is A Cat (Not A Dog!)*, NeurIPS 2024: 400 prompts, sesgo
sistemático hacia el objeto mencionado primero.

Orden recomendado:

```
sujeto y rasgos → acción → entorno → encuadre → luz → color → medio/estilo
```

### 3.3 Los pesos van inflados

**CÓDIGO + FAQ oficial.** ComfyUI **no normaliza** los pesos; A1111 y Civitai sí.
Los números copiados de ese mundo pegan más fuerte aquí.

Y el peso **no hace que el modelo mire más esa palabra**: se aplica *después* del
transformador, extrapolando el vector de salida lejos del prompt vacío. No cambia
la atención — y **arrastra todo el contexto ligado a ese token**, que es por qué
`(emerald jungle:1.3)` no reforzó un color: convirtió la paleta en la escena.

```
trabajo  0,8 – 1,3        techo  1,4        nunca  > 1,5
```

### 3.4 `BREAK` no existe en ComfyUI

**CÓDIGO.** La palabra se tokeniza y el modelo dibuja «romper». El equivalente
nativo es dos `CLIPTextEncode` unidos con `ConditioningConcat`.

### 3.5 Plantillas oficiales de Stability

Las que trae Fooocus de fábrica (`sdxl_styles_sai.json`). `{prompt}` es el sujeto:

```
cinematic
P: cinematic film still {prompt} . shallow depth of field, vignette, highly detailed,
   high budget, bokeh, cinemascope, moody, epic, gorgeous, film grain, grainy
N: anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch,
   deformed, mutated, ugly, disfigured

analog film
P: analog film photo {prompt} . faded film, desaturated, 35mm photo, grainy, vignette,
   vintage, Kodachrome, Lomography, stained, highly detailed, found footage
N: painting, drawing, illustration, glitch, deformed, mutated, cross-eyed, ugly, disfigured

watercolor
P: watercolor painting {prompt} . vibrant, beautiful, painterly, detailed, textural, artistic
N: anime, photorealistic, 35mm film, deformed, glitch, low contrast, noisy

line art
P: line art drawing {prompt} . professional, sleek, modern, minimalist, graphic,
   line art, vector graphics
N: anime, photorealistic, 35mm film, deformed, glitch, blurry, noisy, realism, realistic,
   impressionism, expressionism, oil, acrylic

comic book
P: comic {prompt} . graphic illustration, comic art, graphic novel art, vibrant, highly detailed
N: photograph, deformed, glitch, noisy, realistic, stock photo

flat papercut
P: flat papercut style {prompt} . silhouette, clean cuts, paper, sharp edges, minimalist, color block
N: 3D, high detail, noise, grainy, blurry, painting, drawing, photo, disfigured
```

**El patrón que hay que copiar:** cada estilo pictórico **veta explícitamente la
fotografía y el 3D**, y cada estilo fotográfico veta el dibujo. El registro se
define por lo que prohíbes, no solo por lo que pides.

### 3.6 `epic` es una trampa, y está en la plantilla oficial

`epic` es **la única palabra sustantiva que comparten** el preset de cine y el de
arte fantástico — donde vive rodeada de `celestial, majestic, magical, cover art,
dreamy`. En el corpus de entrenamiento habita en portadas de fantasía, no en
fichas de rodaje.

**Pedir «épico» no da escala: da el vecindario semántico de la portada de
fantasía**, con sus montañas, su tormenta y sus ruinas de regalo.

La escala es una **relación**, no un adjetivo:

| en vez de | pide |
|---|---|
| `epic` | una figura pequeña reconocible junto al objeto grande |
| `epic landscape` | `extreme long shot`, `figure dwarfed by`, `low horizon line` |
| `dramatic sky` | `atmospheric perspective, layered haze, distant ridgelines fading` |
| `majestic, grand` | el lugar **concreto y nombrado** |

Y al negativo: `epic, fantasy art, concept art, cover art, matte painting,
mountains, storm clouds, ruins, castle, flowing cloak, god rays, lens flare`.

### 3.7 El encuadre: por qué «extreme wide shot» nunca funcionó

**Esto explica el fallo que más veces hemos repetido.** Lo pedimos en el cuento
del elefante y en la prueba de la caja, y las dos veces salió un plano medio.

**La causa está en el paper de Playground v2.5**, sobre el condicionamiento de
SDXL, literal:

> *«La estrategia de condicionamiento de SDXL **obligó al modelo a aprender a
> colocar el sujeto en el centro** bajo distintas proporciones.»*

No estábamos peleando con un prompt mal escrito. Peleábamos contra un sesgo
grabado en el entrenamiento.

**Y hay una rejilla publicada** —SDXL 1.0, 1216×832, CFG 8.5, 25 pasos— que
prueba término por término qué obedece. El resultado, revisado imagen a imagen:

| | |
|---|---|
| **no hacen nada** | `long shot`, `medium full shot`, `full shot`, `upper body shot` — dan lo mismo que `medium shot` |
| **sí funciona** | **`establishing shot`**, `extreme close-up`, `close-up`, `full body shot` |
| **el ÁNGULO sí manda** | `from above`, `from below`, `bird's eye view`, `overhead shot`, `top down`, `fisheye view` rompen el encuadre con claridad |

**`extreme wide shot` no aparece en ninguna lista. No es vocabulario del
modelo.** El término que funciona para plano general es **`establishing shot`**.

Cinco cosas que sí obedecen:

1. **`establishing shot`**, al principio **y repetido después del sujeto**.
2. **Lienzo apaisado.** El sesgo de proporción es real y está documentado.
3. **La taxonomía del propio checkpoint.** Juggernaut certifica `Still Mid Shot
   Photo` y `Full Body Photo` como tokens fiables. Usar la suya, no la de cine.
4. **El plano como núcleo gramatical**: `A mid-shot of a man standing…`, no
   `…, mid shot` al final.
5. **Ángulo antes que distancia.** Si hay que romper el plano medio, `from
   above` obedece mucho más que cualquier palabra de distancia.

### 3.8 Óptica: qué mueve la aguja y qué es folclore

| funciona | evidencia |
|---|---|
| **encuadre y ángulo** (`close-up`, `low angle`, `bird eye view`, `dutch angle`) | el único bloque con comparativa visual publicada. **Es geometría real** |
| **nombres de película** (`Kodachrome`, `Portra 400`, `CineStill 800T`) | están en el preset oficial de Stability |
| `film grain`, `bokeh`, `shallow depth of field`, `vignette` | ídem |

| es etiqueta, no efecto | evidencia |
|---|---|
| **`halation`** | el autor de un LoRA de cine, entrenando sobre fotoquímico: *«puede que no cree el efecto directamente, pero refuerza la estética porque estaba en los pies de foto del entrenamiento»* |
| **`anamorphic`** | hay **cuatro LoRAs dedicados** solo a esto. Nadie entrena 435 MB para replicar lo que el prompt ya da |
| **`chromatic aberration`** | en SDXL aparece como **artefacto no deseado**; hay hilo abierto en el repo de Stability |
| **distancias focales** (`85mm f/1.4`) | etiqueta de género, no geometría. No cambia la compresión de perspectiva |

**Regla:** el encuadre es geometría; la óptica y la película son etiquetas de
estilo. Pide geometría con precisión y estilo con moderación.

---

## 4. Las mejoras que cuestan cero segundos

Todas verificadas en el código de ComfyUI. Ninguna necesita instalar nada.

### 4.1 `CLIPTextEncodeSDXL` — **dos especialistas se contradicen aquí**

El nodo separa el prompt en dos campos, uno por cada codificador de texto de
SDXL, y eso **no está en discusión**:

```
text_g = escena, en lenguaje natural   (OpenCLIP-bigG · manda el vector pooled)
text_l = look, paleta y estilo         (CLIP-L · responde al estilo)
```

Hay una prueba con semilla fija que invirtió los dos campos y concluyó que
hacerlo al revés es «la forma equivocada de usarlos». **Esa parte, adoptada.**

**Lo que SÍ está en disputa: poner 4096 en `width`/`height`/`target`.**

| a favor | en contra |
|---|---|
| «con 4096 el modelo cree que viene de un original grande, y eso correlaciona con fotos nítidas» — el autor de IPAdapter | la documentación de diffusers dice que bajar `original_size` **degrada el detalle**, no aleja la cámara; y un experimento con rejillas concluye *«el impacto es mínimo»* y recomienda dejar el recorte en 0,0 |

**No está resuelto, y no lo vamos a resolver leyendo.** Es una rejilla de dos
imágenes con semilla fija: 4096 contra el valor por defecto. Hasta entonces, **no
figura como recomendación**.

Lo que sí queda claro de la discusión: **`original_size` no sirve para alejar la
cámara.** Eso se pide con `establishing shot` y con el ángulo (§3.7).

### 4.2 `ConditioningSetTimestepRange` — que el color llegue tarde

**Ésta resuelve estructuralmente el problema que más nos ha costado.** La
composición se decide en el 20-35 % inicial del muestreo; el color y la textura,
en el resto. Metiendo el color solo en la parte final, **no puede competir con la
escena aunque quiera**.

```
escena          ConditioningSetTimestepRange  start 0.00  end 0.35
paleta / look   ConditioningSetTimestepRange  start 0.30  end 1.00
veto de ánimo   ConditioningSetTimestepRange  start 0.00  end 0.40
                                    unidos con ConditioningCombine
```

Es la alternativa correcta a subir el peso de la paleta — que ya probamos y
empeoró.

### 4.3 `ConditioningConcat` para conceptos que se contaminan

Dos conceptos en un solo prompt se mezclan atributos («un cubo rojo y una pelota
azul» acierta ~1 de 25 veces). Codificados por separado y concatenados, ~1 de 3.

Es también el arreglo para la ficha de personaje: en su propio bloque de 75
tokens, no se parte nunca.

### 4.4 Agrupar el lote por prompt

**CÓDIGO** — la clave de caché de cada nodo incluye sus entradas y las de todos
sus ancestros. **Si entre dos trabajos solo cambia la semilla, los
`CLIPTextEncode` no se vuelven a ejecutar.**

Agrupar por prompt y variar la semilla dentro del grupo es gratis de programar y
ahorra tiempo real. Cambiar el prompt en cada imagen invalida la cadena entera.

### 4.5 Podar el negativo

El autor del modelo lo pide explícitamente. Los tokens negativos compiten entre
sí: un negativo de 60 palabras diluye las 5 que importan.

---

## 5. Ahorro de tiempo

### `AlignYourStepsScheduler` — la palanca grande

**CÓDIGO.** Nodo core, con la tabla de sigmas de NVIDIA horneada. Son **10 pasos
exactos**; con otro número interpola.

```
AlignYourStepsScheduler(model_type="SDXL", steps=10)  ->  SamplerCustom
```

Produce a 10-12 pasos algo comparable a `karras` a 25-30: **130 s → ~45 s**.

**Ojo con el matiz que ya medimos:** a 30 pasos, AYS **no aporta nada** — el
propio paper de NVIDIA dice que el efecto se desvanece al subir pasos. Su valor
es exclusivamente **bajar el número de pasos**.

### DMD2 en vez de Lightning — recupera el negativo

Nuestro flujo rápido usa Lightning a **CFG 1.0**, donde el prompt negativo
**literalmente no se evalúa** (verificado dos veces en el código). Eso deja
muerto el veto de color y el de ánimo en todo lo que producimos en serie.

**DMD2** funciona a **CFG 1.4-1.8**, donde la guía sin clasificador **sí está
activa**: 8 pasos, LoRA a 0.7, muestreador LCM, scheduler Normal.

Cambiar de LoRA recupera el negativo en el flujo de producción.

---

## 6. Escalado

**COMUNIDAD, medido por cubiq** (autor de IPAdapter):

```
escalar en LATENTE  ->  denoise mínimo 0,55   (el latente escalado es muy ruidoso)
escalar en PÍXEL    ->  denoise 0,25 a 0,5
con modelo ESRGAN   ->  denoise 0,25 basta
```

La cadena, con la receta oficial de Juggernaut:

```
VAEDecode
  → UpscaleModelLoader(4x_NMKD-Siax_200k)   ← WTFPL, comercial
  → ImageUpscaleWithModel                    (escala fija 4×, siempre)
  → ImageScale(bilinear, 1,5× del original)  (hay que bajar: la escala está horneada)
  → VAEEncode
  → KSampler(15 pasos, denoise 0,25-0,3)
  → VAEDecode
```

**Coste ≈ +150 s.** Pero hay una versión barata que da la mayor parte del
beneficio percibido: **solo el ESRGAN, sin segunda pasada, ≈ +4 s.** No inventa
detalle, pero sube la resolución de entrega. Probar ésa primero.

**Aviso práctico:** el grano y la textura de papel **se destruyen al reescalar y
al guardar en JPG**. Si el estilo es pintado a mano, escalar borra justo lo que
lo hacía parecer manual.

---

## 7. Que parezca pintado a mano y no un render

Tres palancas, en orden de eficacia:

**Nombra el soporte y la herramienta, no el resultado.** `watercolor on paper`,
`gouache`, `ink wash`, `linocut`, `charcoal`, `textured brushwork`. El preset
oficial dice *«watercolor painting … painterly, **textural**»*, no «beautiful
watercolor art».

**Veta el render en el negativo:**

```
3d render, octane render, cgi, unreal engine, artstation, digital painting,
airbrushed, plastic, glossy, photorealistic, 35mm film, smooth gradient, hdr
```

**Baja el acabado.** Contraintuitivo y demostrado en las fichas oficiales:
`highly detailed` es **enemigo** del aspecto manual. Los presets de medio físico
lo ponen **en el negativo**. La mano humana deja zonas sin resolver; el render
resuelve todo por igual. Y bajar el CFG a 3-5 quita el brillo de plástico.

---

## 8. Consistencia de personaje: el orden correcto

**MEDIDO por alguien que hizo libros ilustrados enteros**, en este orden:

| intento | resultado |
|---|---|
| prompt fijo con descripción detallada | *«mejora mínima»* — sus hijos le señalaban el pelo y la ropa cambiando de página |
| img2img con foto de referencia | lento y *«a veces sí, a veces no»* |
| **LoRA entrenado** | **el punto de inflexión.** 30-40 imágenes, ~1 hora |

Su conclusión: *«cuanto mejores son las imágenes de entrada, mejor sale el
modelo»*.

**Veredicto: LoRA de estilo o de personaje. No prompt fijo, no IPAdapter solo.**

IPAdapter sí tiene un uso preciso, y es el que descubrimos midiendo: en SDXL
**no escala pesos, aplica el adaptador a capas de atención concretas**.

```
style transfer .......... solo la capa 6      ← estilo: color, material, atmósfera
composition ............. solo la capa 3      ← layout espacial
strong style transfer ... todas menos la 3
```

Esto no es heurística: está identificado en la literatura — en SDXL el estilo y
el layout viven en bloques distintos de la U-Net. **Es el único método que separa
color de lugar por diseño y no por equilibrio de pesos.**

**MEDIDO aquí:** sobre cinco tomas de un objeto, la capa 3 en −0,5 subió el
parecido de 0,731 a 0,768. Real, pero insuficiente sola.

---

## 9. Lo descartado, con su prueba

| qué | por qué |
|---|---|
| **Refiner de SDXL** | entrenado sobre latentes de SDXL base; Juggernaut es un ajuste fuerte. Ni su ficha ni la plantilla oficial de ComfyUI lo usan |
| **FreeU** | el paper no reporta FID ni CLIP en el cuerpo, solo una encuesta de los propios autores sobre SD1.x. Y hay medición independiente de que **empeora**: FID 25,47 → 33,70 |
| **AYS a 30 pasos** | el paper de NVIDIA: el efecto se desvanece al subir pasos |
| **fp8** | no existe en M4; y en tarjetas serie 30 (Ampere) tampoco es nativo |
| **GGUF para SDXL** | su autor lo desaconseja: SDXL es convolucional y las conv2d se degradan |
| **`--lowvram`** | **no-op**: su propia ayuda dice que no hace nada con VRAM dinámica, que está activa por defecto |
| **FaceDetailer / Impact Pack** | nuestra regla dura es cero caras y manos. Toda esa rama no nos aplica |
| **`masterpiece`, `8k`, `award winning`** | en SDXL la estética y la resolución son **entradas numéricas propias** del condicionamiento, no tokens. Escribirlas es pedir por la puerta de servicio algo que tiene puerta principal. No están en ninguna lista certificada por autor, y gastan tokens de los 75 |
| **`octane render`, `unreal engine`** | empujan **activamente** hacia render 3D. Aparecen en prompts que piden fotografía: folclore heredado de SD 1.5 |
| **`rule of thirds`, `negative space`** | sin ninguna prueba controlada sobre SDXL, y con un mecanismo en contra: el modelo fue condicionado para **centrar el sujeto**. Describir el espacio (`vast empty sky above`) en vez de nombrar la regla |
| **Nombres de película fotográfica** | salvo `Kodachrome` y `Lomography`, que sí están en el preset oficial de Stability, no hay ninguna comparativa publicada. Decorativo |

---

## 9 bis. Varias tomas del mismo objeto: resuelto

**MEDIDO aquí**, cinco vistas del mismo objeto:

| método | parecido | veredicto |
|---|---|---|
| SDXL, cinco tomas por prompt | 0,731 | probablemente **otro** objeto |
| IPAdapter, capa 3 en −0,5 | 0,768 | el mismo, con variación |
| **Stable Zero123-C** | **0,884** | **el mismo, sin duda** |

El mínimo pasó de 0,638 a **0,800**: ni el peor par baja de «el mismo objeto».

**SDXL no puede rodear un objeto por prompt.** No es que lo haga mal: no tiene
representación tridimensional. Cinco tomas dieron cinco cajas distintas, con
herrajes diferentes en cada una, y la abolladura declarada en una esquina
concreta no apareció en ninguna.

Zero123 es otra cosa: **no genera desde texto** —no hay prompt en su flujo— sino
que toma una imagen y produce la vista de **ese** objeto desde el ángulo pedido.

La receta completa está en `herramientas/vistas.py`. Las dos cosas que hacen
falta, y las dos son obligatorias:

1. **`--gpu-only` al arrancar ComfyUI.** Sin ella, imágenes negras
   intermitentes: 2 de 5 limpias sin la bandera, **11 de 11 con ella**.
2. **La imagen de entrada al formato oficial**: fondo blanco puro, recorte al
   objeto, lado largo ≤200 px, centrado en 256×256.

**Su límite:** no sabe dibujar texto legible — lo dice su propia ficha. Para un
objeto con marca hay que componer el texto real encima.

### Probado con tres objetos más: cuándo sirve y cuándo no

**MEDIDO** sobre una tetera, una cámara analógica y una bota, cinco vistas cada
una. Elegidos para que pudieran fallar de forma visible.

```
           0°     45°    90°    180°   alto     parecido
tetera    0,836  0,750  0,518  0,752  0,587      0,726
cámara    0,735  0,611  0,289  0,353  0,559      0,538
bota      0,780  0,719  0,721  0,637  0,689      0,860
```

**La prueba dura la pasa.** El pico de la tetera está a la izquierda en la
original y aparece **a la derecha a 180°**: es una rotación real, no otra tetera
parecida.

Tres reglas que salen de aquí:

| | |
|---|---|
| **90° rompe en los tres** | sin excepción. La tetera pierde el pico; la cámara se degrada hasta un cilindro irreconocible. **Es el ángulo a evitar** |
| **45° y 180° son fiables** | los dos ángulos donde el objeto sobrevive |
| **la complejidad manda** | formas sólidas y simples (bota) aguantan; objetos mecánicos con piezas finas y texto (cámara) se desintegran |

**Y el aviso que más importa: la métrica premió un fallo.** La bota puntuó
**0,860 — «el mismo, sin duda»— y a 180° está mal**: generó **dos botas**, un
par, en vez de una bota girada. Como el cuero, los cordones y la suela son
correctos, el parecido sale altísimo.

Es exactamente por lo que existe la regla de auditar cada imagen. Con la métrica
sola habríamos publicado un par de botas como si fuera una rotación.

---

## 10. Lo que la investigación recomendó y la medición tumbó

Esta sección existe para recordar que **medir manda**.

| recomendado | medido aquí | veredicto |
|---|---|---|
| `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.85` + `--reserve-vram 3` | 130 s → **298 s y 193 s** | **revertido** |
| `--cpu-vae` para Zero123 | todas las imágenes negras | descartado |
| IPAdapter resolvería la consistencia de objeto | 0,731 → 0,768, insuficiente | parcial |

La investigación era impecable, con fuentes primarias y aritmética correcta. En
esta máquina, falsa. **Nada entra como configuración recomendada sin medirlo.**

---

## 11. Deuda técnica conocida

**La métrica está midiendo la categoría, no la identidad.** CLIP se entrena con
pares texto-imagen: codifica lo descriptivo, no los detalles finos que no
aparecen en las anotaciones. Puntúa igual nuestra caja y otra caja distinta de la
misma clase — que es exactamente el fallo que queremos detectar.

**Hay que cambiar a DINOv2**, que se entrena de forma autosupervisada para
distinguir imágenes entre sí y es el estándar en la literatura para fidelidad de
sujeto. Los números bajarán, pero por primera vez medirán identidad.

**`lote.py` edita el flujo por índice de widget.** Si ComfyUI mueve un widget,
`v[2]` deja de ser `steps` y **no salta ningún error**: se generaría con
parámetros equivocados durante semanas. En formato API los campos van por nombre
y eso es imposible. `flujo_referencia.py` ya lo hace bien; `lote.py` no.
