# Investigación: imágenes con texto para redes (11-ago-2026)

Dos investigaciones en paralelo. Resumen de lo accionable. Fuentes al final.

---

## 1. SDXL no escribe texto. Es arquitectura, no ajuste.

Benchmark OneIG-Bench (NeurIPS 2025), texto legible de 0 a 1:

| Modelo | Puntuación |
|---|---|
| SD 1.5 | 0,010 |
| **SDXL (el nuestro)** | **0,029** |
| FLUX.1 dev | 0,523 |
| SD 3.5 Large | 0,629 |
| **Z-Image-Turbo** | **0,994** |

**Causa:** SDXL usa codificadores CLIP con límite de 77 tokens que comprimen el *significado*.
No transportan la secuencia exacta de caracteres. Los modelos que sí escriben usan codificadores
tipo T5/Qwen3. **Ningún LoRA ni sampler lo arregla.**

En la práctica: una palabra corta en mayúsculas puede colar tras varios intentos. Dos palabras,
minúsculas o tildes: falla siempre.

## 2. El texto va ENCIMA, y fuera de ComfyUI

Para producción de 5–10 piezas con textos distintos:

| Herramienta | Veredicto |
|---|---|
| **Adobe Express + MCP (HTML)** | ✅ **Principal.** `export_html_to_express` convierte HTML en documento Express editable. El asistente maqueta las 8 diapositivas de una vez |
| Adobe Express bulk create | ✅ Hasta 99 variaciones desde hoja de cálculo |
| Canva manual | ⚠️ Bien para 1–3 piezas. **El autofill por MCP es solo Enterprise** |
| Canva Bulk Create | ⚠️ Requiere Pro+, solo escritorio, no por MCP |
| Keynote | ⚠️ Gratis y ya lo tienes. Trabajo manual alto |
| **Nodo TextOverlay de ComfyUI** | ❌ **Trampa:** la documentación dice que aplica *el mismo texto a todo el lote*. Sirve para marca de agua, no para narrativa |

Si algún día hacen falta lotes de la misma composición con muchos textos, el nodo vivo es
`Advanced Text Overlay` (scofano, v1.5.0 jun-2026): detecta las fuentes de macOS solo y corre en
CPU, así que **no gasta memoria de GPU**. Evitar Comfyroll (2 años sin tocar) y WAS Node Suite
(archivado).

## 3. Resoluciones — CORRECCIÓN a lo que hacíamos

Instagram acepta fotos de feed con proporción **1.91:1 a 3:4 (0,75)**.
Nuestro 768×1344 = **0,571 → fuera de rango, lo recorta**.

| Destino | Generar | Escalar a | Proporción |
|---|---|---|---|
| Reel / Story / TikTok / Shorts | **768×1344** | 1080×1920 | 0,571 → 0,5625 ✅ |
| **Carrusel / foto de feed** | **896×1152** | 1080×1350 | 0,778 → 0,80 ✅ |

Ambas son resoluciones nativas de SDXL: mismo coste de memoria, sin pérdida de calidad.

**Engagement por formato** (Socialinsider, 35 M de posts): carrusel 0,55 % · reels 0,52 % ·
imagen suelta 0,37 % (−17 % interanual). *Escepticismo: son cuentas de marcas, no creadores, y
el informe etiqueta datos de 2025 como 2026.*

## 4. Zona segura — la única cifra oficial

Meta, para Stories y Reels: libre de texto **14 % arriba, 35 % abajo, 6 % a los lados**.

Sobre lienzo **1080×1920**:

| Zona | Píxeles |
|---|---|
| Prohibido arriba | 269 px |
| Prohibido abajo | 672 px |
| Laterales | 65 px cada uno |
| **Caja segura** | **950 × 979 px, entre y=269 e y=1248** |

TikTok y YouTube no publican cifras en píxeles. La de Meta es más conservadora que las
estimaciones de terceros → **diseña para Meta y quedas cubierto en las tres**.

**Legibilidad:** contraste WCAG 4,5:1 (3:1 si el texto es grande). Usa **scrim** (capa
semitransparente bajo el texto), más fiable que la sombra. Cuerpo 48–72 px en 1080×1920.

## 5. Consistencia de personaje entre imágenes

| Técnica | Memoria extra | ¿Funciona en 16 GB? |
|---|---|---|
| **LoRA de personaje** | 50–200 MB | ✅ **La única que da identidad real** |
| **FaceDetailer** (Impact Pack) | decenas de MB | ✅ No crea identidad, pero **amplifica el parecido** |
| ControlNet (uno solo) | 1,5–3 GB | ⚠️ Al filo. Controla pose, no cara |
| IPAdapter normal | ~3 GB | ❌ Swap |
| IPAdapter FaceID / InstantID / PuLID | 5–8 GB | ❌ **Doble bloqueo** |

**El doble bloqueo, en concreto:** dependen de `insightface` + `onnxruntime-gpu`, y
**`onnxruntime-gpu` no existe para macOS** (es CUDA). Issues abiertos sin resolver. Y aunque se
arreglara, no caben en memoria. Además los repos de referencia están en "maintenance only"
desde abril de 2025.

**Entrenar la LoRA:** en la nube, una vez (~5 USD en fal.ai o RunPod). Localmente es posible
(Draw Things, pico ~10,3 GiB) pero tarda horas y deja el Mac inutilizable.

## 6. Por qué fp8 no sirve en Mac (confirma nuestra decisión del día 1)

El backend MPS **no soporta tipos FP8**: al cargar los convierte a float16/float32, **usando el
doble o el cuádruple de memoria**. Por eso todos los modelos que "caben en 8 GB de VRAM" en PC
**no caben aquí**: su ahorro venía justo de fp8. Las cifras de VRAM de NVIDIA no se traducen a
memoria unificada.

Además, cargar un checkpoint fp8 **crashea**: `Trying to convert Float8_e4m3fn to the MPS backend`.

## 7. Si algún día hace falta texto DENTRO de la escena

Única opción viable: **Z-Image-Turbo en GGUF**.
- `z-image-turbo-Q5_K_S.gguf` (5,24 GB) + encoder Qwen3-4B GGUF Q5 (~2,9 GB) + VAE (0,34 GB)
- Custom node `ComfyUI-GGUF` de city96 · 8–9 pasos · CFG 0.0
- **1,5–3 min por imagen** de 1024×1024 (estimación derivada de mediciones en M4 Pro y M3)
- ⚠️ **Entrenado en inglés y chino.** Sin evidencia de tildes, "ñ" ni "¿". Para español, probablemente falle.

**Descartados con datos:** Flux.1 dev (**760 s/imagen** medidos en Mac de 16 GB) · Qwen-Image
(30 GB en pesos; 2:33 en un Mac de **64 GB**) · SD 3.5 Large (el encoder T5-XXL solo son 9,9 GB).

---

## Nuestros propios datos llenan un hueco de la literatura

La investigación no encontró **ningún benchmark publicado de SDXL en Mac mini M4 base de 16 GB**.
Nosotros lo medimos el 11-ago-2026 en esta máquina:

| Configuración | Tiempo |
|---|---|
| 768×1344, 8 pasos (Lightning) | **37 s** |
| 768×1344, 30 pasos | **144 s** |
| Coste por paso | **~4,8 s** |
| `--use-pytorch-cross-attention` | **27 % más rápido** (37 s vs 51 s) |

Encaja con los ~143 s reportados para 30 pasos en un M4 de 24 GB.

**Matiz importante sobre los modelos de pocos pasos:** menos pasos reduce el **tiempo**, no el
**pico de memoria**. Los pesos siguen cargados igual. Ayuda porque pasas menos rato en swap, no
porque consumas menos.

---

## FLUJO RECOMENDADO

**Una sola vez:**
0. Entrenar LoRA del personaje en la nube (~5 USD) — la única vía de consistencia real
0b. Definir la plantilla HTML de marca (tipografía, colores, caja segura, scrim)

**Por cada historia:**
1. Guion en Notion: una fila por diapositiva (nº, prompt, texto en pantalla)
2. Generar en ComfyUI: SDXL + LoRA + Lightning 8 pasos · reels 768×1344 / carrusel 896×1152 ·
   prompts pidiendo espacio negativo en la mitad superior
3. FaceDetailer con la LoRA activa (sube el parecido, poca memoria, sin insightface)
4. Subir a Google Drive
5. Maquetar el texto: HTML → `export_html_to_express` → documento Express editable
6. Revisar caja segura 950×979 px · scrim bajo el texto · cuerpo 48–72 px
7. Si es reel: animar en Express (Zoom/Pan)
8. Exportar 1080×1920 y/o 1080×1350

---

## Fuentes principales

**Texto en imágenes**
- [OneIG-Bench (arXiv 2506.07977)](https://arxiv.org/html/2506.07977v1)
- [Z-Image technical report (arXiv 2511.22699)](https://arxiv.org/html/2511.22699v1)
- [FP8 no soportado en MPS — ComfyUI #10292](https://github.com/Comfy-Org/ComfyUI/issues/10292)
- [Q4_0 más lento que Q8 en MPS — ComfyUI-GGUF #236](https://github.com/city96/ComfyUI-GGUF/issues/236)
- [scofano/ComfyUI-Advanced-TextOverlay](https://github.com/scofano/ComfyUI-Advanced-TextOverlay)

**Redes y formatos**
- [Instagram: proporciones de foto (oficial)](https://www.facebook.com/help/instagram/1631821640426723)
- [Meta Ads Guide: zonas seguras de Reels (oficial)](https://www.facebook.com/business/ads-guide/update/image/instagram-reels)
- [TikTok Ads: especificaciones (oficial)](https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads)
- [Socialinsider: benchmarks de engagement](https://www.socialinsider.io/social-media-benchmarks/instagram)
- [Canva MCP: límites por plan (oficial)](https://www.canva.com/help/mcp-canva-usage/)
- [Adobe Creativity Connector (oficial)](https://developer.adobe.com/adobe-for-creativity/)
- [WCAG contraste — WebAIM](https://webaim.org/articles/contrast/)

**Consistencia de personaje**
- [ComfyUI-InstantID #8 — onnxruntime-gpu no existe en macOS](https://github.com/ZHO-ZHO-ZHO/ComfyUI-InstantID/issues/8)
- [insightface #2538 — fallo de compilación en M2 Max](https://github.com/deepinsight/insightface/issues/2538)
- [Draw Things: fine-tuning on-device](https://engineering.drawthings.ai/p/draw-things-democratizes-local-large-model-fine-tuning-on-iphone-ipad-and-mac-2ceb60b5b462)
