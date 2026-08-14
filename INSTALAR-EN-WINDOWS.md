# Instalar Fuente Primaria en Windows

Este proyecto se escribió y se ejecuta en un Mac mini M4. **Migrarlo a Windows es
posible y la generación de imágenes incluso mejora**, pero hay tres piezas que no
funcionan tal cual y hay que sustituir. Aquí está todo medido, no supuesto.

Lo que sigue está verificado contra el código de este repositorio el 13 de agosto
de 2026: 44 módulos, 7.632 líneas de Python.

---

## Resumen honesto en una tabla

| Pieza | En Windows | Qué hay que hacer |
|---|---|---|
| Generación de imágenes (ComfyUI + SDXL) | ✅ **mejor** | Nada. Con NVIDIA va **5-8× más rápido** |
| **Entrenar un LoRA propio** | ✅ **se desbloquea** | En Mac está roto, no lento. Ver §7 |
| **Las semillas guardadas** | ⚠️ **no reproducen** | Las imágenes no salen idénticas. Ver §7 |
| Composición de láminas (Chromium) | ✅ | Cambiar la ruta del navegador |
| Montaje de vídeo (ffmpeg + PIL) | ✅ | Nada |
| Carrusel PDF y ZIP | ✅ | Nada |
| Portal y estudio visual | ✅ | Nada |
| Contrato, paletas, disposiciones | ✅ | Nada |
| **Transcripción de audio** | ❌ | Sustituir `mlx-whisper` por `faster-whisper` |
| **Guardián de salud** | ❌ | Sustituir `sysctl` por la API de Windows |
| **Rutas del proyecto** | ⚠️ | 17 de 44 módulos llevan rutas de este Mac |

**Esfuerzo estimado: 2-3 días de trabajo.** No es un port, son tres sustituciones
y una capa de configuración.

---

## 1 · Requisitos

| | Mínimo | Recomendado |
|---|---|---|
| SO | Windows 10 x64 | Windows 11 |
| GPU | Cualquiera (irá por CPU, muy lento) | **NVIDIA con 12 GB de VRAM** |
| RAM | 16 GB | 32 GB |
| Disco | 25 GB libres | 50 GB |
| Python | **3.12** | 3.12 |

### Cuánta VRAM, y por qué 12 y no 8

**12 GB, no 8.** Con 8 GB cabe SDXL solo, pero **no caben SDXL + ControlNet +
IPAdapter a la vez**, que es justo el flujo que hace falta para mantener un
personaje entre imágenes. Hay incidencias de falta de memoria documentadas en
tarjetas de 12 GB con dos IPAdapters encadenados, o sea que 12 es el suelo, no
el confort.

Aviso de nomenclatura que confunde a todo el mundo: **la RTX 3060 Ti tiene 8 GB;
la que tiene 12 GB es la RTX 3060 a secas.** Al comprar de segunda mano, mira la
memoria, no el nombre.

### Velocidad, con la honestidad por delante

**MEDIDO en este Mac** (SDXL 832×1216, 30 pasos, `dpmpp_2m`/`karras`):
**130 s por imagen** = 4,33 s por paso.

**MEDIDO por terceros** — el único banco de pruebas con metodología declarada
(repo oficial de ComfyUI, SDXL 1024×1024, 20 pasos, semilla fija):

| GPU | it/s |
|---|---|
| RTX 4090 | 6,17 |
| RTX 3090 | 3,61 |
| RTX 3060 Ti | 2,05 |
| RTX 4060 8 GB | 1,72 |

**INFERIDO, no medido:** ese banco **no incluye la 3060 de 12 GB**, que caería
entre la 4060 y la 3060 Ti → ~1,3-1,7 it/s. Contra nuestros 4,33 s/paso, eso da
**entre 5× y 8×**: la imagen de 130 s pasaría a **20-25 segundos**.

Circulan cifras de 22, 27 y 30 segundos en blogs. Caen en la misma horquilla,
pero **ninguno declara muestreador ni pasos** y varios parecen contenido
generado para posicionar en buscadores. No cuentan como medición.

### Sobre la RAM del sistema

Con 16 GB este Mac va al filo, pero **la causa de las degradaciones no era la
que creíamos**. Está contada entera en `MEMORIA.md` §2 y §3: el Mac se dormía
154 veces por noche, y PyTorch tenía permiso para pedir 21,6 GB en una máquina
de 16. **Ninguno de esos dos problemas existe en Windows con una GPU dedicada**,
porque la VRAM es un espacio propio y separado de la RAM del sistema.

La RAM del sistema **no acelera la generación**. Sirve para no ir al disco al
cambiar de modelo. Con 32 GB vas holgado; con 64, de sobra.

---

## 2 · Lo que hay que instalar

### 2.1 · ComfyUI

```powershell
python -m venv %USERPROFILE%\comfy-env
%USERPROFILE%\comfy-env\Scripts\pip install "comfy-cli>=1.16.0"
%USERPROFILE%\comfy-env\Scripts\comfy --skip-prompt --workspace %USERPROFILE%\comfy install --nvidia
```

`--nvidia` en vez de `--m-series`. Si no hay NVIDIA, usa `--cpu` y asume que
cada imagen tardará varios minutos.

Arrancarlo:

```powershell
%USERPROFILE%\comfy-env\Scripts\comfy --workspace %USERPROFILE%\comfy launch --background -- --listen 127.0.0.1 --port 8188
```

Comprobar que vive de verdad, no que "parece que sí":

```powershell
curl http://127.0.0.1:8188/system_stats
```

Debe devolver `"device_type": "cuda"`. En el Mac dice `"mps"`, y varias pruebas
del proyecto comprueban ese valor — hay que cambiarlas (ver §5.3).

### 2.2 · Los tres modelos

**No están en el repositorio**: pesan 7,3 GB y `.gitignore` los excluye. Se
descargan una vez y se colocan en estas carpetas exactas.

| Fichero | Peso | Carpeta | Origen |
|---|---|---|---|
| `juggernautXL_v9.safetensors` | 6,62 GB | `comfy\models\checkpoints\` | Civitai — Juggernaut XL v9 |
| `sdxl_lightning_8step_lora.safetensors` | 0,37 GB | `comfy\models\loras\` | Hugging Face — ByteDance/SDXL-Lightning |
| `sdxl_vae_fp16fix.safetensors` | 0,31 GB | `comfy\models\vae\` | Hugging Face — madebyollin/sdxl-vae-fp16-fix |

Descárgalos con reanudación. Ya nos pasó que una descarga de 7 GB se cortó al
88 % y `comfy model download` **no reanuda**: hubo que empezar de cero.

```powershell
curl.exe -L -C - --retry 8 --retry-all-errors -o juggernautXL_v9.safetensors <URL>
```

### 2.3 · Dependencias de Python

Todo se ejecuta con el intérprete de ComfyUI (`comfy\.venv\Scripts\python.exe`),
no con el Python del sistema. Versiones verificadas en este proyecto:

```
pillow          12.3.0
numpy           2.5.2
av              18.0.0
imageio-ffmpeg  0.6.0     ← trae su propio ffmpeg, no hace falta instalarlo aparte
pyyaml          6.0.3
fonttools       4.63.0
```

`imageio-ffmpeg` es importante: **el proyecto nunca llama a un ffmpeg del
sistema**, siempre al binario que trae ese paquete. Eso funciona igual en
Windows y ahorra una instalación.

### 2.4 · Chromium

La composición tipográfica se hace con **Chromium headless, no con Pillow**.
Es una decisión de diseño, no un capricho: Pillow no tiene raqm, así que no
aplica kerning ni ejes de fuente variable, y este proyecto usa `opsz`, `WONK` y
`SOFT` de Fraunces.

En el Mac apunta a Brave. En Windows vale Brave, Chrome o Edge:

```
C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe
C:\Program Files\Google\Chrome\Application\chrome.exe
C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
```

**Aviso medido:** un cambio de versión del navegador mueve el kerning y el
`text-wrap: balance`. Las láminas cacheadas con una versión no coinciden con las
nuevas. Si migras a mitad de una serie, borra `herramientas\cache-texto`.

---

## 3 · Lo que NO funciona y hay que sustituir

### 3.1 · La transcripción de audio — **bloqueante**

`herramientas\transcribir.py` usa **`mlx-whisper`**, que corre sobre el
framework MLX de Apple. **No existe en Windows.** Afecta a 3 ficheros:
`transcribir.py`, `banco_asr.py`, `prueba_sistema.py`.

El sustituto natural es **`faster-whisper`** (CTranslate2), que además aprovecha
la NVIDIA:

```powershell
pip install faster-whisper
```

```python
from faster_whisper import WhisperModel
modelo = WhisperModel("large-v3", device="cuda", compute_type="float16")
segmentos, _ = modelo.transcribe(audio, language="es",
                                 word_timestamps=True,
                                 condition_on_previous_text=False,
                                 initial_prompt=CONTEXTO,
                                 temperature=0.0)
```

**Vuelve a medir el WER.** El 5,70 % que documenta este proyecto está medido con
MLX sobre este Mac; no es transferible. El banco de pruebas ya existe
(`herramientas\banco_asr.py`, ocho frases de verdad conocida) — solo hay que
cambiar el motor y ejecutarlo. Y cambia `say` por SAPI o por audio grabado: el
banco genera las muestras con la voz del sistema macOS.

Dos parámetros que **no** son opcionales, medidos aquí:

- `condition_on_previous_text=False` — sin esto un error se arrastra y contamina
  todo lo que viene detrás.
- `initial_prompt` — bajó el error de 9,17 % a 5,70 %. Es la mejora más barata
  del proyecto y no cuesta ni un byte de disco.

### 3.2 · El guardián de salud — **fácil, pero lee esto antes**

`herramientas\guardian.py` usa dos cosas de macOS: `sysctl -n vm.swapusage` y
`pgrep`. También lo usan `alimentador.py`, `reto30_producir.py` y
`estudio_seis.py`.

Sustitución mecánica:

```python
import psutil

def swap_mb():
    return psutil.swap_memory().used / 1e6

def cpu_de_comfy(muestra=3.0):
    for p in psutil.process_iter(["pid", "cmdline"]):
        if p.info["cmdline"] and "main.py" in " ".join(p.info["cmdline"]):
            p.cpu_percent()          # primera llamada: siempre devuelve 0.0
            time.sleep(muestra)
            return p.cpu_percent()
    return -1.0
```

**Pero lo que hay que llevarse de aquí no es el código, es la historia.** Este
guardián **destruyó un estudio de seis horas** y el fallo fue de criterio, no de
sistema operativo — así que se repite igual en Windows si se copia mal:

- El umbral era `max(normal, ritmo) × 3 = 450 s`, un número inventado.
- Las imágenes tardaban 49 minutos (el Mac se dormía, ver `MEMORIA.md` §2).
- **Mataba cada imagen a los 7 minutos y medio, siempre, antes de terminar.**
  Trece veces en seis horas. Ocho imágenes de 36.
- Y el ritmo no podía corregirse solo, porque solo se actualiza cuando algo
  avanza — y nada avanzaba nunca.

La versión actual arregla las tres cosas y **eso sí es portable**:

1. **Mide de verdad, no estima.** El ritmo sale de `/history` de ComfyUI, que
   guarda `execution_start` y `execution_success` de cada trabajo. Ese endpoint
   es idéntico en Windows.
2. **No mata a quien está trabajando.** Antes de reiniciar comprueba si el
   historial creció o si el proceso quema CPU. Cualquiera de las dos = está
   vivo, no lo toques.
3. **Suelo absoluto de 30 minutos.** Por debajo no se reinicia jamás, pase lo
   que pase con la aritmética.

**Con una GPU dedicada este guardián probablemente no salte nunca.** Déjalo
puesto igual: cuesta nada y el día que algo se atasque, lo dice.

### 3.2b · Lo que hay que QUITAR al pasar a Windows

Hay ajustes en este repositorio que existen **solo** por limitaciones de Apple
Silicon. En Windows sobran, y dejarlos puestos hace daño:

| Qué | Por qué se quita |
|---|---|
| `PYTORCH_MPS_HIGH_WATERMARK_RATIO` y `LOW_WATERMARK` | Son de MPS. En CUDA no existen. |
| `PYTORCH_ENABLE_MPS_FALLBACK=1` | Ídem. |
| `--use-pytorch-cross-attention` | En Mac es obligatorio (evita que la atención se fuerce a fp32 por un fallo de macOS). En NVIDIA, ComfyUI ya elige bien solo. |
| `caffeinate` alrededor de las tandas | Es el comando de macOS que impide dormir. **En Windows el equivalente es necesario igual**: `powercfg /change standby-timeout-ac 0`, o `SetThreadExecutionState`. **No lo olvides: es lo que costó una noche entera.** |
| `VAEDecodeTiled` | En Mac quita 3,5 GB del pico porque la memoria es compartida. Con 12 GB de VRAM dedicada puedes volver a `VAEDecode` normal y ahorrar tiempo. |

### 3.3 · Las rutas — **molesto pero mecánico**

**17 de los 44 módulos** llevan rutas absolutas de este Mac:

```
/Users/maity/Desktop/Confy Imagenes     el proyecto
/Users/maity/comfy                      ComfyUI
/Users/maity/comfy/output/reels         donde ComfyUI deja las imágenes
/Users/maity/comfy-env/bin              el ejecutable comfy
/Users/maity/asr/.venv                  el entorno de transcripción
```

Ficheros afectados: `audio.py`, `catalogo.py`, `reel2.py`, `montar_serie.py`,
`recetario.py`, `banco_asr.py`, `buzon.py`, `transcribir.py`, `estudio2.py`,
`guardian.py`, `lote.py`, `alimentador.py`, `prueba_sistema.py`, `recursos.py`,
`reto30_producir.py`, `armar_idea1.py`, `tipografia.py`.

**Lo correcto es una capa de configuración** que los centralice y lea variables
de entorno. Eso además arregla algo que ya duele en el Mac: hoy no se puede
mover el proyecto de carpeta sin romper diecisiete ficheros.

Mientras no exista, un buscar-y-reemplazar funciona.

---

## 4 · Lo que sí es portable tal cual

Y es la mayor parte del valor:

- **La configuración completa del modelo**, en `voz\fuente-primaria.yaml`:
  checkpoint, LoRA y su peso, VAE, pasos, CFG, muestreador, planificador y
  semilla. No hay que adivinar nada.
- **El contrato** (`contrato.py`): pedir lo mismo dos veces da lo mismo, y
  `huella()` lo demuestra en 16 caracteres.
- **Las 16 paletas con su veto** y los 10 ánimos. El veto es lo que hace que el
  color funcione: a CFG 1.0 el modelo casi no obedece una instrucción de color
  en positivo, y solo con el positivo cinco de ocho paletas caían en la franja
  azul-cian.
- **Las 10 disposiciones de lámina** y las 5 voces tipográficas.
- **Los montadores**: Ken Burns con velocidad constante, texto palabra a palabra,
  sincronía con audio.
- **El portal y el estudio visual**, HTML estático servido por `servidor.py`.
- **El recetario**: 371 recetas recuperadas de los metadatos de los propios PNG.
  ComfyUI escribe el flujo entero dentro de cada imagen — eso funciona igual en
  cualquier sistema.

---

## 5 · Pasos concretos, en orden

1. **Clona el repositorio** y crea la estructura: `out\`, `sitio\descargas\`,
   `audio\ENTRADA\`.
2. **Instala ComfyUI** con `--nvidia` y comprueba `"device_type": "cuda"`.
3. **Descarga los tres modelos** a sus carpetas exactas (§2.2).
4. **Sustituye las rutas** de los 17 módulos, o escribe la capa de
   configuración.
5. **Cambia el navegador** en `estudio2.py` y `reel2.py`.
6. **Adapta las pruebas**: `prueba_sistema.py` exige `"mps"` en dos sitios y
   `sysctl` en uno. Cámbialos por `"cuda"` y `psutil`.
7. **Ejecuta la prueba de humo**:
   ```powershell
   comfy\.venv\Scripts\python.exe herramientas\prueba_sistema.py
   ```
   Debe dar verde en todo menos transcripción hasta que hagas el §3.1.
8. **Genera una imagen de prueba** con un pedido existente antes de tocar nada
   más.
9. **Sustituye la transcripción** (§3.1) y vuelve a correr el banco.

---

## 6 · Reglas del proyecto que hay que respetar, vengas de donde vengas

No son estilo: cada una viene de un fallo que ya se pagó.

- **Ningún dato sin verificar en fuente primaria.** Si una cita no aguanta, se
  cambia el tema o se publica el desmentido, que suele ser mejor gancho.
- **Cero caras y cero manos.** SDXL falla ahí de forma estructural. Los humanos
  van como siluetas lejanas, de espaldas o en niebla. El negativo lleva pesos:
  `(face:1.6) (hands:1.6) (fingers:1.6)`.
- **Verificar en pantalla antes de decir que algo está listo.** Renderizar con
  Chromium headless y mirar la captura. Nunca dar por bueno porque el archivo se
  abrió o el script terminó sin error.
- **El portal se actualiza en el mismo turno en que nace el archivo.** Terminar
  un vídeo y no publicarlo cuenta como no haberlo terminado.
- **No editar módulos de un proceso que está corriendo.** Python los carga al
  arrancar: una hora de ediciones no llegó nunca al productor vivo y publicó 17
  vídeos que nadie veía.

---

## 7 · Lo que cambia de verdad al pasar a NVIDIA

Esta sección es la más importante del documento y se escribió el 14 de agosto de
2026, después de una auditoría con seis especialistas. Lo demás es instalación;
esto es lo que cambia el proyecto.

### 7.1 · Se desbloquea entrenar un LoRA del personaje

**Es el motivo real para migrar.** Llevamos días bloqueados en mantener el mismo
personaje entre imágenes, y todo lo probado ha fallado (está en `MEMORIA.md` §7).
La solución de fondo es entrenar un **LoRA del personaje**: modifica los pesos
del modelo en vez de inyectar una imagen en la atención, así que **no tiene
forma de copiar el encuadre** — que es exactamente lo que arruinaba IPAdapter.

**En Mac esto no es «más lento», es ROTO:**

- `bitsandbytes` es solo CUDA → sin optimizadores de 8 bits
- `xformers` y `flash-attn` no existen en Apple Silicon
- kohya desactiva el escalado de gradientes AMP en MPS → **fp16 se va a cero** y
  hay que entrenar en fp32, más memoria y más lento, en 16 GB compartidos

**En Windows con CUDA:** `kohya_ss` funciona y es lo estándar. Con *gradient
checkpointing* entra en 12 GB. Un usuario con una 3060 de 12 GB reporta 3-5 h
para 4000-5000 pasos; con nuestras 20-25 imágenes serían **entre hora y media y
tres horas por LoRA** (inferido de ese dato, no medido).

El fichero resultante (50-170 MB) se carga con `LoraLoader` y **funciona
también en el Mac**. O sea que se puede entrenar en el PC y producir en
cualquiera de los dos.

### 7.2 · Las semillas guardadas NO reproducen las mismas imágenes

**Cuenta con esto antes de migrar, no después.**

La documentación de HuggingFace Diffusers lo dice explícitamente: la
reproducibilidad se da entre plataformas **«dentro de cierta tolerancia»**, y la
GPU usa un generador de números aleatorios distinto del de la CPU. Las notas de
PyTorch añaden que ni con la misma semilla se garantiza el mismo resultado entre
dispositivos o versiones.

Qué significa en la práctica:

- El recetario (`recetario.py`) **sigue valiendo**: guarda prompts, ajustes y
  semillas dentro de los metadatos de cada PNG, y todo eso es portable.
- **La composición general se conserva** — el ruido latente inicial se genera en
  CPU, así que el punto de partida es el mismo.
- **Los detalles finos cambian.** Una imagen aprobada no volverá idéntica.

Y una regla que nace de aquí: **nunca uses las variantes `_gpu` del muestreador**
(`dpmpp_2m_sde_gpu` y compañía). Generan el ruido en el acelerador, así que la
divergencia entre plataformas es total en vez de sutil. Usa siempre la versión a
secas.

### 7.3 · Lo que sigue sin servir, aunque tengas NVIDIA

Para que no pierdas tiempo con lo que ya está descartado con medición (detalle
completo en `MEMORIA.md` §8):

| | |
|---|---|
| **fp8** en tarjetas serie 30 | La 3060/3090 son Ampere y **no tienen fp8 nativo** — eso empieza en la serie 40. Solo ahorra memoria, no da velocidad. |
| **FreeU / FreeU_V2** | Evidencia independiente **medida** de que empeora: FID 25,47 → 33,70 aplicándolo en todos los pasos, que es lo que hace el nodo. |
| **AlignYourSteps a 30 pasos** | El propio paper de NVIDIA dice que el efecto se desvanece al subir pasos. Solo sirve para bajar a 10-12. |
| **El refiner de SDXL** | Entrenado sobre latentes de SDXL base; Juggernaut es un ajuste fuerte y ya no son los que espera. |
| **GGUF para SDXL** | Su propio autor lo desaconseja: SDXL es convolucional y las conv2d se degradan al cuantizar. |

### 7.4 · Lo que sí conviene hacer el primer día en Windows

1. **`powercfg /change standby-timeout-ac 0`** antes de la primera tanda larga.
   Es el equivalente de `caffeinate` y es el error que costó una noche entera.
2. **Instalar `kohya_ss`** y entrenar el LoRA del personaje. Es lo que no se
   podía hacer aquí.
3. **Volver a `VAEDecode` normal** si lo habías cambiado por el de baldosas.
4. **Regenerar una imagen ya aprobada con su semilla** y comparar contra la
   original del Mac. Sirve para ver con tus ojos cuánto cambia, en vez de
   fiarte de este documento.
5. **Subir el CFG de exploración**: en Mac tenemos un flujo rápido a CFG 1.0
   donde el prompt negativo **no existe** (ver `MODELO.md`). Con una GPU rápida,
   30 pasos a CFG 4,5 cuestan 25 segundos y ya no hace falta ese apaño.

---

## 8 · Rendimiento medido, para que compares

En el Mac mini M4 de 16 GB, con Metal:

| | |
|---|---|
| Una imagen 720×1280, 8 pasos | **57 s** (mediana de 54 muestras) |
| Seis imágenes de un tema | 5,4 min |
| Composición de 6 láminas (Chromium) | 13 s |
| Montaje de un reel (ffmpeg) | 40 s |
| Música con loudness en dos pasadas | 1 s |
| **Un reel completo** | **≈ 8 min de máquina** |
| Transcripción | 2,6× tiempo real |
| Reconstrucción del catálogo | 0,0 s con caché (47,5 s sin ella) |

El cuello de botella nunca fue la GPU: es escribir el guion y auditar las
imágenes.
