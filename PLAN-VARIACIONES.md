# Plan de variaciones — partiendo de la imagen que te gustó

## Punto de partida (verificado)

- **Trabajo original:** `e72d357d-2b9a-47a2-8d18-bd319c24b976` → `espartano_00001_.png`
- **Semilla: 101010** · 8 pasos · CFG 1.0 · euler / sgm_uniform · LoRA Lightning
- **Flujo nuevo:** `LAB ESPARTANO - variaciones` (en tu barra lateral de ComfyUI)
- **Comprobado:** ejecutado sin cambios da la imagen original, **0 píxeles de diferencia**

El prompt está partido en 6 cajas que se unen solas. El texto resultante es idéntico al
original (854 caracteres, verificado carácter a carácter).

| Caja | Qué controla |
|---|---|
| 1 | Escena y casco (la base — cámbiala poco) |
| **2** | **Capa: color y tela** |
| **3** | **Arma y escudo** |
| 4 | Cuerpo y ángulo de cámara |
| **5** | **Cielo, luz y ambiente** |
| **6** | **Color y óptica (el "look" de cine)** |

---

## La regla de oro

**Un cambio por vez, con la semilla fija en 101010.**

Si cambias tres cosas a la vez y el resultado mejora, no sabrás cuál lo mejoró. Con la semilla
fija y una sola caja modificada, la diferencia que ves **es** el efecto de tu cambio. Nada más.

---

## Fase A — Barridos de una variable (≈37 s por imagen)

Haz cada bloque entero antes de pasar al siguiente. Guarda la que gane de cada uno.

### A1. Capa (caja 2) — 5 imágenes, ~3 min
Prueba los 5 colores del menú. Sale el color que mejor contrasta con el cielo.

### A2. Cielo y ambiente (caja 5) — 5 imágenes, ~4 min
Es **el cambio de mayor impacto de todos**. Un cielo distinto cambia la imagen entera:
luz, color del bronce, sensación. Empieza por aquí si tienes prisa.

### A3. Color y óptica (caja 6) — 4 imágenes, ~3 min
Define si la imagen se ve a lo *300*, a lo documental o a lo vintage. Cambia el ánimo sin
cambiar la escena.

### A4. Arma y escudo (caja 3) — 5 imágenes, ~4 min
⚠️ **Aquí es donde vas a chocar con el límite del modo rápido.** A CFG 1.0 el modelo obedece
poco y te va a poner la espada que le dé la gana. Ya nos pasó. Este eje conviene probarlo en
modo calidad (ver Fase C).

**Total Fase A: ~15 minutos y 19 imágenes.**

## Fase B — Combinar ganadores

Junta la mejor capa + el mejor cielo + el mejor look en una sola pasada. Sigue con semilla
101010.

Aviso honesto: **el combinado no siempre gana**. A veces la mejor capa y el mejor cielo se
pelean (dos colores fuertes compitiendo). Si pasa, cede en uno de los dos.

## Fase C — Llevarlo a calidad

En la caja del motor:
- `pasos`: 8 → **30**
- `cfg`: 1.0 → **5.5**
- `muestreador`: euler → **dpmpp_2m**
- `programador`: sgm_uniform → **karras**
- Y **desconectar el LoRA**: arrastra el cable de "Modelo base" (salida MODELO) directamente a
  la entrada "modelo" del motor.

Tarda 144 s en vez de 37 s, pero **el prompt manda de verdad** y la caja del negativo se activa.
Aquí sí puedes imponer el arma.

> ⚠️ **La semilla 101010 NO conserva la imagen al pasar a calidad.** Al quitar el LoRA y cambiar
> el muestreador, cambia todo el cálculo. Obtendrás una imagen nueva del mismo estilo, no una
> versión mejorada de la misma. Es una limitación real, no un error de configuración.

## Fase D — Pendiente: resolución de Instagram

Ahora generamos 768×1344. Instagram pide **1080×1920**. Falta añadir un paso de escalado
(≈40 s más por imagen). No está montado todavía.

---

## Registro de resultados

Apunta aquí lo que vaya ganando, o dímelo y lo anoto yo.

| Fecha | Caja cambiada | Valor probado | ¿Gana? | Archivo |
|---|---|---|---|---|
| 11-ago | — | original (dorado) | base | `espartano_00001_.png` |
| 11-ago | 5 cielo | luna / noche | 2º | `A2-cielo-luna.png` |
| 11-ago | 5 cielo | atardecer sangre | ✗ se come la capa | `A2-cielo-sangre.png` |
| 11-ago | 5 cielo | **lluvia / tormenta** | ✅ **GANADORA** | `A2-cielo-lluvia.png` |
| 11-ago | 5 cielo | mediodía | ✗ poco épica | `A2-cielo-mediodia.png` |
| 11-ago | 2 capa | negra (rápido) | ✗ salió roja | `A1-capa-negra.png` |
| 11-ago | 2 capa | azul real (rápido) | ✗ salió roja | `A1-capa-azul.png` |
| 11-ago | 2 capa | blanca (rápido) | ✗ salió roja | `A1-capa-blanca.png` |
| 11-ago | 2 capa | verde (rápido) | ✗ salió roja | `A1-capa-verde.png` |
| 11-ago | 2 capa | negra (calidad) | ✗ sigue roja, penacho sí negro | `TEST-calidad-capa-negra.png` |
| 11-ago | 2 capa | negra + peso 1.6 + negativo | ⚠️ negra SÍ, pero se oscureció todo | `TEST-capa-negra-forzada.png` |

| 11-ago | 7 look | bleach bypass | ~ pierde la tormenta | `A3-look-bleach.png` |
| 11-ago | 7 look | sepia vintage | ✗ poco "reel" | `A3-look-sepia.png` |
| 11-ago | 7 look | azul acero | ✅ relámpago + lluvia visibles | `A3-look-acero.png` |
| 11-ago | 7 look | **noir B/N** | ✅✅ **color selectivo accidental** | `A3-look-noir.png` |

**Hallazgo del barrido de look:** pedir `black and white film noir` con "crimson" ya presente en
las cajas 1 y 2 NO da blanco y negro puro — el modelo desatura todo **menos el carmesí**. Efecto
"color selectivo" gratis. Es la mejor base para poner texto encima: fondo sin color = titular
perfectamente legible.

**Estado actual de la base:** tormenta (cielo lluvia) + capa carmesí + semilla 101010.

**Pendiente:** repetir capa negra con peso 1.2–1.3 y negativo solo `crimson cape`.
Barridos de *look de cine* y *armas en calidad*: no lanzados todavía (se reinició el Mac).
