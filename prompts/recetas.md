# Recetas de prompt — SDXL / Juggernaut XL v9

Los prompts van **en inglés**: el modelo se entrenó en inglés y entiende bastante peor el
español. Tú piénsalo en español y yo lo traduzco cuando quieras.

## Estructura que funciona

`[tipo de foto] of [sujeto], [acción/pose], [entorno], [luz], [lente/cámara], [estilo]`

Cuanto más concreto, mejor. "mujer bonita" da resultados genéricos; "woman in a red linen
blazer, leaning on a concrete wall, overcast light" da una foto.

---

## 1. Fotorrealismo / personas

```
editorial portrait photograph of a woman in her 30s wearing a beige wool coat,
standing in a narrow european street, soft overcast daylight, shallow depth of field,
85mm lens, natural skin texture with visible pores, subtle film grain
```
**Negativo:** `plastic skin, airbrushed, deformed hands, extra fingers, blurry, watermark, cartoon`

> Truco: `natural skin texture`, `visible pores` y `film grain` son lo que separa una foto
> creíble del típico look de plástico de IA.

## 2. Portada de reel / social (9:16 con hueco para texto)

```
cinematic vertical composition, young man in a black hoodie looking at camera,
standing on the left third of the frame, dark teal gradient background with negative space
on the right, dramatic side lighting, high contrast, bold modern advertising look
```
**Negativo:** `text, letters, watermark, logo, cluttered background, busy composition`

> Clave: pide **`negative space`** en el lado donde luego pondrás el titular. El modelo no sabe
> escribir texto legible — el texto se pone después en Canva/Express, nunca en el prompt.

## 2-bis. Épico cinematográfico (espartanos) — probado 11-ago-2026

```
epic cinematic film still of a lone Spartan hoplite warrior standing on a windswept rocky cliff
at dawn, bronze Corinthian helmet with tall crimson horsehair crest, deep crimson wool cloak
billowing violently in the wind, battle-worn bronze hoplon shield and long ash spear, muscular
scarred physique, leather and bronze greaves, low camera angle looking up at him, dramatic
golden backlight from the rising sun behind his silhouette, volumetric god rays cutting through
haze, swirling dust and glowing embers in the air, distant storm clouds over the aegean sea,
teal and orange color grading, high contrast chiaroscuro lighting, anamorphic lens flare,
shallow depth of field, 35mm anamorphic film, heavy film grain, hyper detailed metal and skin
textures, vertical composition with the warrior in the lower third and dramatic sky filling the
upper half
```

**Versión final corregida** (`workflows/04-espartano-final.json`, semilla 202020, 30 pasos):
cara visible, lanza correcta, medio cielo libre para el titular.

**Lecciones aprendidas al probarlo:**
- ⚠️ **Nunca uses términos técnicos que suenen a otra cosa.** Escribí `bronze leaf-shaped tip`
  (el nombre real de la punta de lanza griega) y SDXL dibujó **una hoja gigante**. El modelo no
  sabe de terminología, solo de imágenes. Di `small narrow pointed bronze spearhead`.
  Regla general: si una palabra tiene un significado literal común, el modelo usará ese.
- `soft warm fill light revealing the detail of his armor` rescata el detalle cuando el
  contraluz te deja al personaje en sombra total.
- `backlight from behind his silhouette` hace que salga **de espaldas**. Si quieres verle la
  cara, añade `facing the camera, helmet and face visible, three-quarter view`.
- A CFG 1.0 (flujo rápido) el modelo **cambia la lanza por una espada**. Para que respete el
  arma hay que usar `02-calidad.json` (CFG 5.5), donde el prompt sí manda.
- Lo que sí funciona siempre: `low camera angle` (heroico), `volumetric god rays`,
  `teal and orange color grading`, `heavy film grain`.

## 2-ter. LO QUE APRENDIMOS MIDIENDO (11-ago-2026)

Resultados de 13 imágenes generadas cambiando **una sola variable** con semilla fija 101010.
Esto no es teoría de internet: está medido en esta máquina.

### 1. El cielo decide si tu color protagonista existe
Cielo frío (azul, verde tormenta) → la capa carmesí **explota**.
Cielo cálido (naranja, rojo atardecer) → la capa **se pierde** dentro del fondo.
Regla: protagonista rojo pide fondo frío.

### 2. A CFG 1.0 no puedes contradecir al modelo
Pedí capa negra, azul, blanca y verde. **Las cuatro salieron rojas.**
Pero la *túnica* de debajo sí cambió de color. El modelo lee tu color y lo pinta en la prenda
equivocada, porque "espartano = capa carmesí" está demasiado grabado.
→ El modo rápido (8 pasos) sirve para explorar composición y cielo, **no para imponer detalles**.

### 3. CFG 5.5 mejora, pero tampoco basta solo
A 30 pasos el negro entró en el penacho y apareció el relámpago… pero la capa seguía roja.
Subir CFG **no vence un concepto muy cementado**, solo lo empuja.

### 4. Lo que SÍ funciona para forzar un detalle
Combinar dos palancas:
```
caja del detalle:  (torn jet black wool cloak:1.6), (black fabric:1.3)
negativo:          (red cloak:1.5), (crimson cloak:1.5), (orange cloak:1.4)
```
**Resultado: capa negra de verdad.** Pero con dos efectos secundarios reales:
- Peso 1.6 **desborda**: el negro se comió la túnica, las grebas y la armadura.
- Negar "red cloak" **mató también el penacho rojo del casco**. Para el modelo "rojo en la
  capa" y "rojo en el casco" son el mismo concepto — no sabe distinguir dónde.

**Ajuste recomendado la próxima vez:** peso **1.2–1.3** y negativo solo `crimson cape`,
nunca `red` a secas.

### 5. La sintaxis de peso
`(texto:1.5)` sube la importancia, `(texto:0.7)` la baja. 1.0 es neutro.
Por encima de 1.5 empieza a deformar la imagen entera, no solo lo que pediste.

## 3. Ilustración / arte

```
digital illustration of a fox sitting on a mossy rock in a foggy pine forest,
flat vector shapes, limited palette of teal and burnt orange, clean linework,
poster art style, minimal detail
```
**Negativo:** `photorealistic, 3d render, blurry, messy lines, watermark`

> Para anime de verdad conviene otro checkpoint (Illustrious / Animagine). Juggernaut hace
> ilustración decente pero no es su terreno. Dímelo y lo añadimos.

## 4. Producto / e-commerce

```
professional product photograph of a matte black ceramic coffee mug on a light grey seamless
backdrop, soft large softbox from the left, subtle reflection on the surface,
studio lighting, sharp focus, commercial catalog photography
```
**Negativo:** `cluttered, hands, text, logo, harsh shadows, blurry, distorted proportions`

> Para fondo perfectamente limpio, es más fiable **quitar el fondo después** que pedirlo en el
> prompt. Se puede añadir un nodo de recorte automático cuando lleguemos ahí.

---

## Ajustes según qué flujo uses

| | `01-rapido.json` | `02-calidad.json` |
|---|---|---|
| Pasos | 8 | 30 |
| CFG (cuánto obedece al prompt) | 1.0 | 5.5 |
| Para qué | Explorar ideas, muchas variantes | La toma final |

**Ojo con el flujo rápido:** a CFG 1.0 el prompt **negativo prácticamente no hace nada** (es
como funciona Lightning). Si algo te molesta en la imagen, quítalo describiendo lo que SÍ
quieres, no lo que no quieres. En el flujo de calidad el negativo sí manda.

## La semilla (seed)

Es el número que fija el "azar". Misma semilla + mismo prompt = misma imagen exacta.
- Cambiar la semilla = otra imagen distinta con el mismo prompt.
- Dejarla fija mientras ajustas el prompt = ves solo el efecto de tu cambio.

Ambos flujos vienen con `seed: 424242` para que podamos comparar peras con peras.
