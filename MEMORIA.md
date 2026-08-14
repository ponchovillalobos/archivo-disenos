# Memoria de lo probado

Todo lo que se ha ensayado en este proyecto, con su medición y su veredicto.
Existe para **no repetir errores**, y por eso incluye —sobre todo— lo que salió
mal y lo que creímos y era falso.

**Cómo se lee:**

- **MEDIDO** — hay un número, sacado de esta máquina o de una fuente primaria.
- **VERIFICADO EN CÓDIGO** — se leyó el código de ComfyUI o de PyTorch.
- **OPINIÓN** — consenso de comunidad sin medición. Se marca para no confundirlo.

Regla de la casa: **una variable por prueba.** El error más caro del proyecto
—dos veces— fue cambiar dos cosas a la vez y atribuir el resultado a la que más
nos gustaba.

---

## 1. La máquina

Mac mini M4 base, 16 GB unificados, macOS 26.5, ComfyUI 0.31.0, PyTorch 2.13, MPS.

| | |
|---|---|
| Ritmo sano, SDXL 832×1216, 30 pasos | **130 s por imagen** |
| Referencia pública para el mismo equipo | ~143 s |
| Nuestra posición | **8 % más rápidos, y con 16 GB en vez de 24** |

**No tenemos un problema de rendimiento base.** Todo el margen está en no caer
al swap. Cuando algo tarda mucho más de 130 s, hay una causa concreta y está
listada abajo.

---

## 2. La causa raíz de los desastres: el Mac se duerme

**MEDIDO.** La noche del 13 al 14 de agosto se perdieron seis horas de estudio.
Se culpó al swap, luego al Guardián. Ninguno era la causa raíz.

`pmset -g log` de esa noche, patrón repetido **154 veces**:

    03:16  duerme ....... 948 s   (15,8 min)
    03:32  despierta ....  45 s
    03:32  duerme ....... 953 s
    03:48  despierta .... 138 s

**El Mac estuvo dormido el 95 % de la noche.** Despertaba 45-60 segundos cada
16 minutos.

La aritmética cuadra exacta: una imagen necesita 130 s despierto; a 45-60 s por
ciclo hacen falta tres ciclos ≈ **48 minutos**. Las imágenes de esa noche
salieron a las 04:13, 05:03, 05:52 y 07:07 — **49, 49 y 49 minutos**.

**El arreglo:** `caffeinate -i -m -s -w <pid>` mientras dura una tanda. No se
cambia la configuración del sistema: se impide dormir solo mientras hay trabajo.

    caffeinate -i -m -s -w $(pgrep -f mi_productor.py)

**Ninguna tanda larga se lanza sin esto.** Es la primera comprobación cuando
algo va lento.

---

## 3. El techo de memoria de PyTorch está por encima de la RAM

**MEDIDO en esta máquina:**

    torch.mps.recommended_max_memory() ....... 12,71 GB
    PYTORCH_MPS_HIGH_WATERMARK_RATIO ......... 1,7 (por defecto)
    techo real ............................... 21,6 GB
    RAM física ............................... 16 GB

PyTorch tiene permiso para pedir **21,6 GB en una máquina de 16**. Por eso
**nunca da error de memoria**: pide, y macOS lo sirve con swap.

**La consecuencia grave:** ComfyUI tiene redes de seguridad —reintento del VAE
por baldosas, troceado de la atención— y **todas se disparan ante un error de
memoria que en Mac no llega jamás**. Están ahí, inertes.

**El arreglo:**

    PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.85    # techo 10,8 GB
    PYTORCH_MPS_LOW_WATERMARK_RATIO=0.75     # recolección a partir de 9,5 GB

Hay que mover **las dos**: bajar la alta por debajo de 1,4 sin bajar la baja
aborta el arranque.

**NUNCA `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0`.** Es el consejo que más circula
por internet —sale hasta en el propio mensaje de error de PyTorch— y hace lo
contrario: **quita el techo**. En 16 GB cambia un error limpio por un cuelgue.

**NUNCA tocar `iogpu.wired_limit_mb`** (está en 0, correcto). Hay pánicos de
núcleo documentados en un M4 Pro de 24 GB, con el sistema arrastrándose y los
altavoces distorsionando antes de morir. La memoria *wired* no la puede
reclamar el sistema.

---

## 4. Errores propios, y cuál era la verdad

### 4.1 «El veto de color es el hallazgo más rentable» — FALSO

Ver `MODELO.md`. Cuatro variantes, idénticas por pares píxel a píxel. **A CFG
1.0 el prompt negativo no existe**: se cancela en la fórmula y ComfyUI ni
siquiera lo evalúa. Todo el mérito era de los pesos en positivo.

### 4.2 «CLIP corta en 77 tokens» — MAL PLANTEADO

**VERIFICADO EN CÓDIGO** (`comfy/sd1_clip.py`). ComfyUI **no trunca**: trocea en
bloques de 77 y los concatena. Nada se pierde por pasarse. Pero:

- **El vector *pooled* sale solo del primer bloque** (línea 49). En SDXL ese
  vector es una entrada de condicionamiento propia. Lo que va después del token
  75 **no lo toca en absoluto**.
- **No hay atención entre bloques.** Un concepto partido por el corte pierde su
  contexto.
- **El relleno no es gratis.** SDXL se crea sin máscaras de atención, así que los
  tokens de relleno del segundo bloque participan y llegan al modelo.

La conclusión práctica (**caber en 75 tokens, lo esencial primero**) era
correcta; el motivo que dábamos, no.

### 4.3 «El orden del prompt importa» — CIERTO, con dos pruebas

**VERIFICADO EN CÓDIGO:** el codificador de CLIP lleva máscara causal
(`clip_model.py:174`), o sea que cada token solo ve los anteriores; lo primero
se acumula en todo lo demás.

**MEDIDO:** *A Cat Is A Cat (Not A Dog!)*, NeurIPS 2024, arXiv 2410.00321 — 400
prompts, sesgo sistemático hacia el objeto mencionado primero.

### 4.4 «El Guardián fue la causa de la noche perdida» — A MEDIAS

El Guardián reiniciaba si una imagen tardaba más de 450 s. Con el Mac dormido
tardaban 49 minutos. Las mataba **siempre**, justo antes de terminar, trece
veces en seis horas.

Pero la causa raíz era el sueño (§2). **Sin el sueño, las imágenes tardan 130 s
y su umbral no habría saltado nunca.** El Guardián convirtió «lento» en «nada»;
no creó la lentitud.

### 4.5 «Falta pasar target_width al condicionamiento» — FALSO

**VERIFICADO EN CÓDIGO:** `comfy/samplers.py:encode_model_conds` rellena
`width`/`height` automáticamente desde la forma del latente, y
`model_base.SDXL.encode_adm` hace `target_width = kwargs.get("target_width",
width)`. Con `CLIPTextEncode` plano, SDXL **ya recibe** los valores correctos.
`CLIPTextEncodeSDXL` solo aportaría separar `text_g` de `text_l`.

### 4.6 «Coherencia alta = buen resultado» — FALSO, y premiaba el fracaso

Medíamos coseno CLIP entre las imágenes completas. Ese vector codifica el fondo,
el encuadre y la luz tanto como al sujeto.

**Un 0,99 se consigue de la peor forma posible: generando seis veces la misma
imagen.** Celebramos un 0,990 que significaba exactamente eso.

Peor: pedir «0,90 de parecido con seis escenas distintas» es casi una
**contradicción** con esa métrica.

Ahora se mide con tres números y hay que pasar los tres (`adherencia.py`):

| | qué mide | hacia dónde debe ir |
|---|---|---|
| **fidelidad** | cada imagen contra la ficha del personaje, en texto | alta |
| **margen** | cada imagen identifica SU escena y no la del vecino | alta |
| **parecido** | cuánto se parecen entre sí | **baja** con escenas distintas |

---

## 5. La trampa que más veces nos ha mordido: describir un LUGAR

Tres veces, la misma forma:

| dónde | decía | qué pasó |
|---|---|---|
| ánimo `reflejo` | «aire limpio **sobre el agua**» | inundó cuatro interiores de diez |
| objeto | «punta de lanza **con forma de hoja**» | una hoja gigante |
| paleta `dorado-selva` | «**emerald jungle**» a peso 1,3 | cuatro prompts distintos, la misma foto de follaje |

**La regla:** una paleta describe **color**; un ánimo describe la **cualidad de
la luz**. Ninguno de los dos puede nombrar un sitio ni un objeto que pueda
aparecer en el cuadro. Si lo nombra, compite con la escena — y como la paleta va
con peso 1,3 y la escena con 1,0, **gana la paleta**.

**Y subir el peso de la escena no lo arregla.** Se probó `(extreme wide
shot:1.5)` para compensar: salió peor. Lo que funcionó fue **quitar lo que
competía**.

Auditado a 14-ago-2026: las 16 paletas y los 10 ánimos, limpios.

---

## 6. Los pesos van inflados

**VERIFICADO EN CÓDIGO + FAQ oficial de ComfyUI.** ComfyUI **no normaliza** los
pesos; A1111 y Civitai sí. Los números copiados de ese mundo pegan mucho más
fuerte aquí.

Y el peso no hace que el modelo «mire más» esa palabra: se aplica *después* del
transformador (`sd1_clip.py:56-62`), extrapolando el vector de salida lejos del
prompt vacío. No cambia la atención.

    trabajo ....... 0,8 – 1,3
    techo ......... 1,4
    nunca ......... > 1,5

Teníamos **26 pesos por encima de 1,4** (`(hands:1.6)`, `(portrait:1.5)`…).
Corregidos en `paletas.py`.

---

## 7. Consistencia de personaje: lo que NO funciona

Tres días de intentos. Todo esto está descartado **con medición**, no por
impresión:

| método | resultado |
|---|---|
| Semilla fija + ficha repetida | el personaje deriva |
| IPAdapter `linear`, pesos 0,20 → 1,00 | copia la composición; **el peso no cambia nada** (0,977 en todo el barrido) |
| IPAdapter `style transfer` 0,85 y 1,00 | copia el encuadre igual |
| Subir el peso del encuadre a 1,5 | peor |
| IPAdapter FaceID / InstantID / PuLID | **imposible**: exigen detectar un rostro **humano** y fallan sin él |

**Lo que sí queda por probar** (de la asamblea, verificado en el código de
cubiq): en SDXL, IPAdapter no escala pesos — **aplica el adaptador a capas de
atención concretas**, y **la capa 3 es la que copia la composición**.

    linear .................. todas las capas (0-10) → copia el encuadre
    style transfer .......... solo la capa 6
    composition ............. solo la capa 3
    strong style transfer ... todas menos la 3

De ahí salen tres palancas sin tocar:
1. `style_boost` **negativo** (rango −5 a 5) en `IPAdapter Precise Style
   Transfer`: va directo a la capa 3 y **resta** composición.
2. `combine_embeds: average` en vez de `concat`: promedia varias vistas del
   personaje y **cancela la pose**.
3. `start_at 0.25`: la composición se fija en los primeros pasos; entrando
   después, el prompt decide el encuadre.

**Trampa detectada:** si la imagen de referencia no es cuadrada, se **recorta al
centro**. Las nuestras son 832×1216 — llevábamos días alimentando recortes
centrales. Se arregla con `Prep Image For ClipVision`.

**La solución de fondo:** entrenar un **LoRA del personaje**. Un LoRA modifica
pesos, no inyecta imágenes en la atención, así que **no tiene forma de copiar el
encuadre**. En este Mac se entrena con Draw Things, a 512 px por el límite de
16 GB.

---

## 8. Descartado sin más pruebas

| qué | por qué |
|---|---|
| **FreeU / FreeU_V2** | El paper no reporta FID ni CLIP en el cuerpo; solo una encuesta de preferencia de los propios autores, sobre SD1.x. Y hay evidencia independiente **medida** de que **empeora**: FID 25,47 → 33,70 aplicándolo en todos los pasos, que es lo que hace el nodo de ComfyUI. En Mac, además, puede caerse a CPU en cada paso. |
| **AlignYourSteps a 30 pasos** | El propio paper de NVIDIA: *«al aumentar los pasos, el impacto de los distintos calendarios se desvanece»*. Su tabla para SDXL tiene 11 valores = optimizada para 10 pasos. Solo sirve para **bajar** a 10-12. |
| **Refiner de SDXL** | Entrenado sobre latentes de SDXL base 1.0; Juggernaut es un ajuste fuerte y sus latentes ya no son los que espera. Ninguna fuente oficial de RunDiffusion lo menciona. Y dos modelos en 16 GB = swap. |
| **Self-Attention Guidance** | Superado por PAG y marcado experimental. |
| **fp8** | No existe en M4: Metal no tiene tipo float de 8 bits. Fallo duro, no lentitud. |
| **GGUF para SDXL** | Su propio autor lo desaconseja (*«no cuantices SDXL / SD1»*): SDXL es convolucional y las conv2d se degradan. Y en MPS falta `aten::__rshift__`, que cae a CPU. |
| **`--lowvram` / `--highvram`** | **No hacen nada en Mac**: el código los asigna y luego los pisa incondicionalmente con `SHARED`. |
| **`sdxl_vae_fp16fix`** | **Bit a bit idéntico** al VAE del checkpoint: 248 tensores comparados, diferencia máxima 0,0. Y nuestro VAE corre en bf16, que no desborda. 319 MB y un nodo para nada. |
| **`BREAK` en el prompt** | No existe en ComfyUI. La palabra se tokeniza y el modelo dibuja «romper». El equivalente nativo es `ConditioningConcat`. |

---

## 9. Lo que dice el autor del modelo que usamos

Ficha oficial de Juggernaut (RunDiffusion), contrastada en cuatro fuentes:

| | recomendado | nosotros |
|---|---|---|
| Resolución | 832×1216 | ✔ igual |
| Pasos | 30-40 | ✔ 30 |
| CFG | **3-6** («menos = más realista») | ✘ 5,5, borde alto |
| Muestreador | **DPM++ 2M SDE** (cambió desde 2M Karras) | ✘ `dpmpp_2m` |
| Negativo | **empezar SIN negativo** y añadir solo lo que aparezca | ✘ 208-321 tokens |
| Escalado | `4xNMKD-Siax_200k`, 15 pasos, denoise 0.3, 1.5× | ✘ no lo hacemos |

**Nunca usar las variantes `_gpu` del muestreador**: generan el ruido en el
acelerador, así que la misma semilla da imágenes distintas entre Mac y PC. El
recetario de semillas dejaría de valer al migrar a Windows.

---

## 10. Avisos con fecha de caducidad

- **No actualizar a macOS 27.** Incidencia abierta en PyTorch: SDXL sobre MPS
  devuelve **ruido puro** en macOS 27; funcionaba en 26. Vamos en 26.5.
- **Mantener la resolución constante dentro de una tanda.** Hay una fuga de
  memoria documentada en MPS asociada a la caché de compilación **indexada por
  formas de tensor**: +1 MB por llamada con formas variables, +0,4 MB total con
  forma fija.
- **Cerrar el navegador durante una tanda.** Con 16 GB, ComfyUI (~7 GB) más el
  editor más el navegador no caben. Vale más que cualquier bandera.

---

## 10 bis. El encuadre: peleábamos con el entrenamiento, no con el prompt

**`extreme wide shot` no es vocabulario del modelo.** El término que funciona es
**`establishing shot`**.

Hay una rejilla publicada donde `long shot`, `medium full shot`, `full shot` y
`upper body shot` producen **todos lo mismo** que `medium shot`. Y la causa está
en el paper de Playground v2.5, sobre el condicionamiento de SDXL:

> *«obligó al modelo a aprender a colocar el sujeto **en el centro**»*

Es el fallo que repetimos en el cuento del elefante («el árbol dominando el
cuadro, el elefante pequeño») y en la prueba de la caja. **Dos semanas culpando
al prompt.**

Lo que sí obedece es el **ángulo**: `from above`, `bird's eye view`,
`overhead shot` rompen el encuadre donde ninguna palabra de distancia lo logra.

---

## 10 ter. La métrica premia el parecido de categoría, no la identidad

Dos veces en el mismo día me engañó, y las dos en la misma dirección.

**La acuarela salió última** en el estudio de siete estilos, cuando a ojo es de
las mejores para un cuento infantil. CLIP puntúa sistemáticamente más alto las
imágenes fotográficas contra un texto.

**La bota puntuó 0,860 —«el mismo, sin duda»— y estaba mal.** A 180° generó
**dos botas**, un par, en vez de una bota girada. Como el cuero, los cordones y
la suela son correctos, el parecido sale altísimo.

La causa, explicada en el paper de DreamBooth: CLIP se entrena con pares
texto-imagen y codifica lo descriptivo, **no los detalles finos que no aparecen
en las anotaciones**. Puntúa igual nuestra caja y otra caja distinta de la misma
clase — que es justo el fallo que queremos detectar.

**Pendiente: cambiar a DINOv2**, entrenado de forma autosupervisada para
distinguir imágenes entre sí. Los números bajarán y por fin medirán identidad.

**Mientras tanto, la regla se mantiene: se audita cada imagen a ojo.** La métrica
sola habría publicado un par de botas como si fuera una rotación.

---

## 10 quater. Girar un objeto: se puede, con condiciones

**MEDIDO** sobre cinco vistas:

    SDXL, cinco tomas por prompt .....  0,731   probablemente OTRO objeto
    IPAdapter, capa 3 en -0,5 ........  0,768   el mismo, con variación
    Stable Zero123-C .................  0,884   el mismo, sin duda

SDXL **no puede rodear un objeto por prompt**: no tiene representación
tridimensional. Cinco tomas dieron cinco cajas distintas y la abolladura
declarada en una esquina concreta no apareció en ninguna.

La receta completa está en `herramientas/vistas.py`. Dos cosas obligatorias:
**`--gpu-only`** (sin ella salen negras de forma intermitente: 2 de 5 limpias
frente a 11 de 11) y la **entrada al formato oficial** (blanco puro, recorte al
objeto, lado largo ≤200 px, centrado en 256×256).

Probado con tres objetos más — tetera, cámara y bota:

| | |
|---|---|
| **90° rompe en los tres** | sin excepción. Es el ángulo a evitar |
| **45° y 180° son fiables** | ahí el objeto sobrevive |
| **la complejidad manda** | formas sólidas aguantan; objetos mecánicos con piezas finas y texto se desintegran |

Y la prueba dura la pasa: el pico de la tetera está a la izquierda en la original
y aparece **a la derecha a 180°**. Es una rotación real.

---

## 11. Reglas duras del proyecto

1. **Nada se publica sin verificar contra la fuente primaria.**
2. **Cero caras humanas y cero manos** en la serie de comunicación. (Un
   personaje de cuento sí lleva cara: es su identidad. Ese estudio usa su propio
   negativo.)
3. **Se audita cada imagen.** Si falla una, se regenera esa, no la tanda.
4. **Se verifica en pantalla antes de decir que algo está listo.** Que un script
   termine sin error no significa que el resultado sea correcto.
5. **El portal se actualiza en el mismo turno en que nace el fichero.**
6. **Nunca se edita un módulo de un proceso en marcha.** Python carga al
   arrancar; el proceso vivo no ve el cambio. Ya costó 90 minutos de producción
   con código viejo.
7. **Una variable por prueba.**
