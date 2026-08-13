# Plan — color, formato horizontal y audio → vídeo

Tres encargos distintos. Los dos primeros son ajustes de lo que ya funciona; el tercero es un
módulo nuevo. **Nada de esto toca el pipeline actual**: todo entra como parámetro o como
archivo aparte.

---

## 1 · Color — el problema y por qué pasa

Las imágenes salen grises porque el prompt de tratamiento dice literalmente
`black and white film noir`. No es un efecto lateral: se lo estamos pidiendo.

En las series históricas sobrevivía un color (carmesí, añil, turquesa) porque **había un objeto
de ese color en la escena** y el modelo no podía desaturarlo del todo. En la serie de
comunicación no hay objetos de color, así que sale monocromo puro.

**Prueba en marcha:** la misma escena con seis tratamientos, ya encolada.

| Clave | Tratamiento |
|---|---|
| `noir` | El actual, para comparar |
| `teal-naranja` | Cian y naranja cinematográfico, saturación contenida |
| `bleach` | Bleach bypass **con color**, verdes apagados y azules acero |
| `dorado` | Hora dorada: ámbar y sombras azul profundo |
| `frío` | Índigo y pizarra con un solo acento cálido |
| `tierra` | Ocres y verde musgo, tonos de piel naturales |

Se elige por comparación visual y **se guarda como paleta por serie**, igual que ahora se guarda
el color de acento tipográfico. Cada tema podrá tener su mundo cromático.

**Lo que NO se toca:** las 20 fichas ya publicadas se quedan como están. El color entra en lo
nuevo.

---

## 2 · Formato horizontal — resuelto

| Destino | Generar | Publicar | Proporción |
|---|---|---|---|
| Reel / TikTok / Shorts | 720×1280 | 1080×1920 | 0,5625 exacto |
| Carrusel Instagram | 864×1080 | 1080×1350 | 0,8 exacto |
| **YouTube / apaisado** | **1280×720** | **1920×1080** | **1,7778 exacto** |

1280×720 es un tamaño nativo de SDXL y da 16:9 **exacto**: escala ×1,5 sin recortar nada.

Cambios necesarios, todos pequeños:
- `lote.py` ya acepta ancho y alto como parámetros. Hecho.
- `reel3.py` tiene `W, H` fijos → pasan a parámetros del montador.
- La maquetación del texto cambia: en apaisado el texto va a un **lado**, no arriba, y la zona
  segura es otra (YouTube no publica cifras; se usa un margen del 5 % y se deja libre la franja
  inferior donde aparecen los controles).

---

## 3 · Audio → vídeo horizontal

El encargo real: **das un audio, sale un vídeo**. Con transcripción, troceado en bloques,
imágenes generadas para cada bloque y texto sincronizado.

### Cómo va a funcionar

```
audio.mp3
   ↓ transcribir con marcas de tiempo por palabra
transcripción con tiempos
   ↓ trocear por pausas y por sentido
bloques (texto + inicio + fin)
   ↓ escribir un prompt visual por bloque
prompts
   ↓ ComfyUI, 1280×720
imágenes
   ↓ auditar caras y manos
imágenes aprobadas
   ↓ componer + montar con el audio original
vídeo horizontal 1920×1080
```

### La pieza crítica: las marcas de tiempo

Sin tiempos precisos por palabra no hay sincronía, y el vídeo se ve mal aunque todo lo demás
esté bien. **Un agente está verificando ahora** qué transcriptor funciona de verdad en este Mac
con español y marcas por palabra: whisper.cpp con Metal, mlx-whisper, faster-whisper, y si hace
falta alineación forzada aparte.

Requisitos que le he puesto: sin Homebrew, menos de ~4 GB de memoria, y **que no rompa ComfyUI**
—nada que degrade PyTorch 2.13, que es lo que nos dejaría sin generación de imágenes.

### Cómo se trocea

Dos señales combinadas:
1. **Las pausas del audio** — donde el hablante respira suele haber frontera de idea.
2. **La longitud** — un bloque de 4 a 9 segundos, igual que la regla de lectura que ya usamos
   (`1,6 s + caracteres/19`), pero al revés: aquí manda el audio y el texto se ajusta.

### Riesgos que hay que decir antes de empezar

- **La transcripción se equivoca.** Nombres propios, cifras y tecnicismos son lo primero que
  falla. El guion transcrito habrá que revisarlo, no publicarlo a ciegas.
- **Un prompt automático es peor que uno escrito.** Generar la imagen desde la frase literal da
  ilustraciones planas. Hay que traducir cada bloque a una **escena**, y eso sigue siendo trabajo
  de redacción.
- **Duración.** Un audio de 5 minutos son ~40 bloques = 40 imágenes = **35 minutos de GPU**.
  Conviene fijar un tope y avisar antes de lanzarlo.

---

## Qué se toca y qué no

| | |
|---|---|
| **No se toca** | Las 20 fichas publicadas · el portal · el catálogo · los reels ya hechos |
| **Se amplía** | `lote.py` (ya acepta tamaño) · `reel3.py` (W y H a parámetros) · paleta por serie |
| **Nuevo, aparte** | `transcribir.py` · `bloques.py` · `guion_desde_audio.py` |
| **Entorno** | El transcriptor va en un **venv separado** si amenaza a PyTorch |

## Orden de trabajo

1. Elegir paleta con las seis pruebas *(en marcha)*
2. Parametrizar el formato en el montador *(cambio pequeño)*
3. Esperar el informe de transcripción y montar el entorno
4. Probar el circuito completo **con un audio corto**, no con uno de diez minutos
5. Documentar y versionar en `herramientas/`
