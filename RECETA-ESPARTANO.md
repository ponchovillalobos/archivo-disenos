# La receta del espartano

La que produce las imágenes de `out/A1-capa-negra.png`. **Verificada: reproduce
píxel a píxel.**

Este documento existe porque esa receta se perdió. Estaba dentro del PNG desde
el principio —cada imagen lleva la suya— y se tardaron horas en encontrarla
porque nadie la había escrito en ningún sitio legible.

---

## La configuración

**No es lo que la diferencia.** Es idéntica a la que se usaba fallando:

```
modelo        juggernautXL_v9.safetensors
LoRA          sdxl_lightning_8step_lora.safetensors  ·  peso 1.0
tamaño        768 × 1344          (múltiplo de 64, cubo de SDXL)
pasos         8
CFG           1.0
muestreador   euler
planificador  sgm_uniform
semilla       101010
```

Se probaron cuatro semillas: el look aguanta en las cuatro. No es suerte.

---

## Los siete campos, palabra por palabra

```
escena       epic cinematic film still of a lone Spartan hoplite warrior
             standing on a windswept rocky cliff at dawn, bronze Corinthian
             helmet with tall crimson horsehair crest

ropa         torn black wool cloak whipping in the wind

objeto       battle-worn bronze hoplon shield and long ash spear

encuadre     muscular scarred physique, leather and bronze greaves,
             low camera angle looking up at him

aire         heavy grey rain

luz          wet bronze reflecting a dull sky, lightning on the horizon

tratamiento  teal and orange color grading, high contrast chiaroscuro lighting,
             anamorphic lens flare, shallow depth of field, 35mm anamorphic
             film, heavy film grain, hyper detailed metal and skin textures,
             vertical composition with the warrior in the lower third and
             dramatic sky filling the upper half
```

**El negativo, y son solo diez términos:**

```
blurry, low quality, deformed hands, extra fingers, modern clothing,
watermark, text, logo, cartoon, plastic skin, flat lighting
```

---

## Las tres cosas que lo hacen funcionar

Y las tres se hacían al revés en la serie espartana publicada.

### 1. El guerrero es el SUJETO

De cuerpo entero, ocupando el cuadro. No un objeto en el polvo, no una silueta
diminuta al fondo.

Las 184 láminas espartanas aprobadas dicen en su encuadre *«no people or one
tiny distant silhouette»* — y por eso son paisajes atmosféricos bonitos que **no
tienen nada de Esparta**. Se comprobó abriendo tres al azar: cubos de neón rosa
en una playa, un camino entre colinas verdes, y una verja de hierro forjado del
XIX ante ruinas romanas.

### 2. El tratamiento no es una paleta: es una hoja de cámara

Nueve especificaciones encadenadas, no un color:

```
etalonaje        teal and orange color grading
iluminación      high contrast chiaroscuro
óptica           anamorphic lens flare
profundidad      shallow depth of field
película         35mm anamorphic film
grano            heavy film grain
textura          hyper detailed metal and skin textures
COMPOSICIÓN      warrior in the lower third, dramatic sky in the upper half
```

**La composición va escrita.** No se deja al azar. Es la línea que nadie
documenta y la que coloca al guerrero donde tiene que estar.

### 3. El negativo es corto

Diez términos, y **ninguno de ánimo ni de color**. La serie espartana arrastraba
veinticinco con vetos de `horror`, `creepy`, `grimdark` y colores rivales. El
autor del modelo lo dice en su ficha: *«empieza sin negativo; los negativos
pesados suelen hacer más daño que bien»*.

---

## Lo medido en la reconstrucción (104 imágenes)

Una variable por fase, congelando el resto.

| fase | qué movía | resultado |
|---|---|---|
| semillas | 4 semillas | **el look aguanta en las cuatro** |
| etalonaje | 8 tratamientos | ver abajo |
| clima | 6 aires y luces | ver abajo |
| **ángulo** | 5 ángulos de cámara | **casi ninguna diferencia** |
| cuento | 6 momentos | ver abajo |

**El ángulo de cámara no es la palanca.** Las cinco variantes —contrapicado
extremo, a la altura de los ojos, tres cuartos, plano general— salieron
prácticamente iguales. El resto de la receta ya impone el plano heroico.

Es el mismo patrón que con el peso de IPAdapter: cuando cinco valores muy
distintos de un parámetro dan lo mismo, **ese parámetro no es la causa**.

---

## Lo que hay que vigilar al usarla

Auditado sobre hoja de contacto, que es la única forma de ver 104 imágenes de
verdad. La herramienta es `herramientas/contacto.py`.

**Las manos.** El escudo tapa la mano en la imagen de referencia, y ahí está
parte del truco. Cuando el arma se lleva suelta, la mano **se funde con el
brazal** y no se lee. Si el plano deja la mano al aire, hay que auditarla
ampliada.

**El torso.** `muscular scarred physique` hace que el modelo pinte a veces
**torso desnudo** y a veces **coraza de bronce**, dentro de la misma tanda. Para
una serie hay que fijar uno de los dos y decirlo explícitamente.

**La cara.** El casco corintio la cubre por construcción. Es lo que hace esta
receta compatible con la regla dura de cero caras — no hay que vetarla, la tapa
el atrezo.

---

## Cómo se recuperó, y la lección

El usuario señaló el fichero. `recetario.receta()` lo abrió y devolvió todo,
porque **cada PNG lleva su receta dentro** desde siempre.

Lo que faltaba no era el dato: era **haberlo escrito donde se lee**. Se
generaron decenas de imágenes intentando reconstruir de memoria un estilo que
estaba guardado a un comando de distancia.

```python
import recetario
recetario.receta("out/A1-capa-negra.png")
```

**Antes de intentar reproducir un estilo, se abre su receta.** No se reconstruye
de memoria.
