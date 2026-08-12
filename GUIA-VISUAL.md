# Guía para ver y tocar el flujo tú mismo

## Paso 1 — Abre la interfaz

En Safari o Chrome, ve a:

**http://127.0.0.1:8188**

Si no carga, es que ComfyUI está apagado. Enciéndelo con lo de `COMANDOS.md`, o pídemelo a mí.

## Paso 2 — Carga el flujo

En la **barra lateral izquierda** busca el icono de **Workflows** (una carpeta o un icono de
diagrama, según versión). Dentro verás:

> **ESPARTANO editable**

Haz clic. Aparece el diagrama completo en pantalla.

> No hace falta arrastrar ningún archivo. Ya está dentro de ComfyUI.

## Paso 3 — Entiende lo que ves

Se lee de **izquierda a derecha**. Cada caja es un paso, y las líneas de colores son "cables"
que llevan la información de una caja a la siguiente.

| Caja | Qué hace |
|---|---|
| 1. Modelo base | Carga el cerebro que dibuja (Juggernaut XL, 6,6 GB) |
| 2. VAE | Traduce el resultado interno a colores correctos |
| **3. PROMPT (verde)** | **Lo que SÍ quieres. Aquí escribes tú.** |
| 4. NEGATIVO (rojo) | Lo que NO quieres |
| 5. Tamaño | 768 × 1344 = vertical 9:16 de reels |
| **6. GENERADOR (morado)** | **Aquí está la SEMILLA y los pasos** |
| 7. Convertir | Pasa de datos a imagen visible |
| 8. Resultado | Te enseña la imagen y la guarda sola |

Dentro del lienzo hay una caja marrón, **"LEEME PRIMERO"**, con este mismo resumen, para
cuando no tengas esta guía a mano.

## Paso 4 — Las dos únicas cosas que necesitas tocar

### El PROMPT (caja verde)
Doble clic sobre el texto → escribes → clic fuera. **En inglés.**
Las recetas están en `prompts/recetas.md`.

### La SEMILLA (caja morada, campo `seed`)
Es el número que fija el azar.

- **Mismo número + mismo prompt = exactamente la misma imagen.** Siempre. Es reproducible.
- **Cambias el número = otra imagen distinta**, con el mismo prompt y el mismo estilo.
- Debajo hay un desplegable que ahora dice **`fixed`** (fija). Si lo pones en **`randomize`**,
  cada vez que ejecutes saldrá una semilla nueva → ideal para explorar sin pensar.

**Estrategia recomendada:**
1. Pon `randomize` y genera 4-5 veces hasta que una composición te guste.
2. Cuando te guste una: mira qué semilla salió, apúntala, y vuelve a poner `fixed` con ese número.
3. Ahora ajusta el prompt poco a poco. Como la semilla está fija, **solo verás el efecto de tu
   cambio**, no del azar.

## Paso 5 — Generar

Botón **Run** (arriba, o el botón grande de reproducir). Verás las cajas iluminarse en orden.

- Flujo actual (30 pasos): **~144 segundos**
- La imagen aparece en la última caja y se guarda sola en `~/comfy/output/reels/`

## Semillas que ya probamos (para que no partas de cero)

| Semilla | Qué salió |
|---|---|
| **202020** | El espartano final: cara visible, lanza, cielo despejado arriba. **La buena.** |
| 101010 | Perfil con capa roja enorme, pero con espada en vez de lanza |
| 303030 | Contrapicado con escudo a la espalda, arma fantasiosa |
| 424242 | Las fotos de prueba de la mujer en la azotea |

## Si quieres la versión rápida (37 s en vez de 144 s)

En la caja morada cambia:
- `steps`: 30 → **8**
- `cfg`: 5.5 → **1.0**

Y hay que añadir el nodo del LoRA Lightning. **Pídemelo y te lo dejo montado** — es más fácil
que explicártelo por escrito.

⚠️ Con esos ajustes la **caja roja (negativo) deja de funcionar**. No es un fallo: a CFG 1.0 el
negativo matemáticamente no interviene. Por eso en el modo rápido salían espadas aunque yo las
había prohibido.

---

## Nota sobre los otros archivos de `workflows/`

Los que terminan en `.json` normales (`01-rapido`, `02-calidad`, `03-espartano`,
`04-espartano-final`) están en **formato API**: sirven para que yo los ejecute por comando, pero
**la interfaz no los muestra como diagrama**. El único que puedes abrir y ver es
`ESPARTANO-editable-VISUAL.json` (y su copia dentro de ComfyUI).

Si quieres que convierta alguno de los otros a formato visual, dímelo.
